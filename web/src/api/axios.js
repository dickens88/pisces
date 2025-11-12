import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Create axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    // Get token from store (for future SSO integration)
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    // Can add other request headers here, such as language settings
    config.headers['Accept-Language'] = localStorage.getItem('locale') || 'zh-CN'
    
    return config
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
          const authStore = useAuthStore()
          authStore.logout()
          // Can add route redirect to login page here
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

