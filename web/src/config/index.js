/**
 * 应用配置
 * 可以通过环境变量 VITE_ENABLE_AUTH 来控制是否启用认证
 * 默认值：true（启用认证）
 */
export const config = {
  // 是否启用前端认证页面
  // 设置为 false 时，将跳过所有登录检查，直接访问页面
  enableAuth: import.meta.env.VITE_ENABLE_AUTH !== 'false',
  
  // API 基础URL
  apiBaseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  
  // API 目标地址
  // 开发环境：http://localhost:8080
  // 生产环境：http://pisces.eu.dearcharles.cn:8080
  apiTarget: import.meta.env.VITE_API_TARGET || (
    import.meta.env.PROD 
      ? 'http://pisces.eu.dearcharles.cn:8080'
      : 'http://localhost:8080'
  )
}

export default config

