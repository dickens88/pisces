import { defineStore } from 'pinia'
import { getCurrentUserInfo } from '@/api/auth'

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

// 获取token的优先级：localStorage > cookie中的access_token
function getInitialToken() {
  // 1. 优先从localStorage读取
  const localToken = localStorage.getItem('token')
  if (localToken) {
    return localToken
  }
  // 2. 从cookie读取access_token（tianyan-web将token存储在cookie中）
  const cookieToken = getCookie('access_token')
  if (cookieToken) {
    return cookieToken
  }
  return null
}

let fetchUserPromise = null

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getInitialToken(),
    user: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    
    setUser(user) {
      this.user = user
    },
    
    async fetchCurrentUser({ force = false } = {}) {
      if (!force && this.user) {
        return this.user
      }

      if (fetchUserPromise) {
        return fetchUserPromise
      }

      fetchUserPromise = getCurrentUserInfo()
        .then((res) => {
          const payload = res?.data && typeof res.data === 'object'
            ? res.data
            : (res && typeof res === 'object' ? res : null)

          if (payload) {
            const normalized = {
              ...payload,
              username: payload.cn || payload.username || payload.name || payload.user_name || null
            }
            this.setUser(normalized)
            return normalized
          }

          this.setUser(null)
          return null
        })
        .catch((error) => {
          console.warn('authStore.fetchCurrentUser failed', error)
          this.setUser(null)
          return null
        })
        .finally(() => {
          fetchUserPromise = null
        })

      return fetchUserPromise
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})

