// Node.js API 压测（零依赖）
// 用途：在缺少 k6/locust/jmeter 时，仍能做基本并发压测并输出 p50/p95、RPS、错误率。
//
// 运行示例（PowerShell）：
//   node perf/node/api_load_test.mjs --baseUrl http://localhost:8000 --path /api/v1/health/ --vus 10 --duration 30
//
// 多路径：
//   node perf/node/api_load_test.mjs --baseUrl http://localhost:8000 --path /api/v1/health/ --path /api/v1/list/ --vus 10 --duration 30

import { performance } from 'node:perf_hooks';
import fs from 'node:fs';
import path from 'node:path';

function parseArgs(argv) {
  const args = {
    baseUrl: 'http://localhost:8000',
    paths: ['/api/v1/health/'],
    vus: 5,
    durationSec: 30,
    timeoutMs: 10_000,
    outDir: null,
  };

  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--baseUrl') args.baseUrl = argv[++i];
    else if (a === '--path') args.paths.push(argv[++i]);
    else if (a === '--vus') args.vus = Number(argv[++i]);
    else if (a === '--duration') args.durationSec = Number(argv[++i]);
    else if (a === '--timeout') args.timeoutMs = Number(argv[++i]);
    else if (a === '--outDir') args.outDir = argv[++i];
    else if (a === '--help' || a === '-h') return { ...args, help: true };
  }

  // 默认会多 push 一个 path（因为初始化 paths 已有 health），若用户显式传了 path，需要去掉默认项。
  // 最简单：如果 argv 中出现了 --path，就移除第一个默认 health。
  if (argv.includes('--path')) {
    args.paths = args.paths.filter((p, idx) => !(idx === 0 && p === '/api/v1/health/'));
  }

  if (!args.paths.length) args.paths = ['/api/v1/health/'];
  return args;
}

function nowIsoCompact() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function percentile(sorted, p) {
  if (sorted.length === 0) return null;
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.ceil((p / 100) * sorted.length) - 1));
  return sorted[idx];
}

function summarizeLatenciesMs(latencies) {
  const sorted = [...latencies].sort((a, b) => a - b);
  return {
    count: sorted.length,
    min: sorted[0] ?? null,
    max: sorted.at(-1) ?? null,
    p50: percentile(sorted, 50),
    p90: percentile(sorted, 90),
    p95: percentile(sorted, 95),
    p99: percentile(sorted, 99),
    avg: sorted.length ? sorted.reduce((s, x) => s + x, 0) / sorted.length : null,
  };
}

async function fetchWithTimeout(url, timeoutMs) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  const start = performance.now();
  try {
    const res = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    });
    const text = await res.text();
    return {
      ok: res.ok,
      status: res.status,
      latencyMs: performance.now() - start,
      bytes: Buffer.byteLength(text, 'utf8'),
    };
  } catch (e) {
    // 统一把网络错误也转成“有结果”的 sample，方便在 summary 中定位。
    return {
      ok: false,
      status: 0,
      latencyMs: performance.now() - start,
      bytes: 0,
      error: e?.name ? `${e.name}: ${e.message}` : String(e),
    };
  } finally {
    clearTimeout(t);
  }
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(`Usage:
  node perf/node/api_load_test.mjs --baseUrl http://localhost:8000 --path /api/v1/health/ --vus 10 --duration 30

Options:
  --baseUrl   Base URL, default http://localhost:8000
  --path      可重复指定，API 路径（以 / 开头）
  --vus       并发数（虚拟用户数），default 5
  --duration  持续时间（秒），default 30
  --timeout   单请求超时（毫秒），default 10000
  --outDir    输出目录（默认 perf/results/<timestamp>）
`);
    process.exit(0);
  }

  const base = args.baseUrl.replace(/\/$/, '');
  // 路径必须以 / 开头；如果用户没写，自动补上，避免拼出 http://hostapi/v1 这种错误 URL。
  const targets = args.paths.map((p) => {
    const p2 = p.startsWith('/') ? p : `/${p}`;
    return base + p2;
  });

  const ts = nowIsoCompact();
  const outDir = args.outDir || path.join('perf', 'results', ts);
  fs.mkdirSync(outDir, { recursive: true });

  const endAt = performance.now() + args.durationSec * 1000;

  const all = {
    config: {
      baseUrl: args.baseUrl,
      paths: args.paths,
      vus: args.vus,
      durationSec: args.durationSec,
      timeoutMs: args.timeoutMs,
      startedAt: new Date().toISOString(),
    },
    metrics: {
      total: 0,
      ok: 0,
      failed: 0,
      statusCounts: {},
      bytes: 0,
      latenciesMs: [],
    },
    samples: [], // 仅保留前 200 条，避免文件太大
  };

  function record(sample) {
    all.metrics.total++;
    all.metrics.bytes += sample.bytes || 0;
    all.metrics.latenciesMs.push(sample.latencyMs);
    all.metrics.statusCounts[String(sample.status)] = (all.metrics.statusCounts[String(sample.status)] || 0) + 1;
    if (sample.ok) all.metrics.ok++; else all.metrics.failed++;
    if (all.samples.length < 200) all.samples.push(sample);
  }

  async function vuLoop(vuId) {
    let i = 0;
    while (performance.now() < endAt) {
      const target = targets[i % targets.length];
      i++;
      try {
        const r = await fetchWithTimeout(target, args.timeoutMs);
        record({ ...r, url: target, vuId, at: new Date().toISOString() });
      } catch (e) {
        record({ ok: false, status: 0, latencyMs: args.timeoutMs, bytes: 0, url: target, vuId, at: new Date().toISOString(), error: String(e) });
      }
    }
  }

  const startedAtMs = performance.now();
  await Promise.all(Array.from({ length: args.vus }, (_, i) => vuLoop(i + 1)));
  const elapsedSec = (performance.now() - startedAtMs) / 1000;

  const latencyStats = summarizeLatenciesMs(all.metrics.latenciesMs);
  const rps = all.metrics.total / Math.max(elapsedSec, 1e-9);
  const failRate = all.metrics.failed / Math.max(all.metrics.total, 1);

  const summary = {
    ...all.config,
    finishedAt: new Date().toISOString(),
    elapsedSec,
    rps,
    failRate,
    ok: all.metrics.ok,
    failed: all.metrics.failed,
    total: all.metrics.total,
    bytes: all.metrics.bytes,
    latency: latencyStats,
    statusCounts: all.metrics.statusCounts,
  };

  fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2), 'utf8');
  fs.writeFileSync(path.join(outDir, 'raw.json'), JSON.stringify(all, null, 2), 'utf8');

  console.log('== API Load Test Summary ==');
  console.log(JSON.stringify(summary, null, 2));
  console.log('\nSaved to:');
  console.log(`  ${path.join(outDir, 'summary.json')}`);
  console.log(`  ${path.join(outDir, 'raw.json')}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
