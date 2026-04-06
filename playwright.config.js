const { defineConfig, devices } = require('@playwright/test')

module.exports = defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'line',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
  webServer: {
    command: 'NODE_OPTIONS=--openssl-legacy-provider npx serve -s build -p 3000',
    port: 3000,
    timeout: 180 * 1000,
    reuseExistingServer: !process.env.CI,
  },
})
