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

> 说明：本仓库的压测需求是 **只用 HTTP**。
> 在 Windows 上，`localhost` 同时解析到 IPv4(127.0.0.1) 与 IPv6(::1)，而本项目的 nginx 对 IPv4 侧可能会返回 `302 Location: https://...`（会导致 k6 走 TLS 报错）。
> 因此 k6 脚本里默认把 `BASE_URL=http://localhost` 规范化替换为 `http://[::1]`，以稳定命中 IPv6 loopback，避免 302->https。

### 推荐的 BASE_URL（HTTP-only，稳定）

- 推荐：`BASE_URL=http://[::1]`
	- 这是 Windows 上最稳的 HTTP-only 访问方式（直连 nginx 80）。
	- k6 脚本也会对 `http://localhost` 做 normalize，尽量规避 IPv4 下的 302->https。

注意：脚本里所有请求都强制 `redirects: 0`，避免被 302 带到 https。

## 约定：跳过所有“审核/管理员”接口

为保证稳定性与贴近普通用户流量，本仓库的 k6 压测脚本**不会覆盖**下列类型接口：

- 任何包含 `audit` 的接口（例如 `GET /api/v1/audit/pending`、`POST /api/v1/audit/<type>/<id>`）
- 任何 `approve` / `reject` 的管理员审核接口（例如 `POST /api/v1/dishes/<id>/tags/approve/|reject/`）

这些接口需要管理员权限或人工流程，且返回码/数据状态差异较大，不适合作为默认 smoke 的稳定阈值来源。

### k6 可执行文件位置（Windows）

- 压测使用的 k6 以 zip 形式存放在：`tools/k6/k6-v1.4.2-windows-amd64.zip`
- 解压后可执行文件路径（本地默认解压目标）：`tools/k6/k6-v1.4.2-windows-amd64/k6.exe`

脚本位置：

- Core flows（A/B/C/D，推荐）：`perf/k6/api-core-stages.js`
- Review-only（只测评论创建尾延迟）：`perf/k6/api-review-create-only.js`

### 基础 smoke（Core flows，推荐）

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

## 带鉴权（JWT）的 staged 压测

本仓库当前主要维护的是 `api-core-stages.js`（A/B/C/D）与 `api-review-create-only.js`（review-only）。
如果你需要一个更小的“仅鉴权读”脚本，可以从 `api-core-stages.js` 的 A 流里裁剪出来。

### 测试内容（每次迭代）

- `GET /api/v1/user`（需要 JWT，核心链路）
- `GET /api/v1/dishes/`（AllowAny，公共读）
- `GET /api/v1/dishes/hot/`（AllowAny，公共读）

JWT 获取方式：`PATCH /api/v1/login`，请求头使用 `Authorization: Bearer <jwt>`。

### 关键环境变量

- `BASE_URL`：默认 `http://[::1]`（强制 HTTP-only，且规避 Windows localhost->IPv4 的 302->https）
- `STAGES`：分阶段配置，格式为：`"30s:5,2m:10"`
- `REGISTER_USER`：默认会尝试自动注册一次以“开箱即用”。如果你已准备好账号，运行时设置 `REGISTER_USER=0`。
- `TEST_USERNAME`/`TEST_PASSWORD`/`TEST_NICKNAME`：测试账号；默认值满足前端校验规则：
	- username: `Perf01`
	- password: `Aa1-aaaa`
	- nickname: `性能压测`

### 测试账号（推荐固定，避免每轮注册）

压测更建议固定一个账号，避免注册接口影响压测结果，同时减少 401/账号不存在的问题。

仓库已经加了一个 Django management command：`seed_loadtest_user`，用于直接在 DB 里创建/更新压测用户。

- 账号默认值（与 k6 默认一致）：
	- username: `Perf01`
	- password: `Aa1-aaaa`

在 `backend` 容器里执行（示例）：

- 创建/更新账号：`python manage.py seed_loadtest_user --username Perf01 --password Aa1-aaaa`
- 强制重置密码（推荐偶尔用一次保证对齐）：`python manage.py seed_loadtest_user --username Perf01 --password Aa1-aaaa --reset-password`

说明：该命令会写入 `login_user`，并使用后端同款 `encrypt_password()` 生成密码哈希。

### 推荐：8 分钟 staged（校园内师生使用的温和峰值）

该轮参数：2m ramp 到 10 VUs → 2m ramp 到 30 VUs → 3m hold 30 VUs → 1m ramp down。

本地最新一次落盘目录：`perf/results/20260103-000817/`

摘要（来自 k6 控制台/summary）：

- 阈值（仅统计 `expected_response:true`）：
	- `http_req_failed`：0.00%（阈值 rate<1% 通过）
	- `http_req_duration p95`：11.03ms（阈值 p95<500ms 通过）
- `checks_succeeded`：100%

## Core flows（A+B 为主，C+D 适量）

脚本：`perf/k6/api-core-stages.js`

### 覆盖范围（按 flow）

- A（主要）：逛吃/搜索/详情（高频读）
	- `GET /api/v1/canteens/`
	- `GET /api/v1/canteens/<id>/`、`GET /api/v1/canteens/<id>/floors/`
	- `GET /api/v1/dishes/`（search/ordering/tag_ids 等）
	- `GET /api/v1/dishes/<id>/`、`GET /api/v1/dishes/hot/`、`GET /api/v1/dishes/new/`
	- `GET /api/v1/tags/`
- B（主要）：互动写（评分/标签/评论/打卡）
	- `POST /api/v1/dishes/<id>/rate/`
	- `POST /api/v1/dishes/<id>/tags/`
	- `POST /api/v1/dishes/<id>/reviews/create/`
	- `POST /api/v1/dishes/<id>/check-in/`
	- `GET /api/v1/reviews/my/`
- C（少量）：论坛（读为主，少量点赞）
	- `GET /api/v1/forum/home/`（可选）
	- `GET /api/v1/posts/`、（可选）`GET /api/v1/posts/<id>/`、`GET /api/v1/posts/<id>/comments/`
	- （轻量写，non-strict）`POST /api/v1/posts/<id>/like/`
	- （轻量写，non-strict）`POST /api/v1/comments/create/`、`POST /api/v1/comments/<id>/like/`、`POST /api/v1/comments/<id>/delete/`
	- （可选，non-strict）`GET /api/v1/dishes/<dish_id>/posts/`
	- （可选，non-strict/edge）`POST /api/v1/upload/image/`、`POST /api/v1/posts/create/`
- D（少量）：个人中心（轻量读）
	- `GET /api/v1/profile`、`GET /api/v1/profile/stats`、`GET /api/v1/profile/check-in-history`

### 参数与开关

- `FLOW_WEIGHTS`：按权重选择 A/B/C/D 的比例，例如：`{"A":70,"B":20,"C":7,"D":3}`
- `ENABLE_WRITES`：`1`（默认）启用 B 的写接口；`0` 则 B 会退化为安全读（便于先做纯读压测）

### 写链路依赖：确保 dishes 非空

B 流需要有 dish 数据才能产生写样本。
如果你遇到 `dishes=[]`，请先在测试库造数（仓库已提供对应的 management command / 造数脚本；如果你没看到命令名，以 `dishes` / `seed` 关键字在 `src/backend/app/**/management/commands/` 里搜一下即可）。

（如果你希望我把“造 dish 数据”的命令名与完整用法也写进这里，我可以再补一段，确保真正开箱即用。）

### 写链路阈值口径：strict vs allowed

很多写接口会出现业务允许的 400（例如“已打卡/重复提交/已存在”）。为了不让阈值被这些“可接受失败”污染：

- **strict**：只把 HTTP 200 视为 `expected_response:true`，用于阈值统计（更接近“成功写入/成功变更”）。
- **allowed**：允许 200/400，只做功能 check，不纳入阈值（更接近“用户反复点击/幂等”）。

如果你希望把“400=幂等成功”也算作成功率，我们可以把阈值逻辑改成以 `checks` 为门槛（而不是 http_req_failed）。

### 覆盖策略：strict vs edge

- `expected_response:true`：用于严格阈值统计（global p95、flow A p95 等）
- `expected_response:false` / `semantic=edge`：用于覆盖但不纳入严格阈值（边界参数、可能较慢、或依赖环境配置的请求）

### 性能关键开关：禁用外部内容审核（本地压测建议开启）

`create_review` 默认会走一次外部内容审核调用（可能带来秒级 p95）。为了让本地压测聚焦在“自身接口性能”，后端提供了开关：

- `DISABLE_CONTENT_AUDIT=1`：直接跳过外部审核

仓库已添加 `docker-compose.override.yaml`，默认会给 `backend` 注入 `DISABLE_CONTENT_AUDIT: "1"`（仅本地 override，不影响主 compose）。
如果你需要在某次压测里恢复真实审核链路，临时关掉这个环境变量即可（或移走 override 文件）。

### 最近一次结果

- `perf/results/20260103-004139/`
	- 阈值（expected_response:true）整体 p95 ≈ 10ms、失败率 0%
	- `checks_succeeded` 100%


