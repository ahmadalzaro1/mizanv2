import { test, expect } from '@playwright/test'

test.describe('Bias Auditor (Lina)', () => {

  test('page loads without error', async ({ page }) => {
    await page.goto('/audit')

    // Page should not redirect to /login (auth works)
    await page.waitForTimeout(2_000)
    expect(page.url()).toContain('/audit')
  })

  test('displays cached results OR empty state', async ({ page }) => {
    await page.goto('/audit')

    // Wait for the page to settle after the API call
    // Two possible states:
    // 1. Cached results exist: metrics section visible
    // 2. No cached results: empty state with start button

    const hasResults = await page.getByText('F1').isVisible({ timeout: 10_000 }).catch(() => false)

    if (hasResults) {
      // Cached results path: verify metrics and chart
      await expect(page.getByText('الدقة')).toBeVisible()
      await expect(page.getByText('الاسترجاع')).toBeVisible()

      // BiasChart SVG should be visible with rect elements (horizontal bars)
      const svg = page.locator('svg')
      await expect(svg.first()).toBeVisible({ timeout: 10_000 })
      const rects = svg.first().locator('rect')
      expect(await rects.count()).toBeGreaterThan(0)

      // CSV download button visible
      await expect(page.getByText(/تحميل التقرير|CSV/)).toBeVisible()
    } else {
      // No cached results path: verify empty state
      await expect(
        page.getByText(/بدء التدقيق/).or(page.getByText(/اضغط/))
      ).toBeVisible({ timeout: 10_000 })
    }
  })

  test('does NOT trigger a new audit run', async ({ page }) => {
    // This test explicitly verifies we do NOT click the "بدء التدقيق" button
    // (which would trigger the 140s MARBERT batch run).
    // We only verify the page loads and shows either results or the empty state.

    await page.goto('/audit')
    await page.waitForTimeout(3_000)

    // Page is still on /audit and rendered without crashing
    expect(page.url()).toContain('/audit')

    // Verify Arabic content is present (RTL rendering works)
    const htmlDir = await page.locator('html').getAttribute('dir')
    expect(htmlDir).toBe('rtl')
  })
})
