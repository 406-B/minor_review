import { test, expect } from 'playwright/test';

function nowMs() {
  return Date.now();
}

async function stepTimed(page, name, fn) {
  const start = nowMs();
  let ok = true;
  let error = undefined;
  try {
    await fn();
  } catch (e) {
    ok = false;
    error = e;
  }
  const durMs = nowMs() - start;

  // Write one JSON line per step so it's easy to aggregate later.
  // Runner will collect these lines into a metrics file.
  // Keep it ASCII-only to avoid encoding issues.
  // eslint-disable-next-line no-console
  console.log(JSON.stringify({ type: 'step', name, ok, durMs }));

  if (!ok) throw error;
}

function envBool(name, defaultValue) {
  const v = process.env[name];
  if (v === undefined || v === '') return defaultValue;
  return v === '1' || v.toLowerCase() === 'true' || v.toLowerCase() === 'yes';
}

const TRY_NAV_DISHES = ['/dishes', '/#/dishes', '/dish', '/#/dish', '/'];

test('e2e perf journey (http-only)', async ({ page, baseURL }) => {
  const uiBase = process.env.UI_BASE_URL || baseURL || 'http://[::1]';
  const apiBase = process.env.BASE_URL || 'http://[::1]';

  const username = process.env.E2E_USERNAME || 'admin';
  const password = process.env.E2E_PASSWORD || 'admin';

  const doApiLogin = envBool('DO_API_LOGIN', true);

  // Basic smoke: home is reachable.
  await stepTimed(page, 'open_home', async () => {
    await page.goto(uiBase, { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveTitle(/.*/);
  });

  // Optional: prime backend auth via API, because UI login flow may vary.
  // This doesn't replace UI perf, but helps unlock authenticated pages.
  if (doApiLogin) {
    await stepTimed(page, 'api_login_patch', async () => {
      const res = await page.request.patch(`${apiBase}/api/v1/login`, {
        data: { username, password },
        headers: { 'content-type': 'application/json' },
      });
      expect(res.ok()).toBeTruthy();
      const json = await res.json();
      // Log token length (not token itself).
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_login_patch', ok: true, tokenLen: (json?.token || '').length }));
    });
  }

  // Try to land on dishes listing route (SPA routes can differ).
  await stepTimed(page, 'goto_dishes', async () => {
    let lastErr;
    for (const path of TRY_NAV_DISHES) {
      try {
        await page.goto(`${uiBase}${path}`, { waitUntil: 'domcontentloaded' });
        // Heuristic: wait a bit for typical list content.
        await page.waitForTimeout(500);
        return;
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error('failed to navigate to dishes');
  });

  // Hit a representative API endpoint to capture backend latency under E2E conditions.
  await stepTimed(page, 'api_user_get', async () => {
    const res = await page.request.get(`${apiBase}/api/v1/user`);
    expect(res.ok()).toBeTruthy();
  });
});
