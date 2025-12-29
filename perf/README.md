# 性能测试（接口压测）

本目录用于 **API 压测（用户选择：B）**，目标是给出可复现的压测脚本、运行方式与结果沉淀。

## 前置条件

- Docker Desktop 可用
- `backend` 服务可启动并健康（`/api/v1/health/` 返回 200）

当前仓库在 Windows 上编辑 `*.sh` 时容易引入 CRLF 导致容器启动失败；本分支已通过 `.gitattributes` 固化 `*.sh` 为 LF。

## 启动被测环境（Docker Compose）

在仓库根目录启动：
- `db` + `redis` + `backend`
- 或完整栈（包含 nginx / frontend）

你应该能看到 `backend` 状态为 `healthy`。

注意：当前 compose 配置里 `backend` **未必**把 8000 端口映射到宿主机（`docker compose port backend 8000` 可能返回 `:0`）。
所以从宿主机发起压测时，建议默认走 `nginx`：

- `BASE_URL=http://localhost`（80）
- health：`http://localhost/api/v1/health/`

## k6 压测

脚本位置：`perf/k6/api-smoke.js`

### 基础 smoke

- 默认：VUs=5，duration=30s
- 通过环境变量覆盖：`BASE_URL` / `VUS` / `DURATION`

建议：
- 走 nginx（推荐）：`BASE_URL=http://localhost`
- 直连后端：只有在 compose 显式映射了 8000 时才用 `BASE_URL=http://localhost:8000`

### 结果保存

建议使用 `--summary-export` 导出 json，再配合 k6 终端输出保存到文本。

产物建议存放：
- `perf/results/<yyyymmdd-hhmm>/k6-summary.json`
- `perf/results/<yyyymmdd-hhmm>/k6-console.txt`

（我下一步可以加一个 PowerShell 脚本自动生成 timestamp 目录并保存输出。）
