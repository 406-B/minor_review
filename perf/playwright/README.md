# Playwright 浏览器 E2E 性能测试

目标：用 **真实浏览器** 跑最小用户旅程，并把每个步骤耗时落盘，便于做 p95 回归。

## 为什么用 Playwright

- Windows 体验好，浏览器由 Playwright 管理，避免 k6 browser 在部分环境下的浏览器探测问题。
- 适合做「低并发（1~N）」的真实性能回归与诊断（trace/HAR/录像）。

## 运行（推荐用 runner）

在仓库根目录 `minor_review/` 下：

```powershell
powershell -ExecutionPolicy Bypass -File .\perf\utils\run-playwright-e2e-perf.ps1 \
  -UiBaseUrl "http://[::1]" \
  -ApiBaseUrl "http://[::1]" \
  -Workers 1
```

显示浏览器（非 headless）：

```powershell
powershell -ExecutionPolicy Bypass -File .\perf\utils\run-playwright-e2e-perf.ps1 -ShowBrowser
```

## 产物

每次运行会在 `perf/results/playwright-e2e-<timestamp>/` 生成：

- `report.md`：p50/p95 汇总表（best effort）
- `pw-console.txt`：完整控制台输出
- `pw-metrics.jsonl`：步骤耗时（JSON Lines）
- `playwright-blob/`：Playwright 产物（视配置而定）

## 环境变量（可选）

- `E2E_USERNAME` / `E2E_PASSWORD`：用于 API 登录（默认 `admin/admin`）
- `DO_API_LOGIN=0`：跳过 API 登录
- `HEADLESS=0/1`：runner 会自动设置
