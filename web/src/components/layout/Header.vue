<template>
  <header class="flex items-center justify-end px-6 py-4 border-b border-[#324867] bg-[#111822]">
    <div class="flex items-center gap-4">
      <!-- 语言切换 -->
      <div class="relative group" ref="languageButtonRef">
        <button
          @click.stop="showLanguageMenu = !showLanguageMenu"
          class="flex items-center gap-2 bg-[#233348] hover:bg-[#2a3d52] text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 border border-transparent hover:border-[#324867]"
        >
          <span class="material-symbols-outlined text-base">language</span>
          <span class="min-w-[60px] text-left">{{ currentLocale === 'zh-CN' ? '中文' : 'English' }}</span>
          <span class="material-symbols-outlined text-sm transition-transform duration-200" :class="{ 'rotate-180': showLanguageMenu }">expand_more</span>
        </button>
        
        <!-- 下拉菜单 -->
        <div
          v-if="showLanguageMenu"
          ref="languageMenuRef"
          class="absolute right-0 mt-2 w-36 bg-[#1a2332] border border-[#324867] rounded-lg shadow-xl overflow-hidden z-50"
        >
          <button
            @click="selectLanguage('zh-CN')"
            class="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-[#233348] transition-colors flex items-center gap-2"
            :class="{ 'bg-[#233348]': currentLocale === 'zh-CN' }"
          >
            <span class="material-symbols-outlined text-base" v-if="currentLocale === 'zh-CN'">check</span>
            <span :class="{ 'ml-6': currentLocale !== 'zh-CN' }">中文</span>
          </button>
          <button
            @click="selectLanguage('en-US')"
            class="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-[#233348] transition-colors flex items-center gap-2 border-t border-[#324867]"
            :class="{ 'bg-[#233348]': currentLocale === 'en-US' }"
          >
            <span class="material-symbols-outlined text-base" v-if="currentLocale === 'en-US'">check</span>
            <span :class="{ 'ml-6': currentLocale !== 'en-US' }">English</span>
          </button>
        </div>
      </div>
      
      <!-- 用户信息 -->
      <div class="relative group" ref="userMenuButtonRef">
        <button
          @click.stop="showUserMenu = !showUserMenu"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#1a2332] transition-colors"
        >
          <UserAvatar :name="userName || 'Guest'" />
          <span class="text-white text-sm font-medium">{{ userName || 'Guest' }}</span>
          <span class="material-symbols-outlined text-sm text-white/60 transition-transform duration-200" :class="{ 'rotate-180': showUserMenu }">expand_more</span>
        </button>
        
        <!-- 用户菜单 -->
        <div
          v-if="showUserMenu"
          ref="userMenuRef"
          class="absolute right-0 mt-2 w-40 bg-[#1a2332] border border-[#324867] rounded-lg shadow-xl overflow-hidden z-50"
        >
          <button
            v-if="!isAuthenticated"
            @click="handleLogin"
            class="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-[#233348] transition-colors flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-base">login</span>
            <span>{{ $t('common.login.login') }}</span>
          </button>
          <button
            v-if="isAuthenticated"
            @click="handleLogout"
            class="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-[#233348] transition-colors flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-base">logout</span>
            <span>{{ $t('common.login.logout') }}</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { getAppConfig } from '@config'
import UserAvatar from '@/components/common/UserAvatar.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  }
})

const { locale } = useI18n()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()
const config = getAppConfig(import.meta.env, import.meta.env.PROD)

const currentLocale = ref(locale.value)
const showLanguageMenu = ref(false)
const showUserMenu = ref(false)
const languageMenuRef = ref(null)
const languageButtonRef = ref(null)
const userMenuRef = ref(null)
const userMenuButtonRef = ref(null)

const userName = computed(() => {
  return authStore.user?.username || ''
})

const isAuthenticated = computed(() => {
  return authStore.isAuthenticated
})

const selectLanguage = (lang) => {
  currentLocale.value = lang
  locale.value = lang
  appStore.setLocale(lang)
  showLanguageMenu.value = false
}

const handleLogin = () => {
  showUserMenu.value = false
  if (config.authMode === 'tianyan') {
    // 使用tianyan-web认证，重定向到tianyan-web登录页面
    const currentUrl = window.location.href
    const loginUrl = `${config.tianyanWebBaseURL}/login?redirect=${encodeURIComponent(currentUrl)}`
    window.location.href = loginUrl
  } else {
    // 使用本地认证，跳转到本地登录页
    router.push({ name: 'Login' })
  }
}

const handleLogout = async () => {
  showUserMenu.value = false
  authStore.logout()
  if (config.authMode === 'tianyan') {
    // 使用tianyan-web认证，重定向到tianyan-web登录页面
    const loginUrl = `${config.tianyanWebBaseURL}/login`
    window.location.href = loginUrl
  } else {
    // 使用本地认证，跳转到本地登录页
    router.push({ name: 'Login' })
  }
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  // 关闭语言菜单
  if (showLanguageMenu.value && 
      languageButtonRef.value && 
      !languageButtonRef.value.contains(event.target) &&
      languageMenuRef.value && 
      !languageMenuRef.value.contains(event.target)) {
    showLanguageMenu.value = false
  }
  
  // 关闭用户菜单
  if (showUserMenu.value && 
      userMenuButtonRef.value && 
      !userMenuButtonRef.value.contains(event.target) &&
      userMenuRef.value && 
      !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  currentLocale.value = appStore.locale
  locale.value = appStore.locale
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

