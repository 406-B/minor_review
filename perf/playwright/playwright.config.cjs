// Playwright config for perf e2e journeys (CommonJS).
// We use CJS here because Playwright's config loader can be picky about ESM
// when the config sits outside the package that owns node_modules.

const path = require('path');

function envBool(name, defaultValue) {
  const v = process.env[name];
  if (v === undefined || v === '') return defaultValue;
  return v === '1' || v.toLowerCase() === 'true' || v.toLowerCase() === 'yes';
}

const UI_BASE_URL = process.env.UI_BASE_URL || 'http://[::1]';
const HEADLESS = envBool('HEADLESS', true);
const WORKERS = Number(process.env.PW_WORKERS || '1');
const ENABLE_HAR = envBool('PW_HAR', false);

// Resolve test runner from frontend node_modules.
const frontendDir = path.resolve(__dirname, '..', '..', 'src', 'frontend');
// eslint-disable-next-line import/no-dynamic-require
const { defineConfig } = require(require.resolve('@playwright/test', { paths: [frontendDir] }));

module.exports = defineConfig({
  testDir: path.resolve(frontendDir, 'tests', 'playwright'),
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  workers: WORKERS,
  reporter: [['list']],
  use: {
    baseURL: UI_BASE_URL,
    headless: HEADLESS,
    trace: process.env.PW_TRACE || 'retain-on-failure',
    video: process.env.PW_VIDEO || 'retain-on-failure',
    screenshot: process.env.PW_SCREENSHOT || 'only-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 20_000,
    bypassCSP: true,
    ...(ENABLE_HAR
      ? {
          // Save a per-test HAR, helps diagnose slow endpoints.
          recordHar: {
            path: process.env.PW_HAR_PATH || path.resolve(process.cwd(), 'playwright.har'),
            mode: 'minimal',
          },
        }
      : {}),
  },
});
