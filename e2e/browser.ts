/**
 * Browser resolution for the Playwright suite.
 *
 * Normally Playwright launches the Chromium build it downloaded itself
 * (`npx playwright install chromium`). That needs access to
 * `cdn.playwright.dev`, which is not reachable from every CI/sandbox network.
 * When that download is unavailable, `scripts/setup-e2e-browser.mjs` extracts a
 * Chromium build that ships inside the `@sparticuz/chromium` npm package (npm is
 * always reachable if `bun/npm install` worked) into
 * `node_modules/.cache/voicebox-e2e`, together with the shared libraries
 * (libnss3/libnspr4/…) Chromium needs on slim images.
 *
 * Either way the suite talks to a standard Chromium over CDP, so the tests are
 * identical on a laptop with `playwright install` and on a locked-down runner.
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export interface ChromiumLaunchOptions {
  executablePath?: string;
  env?: Record<string, string>;
  args?: string[];
}

/** Written by scripts/setup-e2e-browser.mjs */
export const FALLBACK_BROWSER_MANIFEST = path.resolve(
  'node_modules/.cache/voicebox-e2e/browser.json',
);

const CHROMIUM_RELATIVE_PATHS = [
  'chrome-linux/chrome',
  'chrome-linux64/chrome',
  'chrome-mac/Chromium.app/Contents/MacOS/Chromium',
  'chrome-win/chrome.exe',
];

function findPlaywrightChromium(): string | undefined {
  const root = path.join(os.homedir(), '.cache', 'ms-playwright');
  if (!existsSync(root)) return undefined;
  for (const entry of readdirSync(root)) {
    if (!entry.startsWith('chromium-')) continue;
    for (const relative of CHROMIUM_RELATIVE_PATHS) {
      const candidate = path.join(root, entry, relative);
      if (existsSync(candidate)) return candidate;
    }
  }
  return undefined;
}

/**
 * Flags that keep Chromium stable inside containers: no setuid sandbox, no
 * /dev/shm exhaustion, and software rendering (no GPU in CI sandboxes).
 */
const CONTAINER_ARGS = [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-dev-shm-usage',
  '--disable-gpu',
];

export function chromiumLaunchOptions(): ChromiumLaunchOptions {
  const args = [...CONTAINER_ARGS];

  // Playwright's own build: it knows its matching binary, just pass the args.
  if (findPlaywrightChromium()) return { args };

  if (!existsSync(FALLBACK_BROWSER_MANIFEST)) {
    throw new Error(
      'e2e: no Chromium found. Run `npx playwright install chromium`, ' +
        'or `bun run e2e:setup` for the offline npm-sourced fallback.',
    );
  }

  const manifest = JSON.parse(readFileSync(FALLBACK_BROWSER_MANIFEST, 'utf8')) as {
    executablePath: string;
    ldLibraryPath?: string;
    chromiumVersion?: string;
  };
  if (!existsSync(manifest.executablePath)) {
    throw new Error(
      `e2e: stale browser manifest, ${manifest.executablePath} is gone. Re-run bun run e2e:setup`,
    );
  }
  return {
    executablePath: manifest.executablePath,
    args,
    // Slim images do not ship libnss3/libnspr4; the fallback carries its own copy.
    env: manifest.ldLibraryPath
      ? { ...process.env, LD_LIBRARY_PATH: manifest.ldLibraryPath }
      : undefined,
  };
}
