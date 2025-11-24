import axios from 'axios'
import router from '@/router/router'
import { useAuthStore } from '@/stores/auth'
import { getAppConfig } from '@config'
import { redirectToTianyanLogin } from '@/utils/auth'
const config = getAppConfig(import.meta.env, import.meta.env.PROD)

// Create axios instance
const service = axios.create({
  baseURL: config.apiBaseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

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

// Request interceptor
service.interceptors.request.use(
  requestConfig => {
    // 无论配置如何，都尝试从cookie读取token（因为cookie是最可靠的来源）
    const cookieToken = getCookie('access_token')
    const authStore = useAuthStore()
    let token = null
    
    // 优先从cookie读取（无论什么模式，cookie都是最可靠的）
    if (cookieToken) {
      token = cookieToken
      authStore.setToken(token)
    } else {
      // 如果cookie中没有，尝试其他来源
      // 1. 从URL参数读取
      const urlParams = new URLSearchParams(window.location.search)
      const tokenFromUrl = urlParams.get('token')
      if (tokenFromUrl) {
        token = tokenFromUrl
        authStore.setToken(token)
      } else {
        // 2. 从store读取
        token = authStore.token
        if (!token) {
          // 3. 从localStorage读取
          token = localStorage.getItem('token')
          if (token) {
            authStore.setToken(token)
          }
        }
      }
    }
    
    // 如果找到了token，添加到请求头
    if (token) {
      requestConfig.headers.Authorization = `Bearer ${token}`
    }
    
    // Can add other request headers here, such as language settings
    requestConfig.headers['Accept-Language'] = localStorage.getItem('locale') || 'zh-CN'
    
    return requestConfig
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

function redirectToLogin() {
  // Tianyan mode still relies on external login page
  if (redirectToTianyanLogin()) {
    return
  }

  const currentRoute = router.currentRoute?.value
  const isAlreadyOnLogin = currentRoute?.name === 'Login' || window.location.pathname === '/login'

  if (isAlreadyOnLogin) {
    return
  }

  const query =
    currentRoute && currentRoute.fullPath ? { redirect: currentRoute.fullPath } : undefined

  router
    .replace({
      name: 'Login',
      ...(query ? { query } : {})
    })
    .catch(() => {
      // Fallback to hard navigation if router navigation fails
      const resolved = router.resolve({ name: 'Login', ...(query ? { query } : {}) })
      window.location.href = resolved.href
    })
}

// Response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // Handle response data structure
    // If backend returns format { code: 200, data: {...}, message: '...' }
    if (res.code && res.code !== 200) {
      console.error('API Error:', res.message || 'Error')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)
    
    // Handle HTTP error status codes
    if (error.response) {
      switch (error.response.status) {
        case 401:
        case 422:
          // Unauthorized / invalid token, clear token and redirect to login page
          if (config.enableAuth) {
            const authStore = useAuthStore()
            authStore.logout()
            redirectToLogin()
          }
          break
        case 403:
          console.error('Forbidden: Access denied')
          break
        case 404:
          console.error('Not Found: The requested resource was not found')
          break
        case 500:
          console.error('Server Error: Internal server error')
          break
        default:
          console.error('Error:', error.response.data?.message || error.message)
      }
    }
    
    return Promise.reject(error)
  }
)

export default service

