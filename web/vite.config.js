import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: true,
      port: 3000,
      open: true,
      // 只在开发环境配置代理
      ...(mode === 'development' && {
        proxy: {
          '/api': {
            target: env.VITE_API_TARGET || 'http://localhost:8080',
            changeOrigin: true,
            secure: false
          }
        }
      }),
      headers: {
        // 允许被 iframe 嵌入（开发环境）
        // 生产环境需要在 Web 服务器（如 Nginx）中配置
        // 
        // 方式 1: 使用 CSP 的 frame-ancestors（推荐，支持跨域）
        // 允许所有域名嵌入（开发测试用）
        'Content-Security-Policy': "frame-ancestors *;",
        // 或只允许特定域名: 'Content-Security-Policy': "frame-ancestors 'self' https://example.com;",
        //
        // 方式 2: 使用 X-Frame-Options（仅同源，不推荐用于跨域场景）
        // 'X-Frame-Options': 'SAMEORIGIN', // 只允许同源嵌入
        // 'X-Frame-Options': 'ALLOWALL', // 允许所有（已废弃，但某些浏览器仍支持）
      }
    }
  }
})
