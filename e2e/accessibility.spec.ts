import { expect, test } from '@playwright/test';
import { SAMPLE_PROFILE, stubSidecar } from './api-stub';

/**
 * Accessibility checks that only a browser can answer: axe-core needs layout,
 * computed styles and a real a11y tree. `npm run lint` cannot see any of it.
 *
 * The assertions are ratchets, not clean slates: the counts below are what the
 * app measures *today*, so the suite fails on regressions and stays green while
 * the backlog is worked down. Tighten the numbers as fixes land.
 */
const KNOWN_CRITICAL = 1;
//   button-name    — the effects <Select trigger> renders no accessible name when no effect is set
const KNOWN_SERIOUS = 2;
//   color-contrast — the v0.5.0 badge uses text-muted-foreground/50 (1.79:1)
//   nested-interactive — the voice profile card is a cursor-pointer div that wraps real buttons

test('axe-core finds no new critical or serious violations', async ({ page }, testInfo) => {
  await stubSidecar(page, { overrides: { '/profiles': [SAMPLE_PROFILE] } });
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 2, name: 'Voicebox' })).toBeVisible();

  await page.addScriptTag({ path: 'node_modules/axe-core/axe.min.js' });
  const results = await page.evaluate(
    async () =>
      (await (
        window as unknown as { axe: { run(o: unknown, c: unknown): Promise<unknown> } }
      ).axe.run(document, { resultTypes: ['violates'] })) as {
        violations: { id: string; impact: string | null; nodes: unknown[] }[];
      },
  );

  const byImpact = (impact: string) => results.violations.filter((v) => v.impact === impact);
  for (const v of results.violations) {
    testInfo.annotations.push({
      type: `axe:${v.impact}`,
      description: `${v.id} — ${v.nodes.length} node(s)`,
    });
  }
  expect(
    byImpact('critical').length,
    'axe critical rules — see PLAYWRIGHT_E2E.md',
  ).toBeLessThanOrEqual(KNOWN_CRITICAL);
  expect(
    byImpact('serious').length,
    'axe serious rules — see PLAYWRIGHT_E2E.md',
  ).toBeLessThanOrEqual(KNOWN_SERIOUS);
  expect(results.violations.length).toBeLessThanOrEqual(5);
});

test('the a11y tree names the navigation it renders', async ({ page }) => {
  await stubSidecar(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 2, name: 'Voicebox' })).toBeVisible();

  const snapshot = await page.locator('body').ariaSnapshot();
  for (const entry of ['link "Generate"', 'link "Stories"', 'link "Voices"', 'link "Settings"']) {
    expect(snapshot).toContain(entry);
  }
});

test('keyboard-only users reach every tab in order', async ({ page }) => {
  await stubSidecar(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 2, name: 'Voicebox' })).toBeVisible();

  const visited: string[] = [];
  for (let i = 0; i < 8; i++) {
    await page.keyboard.press('Tab');
    visited.push(
      await page.evaluate(() => {
        const el = document.activeElement as HTMLElement;
        return (
          el.getAttribute('aria-label') ??
          el.innerText?.trim().split('\n')[0] ??
          el.tagName.toLowerCase()
        );
      }),
    );
  }
  expect(visited).toEqual([
    'Generate',
    'Stories',
    'Captures',
    'Voices',
    'Effects',
    'Models',
    'Settings',
    'Import Voice',
  ]);
});

test('a popup closed with Escape returns focus to its trigger', async ({ page }) => {
  await stubSidecar(page, { overrides: { '/profiles': [SAMPLE_PROFILE] } });
  await page.goto('/');
  const modelPicker = page.getByRole('combobox').nth(1);
  await expect(modelPicker).toBeVisible();
  await modelPicker.click();
  await expect(page.getByRole('option')).not.toHaveCount(0);
  await page.keyboard.press('Escape');
  await expect(page.getByRole('option')).toHaveCount(0);
  await expect(modelPicker).toBeFocused();
});
