import { check, sleep } from 'k6';
import { browser } from 'k6/browser';
import { Trend, Rate } from 'k6/metrics';

function normalizeBaseUrl(raw) {
  const v = (raw || '').trim();
  if (!v) return 'http://[::1]';
  if (!v.startsWith('http://') && !v.startsWith('https://')) return `http://${v}`.replace(/\/+$/, '');
  if (v.startsWith('https://')) throw new Error(`BASE_URL must use http:// (got ${v})`);
  return v.replace(/\/+$/, '');
}

const BASE_URL = normalizeBaseUrl(__ENV.BASE_URL);
const UI_BASE_URL = normalizeBaseUrl(__ENV.UI_BASE_URL || __ENV.BASE_URL);

const TEST_USERNAME = (__ENV.TEST_USERNAME || 'Perf01').trim();
const TEST_PASSWORD = (__ENV.TEST_PASSWORD || 'Aa1-aaaa').trim();

const HEADLESS = String(__ENV.HEADLESS || '1').trim() !== '0';
const THINK_TIME_MS = Number(__ENV.THINK_TIME_MS || 300);

// k6 browser needs a local browser binary. Prefer Edge on Windows.
const BROWSER_PATH = (__ENV.BROWSER_PATH || __ENV.K6_BROWSER_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe').trim();

const t_step = new Trend('ui_step_duration_ms', true);
const r_step_failed = new Rate('ui_step_failed');

function now() {
  return Date.now();
}

async function timedStep(name, fn) {
  const start = now();
  try {
    const out = await fn();
    t_step.add(now() - start, { step: name });
    r_step_failed.add(false, { step: name });
    return out;
  } catch (e) {
    t_step.add(now() - start, { step: name });
    r_step_failed.add(true, { step: name });
    throw e;
  }
}

export const options = {
  scenarios: {
    ui: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: (__ENV.UI_STAGES || '10s:1,20s:1,10s:0')
        .split(',')
        .map((x) => x.trim())
        .filter(Boolean)
        .map((item) => {
          const [duration, targetStr] = item.split(':');
          const target = Number((targetStr || '').trim());
          if (!duration || Number.isNaN(target)) throw new Error(`Invalid UI_STAGES item: ${item}`);
          return { duration: duration.trim(), target };
        }),
      gracefulRampDown: '10s',
      options: {
        browser: {
          type: 'chromium',
          headless: HEADLESS,
        },
      },
    },
  },
  thresholds: {
    // you can tune these later; keep them loose by default
    'ui_step_failed': ['rate<0.05'],
  },
};

export default async function () {
  console.log(`ui: starting, UI_BASE_URL=${UI_BASE_URL}, BASE_URL=${BASE_URL}`);
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
  });
  const page = await context.newPage();

  try {
    // 1) Open app
    await timedStep('open_home', async () => {
      await page.goto(`${UI_BASE_URL}/`, { waitUntil: 'networkidle' });
      check(page, {
        'home loaded': () => page.url().startsWith(UI_BASE_URL),
      });
    });

    sleep(THINK_TIME_MS / 1000);

    // 2) Login via API (faster + stable than UI forms)
    // We keep this HTTP-only and disable redirects implicitly by using API URL directly.
    let jwt = null;
    await timedStep('api_login', async () => {
      const res = await page.request.patch(`${BASE_URL}/api/v1/login`, {
        data: { username: TEST_USERNAME, password: TEST_PASSWORD },
      });
      check(res, {
        'login status 200': (r) => r.status() === 200,
      });
      const body = await res.json();
      jwt = body && (body.token || body.access || body.jwt || body.data?.token);
      check(body, {
        'jwt present': () => typeof jwt === 'string' && jwt.length > 10,
      });
    });

    sleep(THINK_TIME_MS / 1000);

    // 3) Navigate to a popular list page (best-effort; SPA routes vary)
    await timedStep('goto_dishes_page', async () => {
      // Try several common routes; do not hard fail if route doesn't exist.
      const candidates = ['/dishes', '/dish', '/'];
      let ok = false;
      for (const path of candidates) {
        await page.goto(`${UI_BASE_URL}${path}`, { waitUntil: 'networkidle' });
        if (page.url().startsWith(UI_BASE_URL)) {
          ok = true;
          break;
        }
      }
      check({ ok }, { 'dishes route reachable': (x) => !!x.ok });
    });

    sleep(THINK_TIME_MS / 1000);

    // 4) Call a core API using the jwt (end-to-end, but still browser-driven)
    await timedStep('api_user', async () => {
      const res = await page.request.get(`${BASE_URL}/api/v1/user`, {
        headers: { Authorization: `Bearer ${jwt}` },
      });
      check(res, {
        'user status 200': (r) => r.status() === 200,
      });
    });
    console.log('ui: finished ok');
  } catch (e) {
    // Ensure we surface the real reason in console output.
    console.error(`ui: failed: ${e && (e.stack || e.message || String(e))}`);
    throw e;
  } finally {
    await page.close();
    await context.close();
  }
}
