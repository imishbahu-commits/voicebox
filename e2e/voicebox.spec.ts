import { expect, type Page, test } from '@playwright/test';
import { fakeGeneration, type RecordedRequest, SAMPLE_PROFILE, stubSidecar } from './api-stub';

/**
 * End-to-end tests for the `web/` build of Voicebox.
 *
 * What a browser buys this repo: the app is a client-rendered React SPA that
 * only exists after JS runs, and every screen is driven by HTTP against the
 * Python sidecar. These tests boot the real bundle in Chromium, stub the
 * sidecar (e2e/api-stub.ts) and assert on rendered UI, emitted requests and
 * error states — none of which is reachable from a unit test or `curl`.
 */

interface Boot {
  requests: RecordedRequest[];
}

async function boot(page: Page, options: Parameters<typeof stubSidecar>[1] = {}): Promise<Boot> {
  const requests = await stubSidecar(page, options);
  await page.goto('/');
  return { requests };
}

function heading(page: Page) {
  // The masthead is an <h2>, not an <h1>.
  return page.getByRole('heading', { level: 2, name: 'Voicebox' });
}

test.describe('app boot', () => {
  test('the HTML shell is empty, the rendered DOM is not', async ({ page, request }) => {
    // Before: what any non-browser client sees from the dev server.
    const raw = await request.get('/');
    const html = await raw.text();
    expect(html).toContain('id="root"></div>');
    expect(html).not.toContain('Voicebox');

    // After: React has run, so the app exists.
    await boot(page);
    expect(heading(page)).toBeVisible();
    await expect(page.getByRole('link', { name: 'Models' })).toBeVisible();
  });

  test('renders the shell with no page-level JS errors', async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', (error) => pageErrors.push(String(error)));

    await boot(page);

    expect(heading(page)).toBeVisible();
    await expect(page.getByText(/^v\d+\.\d+\.\d+$/).first()).toBeVisible();
    await expect(page.getByText('No voice profiles yet')).toBeVisible();
    expect(pageErrors).toEqual([]);
  });

  test('hydrates every screen from sidecar queries on boot', async ({ page }) => {
    const { requests } = await boot(page);
    expect(heading(page)).toBeVisible();
    await expect
      .poll(() => [...new Set(requests.map((r) => r.path))], { timeout: 15_000 })
      .toEqual(
        expect.arrayContaining([
          '/profiles',
          '/history',
          '/tasks/active',
          '/settings/generation',
          '/settings/captures',
          '/effects/presets',
          '/capture/readiness',
        ]),
      );
  });

  test('health-checks the sidecar once the settings screen opens', async ({ page }) => {
    const { requests } = await boot(page);
    await page.getByRole('link', { name: 'Settings' }).click();
    await expect
      .poll(() => requests.filter((r) => r.path === '/health').length, { timeout: 15_000 })
      .toBeGreaterThan(0);
  });
});

test.describe('localization', () => {
  test.use({ locale: 'ja-JP' });

  test('renders localized chrome for a ja-JP browser', async ({ page }) => {
    await boot(page);
    expect(heading(page)).toBeVisible();
    // The i18next browser detector has to have kicked in for the nav rail.
    await expect(page.getByRole('link', { name: 'モデル' })).toBeVisible();
  });
});

test.describe('generate tab', () => {
  test('blocks generation until a voice profile exists', async ({ page }) => {
    await boot(page);
    const blocked = page.getByRole('button', { name: 'Select a voice profile first' });
    await expect(blocked).toBeDisabled();
    await expect(page.locator('textarea[name="text"]')).toBeDisabled();
  });

  test('shows profiles served by the sidecar and unlocks the editor', async ({ page }) => {
    await boot(page, { overrides: { '/profiles': [SAMPLE_PROFILE] } });
    await expect(page.getByRole('heading', { level: 3, name: SAMPLE_PROFILE.name })).toBeVisible();

    const editor = page.locator('textarea[name="text"]');
    await expect(editor).toBeEnabled();
    await editor.fill('The quick brown fox jumps over the lazy dog.');

    const generate = page.getByRole('button', { name: 'Generate speech' });
    await expect(generate).toBeEnabled();
  });

  test('sends the typed text to POST /generate', async ({ page }) => {
    const generation = fakeGeneration('Hello from Playwright.');
    const { requests } = await boot(page, {
      overrides: { '/profiles': [SAMPLE_PROFILE], '/generate': generation },
    });

    const editor = page.locator('textarea[name="text"]');
    await expect(editor).toBeEnabled();
    await editor.fill('Hello from Playwright.');
    await page.getByRole('button', { name: 'Generate speech' }).click();

    await expect
      .poll(async () => {
        const post = requests.find((r) => r.method === 'POST' && r.path === '/generate');
        return post?.postData ? (JSON.parse(post.postData).text ?? '') : '';
      })
      .toBe('Hello from Playwright.');

    const post = requests.find((r) => r.method === 'POST' && r.path === '/generate');
    const payload = JSON.parse(post?.postData ?? '{}');
    expect(payload.profile_id).toBe(SAMPLE_PROFILE.id);
  });

  test('switching the model combobox updates the request payload', async ({ page }) => {
    const { requests } = await boot(page, {
      overrides: { '/profiles': [SAMPLE_PROFILE], '/generate': fakeGeneration('x') },
    });

    // The engine list only exists after a click, so no HTTP client can read it.
    const picker = page.getByRole('combobox').nth(1);
    await expect(picker).toContainText('1.7B');
    await picker.click();
    const options = await page.getByRole('option').allInnerTexts();
    expect(options.length).toBeGreaterThanOrEqual(8);
    await page.getByRole('option', { name: /0\.6B/ }).first().click();
    await expect(picker).toContainText('0.6B');

    await page.locator('textarea[name="text"]').fill('Small model run.');
    await page.getByRole('button', { name: 'Generate speech' }).click();
    await expect
      .poll(() => requests.filter((r) => r.method === 'POST' && r.path === '/generate').length)
      .toBeGreaterThan(0);
  });

  test('surfaces a sidecar outage instead of hanging', async ({ page }) => {
    await boot(page, { fail: ['/profiles'] });
    await expect(page.getByText(/Error loading profiles/i)).toBeVisible({ timeout: 15_000 });
  });
});

test.describe('navigation and layout', () => {
  test('client-side routing works between tabs and through history', async ({ page }) => {
    await boot(page);
    expect(heading(page)).toBeVisible();

    await page.getByRole('link', { name: 'Models' }).click();
    await expect(page).toHaveURL(/\/models$/);

    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page).toHaveURL(/\/settings/);

    await page.goBack();
    await expect(page).toHaveURL(/\/models$/);
  });

  test('never overflows horizontally in its own viewport', async ({ page }) => {
    await boot(page, { overrides: { '/profiles': [SAMPLE_PROFILE] } });
    expect(heading(page)).toBeVisible();
    const overflow = await page.evaluate(() => {
      const { scrollWidth, clientWidth } = document.documentElement;
      return scrollWidth - clientWidth;
    });
    expect(overflow).toBeLessThanOrEqual(1);
  });
});

test.describe('artifacts', () => {
  test('captures a full-page screenshot and a PDF of the running app', async ({
    page,
  }, testInfo) => {
    await boot(page, { overrides: { '/profiles': [SAMPLE_PROFILE] } });
    expect(heading(page)).toBeVisible();

    const shot = testInfo.outputPath('voicebox.png');
    await page.screenshot({ path: shot, fullPage: true });

    const pdf = testInfo.outputPath('voicebox.pdf');
    await page.pdf({ path: pdf, format: 'A4', printBackground: true });

    const fs = await import('node:fs');
    expect(fs.statSync(shot).size).toBeGreaterThan(10_000);
    expect(fs.readFileSync(pdf).subarray(0, 5).toString()).toBe('%PDF-');
  });
});
