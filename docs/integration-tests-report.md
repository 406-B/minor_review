# 后端集成测试报告（Minor Review）

> 日期：2025-12-25

本文档面向本仓库的 **后端集成测试**（pytest + pytest-django，非 Cypress E2E），说明测试环境、测试工具、测试流程与覆盖率计算方法，并给出常见问题排查指南。

---

## 1. 测试范围与口径

### 1.1 什么是“集成测试”

本项目的后端集成测试遵循以下口径：

- **通过 HTTP/API 调用 + 数据库读写** 验证一条业务链路（典型为 DRF APIClient 请求）。
- 允许对不稳定外部依赖做最小化隔离（例如内容审核、外部服务调用），以保证 CI/Docker 内可复现、可稳定运行。
- **不包含** 浏览器端到端测试（E2E），E2E 由 `cypress/` 维护。

### 1.2 选择性运行：`integration` marker

后端测试通过 pytest markers 进行分类。`src/backend/app/pytest.ini` 中声明：

- `integration`: 集成测试
- `unit`: 单元测试
- `slow`: 慢速测试

推荐使用：

```powershell
# 在 src/backend/app 下
pytest -m integration -q
```

---

## 2. 测试环境

### 2.1 本机环境（开发机）

关键点：

- Python（开发期版本可能高于 Docker）
- Django + DRF
- pytest + pytest-django + pytest-cov

本机执行入口（推荐工作目录）：

```powershell
cd C:\rg2025_test\minor_review\src\backend\app
pytest -m integration -q
```

> 说明：在该目录下运行会读取 `pytest.ini`，自动设置 `DJANGO_SETTINGS_MODULE=app.test_settings`。

### 2.2 Docker 环境（权威回归口径）

仓库根目录包含 `Dockerfile.simple`（Python 3.9-slim）。镜像安装依赖来自：

- `src/backend/requirements.txt`

Docker 推荐运行方式：

```powershell
cd C:\rg2025_test\minor_review

docker build -f Dockerfile.simple -t minor-review-tests .

docker run --rm minor-review-tests sh -lc "cd /app/src/backend/app && pytest -m integration -q"
```

**重要注意**：

- 若直接在容器 `WORKDIR=/app` 下执行 `pytest`，可能无法读取 `/app/src/backend/app/pytest.ini`，从而出现：
  - `django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured...`
- 解决方式是：**先 `cd /app/src/backend/app` 再跑 pytest**。

---

## 3. 测试工具链

### 3.1 pytest / pytest-django

配置来源：`src/backend/app/pytest.ini`

关键配置项（摘录解释）：

- `DJANGO_SETTINGS_MODULE = app.test_settings`
  - pytest-django 会用该 settings 初始化 Django。
- `testpaths = tests`
  - 限制收集范围到 `src/backend/app/tests/`。
- `--no-migrations`
  - 跳过迁移执行（加速并减少迁移相关不稳定）。
- `--strict-markers`
  - marker 必须在 ini 中声明，避免拼写错误导致测试集合混乱。

### 3.2 DRF APIClient

测试中常用：

- `rest_framework.test.APIClient()`：模拟 HTTP 请求
- `force_authenticate(user=...)`：在权限相关分支中稳定注入 Django `auth.User`

在 `tests/conftest.py` 中也有基础 fixture：

- `api_client` / `auth_client`
- `test_user`（Django auth.User）

### 3.3 依赖清单

`src/backend/requirements.txt` 中测试相关依赖：

- `pytest==7.4.3`
- `pytest-django==4.7.0`
- `pytest-cov==4.1.0`

---

## 4. 测试流程（推荐实践）

### 4.1 开发期增量流程（小步快跑）

1) **只跑相关文件/用例**（快速验证）

```powershell
cd C:\rg2025_test\minor_review\src\backend\app
pytest -m integration -q tests\test_list_views_branches_integration.py -k "review_"
```

2) **本机局部全量**（同目录下跑 integration 但缩小范围）

```powershell
pytest -m integration -q tests\
```

3) **Docker 全量回归（权威）**

```powershell
cd C:\rg2025_test\minor_review

docker build -f Dockerfile.simple -t minor-review-tests .

docker run --rm minor-review-tests sh -lc "cd /app/src/backend/app && pytest -m integration -q"
```

### 4.2 稳定性策略（避免 flaky）

建议遵循：

- 避免真实外部依赖（网络请求、验证码轮询、Selenium 真浏览器等）。
- 对不可控逻辑进行最小化 monkeypatch（例如内容审核函数返回 pass/fail 分支），确保可重复。
- 权限分支使用 `force_authenticate(user=AuthUser)`，避免 token/user 对象属性缺失导致 500。

---

## 5. 覆盖率计算方法

### 5.1 Coverage 的统计入口

覆盖率由 pytest-cov 驱动，配置在 `src/backend/app/pytest.ini`：

- `--cov=.`：以当前工作目录（建议 `/app/src/backend/app`）作为测量根
- `--cov-config=.coveragerc`：使用项目的 coverage 配置
- `--cov-report=term-missing`：终端输出缺失行
- `--cov-report=html`：生成 HTML 报告

### 5.2 `.coveragerc` 口径（包含/排除规则）

配置文件：`src/backend/app/.coveragerc`

- `source = .`：统计范围从当前目录开始
- `omit =`：排除以下内容（不会计入覆盖率分母）：
  - `*/migrations/*`
  - `*/tests/*`、`*/test_*.py`（测试代码本身不计入）
  - `manage.py`、`wsgi.py`、`asgi.py`、`settings_prod.py`、`auto_login.py`
  - 虚拟环境/缓存目录

因此：
- **分子**：执行到的业务代码行
- **分母**：未被 omit 的业务代码总行数

### 5.3 输出产物

- 终端：`term-missing` 会显示每个文件的 `Stmts/Miss/Cover/Missing`。
- HTML：输出到 `src/backend/app/htmlcov/`（由 `.coveragerc` 的 `[html] directory = htmlcov` 指定）。

### 5.4 如何解读数字

- `TOTAL`：所有被统计文件的整体覆盖率
- 单文件（例如 `list/views.py`）：用于定位最大缺口、优先补测
- `Missing` 列：行号列表，为下一轮补分支提供精确落点

---

## 6. 常见问题与排查

### 6.1 Docker 内提示 settings 未配置

现象：

- `ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured...`

原因：

- pytest 未读取到 `src/backend/app/pytest.ini`，从而没有 `DJANGO_SETTINGS_MODULE`。

解决：

```powershell
# 容器内先进入 /app/src/backend/app

docker run --rm minor-review-tests sh -lc "cd /app/src/backend/app && pytest -m integration -q"
```

### 6.2 marker 使用报错

现象：

- `--strict-markers` 下，未声明 marker 会报错。

解决：

- 在 `src/backend/app/pytest.ini` 的 `markers =` 中声明新的 marker。

---

## 7. 附录：关键配置文件索引

- 后端 pytest 配置：`src/backend/app/pytest.ini`
- 覆盖率配置：`src/backend/app/.coveragerc`
- Docker 测试镜像：`Dockerfile.simple`
- Python 依赖：`src/backend/requirements.txt`
- pytest fixtures：`src/backend/app/tests/conftest.py`
