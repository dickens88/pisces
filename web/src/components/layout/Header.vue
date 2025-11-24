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
          <!-- 已登录但用户名尚未加载时，不再显示 Guest，而是暂时留空 -->
          <UserAvatar :name="displayName" />
          <span class="text-white text-sm font-medium">{{ displayName }}</span>
          <span class="material-symbols-outlined text-sm text-white/60 transition-transform duration-200" :class="{ 'rotate-180': showUserMenu }">expand_more</span>
        </button>
        
        <!-- 用户菜单 -->
        <div
          v-if="showUserMenu"
          ref="userMenuRef"
          class="absolute right-0 mt-2 w-56 bg-[#0b1220] border border-[#1f2937] rounded-xl shadow-xl overflow-hidden z-50"
        >
          <!-- 关于：左侧图标+文字，右侧版本号+状态点 -->
          <button
            @click="openAbout"
            class="w-full px-4 py-2.5 text-sm text-white hover:bg-[#111827] transition-colors flex items-center"
          >
            <div class="flex items-center gap-2 flex-1">
              <span class="material-symbols-outlined text-base text-white/80">info</span>
              <span>About</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-white/70">{{ systemVersion || '-' }}</span>
              <span class="inline-flex h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.9)]"></span>
            </div>
          </button>

          <div class="border-t border-[#1f2937]" />

          <button
            v-if="!isAuthenticated"
            @click="handleLogin"
            class="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-[#111827] transition-colors flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-base">login</span>
            <span>{{ $t('common.login.login') }}</span>
          </button>
          <button
            v-if="isAuthenticated"
            @click="handleLogout"
            class="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-[#111827] transition-colors flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-base">logout</span>
            <span>{{ $t('common.login.logout') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- About 弹窗（参考 Dify 样式） -->
    <div
      v-if="showAboutDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md pt-8 pb-4 px-8 relative text-center">
        <button
          class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
          @click="showAboutDialog = false"
        >
          <span class="material-symbols-outlined text-lg">close</span>
        </button>

        <!-- Logo / 产品名 -->
        <div class="mb-2">
          <div class="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 overflow-hidden">
            <!-- 使用站点自定义 Logo -->
            <img
              src="/pisces_logo.png"
              alt="Pisces Logo"
              class="h-10 w-10 object-contain"
            >
          </div>
          <h3 class="text-xl font-semibold text-slate-900 tracking-tight">
            Pisces
          </h3>
          <p class="text-sm text-slate-500 mt-1">
            Version {{ systemVersion || '-' }}
          </p>
        </div>

        <!-- 版权与链接信息 -->
        <div class="mt-4 space-y-1 text-xs text-slate-500">
          <div>© {{ new Date().getFullYear() }} Pisces Platform.</div>
          <div class="space-x-2">
            <a href="javascript:void(0)" class="text-sky-500 hover:underline">Privacy Policy</a>
            <span class="text-slate-400">•</span>
            <a href="javascript:void(0)" class="text-sky-500 hover:underline">Terms of Service</a>
          </div>
        </div>

        <!-- 底部提示和按钮 -->
        <div class="mt-6 flex items-center justify-between border-t border-slate-200 pt-3 text-xs text-slate-500">
          <span>
            Pisces {{ systemVersion || '-' }} is the latest version available.
          </span>
          <button
            class="ml-4 inline-flex items-center rounded-full border border-slate-300 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
            type="button"
          >
            Changelog
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
import { getSystemInfo } from '@/api/system'
import { getCurrentUserInfo } from '@/api/auth'
import { getAppConfig } from '@config'
import { redirectToTianyanLogin } from '@/utils/auth'
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
const showAboutDialog = ref(false)
const languageMenuRef = ref(null)
const languageButtonRef = ref(null)
const userMenuRef = ref(null)
const userMenuButtonRef = ref(null)
const systemVersion = ref('')

const userName = computed(() => {
  return authStore.user?.username || ''
})

const isAuthenticated = computed(() => {
  return authStore.isAuthenticated
})

// 展示用姓名：
// - 未登录：显示 Guest
// - 已登录但用户名尚未从接口返回：显示空字符串（避免先变 Guest 再变 admin 的闪烁）
const displayName = computed(() => {
  if (!isAuthenticated.value) {
    return 'Guest'
  }
  return userName.value || ''
})

const openAbout = () => {
  showAboutDialog.value = true
  showUserMenu.value = false
}

const selectLanguage = (lang) => {
  currentLocale.value = lang
  locale.value = lang
  appStore.setLocale(lang)
  showLanguageMenu.value = false
}

const handleLogin = () => {
  showUserMenu.value = false
  if (!redirectToTianyanLogin()) {
    // 如果不是 tianyan 模式，使用本地认证，跳转到本地登录页
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

  // 获取当前登录用户信息（用户名等），用于在 Header 显示
  // 仅在已认证且启用认证的情况下调用
  if (config.enableAuth && authStore.token) {
    // 使用新的 /login/rest/token 接口获取用户名
    getCurrentUserInfo()
      .then((res) => {
        if (res && res.data) {
          // 后端返回的字段是 cn，映射为 username
          if (res.data.cn) {
            authStore.setUser({ username: res.data.cn })
          }
        }
      })
      .catch((err) => {
        console.error('Failed to load user info:', err)
      })

    // 仍然使用 /system/info 获取版本号
    getSystemInfo()
      .then((res) => {
        if (res && res.data && res.data.version) {
          systemVersion.value = res.data.version
        }
      })
      .catch((err) => {
        console.error('Failed to load system info:', err)
      })
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

