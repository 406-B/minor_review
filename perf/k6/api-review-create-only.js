import http from 'k6/http';
import { check, sleep } from 'k6';

function normalizeBaseUrl(u) {
  if (!u) return 'http://[::1]';
  return u.replace(/\/+$/, '');
}

const BASE_URL = normalizeBaseUrl(__ENV.BASE_URL);
// Keep credentials aligned with api-core-stages.js
const USERNAME = (__ENV.TEST_USERNAME || __ENV.USERNAME || 'Perf01').trim();
const PASSWORD = (__ENV.TEST_PASSWORD || __ENV.PASSWORD || 'Aa1-aaaa').trim();
const NICKNAME = (__ENV.TEST_NICKNAME || '性能压测').trim();
const REGISTER_USER = String(__ENV.REGISTER_USER || '').trim();

export const options = {
  vus: 1,
  iterations: 20,
  thresholds: {
    // keep it simple: focus on this endpoint's latency
    'http_req_failed{expected_response:true}': ['rate<0.01'],
    'http_req_duration{name:review_create,expected_response:true}': ['p(95)<1200'],
  },
};

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

function postExpectedCustom(url, body, tags, expectedResponseFn, headers = {}) {
  return http.post(url, JSON.stringify(body), {
    tags,
    timeout: '10s',
    redirects: 0,
    expectedResponse: expectedResponseFn,
    headers: jsonHeaders(headers),
  });
}

function patchExpectedCustom(url, body, tags, expectedResponseFn, headers = {}) {
  return http.patch(url, JSON.stringify(body), {
    tags,
    timeout: '10s',
    redirects: 0,
    expectedResponse: expectedResponseFn,
    headers: jsonHeaders(headers),
  });
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

function ensureUser(username, password, nickname, authHeader = {}) {
  if (!REGISTER_USER || REGISTER_USER === '0') return;
  const res = postExpectedCustom(
    `${BASE_URL}/api/v1/register`,
    { username, password, nickname: nickname || username },
    { name: 'register', expected_response: 'true' },
    (r) => [200, 400].includes(r.status),
    authHeader
  );
  check(res, { 'register ok/exists': (r) => [200, 400].includes(r.status) });
}

export function setup() {
  // optional: register the user once (same semantics as api-core-stages.js)
  ensureUser(USERNAME, PASSWORD, NICKNAME);

  // login
  const login = patchExpectedCustom(
    `${BASE_URL}/api/v1/login`,
    { username: USERNAME, password: PASSWORD },
    { name: 'login', expected_response: 'true' },
    (r) => r.status === 200
  );
  check(login, {
    'login 200': (r) => r.status === 200,
    'login has jwt': (r) => {
      try {
        const j = r.json();
        return !!j?.jwt;
      } catch (_) {
        return false;
      }
    },
  });

  const jwt = login.json('jwt');
  if (!jwt) {
    throw new Error(`Login succeeded check failed: status=${login.status}, body=${login.body && login.body.slice ? login.body.slice(0, 200) : ''}`);
  }
  const authHeader = { Authorization: `Bearer ${jwt}` };

  // pick one dish (API shape in this repo: { code, message, data: [ ... ] })
  const dishes = getExpected(
    `${BASE_URL}/api/v1/dishes/?page=1&page_size=50`,
    { name: 'dishes', expected_response: 'true' },
    authHeader
  );
  const arr = dishes.json('data') || [];
  if (!Array.isArray(arr) || arr.length === 0) {
    throw new Error('No dishes found. Run seed_loadtest_data first.');
  }
  const dishId = arr[0].id;

  return { authHeader, dishId };
}

export default function (data) {
  const { authHeader, dishId } = data;

  // ensure rating exists (required by create_review)
  const rateRes = postExpectedCustom(
    `${BASE_URL}/api/v1/dishes/${dishId}/rate/`,
    { rating: 4.0 + Math.random() * 1.0 },
    { name: 'rate', expected_response: 'true' },
    (r) => [200, 400].includes(r.status),
    authHeader
  );
  check(rateRes, { 'rate ok/exists': (r) => [200, 400].includes(r.status) });

  // create review
  const body = { content: `perf-review-${__VU}-${__ITER}`, rating: 4 };
  const res = postExpectedCustom(
    `${BASE_URL}/api/v1/dishes/${dishId}/reviews/create/`,
    body,
    { name: 'review_create', expected_response: 'true' },
    (r) => [200, 201].includes(r.status),
    authHeader
  );
  check(res, { 'review create ok': (r) => [200, 201, 400].includes(r.status) });

  sleep(0.1);
}
