import { defineConfig, devices } from '@playwright/test';
import { chromiumLaunchOptions } from './e2e/browser';

/**
 * Browser (E2E) tests for the web build of Voicebox.
 *
 *   bun run e2e:setup   # one-time: make sure a Chromium build is available
 *   bun run e2e         # runs the suite (starts Vite itself, or reuses a dev server)
 *
 * The suite talks to `web/` (Vite) and stubs the Python sidecar in the browser —
 * see e2e/api-stub.ts — so it is fast and needs no models or GPU.
 */
const PORT = Number(process.env.E2E_PORT ?? 5173);
const BASE_URL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI
    ? [['list'], ['github'], ['html', { open: 'never' }]]
    : [['list'], ['html', { open: 'never' }]],
  timeout: 60_000,
  expect: { timeout: 10_000 },
  outputDir: 'test-results',
  use: {
    baseURL: BASE_URL,
    launchOptions: chromiumLaunchOptions(),
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    // Recording requires Playwright's ffmpeg build; keep it opt-in.
    video: process.env.E2E_VIDEO ? 'retain-on-failure' : 'off',
  },
  projects: [
    { name: 'chromium-desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'chromium-mobile', use: { ...devices['Pixel 7'] } },
  ],
  // Reuse `bun run dev:web` when it is already up, otherwise boot it for the run.
  webServer: {
    command:
      process.env.E2E_WEB_SERVER_COMMAND ??
      `bun run --cwd web dev -- --host 127.0.0.1 --port ${PORT} --strictPort`,
    url: BASE_URL,
    reuseExistingServer: true,
    timeout: 120_000,
    stdout: 'ignore',
  },
});
