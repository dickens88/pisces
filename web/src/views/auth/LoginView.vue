<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-[#0f1419] px-4">
    <div class="w-full max-w-md">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <h1 class="text-gray-900 dark:text-white text-3xl font-bold mb-2">Pisces</h1>
        <p class="text-gray-600 dark:text-white/60 text-sm">{{ $t('common.login.subtitle') }}</p>
      </div>

      <!-- Login Card -->
      <div class="bg-white dark:bg-[#19222c] border border-gray-200 dark:border-[#324867]/50 rounded-xl p-8 shadow-xl">
        <h2 class="text-gray-900 dark:text-white text-xl font-semibold mb-6 text-center">
          {{ $t('common.login.title') }}
        </h2>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username -->
          <div>
            <label for="username" class="block text-gray-700 dark:text-white/80 text-sm font-medium mb-2">
              {{ $t('common.login.username') }}
            </label>
            <div class="relative">
              <span class="material-symbols-outlined absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-white/50 text-lg">
                person
              </span>
              <input
                id="username"
                v-model="form.username"
                type="text"
                :placeholder="$t('common.login.usernamePlaceholder')"
                required
                autocomplete="username"
                class="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-[#0f1419] border border-gray-300 dark:border-[#324867]/50 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-gray-700 dark:text-white/80 text-sm font-medium mb-2">
              {{ $t('common.login.password') }}
            </label>
            <div class="relative">
              <span class="material-symbols-outlined absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-white/50 text-lg">
                lock
              </span>
              <input
                id="password"
                v-model="form.password"
                type="password"
                :placeholder="$t('common.login.passwordPlaceholder')"
                required
                autocomplete="current-password"
                class="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-[#0f1419] border border-gray-300 dark:border-[#324867]/50 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-lg p-3">
            <p class="text-red-600 dark:text-red-400 text-sm flex items-center gap-2">
              <span class="material-symbols-outlined text-base">error</span>
              {{ errorMessage }}
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full bg-primary hover:bg-blue-600 dark:hover:bg-[#5ba0f2] text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary"
          >
            <span
              v-if="isLoading"
              class="material-symbols-outlined text-base animate-spin"
            >
              refresh
            </span>
            <span v-else class="material-symbols-outlined text-base">login</span>
            {{ isLoading ? $t('common.login.loggingIn') : $t('common.login.login') }}
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-gray-500 dark:text-white/40 text-xs mt-6">
        {{ $t('common.login.footer') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const form = reactive({
  username: '',
  password: ''
})

const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await login({
      username: form.username,
      password: form.password
    })

    // 保存token
    if (response.access_token) {
      authStore.setToken(response.access_token)
      authStore.setUser({ username: response.username })
      
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      errorMessage.value = response.message || '登录失败，请检查用户名和密码'
    }
  } catch (error) {
    console.error('Login error:', error)
    errorMessage.value = error.response?.data?.message || error.message || '登录失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}
</script>

