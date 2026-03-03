import { test, expect } from '@playwright/test'

test.describe('Training Flow (Khaled)', () => {

  test('training page shows start button', async ({ page }) => {
    await page.goto('/train')

    // Verify the training landing page loads
    await expect(
      page.getByText(/التدريب/).first()
    ).toBeVisible({ timeout: 10_000 })

    // Start session button should be visible
    await expect(
      page.getByRole('button', { name: /ابدأ/ }).or(
        page.getByText(/ابدأ جلسة جديدة/).or(page.getByText(/ابدأ التدريب/))
      )
    ).toBeVisible()
  })

  test('start session and label items', async ({ page }) => {
    // Extended timeout for ML inference latency
    test.setTimeout(120_000)

    await page.goto('/train')

    // Click start session button
    const startButton = page.getByRole('button', { name: /ابدأ/ }).or(
      page.getByText(/ابدأ جلسة جديدة/).or(page.getByText(/ابدأ التدريب/))
    )
    await startButton.click()

    // Wait for redirect to session page
    await page.waitForURL(/\/train\/sessions\//, { timeout: 30_000 })

    // --- Session page loaded ---

    // Wait for tweet card to appear (content loaded from API)
    await expect(page.locator('.font-tajawal').first()).toBeVisible({ timeout: 10_000 })

    // Verify CalibrationScore shows placeholder before any labeling
    await expect(
      page.getByText('ستظهر نسبة المعايرة بعد أول تصنيف')
    ).toBeVisible()

    // --- Label item 1: not_hate ---

    // Click "ليس كراهية" (not-hate button)
    await page.getByRole('button', { name: /ليس كراهية/ }).click()

    // Click "إرسال" (submit)
    const submitButton = page.getByRole('button', { name: /إرسال/ })
    await submitButton.click()

    // Wait for feedback reveal (ML inference ~250ms but allow generous timeout)
    await expect(page.getByText('إجابتك')).toBeVisible({ timeout: 60_000 })

    // Verify ground truth section appears
    await expect(page.getByText('الإجابة الصحيحة')).toBeVisible()

    // AI explanation: accept either the blue explanation card OR the cold-start fallback
    const hasAIExplanation = await page.getByText('تفسير النموذج').isVisible().catch(() => false)
    const hasFallback = await page.getByText('النموذج غير جاهز بعد').isVisible().catch(() => false)
    expect(hasAIExplanation || hasFallback).toBe(true)

    // CalibrationScore should now show a percentage (no longer placeholder)
    await expect(page.getByText('ستظهر نسبة المعايرة بعد أول تصنيف')).not.toBeVisible()
    await expect(page.getByText(/نسبة المعايرة/)).toBeVisible()

    // --- Label item 2: hate with category ---

    // Click "التالي" (next)
    await page.getByRole('button', { name: /التالي/ }).click()

    // Wait for next item to load
    await page.waitForTimeout(500)

    // Click "خطاب كراهية" (hate button)
    await page.getByRole('button', { name: /خطاب كراهية/ }).click()

    // Category grid should appear — click the first available category
    await page.getByRole('button', { name: /عنصرية/ }).click()

    // Submit should now be enabled (both label + category selected)
    await submitButton.click()

    // Wait for feedback reveal
    await expect(page.getByText('إجابتك')).toBeVisible({ timeout: 60_000 })

    // CalibrationScore should still show a percentage
    await expect(page.getByText(/نسبة المعايرة/)).toBeVisible()

    // --- Label item 3: another label ---

    // Click next
    await page.getByRole('button', { name: /التالي/ }).click()
    await page.waitForTimeout(500)

    // Label as not_hate for speed
    await page.getByRole('button', { name: /ليس كراهية/ }).click()
    await submitButton.click()

    // Wait for feedback
    await expect(page.getByText('إجابتك')).toBeVisible({ timeout: 60_000 })

    // Calibration score visible after 3 labels
    await expect(page.getByText(/نسبة المعايرة/)).toBeVisible()
  })

  test('backward navigation shows previous item', async ({ page }) => {
    test.setTimeout(90_000)

    await page.goto('/train')

    // Start a new session
    const startButton = page.getByRole('button', { name: /ابدأ/ }).or(
      page.getByText(/ابدأ جلسة جديدة/).or(page.getByText(/ابدأ التدريب/))
    )
    await startButton.click()
    await page.waitForURL(/\/train\/sessions\//, { timeout: 30_000 })

    // Wait for first item
    await expect(page.locator('.font-tajawal').first()).toBeVisible({ timeout: 10_000 })

    // Label item 1
    await page.getByRole('button', { name: /ليس كراهية/ }).click()
    await page.getByRole('button', { name: /إرسال/ }).click()
    await expect(page.getByText('إجابتك')).toBeVisible({ timeout: 60_000 })

    // Go to item 2
    await page.getByRole('button', { name: /التالي/ }).click()
    await page.waitForTimeout(500)

    // Label item 2 (back button only appears in feedback view)
    await page.getByRole('button', { name: /ليس كراهية/ }).click()
    await page.getByRole('button', { name: /إرسال/ }).click()
    await expect(page.getByText('إجابتك')).toBeVisible({ timeout: 60_000 })

    // Navigate back to item 1
    await page.getByRole('button', { name: /السابق/ }).click()
    await page.waitForTimeout(500)

    // Item 1's feedback should still be visible (already labeled)
    await expect(page.getByText('إجابتك')).toBeVisible()
  })
})
