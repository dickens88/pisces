import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/router.js'
import i18n from './i18n/i18n.js'
import { useAuthStore } from './stores/auth'
import { getAppConfig } from '@config'
import { handleTianyanLoginRedirect } from './utils/auth'
import './style.css'
import './styles/datepicker.css'

const config = getAppConfig(import.meta.env, import.meta.env.PROD)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

// 从cookie读取指定名称的cookie值
function getCookie(name) {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [cookieName, cookieValue] = cookie.trim().split('=')
    if (cookieName === name) {
      return decodeURIComponent(cookieValue)
    }
  }
  return null
}

// 如果使用tianyan-web认证模式，尝试获取token
if (config.authMode === 'tianyan' && config.enableAuth) {
  const authStore = useAuthStore()
  
  // 1. 优先从URL参数中读取token（从tianyan-web登录后重定向回来时）
  const urlParams = new URLSearchParams(window.location.search)
  const tokenFromUrl = urlParams.get('token')
  if (tokenFromUrl) {
    authStore.setToken(tokenFromUrl)
    
    // 处理重定向：优先使用URL中的redirect参数，其次使用sessionStorage
    setTimeout(() => {
      handleTianyanLoginRedirect(router)
    }, 100)
  }
  // 2. 如果没有token，尝试从cookie读取access_token（tianyan-web将token存储在cookie中）
  else if (!authStore.token) {
    const accessToken = getCookie('access_token')
    if (accessToken) {
      authStore.setToken(accessToken)
    }
    // 3. 如果cookie中也没有，尝试从localStorage读取（同域情况下可以共享）
    else {
      const sharedToken = localStorage.getItem('token')
      if (sharedToken) {
        authStore.setToken(sharedToken)
      }
    }
  }
}

app.mount('#app')

