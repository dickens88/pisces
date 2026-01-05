import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { getAppConfig } from './config.js'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const config = getAppConfig(env, mode === 'production')
  const baseUrl = env.VITE_WEB_BASE_PATH || '/'
  
  return {
    base: baseUrl,
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@config': fileURLToPath(new URL('./config.js', import.meta.url))
      }
    },
    server: {
      host: true,
      port: 3000,
      open: true,
      allowedHosts: [
        'localhost',
        '.dearcharles.cn',
        'pisces.dearcharles.cn'
      ],
      ...(mode === 'development' && {
        proxy: {
          '/api': {
            target: config.apiTarget,
            changeOrigin: true,
            secure: false
          },
          // 通过代理访问 Dify API（解决 CORS 问题）
          '/dify-api': {
            target: config.aiChatApi ? config.aiChatApi.replace(/\/v1\/.*$/, '').replace(/\/$/, '') : 'http://dify.eu.dearcharles.cn',
            changeOrigin: true,
            secure: false,
            rewrite: (path) => path.replace(/^\/dify-api/, ''),
            configure: (proxy, _options) => {
              proxy.on('error', (err, _req, _res) => {
                console.log('Dify API proxy error', err)
              })
            }
          }
        }
      }),
      headers: {
        'Content-Security-Policy': "frame-ancestors *;"
      }
    }
  }
})
