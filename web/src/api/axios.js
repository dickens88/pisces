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
  console.log('[Auth] redirectToLogin() called', {
    authMode: config.authMode,
    enableAuth: config.enableAuth,
    currentPath: window.location.pathname
  })

  // Tianyan mode still relies on external login page
  const tianyanResult = redirectToTianyanLogin()
  console.log('[Auth] redirectToTianyanLogin() result:', tianyanResult)
  if (tianyanResult) {
    console.log('[Auth] Redirected to Tianyan login page')
    return
  }

  const currentRoute = router.currentRoute?.value
  const isAlreadyOnLogin = currentRoute?.name === 'Login' || window.location.pathname === '/login'
  console.log('[Auth] Current route check:', {
    routeName: currentRoute?.name,
    pathname: window.location.pathname,
    isAlreadyOnLogin
  })

  if (isAlreadyOnLogin) {
    console.log('[Auth] Already on login page, skipping redirect')
    return
  }

  const query =
    currentRoute && currentRoute.fullPath ? { redirect: currentRoute.fullPath } : undefined
  console.log('[Auth] Attempting router redirect to Login', { query })

  // 使用 try-catch 确保跳转一定会执行
  try {
    router
      .replace({
        name: 'Login',
        ...(query ? { query } : {})
      })
      .then(() => {
        console.log('[Auth] Router redirect to Login succeeded')
      })
      .catch((error) => {
        console.error('[Auth] Router redirect failed, using window.location fallback:', error)
        // Fallback to hard navigation if router navigation fails
        const resolved = router.resolve({ name: 'Login', ...(query ? { query } : {}) })
        console.log('[Auth] Using window.location.href:', resolved.href)
        window.location.href = resolved.href
      })
  } catch (error) {
    // 如果router操作失败，直接使用window.location跳转
    console.error('[Auth] Router navigation exception, using window.location:', error)
    const loginPath = query ? `/login?redirect=${encodeURIComponent(query.redirect)}` : '/login'
    console.log('[Auth] Direct window.location.href:', loginPath)
    window.location.href = loginPath
  }
}

function handleUnauthorized() {
  console.log('[Auth] handleUnauthorized() called', {
    enableAuth: config.enableAuth,
    authMode: config.authMode,
    hasToken: !!useAuthStore().token
  })

  // 即使 enableAuth 为 false，也应该清除token并尝试跳转
  // 因为401表示认证失败，需要重新登录
  const authStore = useAuthStore()
  authStore.logout()
  console.log('[Auth] Token cleared, user logged out')
  
  // 只有在明确禁用认证时才不跳转
  if (!config.enableAuth) {
    console.warn('[Auth] Authentication is disabled, but received 401. Token cleared.')
    return
  }
  
  console.log('[Auth] Calling redirectToLogin()')
  redirectToLogin()
}

function isUnauthorizedCode(code) {
  if (!code) return false
  const normalized = Number(code)
  return normalized === 401 || normalized === 422
}

// Response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // Handle response data structure
    // If backend returns format { code: 200, data: {...}, message: '...' }
    if (res.code && res.code !== 200) {
      console.log('[Auth] Response with non-200 code:', {
        code: res.code,
        message: res.message,
        isUnauthorized: isUnauthorizedCode(res.code)
      })
      if (isUnauthorizedCode(res.code)) {
        console.log('[Auth] Detected unauthorized code in response.data, calling handleUnauthorized()')
        handleUnauthorized()
      }
      console.error('API Error:', res.message || 'Error')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('[Auth] Response error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url
    })
    
    // Handle HTTP error status codes
    if (error.response) {
      const status = error.response.status
      console.log('[Auth] HTTP error status:', status)
      switch (status) {
        case 401:
        case 422:
          console.log('[Auth] Detected 401/422 status code, calling handleUnauthorized()')
          handleUnauthorized()
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
    } else {
      console.warn('[Auth] No error.response object, network error or request cancelled')
    }
    
    return Promise.reject(error)
  }
)

export default service

