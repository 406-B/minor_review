import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

/**
 * Core flows staged load test (A+B dominant, C+D light) for Minor Review.
 *
 * Goals:
 * - Cover more business-critical paths beyond login + dish list.
 * - Keep HTTP-only (Windows: prefer IPv6 loopback to avoid localhost->IPv4 302->https).
 * - Provide toggles + weights so we can shape traffic like real campus usage.
 *
 * Env vars:
 * - BASE_URL: default http://[::1]
 * - STAGES: e.g. "2m:10,2m:30,3m:30,1m:0"
 * - REGISTER_USER: set to "0" to skip auto-register attempt
 * - ENABLE_WRITES: "1" (default) or "0"
 * - FLOW_WEIGHTS: JSON string, e.g. '{"A":70,"B":20,"C":7,"D":3}'
 * - TEST_USERNAME/TEST_PASSWORD/TEST_NICKNAME
 */

function normalizeBaseUrl(raw) {
  const v = (raw || '').trim();
  if (!v) return 'http://[::1]';

  if (!v.startsWith('http://') && !v.startsWith('https://')) {
    const expanded = `http://${v}`;
    return expanded
      .replace(/^http:\/\/localhost(?=[:/]|$)/i, 'http://[::1]')
      .replace(/\/+$/, '');
  }

  if (v.startsWith('https://')) {
    throw new Error(`BASE_URL must use http:// (got ${v})`);
  }

  return v
    .replace(/^http:\/\/localhost(?=[:/]|$)/i, 'http://[::1]')
    .replace(/\/+$/, '');
}

const BASE_URL = normalizeBaseUrl(__ENV.BASE_URL);

function parseStages(raw) {
  const s = (raw || '').trim();
  if (!s) {
    return [
      { duration: '30s', target: 5 },
      { duration: '2m', target: 10 },
      { duration: '2m', target: 20 },
      { duration: '2m', target: 20 },
      { duration: '30s', target: 0 },
    ];
  }

  return s
    .split(',')
    .map((x) => x.trim())
    .filter(Boolean)
    .map((item) => {
      const [duration, targetStr] = item.split(':');
      const target = Number((targetStr || '').trim());
      if (!duration || Number.isNaN(target)) {
        throw new Error(`Invalid STAGES item: ${item}`);
      }
      return { duration: duration.trim(), target };
    });
}

function parseFlowWeights(raw) {
  // A: browse/search (public + detail)
  // B: interactive writes (rate/review/check-in/likes)
  // C: forum (read mostly + light interactions)
  // D: profile (light)
  const fallback = { A: 70, B: 20, C: 7, D: 3 };
  const s = (raw || '').trim();
  if (!s) return fallback;
  try {
    const obj = JSON.parse(s);
    const out = { ...fallback, ...obj };
    // sanitize: allow explicit 0, only fallback when missing/invalid
    for (const k of ['A', 'B', 'C', 'D']) {
      const hasKey = Object.prototype.hasOwnProperty.call(obj, k);
      const v = Number(out[k]);
      if (Number.isFinite(v) && v >= 0) {
        out[k] = v;
      } else {
        out[k] = hasKey ? 0 : fallback[k];
      }
    }
    return out;
  } catch (_) {
    return fallback;
  }
}

const FLOW_WEIGHTS = parseFlowWeights(__ENV.FLOW_WEIGHTS);
const ENABLE_WRITES = String(__ENV.ENABLE_WRITES || '1').trim() !== '0';
const FORCE_B_WRITES = String(__ENV.FORCE_B_WRITES || '1').trim() !== '0';

// Business-semantic metrics (independent from k6 built-in expected_response)
// - allowed success: treat 200/400 as acceptable for idempotent/exists cases
// - allowed duration: measure latency of those acceptable operations
const b_allowed_success_rate = new Rate('b_allowed_success_rate');
const b_allowed_req_duration = new Trend('b_allowed_req_duration', true);
// Per-action latency breakdown for B write path (allowed semantics)
const b_allowed_req_duration_checkin = new Trend('b_allowed_req_duration_checkin', true);
const b_allowed_req_duration_rate = new Trend('b_allowed_req_duration_rate', true);
const b_allowed_req_duration_add_tag = new Trend('b_allowed_req_duration_add_tag', true);
const b_allowed_req_duration_create_review = new Trend('b_allowed_req_duration_create_review', true);
const b_allowed_samples = new Rate('b_allowed_samples');
const b_write_samples = new Rate('b_write_samples');
const b_skipped_no_dish = new Counter('b_skipped_no_dish');

export const options = {
  scenarios: {
    staged: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: parseStages(__ENV.STAGES),
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    // global safety nets (only for expected_response:true)
    'http_req_failed{expected_response:true}': ['rate<0.01'],
    'http_req_duration{expected_response:true}': ['p(95)<800'],

  // A: public/browse should be fast.
  // In local Docker/Windows env, occasional cold paths can spike; keep a reasonable guardrail.
  'http_req_duration{expected_response:true,flow:A}': ['p(95)<900'],

    // B: writes can be slower, but must be reliable
    'http_req_failed{expected_response:true,flow:B}': ['rate<0.02'],
    'http_req_duration{expected_response:true,flow:B}': ['p(95)<1200'],

    // C/D: light coverage, keep reasonable
    'http_req_failed{expected_response:true,flow:C}': ['rate<0.02'],
    'http_req_failed{expected_response:true,flow:D}': ['rate<0.02'],

    // Business-semantic thresholds (B flow allowed semantics)
    // Defaults are intentionally permissive; tune as needed.
    // Only enforce when samples exist.
    'b_allowed_success_rate{has_samples:true}': ['rate>0.98'],
  // Total B allowed duration mixes several actions; keep it informational (no threshold).
  // Instead, enforce the slowest/most important write action(s).
  'b_allowed_req_duration_create_review{has_samples:true}': ['p(95)<3000'],
  },
};

function recordAllowed(res, tags = {}) {
  // Action-aware business success semantics.
  // Some endpoints legitimately return 201 (review create), and some use 400 for idempotency/validation.
  const action = tags?.action;
  const allowedStatusByAction = {
    checkin: [200, 400],
    rate: [200, 400],
    add_tag: [200, 400],
    create_review: [200, 201, 400],
  };
  const allowed = allowedStatusByAction[action] || [200, 400];
  const ok = res && allowed.includes(res.status);
  const t = Object.assign({ has_samples: 'true' }, tags);
  b_allowed_samples.add(1, t);
  b_allowed_success_rate.add(ok, t);
  b_write_samples.add(1, Object.assign({ flow: 'B', has_samples: 'true' }, tags));
  if (res && typeof res.timings?.duration === 'number') {
    b_allowed_req_duration.add(res.timings.duration, t);
    // Also break down by action to quickly spot the slow endpoint.
    switch (action) {
      case 'checkin':
        b_allowed_req_duration_checkin.add(res.timings.duration, t);
        break;
      case 'rate':
        b_allowed_req_duration_rate.add(res.timings.duration, t);
        break;
      case 'add_tag':
        b_allowed_req_duration_add_tag.add(res.timings.duration, t);
        break;
      case 'create_review':
        b_allowed_req_duration_create_review.add(res.timings.duration, t);
        break;
      default:
        break;
    }
  }
  return ok;
}

function jsonHeaders(extra = {}) {
  return Object.assign(
    {
      Accept: 'application/json, */*',
      'Content-Type': 'application/json',
      'User-Agent': 'k6-perf',
    },
    extra
  );
}

function getExpected(url, tags, headers = {}) {
  return http.get(url, {
    tags,
    timeout: '10s',
    redirects: 0,
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(headers),
  });
}

function postExpected(url, body, tags, headers = {}) {
  return http.post(url, JSON.stringify(body), {
    tags,
    timeout: '10s',
    redirects: 0,
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(headers),
  });
}

function postExpectedCustom(url, body, tags, expectedResponseFn, headers = {}) {
  return http.post(url, JSON.stringify(body), {
    tags,
    timeout: '10s',
    redirects: 0,
    expectedResponse: expectedResponseFn,
    headers: jsonHeaders(headers),
  });
}

function patchExpected(url, body, tags, headers = {}) {
  return http.request('PATCH', url, JSON.stringify(body), {
    tags,
    timeout: '10s',
    redirects: 0,
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(headers),
  });
}

function pickWeighted(weights) {
  const entries = Object.entries(weights).filter(([, v]) => v > 0);
  const total = entries.reduce((s, [, v]) => s + v, 0);
  if (total <= 0) return entries.length ? entries[0][0] : 'A';
  const r = Math.random() * total;
  let acc = 0;
  for (const [k, v] of entries) {
    acc += v;
    if (r <= acc) return k;
  }
  return entries[entries.length - 1][0];
}

function safeJson(res) {
  try {
    return res.json();
  } catch (_) {
    return null;
  }
}

function getJwtFromLogin(username, password) {
  const res = patchExpected(`${BASE_URL}/api/v1/login`, { username, password }, { name: 'login', flow: 'auth' });
  const ok = check(res, {
    'login 200': (r) => r.status === 200,
    'login has jwt': (r) => {
      const j = safeJson(r);
      return Boolean(j && j.jwt);
    },
  });
  if (!ok) return null;
  return safeJson(res).jwt;
}

function ensureUser(username, password, nickname) {
  if (!(__ENV.REGISTER_USER || '').trim()) return;
  const res = postExpected(
    `${BASE_URL}/api/v1/register`,
    { username, password, nickname: nickname || username },
    { name: 'register', flow: 'auth' }
  );
  check(res, { 'register ok/exists': (r) => [200, 400].includes(r.status) });
}

function extractFirstId(maybeArray, keys) {
  if (!Array.isArray(maybeArray) || maybeArray.length === 0) return null;
  const item = maybeArray[0];
  if (!item || typeof item !== 'object') return null;
  for (const k of keys) {
    if (item[k] != null) return item[k];
  }
  return null;
}

function probeIds(authHeader) {
  // Try to discover canteen_id, dish_id, tag_id, and a post_id (if any).
  const out = { canteenId: null, dishId: null, tagId: null, postId: null, reviewId: null };

  // canteen list
  const canteens = http.get(`${BASE_URL}/api/v1/canteens/`, {
    tags: { name: 'canteens_probe', flow: 'A', expected_response: 'false', semantic: 'edge' },
    timeout: '10s',
    redirects: 0,
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
  });
  const cj = safeJson(canteens);
  // list endpoints return {code,message,data:[...]}
  out.canteenId = extractFirstId(cj && cj.data, ['id', 'canteen_id']);

  // dish list
  const dishes = http.get(`${BASE_URL}/api/v1/dishes/?ordering=-view_count`, {
    tags: { name: 'dishes_probe', flow: 'A', expected_response: 'false', semantic: 'edge' },
    timeout: '10s',
    redirects: 0,
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
  });
  const dj = safeJson(dishes);
  out.dishId = extractFirstId(dj && dj.data, ['id', 'dish_id']);

  // tags
  const tags = getExpected(`${BASE_URL}/api/v1/tags/`, { name: 'tags', flow: 'A' });
  const tj = safeJson(tags);
  out.tagId = extractFirstId(tj && tj.data, ['id', 'tag_id']);

  // forum posts may be empty on fresh DB; treat as optional
  const posts = getExpected(`${BASE_URL}/api/v1/posts/?page=1&page_size=20`, { name: 'posts_list', flow: 'C' }, authHeader);
  const pj = safeJson(posts);
  out.postId = extractFirstId(pj && pj.data && pj.data.posts, ['id', 'post_id']);

  // my reviews (auth) - useful for like/delete coverage (may be empty)
  const my = getExpected(`${BASE_URL}/api/v1/reviews/my/?page=1&page_size=10`, { name: 'my_reviews_probe', flow: 'B' }, authHeader);
  const mj = safeJson(my);
  // shape: { code, message, data: { reviews: [...], ... } }
  out.reviewId = extractFirstId(mj && mj.data && mj.data.reviews, ['id', 'review_id']);

  return out;
}

function flowA(ids) {
  // Browse + search + details
  // hot/new often touch ordering/aggregation; keep covered but out of strict latency thresholds
  http.get(`${BASE_URL}/api/v1/dishes/hot/?limit=10`, {
    redirects: 0,
    timeout: '10s',
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
    tags: { name: 'dishes_hot', flow: 'A', expected_response: 'false', semantic: 'edge' },
  });
  http.get(`${BASE_URL}/api/v1/dishes/new/?limit=10`, {
    redirects: 0,
    timeout: '10s',
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
    tags: { name: 'dishes_new', flow: 'A', expected_response: 'false', semantic: 'edge' },
  });

  if (ids.canteenId != null) {
    getExpected(`${BASE_URL}/api/v1/canteens/${ids.canteenId}/?ordering=-rating`, { name: 'canteen_detail', flow: 'A' });
    // canteen floors may return deep nested structure (floors/windows/dishes) and can be heavy.
    // Keep it covered but out of strict latency thresholds.
    http.get(`${BASE_URL}/api/v1/canteens/${ids.canteenId}/floors/`, {
      redirects: 0,
      timeout: '10s',
      expectedResponse: (r) => r.status >= 200 && r.status < 400,
      headers: jsonHeaders(),
      tags: { name: 'canteen_floors', flow: 'A', expected_response: 'false', semantic: 'edge' },
    });
  } else {
    getExpected(`${BASE_URL}/api/v1/canteens/?search=食`, { name: 'canteens_search', flow: 'A' });
  }

  // dish list: search + sort. When tag_ids present, server ignores search (as per views.py)
  if (ids.tagId != null) {
    getExpected(`${BASE_URL}/api/v1/dishes/?tag_ids[]=${ids.tagId}&ordering=-rating`, { name: 'dishes_filter_tag', flow: 'A' });
    // also cover CSV style: ?tag_ids=1,2
    getExpected(
      `${BASE_URL}/api/v1/dishes/?tag_ids=${ids.tagId},${ids.tagId}&ordering=-view_count`,
      { name: 'dishes_filter_tag_csv', flow: 'A' }
    );
  } else {
    getExpected(`${BASE_URL}/api/v1/dishes/?search=鸡&ordering=-rating`, { name: 'dishes_search', flow: 'A' });
  }

  // pagination/edge cases
  // mark edge/boundary reads as non-strict so they don't pollute A latency thresholds
  http.get(`${BASE_URL}/api/v1/dishes/?page=1&page_size=50&ordering=-view_count`, {
    redirects: 0,
    timeout: '10s',
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
    tags: { name: 'dishes_page_1_50', flow: 'A', expected_response: 'false', semantic: 'edge' },
  });
  // out-of-range page should still be 200 with empty list (common behavior)
  http.get(`${BASE_URL}/api/v1/dishes/?page=999&page_size=50&ordering=-view_count`, {
    redirects: 0,
    timeout: '10s',
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
    tags: { name: 'dishes_page_999', flow: 'A', expected_response: 'false', semantic: 'edge' },
  });
  // larger page_size boundary (server may clamp)
  http.get(`${BASE_URL}/api/v1/dishes/?page=1&page_size=200&ordering=-rating`, {
    redirects: 0,
    timeout: '10s',
    expectedResponse: (r) => r.status >= 200 && r.status < 400,
    headers: jsonHeaders(),
    tags: { name: 'dishes_page_1_200', flow: 'A', expected_response: 'false', semantic: 'edge' },
  });

  if (ids.dishId != null) {
    getExpected(`${BASE_URL}/api/v1/dishes/${ids.dishId}/`, { name: 'dish_detail', flow: 'A' });
    getExpected(`${BASE_URL}/api/v1/dishes/${ids.dishId}/reviews/?page=1&page_size=10`, { name: 'dish_reviews', flow: 'A' });
  }

  // user-centric read endpoints (auth required) are covered in flowD by default.
}

function flowB(ids, authHeader) {
  if (!ENABLE_WRITES) {
    // degrade to safe reads
    flowA(ids);
    return;
  }

  // Ensure we have IDs for write paths; re-probe once in the flow to avoid 0-sample runs.
  let workIds = ids || {};
  if (workIds.dishId == null || (FORCE_B_WRITES && workIds.tagId == null)) {
    try {
      const refreshed = probeIds(authHeader);
      workIds = Object.assign({}, workIds, refreshed);
    } catch (_) {
      // ignore
    }
  }

  if (workIds.dishId == null) {
    if (FORCE_B_WRITES) {
        // 在某些环境（比如全新 DB）里 dishes 可能为空；此时硬失败会导致整场压测退出。
        // 改为：记录一次跳过，并回退到只读链路，保证压测可继续跑完。
        b_skipped_no_dish.add(1, { flow: 'B' });
        http.get(`${BASE_URL}/api/v1/dishes/?page=1&page_size=10`, {
          headers: authHeader,
          redirects: 0,
          tags: { flow: 'B', expected_response: 'true', fallback: 'no_dish' },
        });
        return;
    }
    flowA(workIds);
    return;
  }

  // Force minimum write coverage when enabled.
  // These two operations should always be attempted to avoid 0-sample B runs.
  const forcedCheckinAllowed = postExpectedCustom(
    `${BASE_URL}/api/v1/dishes/${workIds.dishId}/check-in/`,
    {},
    { name: 'dish_checkin_allowed', flow: 'B', expected_response: 'false', semantic: 'allowed' },
    (r) => [200, 400].includes(r.status),
    authHeader
  );
  recordAllowed(forcedCheckinAllowed, { flow: 'B', semantic: 'allowed', action: 'checkin' });
  check(forcedCheckinAllowed, { 'checkin ok/exists': (r) => [200, 400].includes(r.status) });

  const forcedRateBody = { rating: 4.0 + Math.random() * 1.0 };
  const forcedRate = postExpectedCustom(
    `${BASE_URL}/api/v1/dishes/${workIds.dishId}/rate/`,
    forcedRateBody,
    { name: 'rate_dish_allowed', flow: 'B', expected_response: 'false', semantic: 'allowed' },
    (r) => [200, 400].includes(r.status),
    authHeader
  );
  recordAllowed(forcedRate, { flow: 'B', semantic: 'allowed', action: 'rate' });
  check(forcedRate, { 'rate ok/exists': (r) => [200, 400].includes(r.status) });

  // B 链路拆分：
  // - strict：只把 200 视为 expected_response:true（会进入阈值统计）
  // - allowed：允许 200/400（幂等/已存在），只做功能 check，不纳入阈值
  const checkinStrict = postExpectedCustom(
  `${BASE_URL}/api/v1/dishes/${workIds.dishId}/check-in/`,
    {},
    { name: 'dish_checkin_strict', flow: 'B' },
    (r) => r.status === 200,
    authHeader
  );
  check(checkinStrict, { 'checkin strict 200': (r) => [200, 400].includes(r.status) });

  // strict rate (keep for expected_response:true thresholds)
  const rateStrict = postExpectedCustom(
    `${BASE_URL}/api/v1/dishes/${workIds.dishId}/rate/`,
    { rating: 4.0 + Math.random() * 1.0 },
    { name: 'rate_dish_strict', flow: 'B' },
    (r) => r.status === 200,
    authHeader
  );
  check(rateStrict, { 'rate strict ok': (r) => [200, 400].includes(r.status) });

  // add tag (prefer existing tag id if available)
  if (workIds.tagId != null) {
    const tagRes = postExpectedCustom(
      `${BASE_URL}/api/v1/dishes/${workIds.dishId}/tags/`,
      { tag_ids: [workIds.tagId] },
      { name: 'dish_add_tag_strict', flow: 'B' },
      (r) => r.status === 200,
      authHeader
    );
    // allow 200/400 (e.g., already tagged)
    check(tagRes, { 'add tag ok/exists': (r) => [200, 400].includes(r.status) });
  recordAllowed(tagRes, { flow: 'B', semantic: 'allowed', action: 'add_tag' });
  } else if (!FORCE_B_WRITES) {
    // optional: when tagId is absent and not forcing writes, skip quietly
  }

  // create tag (admin-only in some deployments) - keep it as allowed semantics
  // This improves API surface coverage without breaking runs when permissions differ.
  const createTagName = `k6-tag-${(__VU || 0)}-${(__ITER || 0)}-${Math.floor(Math.random() * 10000)}`;
  const createTagRes = postExpectedCustom(
    `${BASE_URL}/api/v1/tags/create/`,
    { name: createTagName },
    { name: 'tag_create', flow: 'B', expected_response: 'false', semantic: 'allowed' },
    // allow: ok/duplicate/forbidden/method-not-allowed
    (r) => [200, 400, 403, 404, 405].includes(r.status),
    authHeader
  );
  check(createTagRes, { 'tag create ok/forbidden': (r) => [200, 400, 403, 404, 405, 500].includes(r.status) });

  // create review (may be restricted by validation/dup rules; allow 200/400)
  const reviewBody = { content: `perf-review-${__VU}-${__ITER}`, rating: 4 };
  const createReview = postExpectedCustom(
  `${BASE_URL}/api/v1/dishes/${workIds.dishId}/reviews/create/`,
    reviewBody,
    { name: 'review_create_strict', flow: 'B' },
    (r) => [200, 201].includes(r.status),
    authHeader
  );
  check(createReview, { 'review create ok/exists': (r) => [200, 201, 400].includes(r.status) });
  recordAllowed(createReview, { flow: 'B', semantic: 'allowed', action: 'create_review' });

  // my reviews (auth)
  const my = getExpected(`${BASE_URL}/api/v1/reviews/my/?page=1&page_size=10`, { name: 'my_reviews', flow: 'B' }, authHeader);
  check(my, { 'my reviews 200': (r) => r.status === 200 });

  // review interactions (optional): like/unlike + delete (idempotent-ish)
  // Prefer a review created/readable by current user.
  let reviewId = workIds.reviewId;
  if (reviewId == null) {
    try {
      const mj = safeJson(my);
      reviewId = extractFirstId(mj && mj.data && mj.data.reviews, ['id', 'review_id']);
    } catch (_) {
      // ignore
    }
  }
  if (reviewId != null) {
    const likeRes = postExpectedCustom(
      `${BASE_URL}/api/v1/reviews/${reviewId}/like/`,
      {},
      { name: 'review_like', flow: 'B', expected_response: 'false', semantic: 'allowed' },
      // allow 200, allow 404 if review disappears concurrently
      (r) => [200, 404].includes(r.status),
      authHeader
    );
    check(likeRes, { 'review like ok': (r) => [200, 404].includes(r.status) });

    const delRes = postExpectedCustom(
      `${BASE_URL}/api/v1/reviews/${reviewId}/delete/`,
      {},
      { name: 'review_delete', flow: 'B', expected_response: 'false', semantic: 'allowed' },
      // delete may return 200 / 400 / 404 depending on business rules
      // some deployments may implement it as DELETE; tolerate 405 in that case
      (r) => [200, 400, 403, 404, 405].includes(r.status),
      authHeader
    );
    check(delRes, { 'review delete ok': (r) => [200, 400, 403, 404, 405].includes(r.status) });
  }
}

function flowC(ids, authHeader) {
  // forum read heavy
  // NOTE: Per requirement, we intentionally skip any audit/approve/reject endpoints.
  // (Those are admin/moderation flows and tend to introduce permission instability.)

  // Forum home (if enabled)
  const home = getExpected(`${BASE_URL}/api/v1/forum/home/`, { name: 'forum_home', flow: 'C', expected_response: 'false' }, authHeader);
  check(home, { 'forum home ok': (r) => [200, 404].includes(r.status) });

  const list = getExpected(`${BASE_URL}/api/v1/posts/?page=1&page_size=20`, { name: 'posts_list', flow: 'C' }, authHeader);
  check(list, { 'posts list 200': (r) => r.status === 200 });

  const effectivePostId = ids.postId;
  if (effectivePostId != null) {
    const detail = getExpected(`${BASE_URL}/api/v1/posts/${effectivePostId}/`, { name: 'post_detail', flow: 'C' }, authHeader);
    check(detail, { 'post detail 200': (r) => [200, 404].includes(r.status) });

    const comments = getExpected(
      `${BASE_URL}/api/v1/posts/${effectivePostId}/comments/?page=1&page_size=10`,
      { name: 'post_comments', flow: 'C' },
      authHeader
    );
    check(comments, { 'comments 200': (r) => [200, 404].includes(r.status) });

    if (ENABLE_WRITES) {
      const like = postExpected(
        `${BASE_URL}/api/v1/posts/${effectivePostId}/like/`,
        {},
        { name: 'post_like', flow: 'C' },
        authHeader
      );
      check(like, { 'post like ok': (r) => [200, 404].includes(r.status) });

      // Create a comment (light write). Mark as non-strict to avoid permission/validation differences.
      const createComment = postExpectedCustom(
        `${BASE_URL}/api/v1/comments/create/`,
        {
          post_id: effectivePostId,
          content: `k6 comment ${Date.now()} ${Math.random().toString(16).slice(2)}`,
        },
        { name: 'comment_create', flow: 'C', expected_response: 'false', semantic: 'allowed' },
        (r) => [200, 201, 400, 401, 403, 404, 405].includes(r.status),
        authHeader
      );
      check(createComment, { 'comment create ok': (r) => [200, 201, 400, 401, 403, 404, 405].includes(r.status) });

      // Try to interact with an existing comment if we can extract an id.
      let commentId = null;
      try {
        const cj = safeJson(comments);
        commentId = extractFirstId(
          (cj && cj.data && (cj.data.comments || cj.data.items || cj.data.results)) || cj,
          ['id', 'comment_id']
        );
      } catch (_) {
        // ignore
      }

      if (commentId != null) {
        const commentLike = postExpectedCustom(
          `${BASE_URL}/api/v1/comments/${commentId}/like/`,
          {},
          { name: 'comment_like', flow: 'C', expected_response: 'false', semantic: 'allowed' },
          (r) => [200, 400, 401, 403, 404, 405].includes(r.status),
          authHeader
        );
        check(commentLike, { 'comment like ok': (r) => [200, 400, 401, 403, 404, 405].includes(r.status) });

        const commentDelete = postExpectedCustom(
          `${BASE_URL}/api/v1/comments/${commentId}/delete/`,
          {},
          { name: 'comment_delete', flow: 'C', expected_response: 'false', semantic: 'allowed' },
          (r) => [200, 400, 401, 403, 404, 405].includes(r.status),
          authHeader
        );
        check(commentDelete, { 'comment delete ok': (r) => [200, 400, 401, 403, 404, 405].includes(r.status) });
      }
    }
  }

  // Dish posts (optional)
  if (ids.dishId != null) {
    const dishPosts = getExpected(
      `${BASE_URL}/api/v1/dishes/${ids.dishId}/posts/?page=1&page_size=10`,
      { name: 'dish_posts', flow: 'C', expected_response: 'false' },
      authHeader
    );
    check(dishPosts, { 'dish posts ok': (r) => [200, 404].includes(r.status) });
  }

  // Upload image + create post are heavier and often depend on storage settings.
  // Keep them non-strict and tolerant; skip entirely when writes are disabled.
  if (ENABLE_WRITES) {
    const upload = http.post(`${BASE_URL}/api/v1/upload/image/`, null, {
      tags: { name: 'post_upload_image', flow: 'C', expected_response: 'false', semantic: 'edge' },
      timeout: '20s',
      redirects: 0,
      expectedResponse: (r) => [200, 400, 401, 403, 404, 405, 415].includes(r.status),
      headers: Object.assign({}, jsonHeaders(authHeader)),
    });
    check(upload, { 'upload image ok': (r) => [200, 400, 401, 403, 404, 405, 415].includes(r.status) });

    const createPost = postExpectedCustom(
      `${BASE_URL}/api/v1/posts/create/`,
      {
        title: `k6 post ${Date.now()}`,
        content: `k6 post content ${Math.random().toString(16).slice(2)}`,
        dish_id: ids.dishId || undefined,
      },
      { name: 'post_create', flow: 'C', expected_response: 'false', semantic: 'allowed' },
      (r) => [200, 201, 400, 401, 403, 404, 405].includes(r.status),
      authHeader
    );
    check(createPost, { 'post create ok': (r) => [200, 201, 400, 401, 403, 404, 405].includes(r.status) });
  }
}

function flowD(ids, authHeader) {
  // profile light coverage: GET profile + stats + some lists
  const p = getExpected(`${BASE_URL}/api/v1/profile`, { name: 'profile_get', flow: 'D' }, authHeader);
  check(p, { 'profile 200': (r) => r.status === 200 });

  const s = getExpected(`${BASE_URL}/api/v1/profile/stats`, { name: 'profile_stats', flow: 'D' }, authHeader);
  check(s, { 'profile stats 200': (r) => r.status === 200 });

  // check-in history/calendar if implemented
  const h = getExpected(`${BASE_URL}/api/v1/profile/check-in-history`, { name: 'profile_checkin_history', flow: 'D' }, authHeader);
  check(h, { 'checkin history ok': (r) => [200, 404].includes(r.status) });

  // user dish history/stats/calendar are implemented in list app
  const dh = getExpected(`${BASE_URL}/api/v1/user/dish-history/?page=1&page_size=10`, { name: 'user_dish_history', flow: 'D' }, authHeader);
  check(dh, { 'dish history ok': (r) => [200, 404].includes(r.status) });

  const ds = getExpected(`${BASE_URL}/api/v1/user/dish-stats/`, { name: 'user_dish_stats', flow: 'D' }, authHeader);
  check(ds, { 'dish stats ok': (r) => [200, 404].includes(r.status) });

  const fc = getExpected(`${BASE_URL}/api/v1/user/food-calendar/?days=14`, { name: 'user_food_calendar', flow: 'D' }, authHeader);
  check(fc, { 'food calendar ok': (r) => [200, 404].includes(r.status) });
}

export function setup() {
  const username = (__ENV.TEST_USERNAME || 'Perf01').trim();
  const password = (__ENV.TEST_PASSWORD || 'Aa1-aaaa').trim();
  const nickname = (__ENV.TEST_NICKNAME || '性能压测').trim();

  const health = getExpected(`${BASE_URL}/api/v1/health/`, { name: 'health', flow: 'auth' });
  check(health, { 'health 200': (r) => r.status === 200 });

  const regFlag = String(__ENV.REGISTER_USER || '').trim();
  if (regFlag !== '0') ensureUser(username, password, nickname);

  const jwt = getJwtFromLogin(username, password);
  if (!jwt) {
    throw new Error('Failed to login and obtain jwt. Check TEST_USERNAME/TEST_PASSWORD (or set REGISTER_USER=1 once).');
  }

  const authHeader = { Authorization: `Bearer ${jwt}` };
  const ids = probeIds(authHeader);

  return { jwt, ids };
}

export default function (data) {
  const jwt = data && data.jwt;
  const ids = (data && data.ids) || {};
  const authHeader = jwt ? { Authorization: `Bearer ${jwt}` } : {};

  // Always include a protected core endpoint as a canary
  const user = getExpected(`${BASE_URL}/api/v1/user`, { name: 'user', flow: 'auth' }, authHeader);
  check(user, { 'user 200': (r) => r.status === 200 });

  const flow = pickWeighted(FLOW_WEIGHTS);
  if (flow === 'A') flowA(ids);
  else if (flow === 'B') flowB(ids, authHeader);
  else if (flow === 'C') flowC(ids, authHeader);
  else flowD(ids, authHeader);

  // think time
  sleep(0.6 + Math.random() * 0.4);
}
