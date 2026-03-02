import { test, expect } from '@playwright/test'

test.describe('Observatory (Rania)', () => {

  test('summary cards load with Arabic text', async ({ page }) => {
    await page.goto('/observatory')

    // Wait for API data to load and summary cards to render
    await expect(page.getByText('إجمالي التغريدات')).toBeVisible({ timeout: 15_000 })
    await expect(page.getByText('تغريدات خطاب كراهية')).toBeVisible()
    await expect(page.getByText('نسبة خطاب الكراهية')).toBeVisible()
  })

  test('D3 timeline chart renders SVG with path elements', async ({ page }) => {
    await page.goto('/observatory')

    // Wait for SVG to render (D3 renders inside useRef + useEffect after API response)
    const svg = page.locator('svg')
    await expect(svg.first()).toBeVisible({ timeout: 15_000 })

    // Verify SVG contains at least one <path> element (the area fill and/or line stroke)
    const paths = svg.first().locator('path')
    await expect(paths.first()).toBeVisible({ timeout: 15_000 })
  })

  test('historical events section is visible', async ({ page }) => {
    await page.goto('/observatory')

    // Wait for the events legend section
    await expect(page.getByText('الأحداث التاريخية المرجعية')).toBeVisible({ timeout: 15_000 })

    // Verify at least one known event label is visible
    // Using one of the 8 hardcoded events from the Observatory router
    await expect(page.getByText('حرق الطيار معاذ الكساسبة').or(
      page.getByText('الانتخابات البرلمانية الأردنية')
    )).toBeVisible()
  })

  test('page does not show 401 error (auth works)', async ({ page }) => {
    await page.goto('/observatory')

    // If auth fails, the page would redirect to /login or show an error
    // Wait a moment for any potential redirect
    await page.waitForTimeout(2_000)

    // Should still be on /observatory (not redirected to /login)
    expect(page.url()).toContain('/observatory')

    // Should NOT show login form
    await expect(page.getByRole('button', { name: /تسجيل الدخول/ })).not.toBeVisible()
  })
})
