#!/usr/bin/env node
/**
 * Browser audit for the web build: a side-by-side of what a non-browser client
 * can learn about this app versus what a real Chromium session can learn.
 *
 *   bun run e2e:audit            # expects `bun run dev:web` on :5173 (starts nothing)
 *   E2E_AUDIT_URL=... bun run e2e:audit
 *
 * Prints a report and writes PNG/PDF/HAR evidence to test-results/audit/.
 * Deliberately not a test file: it measures and reports instead of asserting, so
 * it stays useful while the numbers move.
 */
import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Not test-results/: `playwright test` wipes that directory on every run.
const OUT = process.env.E2E_AUDIT_OUT ?? path.join(ROOT, 'tmp/audit');
const BASE = process.env.E2E_AUDIT_URL ?? 'http://127.0.0.1:5173';
const SIDECAR = process.env.E2E_SIDECAR_ORIGIN ?? 'http://127.0.0.1:17493';
const manifest = JSON.parse(
  readFileSync(path.join(ROOT, 'node_modules/.cache/voicebox-e2e/browser.json'), 'utf8'),
);
const PROFILE = {
  id: 'audit-1',
  name: 'Audit Voice',
  language: 'en',
  voice_type: 'preset',
  preset_engine: 'qwen3-tts',
  preset_voice_id: 'serena',
  generation_count: 0,
  sample_count: 0,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};
const READINESS = {
  ready: false,
  model_name: 'none',
  display_name: 'Not downloaded',
  size: '0.6B',
};
const ROUTES = {
  '/health': {
    status: 'healthy',
    model_loaded: true,
    model_downloaded: true,
    model_size: '0.6B',
    gpu_available: false,
    backend_type: 'cpu',
    backend_variant: 'cpu',
  },
  '/profiles': [PROFILE],
  '/profiles/presets': { engine: 'qwen3-tts', voices: [] },
  '/history': { items: [], total: 0, limit: 50, offset: 0 },
  '/stories': [],
  '/captures': { items: [], total: 0 },
  '/capture/readiness': { stt: READINESS, llm: READINESS },
  '/models/status': { models: [] },
  '/effects/presets': [],
  '/effects/available': { effects: [] },
  '/settings/generation': {
    max_chunk_chars: 600,
    crossfade_ms: 50,
    normalize_audio: true,
    autoplay_on_generate: false,
  },
  '/settings/captures': {
    stt_model: 'base',
    language: 'en',
    auto_refine: false,
    llm_model: '0.6B',
    smart_cleanup: true,
    self_correction: false,
    preserve_technical: true,
    allow_auto_paste: false,
    default_playback_voice_id: null,
    hotkey_enabled: false,
  },
  '/tasks/active': { downloads: [], generations: [] },
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const rows = [];
const report = (label, value) => {
  rows.push([label, value]);
  console.log(
    `${String(label).padEnd(38)} ${typeof value === 'string' ? value : JSON.stringify(value)}`,
  );
};

mkdirSync(OUT, { recursive: true });

/* ── 1. BEFORE: everything a non-browser client can know ─────────────────── */
console.log('\n── without a browser ──');
const html = await (await fetch(`${BASE}/`)).text();
report('raw HTML bytes', html.length);
report('UI text in that HTML', /Voicebox/.test(html) ? 'yes' : 'none — body is an empty #root');
report('buttons / links / inputs', {
  buttons: (html.match(/<button/g) ?? []).length,
  links: (html.match(/<a /g) ?? []).length,
  inputs: (html.match(/<input/g) ?? []).length,
});
report(
  'Node fetch of the sidecar',
  await fetch(`${SIDECAR}/health`)
    .then((r) => r.status)
    .catch((e) => `unreachable (${e.cause?.code ?? e.name})`),
);
let nodeHttps = 'n/a';
try {
  nodeHttps = await fetch('https://github.com', { signal: AbortSignal.timeout(15000) }).then(
    (r) => `status ${r.status}`,
  );
} catch (e) {
  nodeHttps = `TLS failure: ${e.cause?.code ?? e.message}`;
}
report('Node fetch of any https site', nodeHttps);
report('performance / a11y / screenshot', 'not obtainable without a browser');

/* ── 2. AFTER: the same questions, asked of a real browser ───────────────── */
console.log('\n── with Playwright + Chromium ──');
const browser = await chromium.launch({
  executablePath: manifest.executablePath,
  env: { ...process.env, LD_LIBRARY_PATH: manifest.ldLibraryPath },
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
});

async function boot(context, { record = true } = {}) {
  const page = await context.newPage();
  const requests = [];
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (m) => m.type() === 'error' && consoleErrors.push(m.text().slice(0, 120)));
  page.on('pageerror', (e) => pageErrors.push(String(e).slice(0, 120)));
  if (record) {
    await page.route(
      (u) => u.origin === SIDECAR,
      async (route) => {
        const pathname = new URL(route.request().url()).pathname;
        requests.push({
          method: route.request().method(),
          path: pathname,
          body: route.request().postData(),
        });
        const hit = Object.keys(ROUTES)
          .filter((k) => pathname.startsWith(k))
          .sort((a, b) => b.length - a.length)[0];
        return route.fulfill({
          status: hit ? 200 : 404,
          contentType: 'application/json',
          body: JSON.stringify(hit ? ROUTES[hit] : { detail: 'not stubbed by the audit harness' }),
        });
      },
    );
  }
  return { page, requests, consoleErrors, pageErrors };
}

const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  recordHar: { path: path.join(OUT, 'load.har'), mode: 'minimal' },
});
const { page, requests, consoleErrors, pageErrors } = await boot(context);
await page.addInitScript(() => {
  window.__audit = { lcp: 0, cls: 0 };
  new PerformanceObserver((l) => {
    for (const e of l.getEntries()) window.__audit.lcp = e.startTime;
  }).observe({ type: 'largest-contentful-paint', buffered: true });
  new PerformanceObserver((l) => {
    for (const e of l.getEntries()) if (!e.hadRecentInput) window.__audit.cls += e.value;
  }).observe({ type: 'layout-shift', buffered: true });
});
const t0 = Date.now();
await page.goto(BASE, { waitUntil: 'load' });
await page.getByRole('heading', { level: 2, name: 'Voicebox' }).waitFor();
const interactiveMs = Date.now() - t0;

const metrics = await page.evaluate(() => {
  const nav = performance.getEntriesByType('navigation')[0];
  const paint = Object.fromEntries(
    performance.getEntriesByType('paint').map((p) => [p.name, Math.round(p.startTime)]),
  );
  const res = performance.getEntriesByType('resource');
  return {
    ttfb_ms: Math.round(nav.responseStart - nav.fetchStart),
    dcl_ms: Math.round(nav.domContentLoadedEventEnd),
    fcp_ms: paint['first-contentful-paint'] ?? null,
    lcp_ms: Math.round(window.__audit.lcp),
    cls: +window.__audit.cls.toFixed(4),
    modules: res.length,
    js_kb: Math.round(
      res.filter((r) => /\.(t|j)sx?$/.test(r.name)).reduce((a, r) => a + r.encodedBodySize, 0) /
        1024,
    ),
    elements: document.querySelectorAll('*').length,
    text_chars: document.body.innerText.replace(/\s+/g, ' ').trim().length,
  };
});
report('rendered DOM', { elements: metrics.elements, text_chars: metrics.text_chars });
report('time to interactive', `${interactiveMs} ms`);
report(
  'web vitals',
  `TTFB ${metrics.ttfb_ms} · DCL ${metrics.dcl_ms} · FCP ${metrics.fcp_ms} · LCP ${metrics.lcp_ms} · CLS ${metrics.cls}`,
);
report('dev-mode payload', `${metrics.modules} modules, ${metrics.js_kb} KB of JS`);
report(
  'sidecar calls observed',
  [...new Set(requests.map((r) => `${r.method} ${r.path}`))].slice(0, 8),
);
report('page errors / console errors', {
  pageErrors: pageErrors.length,
  consoleErrors: consoleErrors.length,
});
await page.screenshot({ path: path.join(OUT, 'app-1440.png') });
await page.pdf({ path: path.join(OUT, 'app-a4.pdf'), format: 'A4', printBackground: true });

// What only exists after an interaction.
const picker = page.getByRole('combobox').nth(1);
await picker.click();
await sleep(500);
const engines = await page.getByRole('option').allInnerTexts();
await page.keyboard.press('Escape');
report('engine list (needs a click)', `${engines.length}: ${engines.slice(0, 3).join(', ')}…`);

// Accessibility engine.
await page.addScriptTag({ path: path.join(ROOT, 'node_modules/axe-core/axe.min.js') });
const axe = await page.evaluate(
  async () => await window.axe.run(document, { resultTypes: ['violates'] }),
);
report('axe-core', {
  rules: axe.passes.length + axe.violations.length,
  passed: axe.passes.length,
  violations: axe.violations.map((v) => `${v.id}(${v.impact})`).join(' '),
});

// Responsive behaviour.
const sweep = [];
for (const width of [320, 390, 768, 1440]) {
  await page.setViewportSize({ width, height: 880 });
  await sleep(500);
  sweep.push({
    width,
    overflow_px: await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    ),
  });
}
report('horizontal overflow by width', sweep);

// Fault handling.
await page.locator('textarea[name="text"]').fill('Audit sentence.');
await page.getByRole('button', { name: 'Generate speech' }).click();
await sleep(1500);
report(
  'generation request body',
  JSON.parse(requests.find((r) => r.path === '/generate' && r.method === 'POST')?.body ?? '{}'),
);

const dead = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
await dead.goto(BASE, { waitUntil: 'load' }).catch(() => {});
await dead.waitForTimeout(4000);
const deadText = await dead
  .locator('body')
  .innerText()
  .catch(() => '');
report('with the sidecar down', {
  shows_error: /error|failed/i.test(deadText),
  stuck_on_splash: /warming up tensors|initializing synthesizer/i.test(deadText),
  snippet: deadText.replace(/\s+/g, ' ').slice(0, 90),
});
await dead.screenshot({ path: path.join(OUT, 'sidecar-down.png') });

await context.close(); // flushes the HAR to disk
const har = JSON.parse(readFileSync(path.join(OUT, 'load.har'), 'utf8'));
report(
  'HAR captured',
  `${har.log.entries.length} entries → ${path.relative(ROOT, path.join(OUT, 'load.har'))}`,
);
report(
  'evidence files',
  ['app-1440.png', 'app-a4.pdf', 'load.har', 'sidecar-down.png'].map(
    (f) => `${f} (${Math.round(statSync(path.join(OUT, f)).size / 1024)} KB)`,
  ),
);

writeFileSync(
  path.join(OUT, 'audit.json'),
  JSON.stringify(
    {
      before: { html_bytes: html.length, node_https: nodeHttps },
      after: {
        metrics,
        engines,
        axe_violations: axe.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          nodes: v.nodes.length,
        })),
        sweep,
      },
    },
    null,
    2,
  ),
);
await browser.close();
console.log(`\nwrote ${path.relative(ROOT, OUT)}/audit.json`);
