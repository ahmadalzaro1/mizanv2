import { test, expect } from '@playwright/test'

// Login UI test uses NO pre-set storageState — exercises the real login form
test.describe('Auth Flow', () => {

  test('login via UI with valid credentials', async ({ browser }) => {
    // Create a fresh context WITHOUT storageState
    const context = await browser.newContext({ storageState: undefined })
    const page = await context.newPage()

    await page.goto('/login')

    // Fill login form
    await page.getByLabel(/email|البريد/i).fill('demo-admin@mizan.local')
    await page.getByLabel(/password|كلمة/i).fill('demo_admin_2026')

    // Click login button
    await page.getByRole('button', { name: /تسجيل الدخول/ }).click()

    // Wait for redirect to dashboard
    await page.waitForURL('/', { timeout: 10_000 })

    // Verify token is stored in localStorage with correct key
    const token = await page.evaluate(() => localStorage.getItem('mizan_token'))
    expect(token).toBeTruthy()
    expect(token!.split('.').length).toBe(3) // JWT has 3 parts

    // Verify dashboard content is visible
    await expect(page.getByText('ميزان')).toBeVisible()

    await context.close()
  })

  test('unauthenticated user is redirected to /login from protected route', async ({ browser }) => {
    // Create a fresh context WITHOUT storageState
    const context = await browser.newContext({ storageState: undefined })
    const page = await context.newPage()

    // Try to access protected Observatory page directly
    await page.goto('/observatory')

    // Should redirect to /login
    await page.waitForURL('/login', { timeout: 10_000 })
    await expect(page.getByRole('button', { name: /تسجيل الدخول/ })).toBeVisible()

    await context.close()
  })

  test('logout clears token and redirects to /login', async ({ page }) => {
    // This test USES storageState (pre-authenticated)
    await page.goto('/')
    await expect(page.getByText('ميزان')).toBeVisible()

    // Click logout button
    await page.getByRole('button', { name: /خروج/ }).click()

    // Wait for redirect to /login
    await page.waitForURL('/login', { timeout: 10_000 })

    // Verify token is cleared
    const token = await page.evaluate(() => localStorage.getItem('mizan_token'))
    expect(token).toBeNull()
  })
})
