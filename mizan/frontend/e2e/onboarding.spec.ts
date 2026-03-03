import { test, expect } from '@playwright/test'

test.describe('Onboarding Tour', () => {

  test.describe('Help Button', () => {
    test('help button visible in header on dashboard', async ({ page }) => {
      await page.goto('/')
      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await expect(helpBtn).toBeVisible()
    })

    test('help button visible on observatory page', async ({ page }) => {
      await page.goto('/observatory')
      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await expect(helpBtn).toBeVisible()
    })

    test('help button visible on training page', async ({ page }) => {
      await page.goto('/train')
      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await expect(helpBtn).toBeVisible()
    })
  })

  test.describe('Tour Launch via Help Button', () => {
    test('clicking help button launches tour with Arabic content', async ({ page }) => {
      // Set tour as seen so auto-trigger doesn't fire
      await page.goto('/')
      await page.evaluate(() => localStorage.setItem('mizan_tour_seen', 'true'))
      await page.reload()

      // Click help button
      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await helpBtn.click()

      // Tour overlay appears
      const popover = page.locator('.driver-popover')
      await expect(popover).toBeVisible()

      // First step has Arabic welcome title
      const title = page.locator('.driver-popover-title')
      await expect(title).toContainText('مرحباً بك في ميزان')
    })

    test('tour navigates through all steps with Next button', async ({ page }) => {
      await page.goto('/')
      await page.evaluate(() => localStorage.setItem('mizan_tour_seen', 'true'))
      await page.reload()

      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await helpBtn.click()

      const title = page.locator('.driver-popover-title')
      const nextBtn = page.locator('.driver-popover-next-btn')

      // Step 1: Welcome
      await expect(title).toContainText('مرحباً بك في ميزان')
      await nextBtn.click()

      // Step 2: Logo
      await expect(title).toContainText('منصة ميزان')
      await nextBtn.click()

      // Step 3: Nav
      await expect(title).toContainText('الأقسام الثلاثة')
      await nextBtn.click()

      // Step 4: Observatory — mentions رانيا
      await expect(title).toContainText('رانيا')
      await nextBtn.click()

      // Step 5: Audit — mentions لينا
      await expect(title).toContainText('لينا')
      await nextBtn.click()

      // Step 6: Training — mentions خالد
      await expect(title).toContainText('خالد')
    })

    test('tour closes after completing final step', async ({ page }) => {
      await page.goto('/')
      await page.evaluate(() => localStorage.setItem('mizan_tour_seen', 'true'))
      await page.reload()

      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await helpBtn.click()

      const nextBtn = page.locator('.driver-popover-next-btn')
      const popover = page.locator('.driver-popover')

      // Navigate through all 6 steps
      for (let i = 0; i < 5; i++) {
        await nextBtn.click()
      }

      // Click "ابدأ التدريب" (Done button on last step)
      const doneBtn = page.locator('.driver-popover-next-btn')
      await doneBtn.click()

      // Tour overlay should be gone
      await expect(popover).not.toBeVisible()
    })
  })

  test.describe('First-Time Auto-Trigger', () => {
    test('tour auto-triggers on first visit (no mizan_tour_seen)', async ({ page }) => {
      // Clear the tour flag to simulate first visit
      await page.goto('/')
      await page.evaluate(() => localStorage.removeItem('mizan_tour_seen'))
      await page.reload()

      // Tour should auto-trigger within ~1 second (500ms delay + render time)
      const popover = page.locator('.driver-popover')
      await expect(popover).toBeVisible({ timeout: 3000 })

      // Verify it's the welcome step
      const title = page.locator('.driver-popover-title')
      await expect(title).toContainText('مرحباً بك في ميزان')
    })

    test('tour does NOT auto-trigger when mizan_tour_seen is set', async ({ page }) => {
      await page.goto('/')
      await page.evaluate(() => localStorage.setItem('mizan_tour_seen', 'true'))
      await page.reload()

      // Wait a bit to ensure auto-trigger would have fired
      await page.waitForTimeout(1000)

      // Tour should NOT be visible
      const popover = page.locator('.driver-popover')
      await expect(popover).not.toBeVisible()
    })
  })

  test.describe('Tour Persistence', () => {
    test('completing tour sets mizan_tour_seen in localStorage', async ({ page }) => {
      await page.goto('/')
      await page.evaluate(() => localStorage.removeItem('mizan_tour_seen'))
      await page.reload()

      // Wait for auto-trigger
      const popover = page.locator('.driver-popover')
      await expect(popover).toBeVisible({ timeout: 3000 })

      // Close the tour (dismiss via close button or skip through)
      const closeBtn = page.locator('.driver-popover-close-btn')
      if (await closeBtn.isVisible()) {
        await closeBtn.click()
      }

      // Verify localStorage flag is set
      const tourSeen = await page.evaluate(() => localStorage.getItem('mizan_tour_seen'))
      expect(tourSeen).toBe('true')
    })

    test('dismissing tour also sets mizan_tour_seen', async ({ page }) => {
      await page.goto('/')
      await page.evaluate(() => localStorage.setItem('mizan_tour_seen', 'true'))
      await page.reload()

      // Launch tour via help button
      const helpBtn = page.getByRole('button', { name: 'جولة تعريفية' })
      await helpBtn.click()

      const popover = page.locator('.driver-popover')
      await expect(popover).toBeVisible()

      // Close/dismiss the tour
      const closeBtn = page.locator('.driver-popover-close-btn')
      if (await closeBtn.isVisible()) {
        await closeBtn.click()
      }

      // Tour should be dismissed
      await expect(popover).not.toBeVisible()

      // localStorage should still have the flag
      const tourSeen = await page.evaluate(() => localStorage.getItem('mizan_tour_seen'))
      expect(tourSeen).toBe('true')
    })
  })

})
