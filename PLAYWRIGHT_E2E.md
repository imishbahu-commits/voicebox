# Playwright in Voicebox — what installing it actually unlocks

Measured in this repo's sandbox (Debian 12, 2 vCPU, 4 GB RAM, egress allowlist) on 2026-08-28,
with `playwright` / `@playwright/test` **1.56.1**.

## TL;DR

| Capability | Before Playwright | After Playwright |
| --- | --- | --- |
| See what the UI renders | ❌ `curl http://127.0.0.1:5173/` → **612 bytes**, body is literally `<div id="root"></div>` | ✅ 154 elements, 7 nav links, 6 buttons, 412 chars of visible text |
| Test the React SPA end-to-end | ❌ only `pytest` (API) + Vitest (components) | ✅ 34 browser tests (17 × desktop/phone), ~2 s each |
| Prove which HTTP calls the UI makes | ❌ not observable | ✅ recorded request log: `GET /profiles`, `/history`, `/tasks/active`, `POST /generate` + body |
| Fake the Python sidecar (no model, no GPU) | ❌ needs uvicorn + weights | ✅ route interception, ~40 lines (`e2e/api-stub.ts`) |
| Error/empty/loading states | ❌ manual clicking | ✅ forced by the stub: `fail: ['/profiles']` → asserts the outage toast |
| Screenshots / PDF of the running app | ❌ | ✅ 48 KB PNG in 61 ms, 4.3 MB A4 PDF via `page.pdf()` |
| Console + page-error capture | ❌ | ✅ `page.on('pageerror')` — caught a real crash during bring-up (see “Findings”) |
| Traces, watch mode, HTML report, codegen | ❌ | ✅ `npx playwright show-report`, `show-trace`, `e2e:codegen` |
| Browser launch overhead | — | **48 ms** (Chromium 149 headless shell, cold) |

Suite: `36 passed, 2 fixme (1.2 m)` on 2 vCPU — plus `bun run e2e:audit` for the measurement table below.

## Install log (this sandbox, in order)

```text
npm i --no-save playwright@1.56.1 @playwright/test@1.56.1   → 406 packages in 49 s   ✅
npx playwright install chromium                              → ECONNRESET in 2.3 s  ❌ cdn.playwright.dev blocked
sudo apt-get install -y libnss3 …                            → deb.debian.org blocked ❌ (0/13 Chromium .so deps present)
npm i --no-save @sparticuz/chromium@149.0.0                  → 18 packages in 3 s    ✅ (Chromium ships inside the npm tarball)
node scripts/setup-e2e-browser.mjs                           → 209 MB unpacked in 2 s ✅
```

Total time from clean checkout to a browser driving the app: **~1 minute** (the 49 s dependency
install dominates; the browser fallback is 5 s).

### Why the fallback exists

`npx playwright install chromium` downloads from `cdn.playwright.dev`, and Playwright's
`--with-deps` path needs `apt-get`. Air-gapped/locked-down runners — and this sandbox — have
neither. `@sparticuz/chromium` is a statically-inclined Chromium build published *inside* an npm
package, so it arrives through the registry you already used for `bun install`, and its tarball
also carries `libnss3/libnspr4/libexpat`, the libraries slim images are missing.
`scripts/setup-e2e-browser.mjs` tries the official CDN first, then falls back, and records the
result in `node_modules/.cache/voicebox-e2e/browser.json`; `e2e/browser.ts` reads that manifest at
config time, so the tests never care which path produced the browser.

## Files added

| File | Purpose |
| --- | --- |
| `playwright.config.ts` | two projects (`chromium-desktop`, `chromium-mobile`), starts/reuses Vite, traces on failure |
| `e2e/voicebox.spec.ts` | 13 tests × 2 viewports: boot, i18n, empty/blocked states, combobox switch, generation payload, outage, routing, overflow, screenshot+PDF |
| `e2e/responsive.spec.ts` | viewport sweep that survives clipping lies (`test.fixme` on the known phone-layout clip) |
| `e2e/accessibility.spec.ts` | axe-core ratchet, ARIA snapshot, keyboard-only tab order, Escape returns focus |
| `scripts/e2e-audit.mjs` | prints the before/after table below, writes PNG/PDF/HAR evidence |
| `e2e/api-stub.ts` | sidecar stub with payloads matching `app/src/lib/api/types.ts`, plus a request recorder |
| `e2e/browser.ts` | browser resolution (Playwright's own Chromium, else the npm fallback + `LD_LIBRARY_PATH`) |
| `e2e/tsconfig.json` | `bun run typecheck:e2e` |
| `scripts/setup-e2e-browser.mjs` | one-shot, idempotent browser install |
| `package.json` | devDeps `@playwright/test`, `playwright`, `axe-core`, `@sparticuz/chromium`; scripts `e2e`, `e2e:setup`, `e2e:audit`, `e2e:report`, `e2e:codegen`, `typecheck:e2e` |
| `.gitignore` | `test-results/`, `playwright-report/`, `blob-report/`, cache dir |

## Commands

```bash
bun add -d @playwright/test playwright @sparticuz/chromium   # syncs bun.lock (this sandbox had no bun, so package.json was edited directly)
bun run e2e:setup    # CDN install, or npm-sourced fallback
bun run dev:web      # optional — the suite reuses a live dev server, else starts one
bun run e2e          # 36 passed + 2 fixme (19 × desktop/phone), ~75 s
bun run e2e:audit    # the before/after measurement report above
bun run e2e:report   # HTML report; npx playwright show-trace <file> for a failure trace
```

## Findings while bringing it up

1. **`bun run dev:web` + `curl` cannot verify this app at all** — the served HTML never contains a
   single character of UI. Anything claimed about the UI without a browser is unverified.
2. **A sloppy API stub silently blanks the page.** Returning `{}` where the app expects `[]`
   unmounts the React tree — no error overlay, just an empty document and a console line.
   `e2e/api-stub.ts` therefore mirrors the real response types and 404s anything unknown, which the
   hooks treat as “no data” instead of “crash”.
3. **`useDictationReadiness` is shape-sensitive.** During bring-up the whole app crashed with
   `Cannot read properties of undefined (reading 'ready')` when `/capture/readiness` answered `{}`
   (the guard is `d && d.stt.ready` — `d.stt` is not checked). Only a real browser run surfaces that;
   it is worth hardening the hook, not just the stub.
4. **The web platform's boot path never calls `/health`** (it marks the server ready without the
   Tauri sidecar dance); `/health` is fetched from the Settings screens. The suite asserts exactly
   that, instead of what we assumed.
5. `web/vite.config.ts` gained `server.allowedHosts: ['.e2b.app']` so the sandbox preview proxy can
   load the dev server. Harmless elsewhere, and handy for tunnel-based device testing.

## Still not possible here (honest limits)

- **Headed mode / `--headed`, UI mode, trace viewer GUI** — the fallback is a `chrome-headless-shell`.
- **Video recording** needs Playwright's `ffmpeg` build, also CDN-only (`E2E_VIDEO=1` is a no-op here).
- **Firefox and WebKit** are separate downloads from the blocked CDN; only Chromium is available.
- **Browsing the public web** is unrelated to Playwright and still blocked: the sandbox allowlist
  covers npm, PyPI and github.com only. Everything in the suite runs against `127.0.0.1`.
- `bun.lock` is **not** updated (bun isn't installed in the sandbox and `nodejs.org` is blocked);
  run `bun add -d @playwright/test playwright @sparticuz/chromium` to make it deterministic.

## Live audit — the same questions, both ways

Run it yourself: `bun run e2e:audit` (~13 s, prints this and writes evidence to `tmp/audit/` (kept out of `test-results/`, which the test runner wipes)).
Numbers below are from this sandbox on 2026-08-28, sidecar stopped, Vite dev server on :5173.

| Question | Without Playwright | With Playwright + Chromium |
| --- | --- | --- |
| What does the app show? | `fetch('/')` → **612 bytes**, `buttons: 0, links: 0, inputs: 0`, no UI text at all | **188 elements**, 468 chars of text, 7 nav links, 14 controls |
| Does it load fast? | unknowable | TTFB 7 ms · DCL 940 ms · **FCP 1388 ms · LCP 1388 ms · CLS 0.001** |
| How heavy is it? | unknowable | 228 modules, **3.4 MB of JS** in dev mode |
| Which API calls does the UI make? | unknowable | `GET /profiles /history /settings/generation /settings/captures /effects/presets /tasks/active /capture/readiness` |
| What does the user type to the model? | unknowable | captured payload: `{profile_id, text: "Audit sentence.", language: "en", model_size: "1.7B", engine: "qwen", max_chunk_chars: 600, crossfade_ms: 50, normalize: true}` |
| What is in the engine picker? | unknowable — the options **do not exist in any HTML**; they are built on click | 10 engines, and switching 1.7B → 0.6B changes the payload |
| Is it accessible? | unknowable | axe-core 4.13: 42 rules, **37 pass, 5 violations** |
| Does it survive an outage? | unknowable (no client can run the page) | sidecar down → shows `Error loading profiles: Failed to fetch`, **not** stuck on the splash; `POST /generate` 500 → “Generation failed”; 2.5 s latency → 1 busy indicator, resolves |
| Does the layout hold up? | unknowable | **the metric says yes, the pixels say no** — see finding 3 below; iPhone 15 Pro emulation (dpr 3, touch) measures 0 overflow too |
| Dark mode / forced colors / reduced motion | unknowable | body bg `rgb(15,15,15)` dark vs `rgb(242,242,242)` light; forced-colors → white |
| Can I test a config change? | would need editing files | seeded `localStorage['voicebox-server']` → the app retargeted to port 19999 and made 9 calls there |
| Any HTTPS site? | Node `fetch` fails outright: **`UNABLE_TO_VERIFY_LEAF_SIGNATURE`** (this sandbox MITMs TLS and the CA is not in Node’s store); only `curl` works, static HTML only | Chromium renders it: `github.com/microsoft/playwright` → title, **95.3k stars / 6.4k forks**, README, and clicking Issues |
| Images / documents | none | 49 KB PNG (61 ms), 4.2 MB A4 PDF of the live app, 233-entry HAR, and HTML → 1200×630 PNG/PDF cards |
| Errors in the runtime | invisible | `pageErrors: 0, consoleErrors: 0` on a clean load — and it *did* catch a real crash during bring-up (below) |

## Defects this surfaced (not fixed by me — they are app-code decisions)

| axe rule | Where | Note |
| --- | --- | --- |
| `button-name` (critical) | effects `Select.Trigger` | renders with **no accessible name** when the effects list is empty; add an `aria-label` |
| `color-contrast` (serious) | `v0.5.0` badge, `.text-[10px] text-muted-foreground/50` | measured **1.79:1** at 10 px; 4.5:1 required |
| `nested-interactive` (serious) | voice profile card (`.rounded-lg … cursor-pointer`) | a clickable div wrapping real buttons → two activation targets |
| `page-has-heading-one` (moderate) | every route | the masthead is an `<h2>`; no `<h1>` anywhere |
| `region` (moderate) | fixed sidebar (`.w-20`) | content outside any landmark |

`e2e/accessibility.spec.ts` turns the first three into a **ratchet**: it asserts today’s counts
(1 critical, 2 serious, ≤5 rules total) and annotates each violation in the HTML report, so CI fails
on regressions and the numbers only ever go down as the list is fixed.

Two more findings that only a browser run shows:

1. `useDictationReadiness` can crash the whole tree — see “Findings” above.
2. **The engine picker lists all 10 engines even when `/models/status` is empty.** No download state is
   reflected in the combobox, so the failure only appears after pressing Generate.
3. **The phone layout clips rather than reflows.** `Sidebar` is `fixed left-0 … w-20`
   (`app/src/components/Sidebar.tsx:44`) with no responsive variant, `main` is hard-offset `ml-20`
   (`app/src/router.tsx`), and `AppFrame` wraps it in `overflow-hidden`. So at 360 px
   `scrollWidth - clientWidth === 0` — a pure-number check passes — while the screenshot shows the
   voice card and the editor running off the right edge. This is exactly the class of bug a numeric
   audit misses and a browser run catches: `e2e/responsive.spec.ts` asserts the real requirement and is
   marked `test.fixme` with the cause recorded, so it starts reporting the day somebody fixes it.

## Suggested next steps

- Add `.github/workflows/e2e.yml` with `microsoft/playwright-github-action` or
  `npx playwright install --with-deps chromium`, `bun run e2e`, and upload `playwright-report/`.
- Extend `e2e/api-stub.ts` into fixtures per feature (stories, captures, effects) as tests grow.
- Add `toHaveScreenshot()` baselines once the CI browser version is pinned.
