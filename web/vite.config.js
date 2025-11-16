import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { getAppConfig } from './config.js'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const config = getAppConfig(env, mode === 'production')
  const basePath = env.VITE_WEB_BASE_PATH || '/'
  
  return {
    base: basePath,
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
          }
        }
      }),
      headers: {
        'Content-Security-Policy': "frame-ancestors *;"
      }
    }
  }
})
