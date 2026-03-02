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

    // Observatory card (Rania)
    await expect(page.getByText('المرصد')).toBeVisible()
    await expect(page.getByText('رانيا')).toBeVisible()

    // Bias Auditor card (Lina)
    await expect(page.getByText('مدقق التحيز')).toBeVisible()
    await expect(page.getByText('لينا')).toBeVisible()

    // Training card (Khaled)
    await expect(page.getByText('التدريب')).toBeVisible()
    await expect(page.getByText('خالد')).toBeVisible()
  })

  test('clicking Observatory card navigates to /observatory', async ({ page }) => {
    await page.goto('/')

    // Click the Observatory card/link
    await page.getByText('المرصد').click()

    // Verify navigation
    await page.waitForURL('/observatory', { timeout: 10_000 })
  })

  test('clicking Bias Auditor card navigates to /audit', async ({ page }) => {
    await page.goto('/')

    await page.getByText('مدقق التحيز').click()

    await page.waitForURL('/audit', { timeout: 10_000 })
  })

  test('clicking Training card navigates to /train', async ({ page }) => {
    await page.goto('/')

    await page.getByText('التدريب').click()

    await page.waitForURL('/train', { timeout: 10_000 })
  })
})
