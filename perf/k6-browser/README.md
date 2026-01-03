# k6 Browser E2E 性能测试

这套脚本用于做 **浏览器端到端（E2E）性能测试**：从前端页面加载到后端 API 调用的完整链路。

## 前置条件

### 1) 需要本机有可用的 Chromium 浏览器

k6 browser 会启动本机浏览器（Chromium 内核）。在 Windows 上推荐使用 **Microsoft Edge**。

默认 runner 会尝试使用：

- `C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`

如果你安装路径不同，请在运行时传 `-BrowserPath`。

> 注意：在本仓库当前内置的 `k6.exe v1.4.2` 上，`options.browser.executablePath` 似乎不会生效（仍会走默认探测）。
> 如果遇到 `k6 couldn't detect google chrome...` 这类报错，建议升级 k6 到更新版本，或改用官方提供的 browser 发行版。

### 1.5)（推荐）并行放置新版 k6（不替换旧版）

为避免影响现有 API 压测脚本，本仓库建议把新版 k6 **并行**放到：

- `tools/k6/k6-browser/k6.exe`

`perf/utils/run-k6-browser-e2e.ps1` 会 **优先**使用这个路径；如果不存在，才会回退到仓库内置的旧版 `tools/k6/k6-v1.4.2-windows-amd64/k6.exe`。

离线安装方式：下载新版 k6（Windows amd64 zip）后，解压并把其中的 `k6.exe` 放到上述路径即可。

### 2) HTTP-only

为了避免 nginx `http -> https` 302 导致 TLS 问题，你仍应使用 HTTP-only 的 base url。
推荐：

- UI_BASE_URL / BASE_URL: `http://[::1]`

## 文件

- `perf/k6-browser/e2e-browser-journey.js`：最小可跑旅程脚本。
- `perf/utils/run-k6-browser-e2e.ps1`：Windows 一键 runner（落盘 report）。

## 运行

在仓库根目录 `minor_review/` 下执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\perf\utils\run-k6-browser-e2e.ps1 \
  -UiBaseUrl "http://[::1]" \
  -ApiBaseUrl "http://[::1]" \
  -UiStages "10s:1,20s:1,10s:0"
```

如果 k6 报找不到浏览器，指定 Edge 路径：

```powershell
powershell -ExecutionPolicy Bypass -File .\perf\utils\run-k6-browser-e2e.ps1 \
  -BrowserPath "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
```

显示浏览器（非 headless）：

```powershell
powershell -ExecutionPolicy Bypass -File .\perf\utils\run-k6-browser-e2e.ps1 -ShowBrowser
```

## 产物

每次运行会在 `perf/results/e2e-browser-<timestamp>/` 生成：

- `report.md`：本次运行的输入与说明
- `k6-summary.json`：k6 summary 导出
- `k6-console.txt`：完整控制台输出

你也可以在 `report.md` / `k6-console.txt` 里看到本次实际使用的 `K6_BIN` 路径，便于复盘。

## 下一步建议

- 升级 k6（带 browser 的官方发行版），解决浏览器可执行文件探测问题。
- 把旅程从“API 登录 + 导航”扩展成真实 UI 登录、搜索、点击菜品、加载评论等。
- 按页面/步骤输出更细粒度的 p95（当前已记录 `ui_step_duration_ms{step=...}`）。
