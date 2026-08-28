import { expect, test } from '@playwright/test';
import { SAMPLE_PROFILE, stubSidecar } from './api-stub';

/**
 * Responsive behaviour of the web shell.
 *
 * A number alone is misleading here: `scrollWidth - clientWidth` is 0 at 360 px, which
 * looks like "no overflow", but only because AppFrame sets `overflow-hidden` and clips
 * the excess. The screenshot is what reveals it — the sidebar is `fixed w-20` with no
 * responsive variant, so the editor is cut off rather than reflowed. Hence the fixme:
 * the assertion is written and will start failing the moment somebody removes the clip.
 */
test('phone width reflows instead of clipping the editor', async ({ page }, testInfo) => {
  test.fixme(
    true,
    'known issue: Sidebar is `fixed … w-20` at every breakpoint and AppFrame clips with `overflow-hidden` — see PLAYWRIGHT_E2E.md',
  );

  await stubSidecar(page, { overrides: { '/profiles': [SAMPLE_PROFILE] } });
  await page.setViewportSize({ width: 360, height: 780 });
  await page.goto('/');

  const layout = await page.evaluate(() => {
    const sidebar = document.querySelector('a[aria-label="Models"]')?.closest('div');
    const editor = document.querySelector('textarea[name="text"]');
    const right = (el: Element | null) => (el ? el.getBoundingClientRect().right : 0);
    return {
      viewport: window.innerWidth,
      sidebar_right: Math.round(right(sidebar?.firstElementChild ?? null)),
      editor_right: Math.round(editor?.getBoundingClientRect().right ?? 0),
      editor_visible_width: Math.round(editor?.getBoundingClientRect().width ?? 0),
    };
  });
  testInfo.annotations.push({ type: 'measured', description: JSON.stringify(layout) });

  // Nothing may extend past the viewport, and the editor must keep a usable width.
  expect(layout.editor_right).toBeLessThanOrEqual(layout.viewport);
  expect(layout.editor_visible_width).toBeGreaterThanOrEqual(240);
});

test('the rail stays usable at every width we claim to support', async ({ page }) => {
  await stubSidecar(page);
  await page.goto('/');
  for (const width of [390, 768, 1024, 1440, 1920]) {
    await page.setViewportSize({ width, height: 900 });
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('heading', { level: 2, name: 'Voicebox' })).toBeVisible();
  }
});
