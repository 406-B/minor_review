import http from 'k6/http';
import { check, sleep } from 'k6';

// k6 运行方式（示例）：
//   k6 run -e BASE_URL=http://localhost:8000 perf/k6/api-smoke.js
// 或通过 nginx：
//   k6 run -e BASE_URL=http://localhost perf/k6/api-smoke.js

// 默认走 nginx（通常对宿主机暴露 80/443），避免 backend 仅容器内可达时本机请求失败。
const BASE_URL = __ENV.BASE_URL || 'http://localhost';

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: Number(__ENV.VUS || 5),
      duration: __ENV.DURATION || '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

function get(url, tags = {}) {
  return http.get(url, {
    tags,
    timeout: '10s',
    headers: {
      Accept: 'application/json',
    },
  });
}

export default function () {
  const health = get(`${BASE_URL}/api/v1/health/`, { name: 'health' });
  check(health, {
    'health status 200': (r) => r.status === 200,
  });

  // 下面两个接口在不同版本/路由下可能不存在；如果不存在，脚本仍会记录失败。
  // 如果你希望“只测存在的接口”，我可以基于当前 openapi.json 自动生成用例列表。
  const list = get(`${BASE_URL}/api/v1/list/`, { name: 'list' });
  check(list, {
    'list status 200/401/404': (r) => [200, 401, 404].includes(r.status),
  });

  const dishes = get(`${BASE_URL}/api/v1/list/dishes/`, { name: 'dishes' });
  check(dishes, {
    'dishes status 200/401/404': (r) => [200, 401, 404].includes(r.status),
  });

  sleep(1);
}
