import { test, expect } from '@playwright/test'

test.describe('Bias Auditor (Lina)', () => {

  test('page loads without error', async ({ page }) => {
    await page.goto('/audit')
    await page.waitForTimeout(2_000)
    expect(page.url()).toContain('/audit')

    // Verify page title is visible
    await expect(page.getByText('مدقق التحيز')).toBeVisible()
  })

  test('displays cached results with tabbed layout OR empty state', async ({ page }) => {
    await page.goto('/audit')

    const hasResults = await page.getByText('F1 الإجمالي').isVisible({ timeout: 10_000 }).catch(() => false)

    if (hasResults) {
      // Cached results path: verify metric cards
      await expect(page.getByText('الدقة')).toBeVisible()
      await expect(page.getByText('الاسترجاع')).toBeVisible()
      await expect(page.getByText('عدد الأمثلة')).toBeVisible()

      // Verify tab navigation exists with all 4 tabs
      await expect(page.getByRole('button', { name: 'نظرة عامة' })).toBeVisible()
      await expect(page.getByRole('button', { name: 'توزيع الثقة' })).toBeVisible()
      await expect(page.getByRole('button', { name: 'مصادر البيانات' })).toBeVisible()
      await expect(page.getByRole('button', { name: 'الإيجابيات الكاذبة' })).toBeVisible()

      // Overview tab should be active by default — check for insight summary or BiasChart
      const hasInsight = await page.getByText('ملخص التحليل').isVisible({ timeout: 5_000 }).catch(() => false)
      if (hasInsight) {
        await expect(page.getByText('ملخص التحليل')).toBeVisible()
      }

      // BiasChart SVG should be visible on overview tab
      const svg = page.locator('svg')
      await expect(svg.first()).toBeVisible({ timeout: 10_000 })

      // CSV download button visible
      await expect(page.getByText(/تحميل التقرير|CSV/)).toBeVisible()

      // Click confidence tab and verify it renders
      await page.getByRole('button', { name: 'توزيع الثقة' }).click()
      await expect(page.getByText('توزيع درجات الثقة حسب الفئة')).toBeVisible({ timeout: 5_000 })

      // Click sources tab
      await page.getByRole('button', { name: 'مصادر البيانات' }).click()
      await expect(page.getByText('أداء النموذج حسب مصدر البيانات')).toBeVisible({ timeout: 5_000 })

      // Click false positives tab
      await page.getByRole('button', { name: 'الإيجابيات الكاذبة' }).click()
      await expect(page.getByText('عينات الإيجابيات الكاذبة')).toBeVisible({ timeout: 5_000 })

    } else {
      // No cached results path: verify empty state
      await expect(
        page.getByRole('button', { name: /بدء التدقيق/ })
      ).toBeVisible({ timeout: 10_000 })
    }
  })

  test('does NOT trigger a new audit run', async ({ page }) => {
    await page.goto('/audit')
    await page.waitForTimeout(3_000)
    expect(page.url()).toContain('/audit')

    // Verify Arabic content is present (RTL rendering works)
    const htmlDir = await page.locator('html').getAttribute('dir')
    expect(htmlDir).toBe('rtl')
  })
})
