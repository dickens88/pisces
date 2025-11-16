import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { config } from '@/config'

// Create axios instance
const service = axios.create({
  baseURL: config.apiBaseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  requestConfig => {
    // Get token from store (for future SSO integration)
    // 只有在启用认证时才添加 token
    if (config.enableAuth) {
      const authStore = useAuthStore()
      if (authStore.token) {
        requestConfig.headers.Authorization = `Bearer ${authStore.token}`
      }
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
          // Unauthorized, clear token and redirect to login page
          // 只有在启用认证时才处理 401 错误
          if (config.enableAuth) {
            const authStore = useAuthStore()
            authStore.logout()
            // Redirect to login page
            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
          }
          break
        case 422:
          // Unprocessable Entity, often used for invalid token or authentication errors
          // 只有在启用认证时才处理 422 错误
          if (config.enableAuth) {
            const authStore = useAuthStore()
            authStore.logout()
            // Redirect to login page
            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
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

