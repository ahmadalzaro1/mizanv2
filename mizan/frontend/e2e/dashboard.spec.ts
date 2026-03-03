import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {

  test('page renders in RTL with Arabic content', async ({ page }) => {
    await page.goto('/')

    // Verify RTL direction is set on <html> element (set in index.html)
    const dir = await page.locator('html').getAttribute('dir')
    expect(dir).toBe('rtl')

    // Verify Arabic heading is visible
    await expect(page.getByText('ميزان')).toBeVisible()
  })

  test('three persona cards are visible', async ({ page }) => {
    await page.goto('/')

    // Card titles (use h3 to avoid matching nav links)
    await expect(page.locator('h3').filter({ hasText: 'المرصد' })).toBeVisible()
    await expect(page.locator('h3').filter({ hasText: 'مدقق التحيز' })).toBeVisible()
    await expect(page.locator('h3').filter({ hasText: 'التدريب' })).toBeVisible()

    // Persona names (substring in longer text)
    await expect(page.getByText(/رانيا/)).toBeVisible()
    await expect(page.getByText(/لينا/)).toBeVisible()
    await expect(page.getByText(/خالد/)).toBeVisible()
  })

  test('clicking Observatory card navigates to /observatory', async ({ page }) => {
    await page.goto('/')

    // Target the card link (inside grid), not the nav link
    await page.locator('.grid a[href="/observatory"]').click()

    await page.waitForURL('/observatory', { timeout: 10_000 })
  })

  test('clicking Bias Auditor card navigates to /audit', async ({ page }) => {
    await page.goto('/')

    await page.locator('.grid a[href="/audit"]').click()

    await page.waitForURL('/audit', { timeout: 10_000 })
  })

  test('clicking Training card navigates to /train', async ({ page }) => {
    await page.goto('/')

    await page.locator('.grid a[href="/train"]').click()

    await page.waitForURL('/train', { timeout: 10_000 })
  })
})
