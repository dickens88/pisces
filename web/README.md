# SIEM Platform Frontend

基于 Vue3 的大型 SIEM 系统前端项目。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 的状态管理库
- **Vue I18n** - 国际化插件
- **Axios** - HTTP 客户端
- **Tailwind CSS** - 实用优先的 CSS 框架

## 项目结构

```
SIEM/
├── config.js             # 统一配置文件（构建时和运行时共用）
├── src/
│   ├── api/              # API 接口
│   │   ├── index.js      # Axios 配置和拦截器
│   │   └── alerts.js     # 告警相关 API
│   ├── assets/           # 静态资源
│   ├── components/       # 组件
│   │   ├── layout/       # 布局组件
│   │   │   └── Sidebar.vue
│   │   └── alerts/       # 告警相关组件
│   │       └── AlertDetail.vue
│   ├── i18n/             # 国际化
│   │   ├── index.js
│   │   └── locales/      # 语言文件
│   │       ├── zh-CN.json
│   │       └── en-US.json
│   ├── layouts/          # 布局
│   │   └── index.vue
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── stores/           # Pinia 状态管理
│   │   ├── app.js        # 应用状态
│   │   └── auth.js       # 认证状态
│   ├── views/            # 页面视图
│   │   └── alerts/       # 告警页面
│   │       └── index.vue
│   ├── App.vue           # 根组件
│   ├── main.js           # 入口文件
│   └── style.css         # 全局样式
├── index.html
├── package.json
├── vite.config.js        # Vite 配置（引用 config.js）
├── tailwind.config.js
└── postcss.config.js
```

## 功能特性

### 1. 多语言支持
- 支持中文（zh-CN）和英文（en-US）
- 可扩展支持其他语言（如匈牙利语）
- 语言设置持久化存储

### 2. 统一 API 拦截器
- 请求拦截器：自动添加认证 token（为 SSO 集成预留）
- 响应拦截器：统一错误处理
- 支持多语言请求头

### 3. 响应式布局
- 左侧导航菜单（可收起/展开）
- 统一的页眉和页脚框架
- 适配桌面端显示

### 4. 告警管理
- 告警列表页面：展示告警信息、统计数据和筛选功能
- 告警详情页面：从右侧滑入的详情抽屉
- Mock 数据支持

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 配置管理

项目使用统一的配置文件 `config.js`（位于项目根目录）来管理所有配置项，确保构建时（`vite.config.js`）和运行时（各个组件文件）使用相同的配置逻辑。

所有配置项都通过环境变量进行设置，配置文件会自动读取环境变量并提供默认值。

在代码中，可以通过 `@config` 别名导入配置函数：
```javascript
import { getAppConfig } from '@config'
const config = getAppConfig(import.meta.env, import.meta.env.PROD)
```

## 环境变量

创建 `.env` 文件配置环境变量：

```env
# API 配置
VITE_API_BASE_URL=/api
VITE_API_TARGET=http://localhost:8080

# 前端基础路径（如部署在子路径或指定完整URL）
VITE_WEB_BASE_PATH=https://huntingportal.dearcharles.cn/pisces

# 认证配置
# 是否启用认证（默认：true）
VITE_ENABLE_AUTH=true

# 认证模式：'local' 使用pisces本地认证，'tianyan' 使用tianyan-web认证
# 当设置为 'tianyan' 时，将关闭pisces的登录页面，401错误会重定向到tianyan-web登录页面
VITE_AUTH_MODE=local

# tianyan-web项目的基础URL（当VITE_AUTH_MODE为'tianyan'时使用）
VITE_TIANYAN_WEB_BASE_URL=http://localhost:3000
```

### 使用 tianyan-web 认证

当需要复用 tianyan-web 项目的 JWT 认证时，需要配置以下内容：

1. **前端配置**：在 `.env` 文件中设置：
   ```env
   VITE_AUTH_MODE=tianyan
   VITE_TIANYAN_WEB_BASE_URL=http://tianyan-web-server:port
   ```

2. **后端配置**：设置环境变量 `JWT_SECRET_KEY`，使其与 tianyan-web 项目使用相同的 JWT secret key：
   ```bash
   export JWT_SECRET_KEY=your-shared-jwt-secret-key
   ```

3. **工作流程**：
   - 当用户访问 pisces 项目但未登录时，会自动重定向到 tianyan-web 的登录页面
   - 用户在 tianyan-web 登录后，tianyan-web 需要重定向回 pisces，并在 URL 参数中传递 token
   - pisces 会自动从 URL 参数中读取 token 并保存到 localStorage
   - 之后 pisces 使用该 token 访问 API 接口

**注意**：使用 tianyan-web 认证模式时，pisces 的登录页面将被禁用，所有认证相关的操作都会重定向到 tianyan-web。

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.js` 添加路由配置
3. 在 `src/components/layout/Sidebar.vue` 添加导航菜单项

### 添加新语言

1. 在 `src/i18n/locales/` 创建新的语言文件（如 `hu-HU.json`）
2. 在 `src/i18n/index.js` 中导入并注册新语言

### API 调用

使用统一的 API 服务：

```javascript
import service from '@/api'
import { getAlerts } from '@/api/alerts'

// 使用 service 进行自定义请求
service.get('/endpoint')

// 使用封装好的 API 方法
const alerts = await getAlerts({ page: 1, pageSize: 10 })
```

## 后续扩展

- [ ] SSO 认证集成
- [ ] 更多页面（事件管理、漏洞管理等）
- [ ] 实时数据更新
- [ ] 图表可视化
- [ ] 权限管理
- [ ] 主题切换

## 许可证

MIT

