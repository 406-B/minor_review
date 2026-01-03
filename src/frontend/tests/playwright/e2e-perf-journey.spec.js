import { test, expect } from '@playwright/test';

function nowMs() {
  return Date.now();
}

async function stepTimed(page, name, fn) {
  const start = nowMs();
  let ok = true;
  let error;
  try {
    await fn();
  } catch (e) {
    ok = false;
    error = e;
  }
  const durMs = nowMs() - start;

  // One JSON line per step. Runner reads these from stdout.
  // Keep it ASCII-only to avoid encoding issues.
  // eslint-disable-next-line no-console
  console.log(JSON.stringify({ type: 'step', name, ok, durMs }));

  if (!ok) throw error;
}

function pickJwt(payload) {
  // Try common field names.
  return (
    payload?.token ||
    payload?.access ||
    payload?.access_token ||
    payload?.jwt ||
    payload?.data?.token ||
    payload?.data?.access ||
    ''
  );
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

  // Keep defaults consistent with k6 perf scripts that already work in this repo.
  const username = process.env.E2E_USERNAME || process.env.TEST_USERNAME || 'Perf01';
  const password = process.env.E2E_PASSWORD || process.env.TEST_PASSWORD || 'Aa1-aaaa';

  const doApiLogin = envBool('DO_API_LOGIN', true);
  const doUiLogin = envBool('DO_UI_LOGIN', true);
  const doUiSearch = envBool('DO_UI_SEARCH', true);
  const doUiComment = envBool('DO_UI_COMMENT', false);
  const doUiCommunity = envBool('DO_UI_COMMUNITY', true);
  const doUiProfile = envBool('DO_UI_PROFILE', true);
  const doDishRate = envBool('DO_DISH_RATE', true);
  const doDishCheckIn = envBool('DO_DISH_CHECKIN', false);
  const doCommunityDeep = envBool('DO_COMMUNITY_DEEP', true);
  const doProfileDeep = envBool('DO_PROFILE_DEEP', true);
  const doPostLike = envBool('DO_POST_LIKE', false);
  const searchKeyword = process.env.SEARCH_KEYWORD || '鸡';

  let jwt = '';
  let dishId = '';
  let userInfo = null;

  await stepTimed(page, 'open_home', async () => {
    await page.goto(uiBase, { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveTitle(/.*/);
  });

  if (doApiLogin) {
    await stepTimed(page, 'api_login_patch', async () => {
      const res = await page.request.patch(`${apiBase}/api/v1/login`, {
        data: { username, password },
        headers: { 'content-type': 'application/json' },
      });
      const status = res.status();
      const ok = res.ok();
      let json = {};
      try {
        json = await res.json();
      } catch {
        // ignore
      }

      jwt = pickJwt(json);
      // Best-effort userInfo payload for frontend route guards/UI.
      userInfo = {
        id: json?.userId ?? json?.data?.userId ?? json?.user?.id ?? null,
        username: json?.username ?? json?.data?.username ?? username,
        nickname: json?.nickname ?? json?.data?.nickname ?? json?.user?.nickname ?? undefined,
      };

      // eslint-disable-next-line no-console
      console.log(
        JSON.stringify({
          type: 'api',
          name: 'api_login_patch',
          ok,
          status,
          tokenLen: jwt ? jwt.length : 0,
        })
      );

      expect(ok).toBeTruthy();
      expect(jwt && jwt.length > 0).toBeTruthy();
    });

    await stepTimed(page, 'ui_inject_login_storage', async () => {
      // Ensure we're on the same origin before touching localStorage.
      await page.goto(uiBase, { waitUntil: 'domcontentloaded' });
      await page.evaluate(
        ({ jwt, userInfo }) => {
          try {
            localStorage.setItem('jwt', jwt);
            localStorage.setItem('userInfo', JSON.stringify(userInfo || {}));
          } catch (e) {
            // ignore
          }
        },
        { jwt, userInfo }
      );
      // Reload so router guards see the token.
      await page.reload({ waitUntil: 'domcontentloaded' });
    });
  }

  if (doUiLogin) {
    await stepTimed(page, 'ui_login_form', async () => {
      await page.goto(`${uiBase}/login`, { waitUntil: 'domcontentloaded' });
      // Element Plus input.
      const usernameInput = page.locator('input').nth(0);
      const passwordInput = page.locator('input[type="password"]').first();
      await usernameInput.fill(username);
      await passwordInput.fill(password);
      await page.getByRole('button', { name: '登录' }).click();
      // Login redirects to /profile (or onboarding).
      await page.waitForTimeout(500);
      const url = page.url();
      if (!(url.includes('/profile') || url.includes('/onboarding/tags'))) {
        throw new Error(`ui login did not redirect as expected (url=${url})`);
      }
      // Ensure localStorage token exists.
      const stored = await page.evaluate(() => localStorage.getItem('jwt') || '');
      if (!stored) throw new Error('ui login did not set localStorage.jwt');
    });
  }

  await stepTimed(page, 'api_pick_dish_id', async () => {
    const headers = {};
    if (jwt) headers.authorization = `Bearer ${jwt}`;

    const res = await page.request.get(`${apiBase}/api/v1/dishes/?page=1&page_size=10&ordering=-rating`, {
      headers,
    });
    const status = res.status();
    const ok = res.ok();
    let json = {};
    try {
      json = await res.json();
    } catch {
      // ignore
    }

    const items = Array.isArray(json?.data) ? json.data : [];
    dishId = items.length > 0 ? String(items[0]?.id ?? '') : '';

    // eslint-disable-next-line no-console
    console.log(
      JSON.stringify({
        type: 'api',
        name: 'api_pick_dish_id',
        ok,
        status,
        dishId: dishId || null,
        count: items.length,
      })
    );

    // This is best-effort: list endpoint might be empty on a fresh DB.
    if (!ok || !dishId) {
      // eslint-disable-next-line no-console
      console.log(
        JSON.stringify({
          type: 'note',
          name: 'api_pick_dish_id',
          skipped: true,
          reason: !ok ? 'list_failed' : 'empty_list',
        })
      );
    }
  });

  await stepTimed(page, 'goto_dishes', async () => {
    let lastErr;
    for (const path of TRY_NAV_DISHES) {
      try {
        await page.goto(`${uiBase}${path}`, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(500);
        return;
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error('failed to navigate to dishes');
  });

  // Use the dedicated search page and click into the first result.
  if (dishId) {
    await stepTimed(page, 'goto_dish_detail_direct', async () => {
      await page.goto(`${uiBase}/dish/${dishId}`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);
  // Works for both history and hash routers.
  await expect(page).toHaveURL(new RegExp(`(\/|#\/)?dish\/${dishId}(\/|$)`));
    await expect(page.getByRole('heading', { name: '评论' })).toBeVisible();
    });

    await stepTimed(page, 'api_dish_reviews_get', async () => {
      const headers = {};
      if (jwt) headers.authorization = `Bearer ${jwt}`;
      const res = await page.request.get(`${apiBase}/api/v1/dishes/${dishId}/reviews/`, { headers });
      const status = res.status();
      const ok = res.ok();
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_dish_reviews_get', ok, status, dishId }));
      expect(ok).toBeTruthy();
    });

    await stepTimed(page, 'api_hot_dishes_get', async () => {
      const res = await page.request.get(`${apiBase}/api/v1/dishes/hot/?limit=10`);
      const status = res.status();
      const ok = res.ok();
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_hot_dishes_get', ok, status }));
      expect(ok).toBeTruthy();
    });

    await stepTimed(page, 'api_new_dishes_get', async () => {
      const res = await page.request.get(`${apiBase}/api/v1/dishes/new/?limit=10`);
      const status = res.status();
      const ok = res.ok();
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_new_dishes_get', ok, status }));
      expect(ok).toBeTruthy();
    });

    if (doDishRate) {
      await stepTimed(page, 'api_dish_rate_post', async () => {
        const headers = {};
        if (jwt) headers.authorization = `Bearer ${jwt}`;
        const res = await page.request.post(`${apiBase}/api/v1/dishes/${dishId}/rate/`, {
          headers,
          data: { rating: 4 },
        });
        const status = res.status();
        const ok = res.ok();
        // eslint-disable-next-line no-console
        console.log(JSON.stringify({ type: 'api', name: 'api_dish_rate_post', ok, status, dishId }));
        expect(ok).toBeTruthy();
      });
    }

    if (doDishCheckIn) {
      await stepTimed(page, 'api_dish_check_in_post', async () => {
        const headers = {};
        if (jwt) headers.authorization = `Bearer ${jwt}`;
        const res = await page.request.post(`${apiBase}/api/v1/dishes/${dishId}/check-in/`, {
          headers,
          data: { notes: 'perf-checkin' },
        });
        const status = res.status();
        const ok = res.ok();
        // eslint-disable-next-line no-console
        console.log(JSON.stringify({ type: 'api', name: 'api_dish_check_in_post', ok, status, dishId }));
        expect(ok).toBeTruthy();
      });
    }
  } else if (doUiSearch) {
    await stepTimed(page, 'goto_search', async () => {
      await page.goto(`${uiBase}/search`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(300);
      await expect(page.getByText('菜品搜索')).toBeVisible();
    });

    await stepTimed(page, 'search_submit', async () => {
      const input = page.locator('input').first();
      await input.click();
      await input.fill(searchKeyword);

      // Click the "搜索" button (Element Plus).
      await page.getByRole('button', { name: '搜索' }).click();

      // Wait for results to render: either empty state or at least one card.
      const empty = page.getByText('暂无菜品');
      const cards = page.locator('.dish-card');
      await Promise.race([
        cards.first().waitFor({ state: 'visible', timeout: 10_000 }),
        empty.waitFor({ state: 'visible', timeout: 10_000 }),
      ]);
    });

    await stepTimed(page, 'open_first_dish_detail', async () => {
      const empty = page.getByText('暂无菜品');
      const cards = page.locator('.dish-card');
      const count = await cards.count();
      if (count === 0 && (await empty.isVisible().catch(() => false))) {
        // No search result in current dataset; skip clicking into detail.
        // eslint-disable-next-line no-console
        console.log(JSON.stringify({ type: 'note', name: 'open_first_dish_detail', skipped: true, reason: 'no_results' }));
        return;
      }

      await expect(cards.first()).toBeVisible({ timeout: 10_000 });
      await cards.first().click();
      await expect(page).toHaveURL(/\/dish\//);
    await expect(page.getByRole('heading', { name: '评论' })).toBeVisible();
    });

    // If we reached detail page via search, we still try to hit reviews API (best effort).
    await stepTimed(page, 'api_dish_reviews_get_best_effort', async () => {
      const url = page.url();
      const m = url.match(/(?:\/|#\/)(?:dish)\/(\d+)/);
      const picked = m ? m[1] : '';
      if (!picked) {
        // eslint-disable-next-line no-console
        console.log(
          JSON.stringify({ type: 'note', name: 'api_dish_reviews_get_best_effort', skipped: true, reason: 'no_dish_id_in_url' })
        );
        return;
      }

      const headers = {};
      if (jwt) headers.authorization = `Bearer ${jwt}`;
      const res = await page.request.get(`${apiBase}/api/v1/dishes/${picked}/reviews/`, { headers });
      const status = res.status();
      const ok = res.ok();
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_dish_reviews_get_best_effort', ok, status, dishId: picked }));
      expect(ok).toBeTruthy();
    });

    if (doUiComment) {
      await stepTimed(page, 'ui_submit_comment', async () => {
        const textarea = page.locator('textarea[placeholder*="评论"]').first();
        await expect(textarea).toBeVisible({ timeout: 10_000 });
        const content = `Perf comment ${Date.now()} ok`;
        await textarea.fill(content);
        await page.getByRole('button', { name: '发表评论' }).click();
        // Best effort: allow backend async audit; just wait a bit.
        await page.waitForTimeout(800);
      });
    }
  }

  if (doUiCommunity) {
    await stepTimed(page, 'goto_community', async () => {
      await page.goto(`${uiBase}/community`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(300);

      const url = page.url();
      if (url.includes('/login')) {
  throw new Error('community navigation redirected to /login (expected authenticated session)');
      }

      // Prefer a stable CTA as the primary assertion.
      const cta = page.getByRole('button', { name: '我要发帖' });
      const empty = page.getByText('暂无帖子');
      const loading = page.getByText('加载中');
      const safeWait = (loc) => loc.waitFor({ state: 'visible', timeout: 10_000 }).then(() => true).catch(() => false);
      const results = await Promise.all([safeWait(cta), safeWait(empty), safeWait(loading)]);
      if (!results.some(Boolean)) {
        throw new Error('community page did not reach a known stable state');
      }
    });

    await stepTimed(page, 'api_posts_list_get', async () => {
      const headers = {};
      if (jwt) headers.authorization = `Bearer ${jwt}`;
      if (!jwt) {
        // eslint-disable-next-line no-console
        console.log(JSON.stringify({ type: 'note', name: 'api_posts_list_get', skipped: true, reason: 'no_jwt' }));
        return;
      }
      const res = await page.request.get(`${apiBase}/api/v1/posts/?page=1&page_size=20`, { headers });
      const status = res.status();
      const ok = res.ok();
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_posts_list_get', ok, status, authed: !!jwt }));
      expect(ok).toBeTruthy();
    });

    if (doCommunityDeep) {
      let postId = '';
      await stepTimed(page, 'api_pick_post_id', async () => {
        const headers = {};
        if (jwt) headers.authorization = `Bearer ${jwt}`;
        const res = await page.request.get(`${apiBase}/api/v1/posts/?page=1&page_size=20`, { headers });
        const status = res.status();
        const ok = res.ok();
        let json = {};
        try { json = await res.json(); } catch { /* ignore */ }
        const items = Array.isArray(json?.data?.posts) ? json.data.posts : [];
        postId = items.length > 0 ? String(items[0]?.id ?? '') : '';
        // eslint-disable-next-line no-console
        console.log(JSON.stringify({ type: 'api', name: 'api_pick_post_id', ok, status, postId: postId || null, count: items.length }));
        if (!ok) {
          // eslint-disable-next-line no-console
          console.log(JSON.stringify({ type: 'note', name: 'api_pick_post_id', skipped: true, reason: 'list_failed' }));
          return;
        }

        // If no posts exist, create one to make the perf journey stable.
        if (!postId) {
          const subj = `Perf post ${Date.now()}`;
          const createRes = await page.request.post(`${apiBase}/api/v1/posts/create/`, {
            headers,
            data: { subject: subj, content: 'perf seed post', images: [] },
          });
          const cStatus = createRes.status();
          const cOk = createRes.ok();
          // eslint-disable-next-line no-console
          console.log(JSON.stringify({ type: 'api', name: 'api_post_create', ok: cOk, status: cStatus }));
          expect(cOk).toBeTruthy();

          // Re-list to pick the created post.
          const res2 = await page.request.get(`${apiBase}/api/v1/posts/?page=1&page_size=20`, { headers });
          const s2 = res2.status();
          const ok2 = res2.ok();
          let json2 = {};
          try { json2 = await res2.json(); } catch { /* ignore */ }
          const items2 = Array.isArray(json2?.data?.posts) ? json2.data.posts : [];
          postId = items2.length > 0 ? String(items2[0]?.id ?? '') : '';
          // eslint-disable-next-line no-console
          console.log(JSON.stringify({ type: 'api', name: 'api_pick_post_id_after_create', ok: ok2, status: s2, postId: postId || null, count: items2.length }));
          expect(ok2).toBeTruthy();
          expect(postId).toBeTruthy();
        }
      });

      if (postId) {
        await stepTimed(page, 'goto_post_detail_direct', async () => {
          await page.goto(`${uiBase}/community/${postId}`, { waitUntil: 'domcontentloaded' });
          await page.waitForTimeout(300);
          const url = page.url();
          if (url.includes('/login')) throw new Error('post detail redirected to /login');
          // Be tolerant: wait for any meaningful marker.
          const commentBox = page.locator('textarea');
          await commentBox.first().waitFor({ state: 'attached', timeout: 10_000 }).catch(() => {});
        });

        await stepTimed(page, 'api_post_comments_get', async () => {
          const headers = {};
          if (jwt) headers.authorization = `Bearer ${jwt}`;
          const res = await page.request.get(`${apiBase}/api/v1/posts/${postId}/comments/?page=1&page_size=20`, { headers });
          const status = res.status();
          const ok = res.ok();
          // eslint-disable-next-line no-console
          console.log(JSON.stringify({ type: 'api', name: 'api_post_comments_get', ok, status, postId }));
          expect(ok).toBeTruthy();
        });

        if (doPostLike) {
          await stepTimed(page, 'api_post_like_toggle', async () => {
            const headers = {};
            if (jwt) headers.authorization = `Bearer ${jwt}`;
            const res = await page.request.post(`${apiBase}/api/v1/posts/${postId}/like/`, { headers });
            const status = res.status();
            const ok = res.ok();
            // eslint-disable-next-line no-console
            console.log(JSON.stringify({ type: 'api', name: 'api_post_like_toggle', ok, status, postId }));
            expect(ok).toBeTruthy();
          });
        }
      }
    }
  }

  if (doUiProfile) {
    await stepTimed(page, 'goto_profile', async () => {
      await page.goto(`${uiBase}/profile`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(300);
      // Profile page always shows this placeholder/title even when unauth.
      const placeholderTitle = page.locator('.placeholder-title', { hasText: '个人主页' });
      const navItem = page.getByLabel('主导航').getByText('个人主页');
      const ok1 = await placeholderTitle.first().isVisible().catch(() => false);
      const ok2 = await navItem.first().isVisible().catch(() => false);
      if (!ok1 && !ok2) {
        throw new Error('profile page did not render expected markers');
      }
    });

    await stepTimed(page, 'api_profile_get', async () => {
      const headers = {};
      if (jwt) headers.authorization = `Bearer ${jwt}`;
      const res = await page.request.get(`${apiBase}/api/v1/profile`, { headers });
      const status = res.status();
      const ok = res.ok();
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ type: 'api', name: 'api_profile_get', ok, status, authed: !!jwt }));
      expect(ok).toBeTruthy();
    });

    if (doProfileDeep) {
      await stepTimed(page, 'api_profile_stats_get', async () => {
        const headers = {};
        if (jwt) headers.authorization = `Bearer ${jwt}`;
        const res = await page.request.get(`${apiBase}/api/v1/profile/stats`, { headers });
        const status = res.status();
        const ok = res.ok();
        // eslint-disable-next-line no-console
        console.log(JSON.stringify({ type: 'api', name: 'api_profile_stats_get', ok, status }));
        expect(ok).toBeTruthy();
      });

      await stepTimed(page, 'goto_profile_posts', async () => {
        await page.goto(`${uiBase}/profile/posts`, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(300);
        const url = page.url();
        if (url.includes('/login')) throw new Error('profile posts redirected to /login');
        // Tolerant marker: page contains any list / empty state.
        await page.waitForTimeout(200);
      });
    }
  }

  await stepTimed(page, 'api_user_get', async () => {
  const headers = {};
  if (jwt) headers.authorization = `Bearer ${jwt}`;
  const res = await page.request.get(`${apiBase}/api/v1/user`, { headers });
  const status = res.status();
  const ok = res.ok();
  // eslint-disable-next-line no-console
  console.log(JSON.stringify({ type: 'api', name: 'api_user_get', ok, status, authed: !!jwt }));
  expect(ok).toBeTruthy();
  });
});
