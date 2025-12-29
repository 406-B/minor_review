# Minor Review（前端）UI 设计报告

> 目标：说明本项目 UI 设计如何落地（UI 统一策略、通用 UI 模块沉淀、配套工具链与流程），并给出代码级证据点，便于评审与后续迭代。

## 1. 技术栈与工具链

### 1.1 核心框架
- **Vue 3 + Vite**：作为 UI 的组件化开发与构建工具链。
- **Element Plus**：作为基础组件库，减少重复造轮子，并通过全局样式做一致性收敛。
- **Vue Router**：承载页面结构与导航体验。

### 1.2 工程化与质量工具
- **Vitest**：前端单元/组件测试框架（仓库中已配置）。
- **vite-plugin-vue-devtools**：开发时的 Vue DevTools 增强（Vite 插件形式）。

> 证据：`src/frontend/package.json`（依赖声明），`src/frontend/vite.config.js`（Vite 插件与代理配置）。

## 2. UI 统一策略（Design System 思路）

本项目的 UI 统一主要通过「全局基础样式 + 主题变量（CSS 变量）+ 通用布局/卡片/标题/工具条类」来实现。

### 2.1 全局样式与主题入口
- 全局样式入口：`src/frontend/src/assets/main.css`
  - 引入 `base.css` 作为全局 reset/基础规范。
  - 引入 `./theme/theme.css` 作为主题变量来源（颜色、圆角、阴影、字号、容器宽度等）。

在 `main.css` 中定义了全局容器、链接交互、通用卡片类、section 标题类、工具条类与滚动条规范，用于跨页面复用。

> 证据：`src/frontend/src/assets/main.css`
- `.main-container` 统一页面背景与布局（flex column、全高）。
- `.ui-card` / `.ui-section-title` / `.ui-toolbar` 提供通用“设计语义类”。
- `*::-webkit-scrollbar` 对滚动条风格统一（与主题色一致）。

### 2.2 与组件库的统一
项目使用 Element Plus，但并不完全依赖“默认主题”，而是结合 `base.css` / `main.css` 进行细节收敛：
- 统一 hover/active 的品牌色反馈。
- 通过 CSS 变量将背景、边框、圆角、阴影等“设计 token”集中管理（降低改版成本）。

> 证据：`src/frontend/base.css`、`src/frontend/src/assets/main.css`。

## 3. 通用 UI 模块沉淀（components/ui）

项目将“与业务无关、跨页面复用的 UI”沉淀在 `src/frontend/src/components/ui/`，用于快速搭建页面并确保视觉一致。

### 3.1 PageContainer：页面骨架
- 文件：`src/frontend/src/components/ui/PageContainer.vue`
- 设计意图：统一页面宽度、内边距、头部区与主体卡片容器。
- 交互/结构：
  - `header` slot 可选（有 slot 才渲染 header），主体为默认 slot。
  - 主体区域默认使用“卡片”视觉（border、radius、shadow），与全局 token 对齐。

### 3.2 AppTopBar：顶栏与全局导航
- 文件：`src/frontend/src/components/ui/AppTopBar.vue`
- 设计意图：统一全站导航入口与品牌识别；减少每个页面各自实现 topbar 的重复。
- 关键点：
  - `position: sticky; top: 0` 固定在顶部，页面滚动时保持关键导航可用。
  - 基于当前路由 `route.path.startsWith(path)` 标记 active 样式，提供一致的“当前位置”反馈。
  - 未登录状态展示登录/注册入口与提示文案（避免用户迷失）。

### 3.3 SectionTitle：统一分区标题
- 文件：`src/frontend/src/components/ui/SectionTitle.vue`
- 设计意图：标题样式统一（颜色、字号、weight、间距），避免不同页面出现多套风格。

### 3.4 EmptyState：统一空状态
- 文件：`src/frontend/src/components/ui/EmptyState.vue`
- 设计意图：统一「暂无数据」类场景的占位表达。
- 关键点：
  - 支持 `text`（默认“暂无数据”）与 `icon`。
  - slot 扩展位（例如放“去创建”“刷新”等动作）。

## 4. 页面路由与信息架构（IA）

### 4.1 路由组织
- 文件：`src/frontend/src/router/index.js`
- 特点：
  - 以页面域划分：登录/注册、食堂浏览、菜品详情、社区、个人主页、引导页等。
  - 多数路由使用 `() => import('...')` 懒加载，降低首屏包体。
  - `scrollBehavior` 统一滚动行为：新导航滚动到顶部，back/forward 恢复保存位置。

### 4.2 登录态与受保护路径
- 在路由守卫中读取 `localStorage.getItem('jwt')`。
- 结合 `isProtectedPath(to.path)` 或 `to.meta.requiresAuth` 判定是否需要登录；未登录跳转 `/login`。

### 4.3 体验细节：滚动位置记忆与过渡优化
- 从“食堂浏览”进入“菜品详情”前，会记录主容器滚动位置（`sessionStorage.setItem('canteenScroll', ...)`）。
- 从“详情返回食堂”时标记 `returningFromDetail` 并加 `document.documentElement.classList.add('no-animate')`，用于页面侧跳过某些动画，减少闪动。

> 证据：`src/frontend/src/router/index.js`

## 5. 前后端联调体验（开发代理）

为了让前端在本地开发时“无感”请求后端接口，Vite 做了代理：
- `/api`、`/media` → `http://localhost:8000`

这样前端代码可以固定使用相对路径 `/api/...`，无需在代码里区分环境，减少配置分散。

> 证据：`src/frontend/vite.config.js`

## 6. 建议的 UI 迭代流程（适合项目当前形态）

1. **确定设计 token**：在 `theme.css`/`base.css` 中定义颜色、圆角、阴影、字号、容器宽度。
2. **沉淀通用模块**：优先把页面里重复出现的结构抽出来放入 `components/ui/`（如容器、顶栏、标题、空状态）。
3. **页面实现只关注业务**：页面组件用通用模块“拼装”，避免重复写 layout/样式。
4. **测试与回归**：Vitest 覆盖关键 UI 逻辑与工具函数；上线前配合 Cypress 进行基础链路回归（仓库已有 Cypress 配置）。

## 7. 证据清单（本报告引用到的文件）
- 全局样式：`src/frontend/base.css`、`src/frontend/src/assets/main.css`
- 通用 UI 组件：
  - `src/frontend/src/components/ui/PageContainer.vue`
  - `src/frontend/src/components/ui/AppTopBar.vue`
  - `src/frontend/src/components/ui/SectionTitle.vue`
  - `src/frontend/src/components/ui/EmptyState.vue`
- 路由与体验：`src/frontend/src/router/index.js`
- 工具链配置：`src/frontend/package.json`、`src/frontend/vite.config.js`

---

### 可选的后续补强（如果你希望报告更“可展示”）
- 补一张“主题 token 表”（品牌色阶、边框色、字号、圆角、阴影）。
- 为 `components/ui/*` 增补最小化的 Story/文档页面（或在 `docs/` 增加截图/动图与使用示例）。
