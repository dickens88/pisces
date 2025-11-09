# 快速启动指南

## 前置要求

- Node.js 16+ 
- npm 或 yarn

## 安装步骤

1. **安装依赖**
   ```bash
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **访问应用**
   打开浏览器访问: http://localhost:3000

## 功能说明

### 1. 告警列表页面
- 访问路径: `/alerts`
- 功能:
  - 查看告警列表
  - 搜索和筛选告警
  - 查看统计数据
  - 点击告警标题查看详情

### 2. 告警详情
- 点击告警列表中的标题
- 详情面板从右侧滑入
- 包含:
  - AI分析
  - 告警信息
  - 关联实体
  - 事件时间线
  - 评论功能

### 3. 语言切换
- 点击右上角语言选择器
- 支持中文和英文
- 语言设置会自动保存

### 4. 侧边栏
- 点击底部按钮可收起/展开
- 包含导航菜单项

## 项目结构说明

```
src/
├── api/              # API接口层
│   ├── index.js      # Axios配置和拦截器
│   └── alerts.js     # 告警相关API（包含Mock数据）
├── components/       # 可复用组件
│   ├── layout/       # 布局组件
│   └── alerts/       # 告警相关组件
├── i18n/             # 国际化配置
├── layouts/          # 页面布局
├── router/           # 路由配置
├── stores/           # 状态管理（Pinia）
└── views/            # 页面视图
```

## 开发提示

1. **添加新页面**
   - 在 `src/views/` 创建新页面
   - 在 `src/router/index.js` 添加路由
   - 在 `src/components/layout/Sidebar.vue` 添加菜单项

2. **添加新语言**
   - 在 `src/i18n/locales/` 创建语言文件
   - 在 `src/i18n/index.js` 导入并注册

3. **API调用**
   - 使用 `src/api/index.js` 中的 service
   - 或使用封装好的API方法（如 `getAlerts`）

4. **样式**
   - 使用 Tailwind CSS 类名
   - 自定义样式在 `src/style.css`

## 后续集成

### SSO认证集成
当需要集成SSO时，修改 `src/api/index.js` 中的请求拦截器：

```javascript
// 在请求拦截器中添加SSO token
config.headers.Authorization = `Bearer ${ssoToken}`
```

### 连接真实API
修改 `src/api/alerts.js`，将Mock数据替换为真实API调用：

```javascript
export const getAlerts = (params) => {
  return service.get('/alerts', { params })
}
```

## 常见问题

**Q: 如何修改端口？**
A: 修改 `vite.config.js` 中的 `server.port`

**Q: 如何添加新语言？**
A: 参考"开发提示"中的"添加新语言"部分

**Q: Mock数据在哪里？**
A: `src/api/alerts.js` 文件中的 `mockAlerts` 数组

