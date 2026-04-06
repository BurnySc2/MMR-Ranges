import { test, expect } from '@playwright/test'

test.describe('MMR-Ranges E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test.describe('App Load Tests', () => {
    test('header is visible on desktop', async ({ page }) => {
      await expect(page.getByTestId('header')).toBeVisible()
      await expect(page.getByTestId('header-title')).toContainText('MMR Ranges')
    })

    test('header is visible on mobile', async ({ page }) => {
      await expect(page.getByTestId('header')).toBeVisible()
      await expect(page.getByTestId('header-title')).toContainText('MMR Ranges')
    })

    test('no console errors on desktop', async ({ page }) => {
      const errors: string[] = []
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          errors.push(msg.text())
        }
      })
      await page.goto('/')
      await page.waitForLoadState('networkidle')
      expect(errors).toHaveLength(0)
    })

    test('no console errors on mobile', async ({ page }) => {
      const errors: string[] = []
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          errors.push(msg.text())
        }
      })
      await page.goto('/')
      await page.waitForLoadState('networkidle')
      expect(errors).toHaveLength(0)
    })
  })

  test.describe('Default Tab Tests', () => {
    test('1v1 tab is selected by default on desktop', async ({ page }) => {
      const tab1v1 = page.getByTestId('tab-1v1')
      await expect(tab1v1).toHaveClass(/bg-blue-500/)
      // Use first() since there are 5 table elements (one per league)
      await expect(page.getByTestId('table').first()).toBeVisible()
    })

    test('1v1 tab is selected by default on mobile', async ({ page }) => {
      const tab1v1 = page.getByTestId('tab-1v1')
      await expect(tab1v1).toHaveClass(/bg-blue-500/)
      await expect(page.getByTestId('table').first()).toBeVisible()
    })
  })

  test.describe('MMR Tab Navigation', () => {
    test('clicking 2v2 tab shows 2v2 table', async ({ page }) => {
      await page.getByTestId('tab-2v2').click()
      await expect(page.getByTestId('tab-2v2')).toHaveClass(/bg-blue-500/)
      await expect(page.getByTestId('tab-1v1')).not.toHaveClass(/bg-blue-500/)
    })

    test('clicking 3v3 tab shows 3v3 table', async ({ page }) => {
      await page.getByTestId('tab-3v3').click()
      await expect(page.getByTestId('tab-3v3')).toHaveClass(/bg-blue-500/)
    })

    test('clicking 4v4 tab shows 4v4 table', async ({ page }) => {
      await page.getByTestId('tab-4v4').click()
      await expect(page.getByTestId('tab-4v4')).toHaveClass(/bg-blue-500/)
    })

    test('clicking Archon tab shows Archon table', async ({ page }) => {
      await page.getByTestId('tab-archon').click()
      await expect(page.getByTestId('tab-archon')).toHaveClass(/bg-blue-500/)
    })

    test('clicking 1v1 tab shows 1v1 table', async ({ page }) => {
      await page.getByTestId('tab-2v2').click()
      await page.getByTestId('tab-1v1').click()
      await expect(page.getByTestId('tab-1v1')).toHaveClass(/bg-blue-500/)
    })
  })

  test.describe('Statistics Tab Tests', () => {
    test('clicking Average games shows region selector', async ({ page }) => {
      await page.getByTestId('tab-avg-games').click()
      // Use nth(0) since avg_games statistics is the first Statistics component
      await expect(page.getByTestId('statistics').nth(0)).toBeVisible()
      // Use getByText to find the Americas button within the visible statistics
      await expect(page.getByTestId('statistics').nth(0).getByText('Americas')).toBeVisible()
    })

    test('clicking Total games shows region selector', async ({ page }) => {
      await page.getByTestId('tab-total-games').click()
      // Use nth(1) since total_games statistics is the second Statistics component
      await expect(page.getByTestId('statistics').nth(1)).toBeVisible()
      await expect(page.getByTestId('statistics').nth(1).getByText('Europe')).toBeVisible()
    })

    test('clicking Average winrate shows region selector', async ({ page }) => {
      await page.getByTestId('tab-avg-winrate').click()
      // Use nth(2) since avg_winrate statistics is the third Statistics component
      await expect(page.getByTestId('statistics').nth(2)).toBeVisible()
      await expect(page.getByTestId('statistics').nth(2).getByText('Korea')).toBeVisible()
    })
  })

  test.describe('Region Selector Tests', () => {
    test.beforeEach(async ({ page }) => {
      await page.getByTestId('tab-avg-games').click()
      // Wait for visibility before proceeding
      await expect(page.getByTestId('statistics').nth(0)).toBeVisible()
    })

    test('Americas region is selected by default', async ({ page }) => {
      await expect(page.getByTestId('statistics').nth(0).getByText('Americas')).toHaveClass(/bg-blue-500/)
      await expect(page.getByTestId('table-us').first()).toBeVisible()
    })

    test('clicking Europe switches to Europe table', async ({ page }) => {
      await page.getByTestId('statistics').nth(0).getByText('Europe').click()
      await expect(page.getByTestId('statistics').nth(0).getByText('Europe')).toHaveClass(/bg-blue-500/)
      await expect(page.getByTestId('table-eu').first()).toBeVisible()
    })

    test('clicking Korea switches to Korea table', async ({ page }) => {
      await page.getByTestId('statistics').nth(0).getByText('Korea').click()
      await expect(page.getByTestId('statistics').nth(0).getByText('Korea')).toHaveClass(/bg-blue-500/)
      await expect(page.getByTestId('table-kr').first()).toBeVisible()
    })
  })

  test.describe('Tooltip Tests', () => {
    test('tooltips appear on hover for Average games', async ({ page }) => {
      await page.getByTestId('tab-avg-games').hover()
      await expect(page.locator('[data-tip="(total wins + total losses) / player accounts"]')).toBeVisible()
    })

    test('tooltips appear on hover for Total games', async ({ page }) => {
      await page.getByTestId('tab-total-games').hover()
      await expect(page.locator('[data-tip="total wins + total losses"]')).toBeVisible()
    })
  })

  test.describe('Footer Tests', () => {
    test('footer is visible', async ({ page }) => {
      await expect(page.getByTestId('footer')).toBeVisible()
      await expect(page.getByTestId('footer-link')).toContainText('Source code')
    })
  })
})
