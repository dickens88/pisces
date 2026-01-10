<template>
  <header class="flex items-center justify-end px-6 py-4 border-b border-border-light dark:border-[#324867] bg-panel-light dark:bg-[#111822]">
    <div class="flex items-center gap-4">
      <!-- AI 对话按钮 -->
      <button
        @click="handleOpenAISidebar"
        class="w-9 h-9 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center transition-all duration-200 hover:scale-110 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
        :title="$t('common.aiChat') || 'AI对话'"
      >
        <span class="material-symbols-outlined text-white text-lg">auto_awesome</span>
      </button>
      <!-- 用户信息 -->
      <div class="relative group" ref="userMenuButtonRef">
        <button
          @click.stop="showUserMenu = !showUserMenu"
          class="flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-100 dark:bg-[#233348] border border-gray-200 dark:border-transparent hover:bg-gray-200 dark:hover:bg-[#1a2332] transition-colors"
        >
          <!-- 已登录但用户名尚未加载时，不再显示 Guest，而是暂时留空 -->
          <UserAvatar :name="displayName" />
          <span class="text-gray-700 dark:text-white text-sm font-medium">{{ displayName }}</span>
          <span class="material-symbols-outlined text-sm text-gray-500 dark:text-white/60 transition-transform duration-200" :class="{ 'rotate-180': showUserMenu }">expand_more</span>
        </button>
        
        <!-- 用户菜单 -->
        <div
          v-if="showUserMenu"
          ref="userMenuRef"
          class="absolute right-0 mt-2 w-64 bg-white dark:bg-[#0b1220] border border-gray-200 dark:border-[#1f2937] rounded-xl shadow-xl overflow-hidden z-50"
        >
          <div class="px-4 py-3 space-y-3">
            <div>
              <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">{{ $t('common.userMenu.preferences') }}</div>
              <div class="w-full flex items-center justify-between px-2.5 py-2 rounded-lg bg-gray-50 dark:bg-[#111827] border border-gray-200 dark:border-[#1f2937]">
                <span class="text-xs font-medium text-gray-700 dark:text-white">{{ $t('common.userMenu.theme') }}</span>
                <div class="flex items-center gap-1 rounded-full bg-white dark:bg-[#0f1729] px-1 py-0.5 border border-gray-200 dark:border-[#1f2937]">
                  <button
                    type="button"
                    class="h-7 w-7 flex items-center justify-center rounded-full transition-all duration-200"
                    :class="appStore.theme === 'light'
                      ? 'bg-sky-500 text-white shadow-sm shadow-sky-500/40'
                      : 'text-gray-500 dark:text-gray-300'"
                    @click.stop="appStore.setTheme('light')"
                    aria-label="Switch to light theme"
                  >
                    <span class="material-symbols-outlined text-sm leading-none">light_mode</span>
                  </button>
                  <button
                    type="button"
                    class="h-7 w-7 flex items-center justify-center rounded-full transition-all duration-200"
                    :class="appStore.theme === 'dark'
                      ? 'bg-slate-800 dark:bg-sky-500 text-white shadow-sm shadow-sky-500/40'
                      : 'text-gray-500 dark:text-gray-300'"
                    @click.stop="appStore.setTheme('dark')"
                    aria-label="Switch to dark theme"
                  >
                    <span class="material-symbols-outlined text-sm leading-none">dark_mode</span>
                  </button>
                </div>
              </div>
            </div>

            <div>
              <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">{{ $t('common.userMenu.language') }}</div>
              <div class="grid grid-cols-2 gap-2">
                <button
                  @click="selectLanguage('zh-CN')"
                  class="px-3 py-2 rounded-lg border text-sm transition-colors"
                  :class="currentLocale === 'zh-CN'
                    ? 'border-sky-500 text-sky-600 bg-sky-50 dark:bg-sky-900/30 dark:text-sky-300'
                    : 'border-gray-200 dark:border-[#1f2937] text-gray-700 dark:text-white bg-white dark:bg-[#111827] hover:bg-gray-50 dark:hover:bg-[#162036]'"
                >
                  中文
                </button>
                <button
                  @click="selectLanguage('en-US')"
                  class="px-3 py-2 rounded-lg border text-sm transition-colors"
                  :class="currentLocale === 'en-US'
                    ? 'border-sky-500 text-sky-600 bg-sky-50 dark:bg-sky-900/30 dark:text-sky-300'
                    : 'border-gray-200 dark:border-[#1f2937] text-gray-700 dark:text-white bg-white dark:bg-[#111827] hover:bg-gray-50 dark:hover:bg-[#162036]'"
                >
                  English
                </button>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-200 dark:border-[#1f2937]" />

          <button
            @click="openIssue"
            class="w-full px-4 py-2.5 text-sm text-gray-700 dark:text-white hover:bg-gray-50 dark:hover:bg-[#111827] transition-colors flex items-center gap-3"
          >
            <svg class="w-5 h-5 text-gray-700 dark:text-white" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"></path>
            </svg>
            <span class="flex-1 text-left">{{ $t('common.github') }}</span>
            <span class="material-symbols-outlined text-xs text-gray-400 dark:text-white/60">open_in_new</span>
          </button>

          <div class="border-t border-gray-200 dark:border-[#1f2937]" />

          <!-- 关于：左侧图标+文字，右侧版本号+状态点 -->
          <button
            @click="openAbout"
            class="w-full px-4 py-2.5 text-sm text-gray-700 dark:text-white hover:bg-gray-50 dark:hover:bg-[#111827] transition-colors flex items-center"
          >
            <div class="flex items-center gap-2 flex-1">
              <span class="material-symbols-outlined text-base text-gray-600 dark:text-white/80">info</span>
              <span>{{ $t('common.userMenu.about') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 dark:text-white/70">{{ systemVersion || '-' }}</span>
              <span class="inline-flex h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.9)]"></span>
            </div>
          </button>

          <div class="border-t border-gray-200 dark:border-[#1f2937]" />

          <button
            @click="handleLogout"
            class="w-full px-4 py-2.5 text-left text-sm text-gray-700 dark:text-white hover:bg-gray-50 dark:hover:bg-[#111827] transition-colors flex items-center gap-2"
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
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md pt-8 pb-4 px-8 relative text-center">
        <button
          class="absolute top-4 right-4 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
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
          <h3 class="text-xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight">
            Pisces
          </h3>
          <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Version {{ systemVersion || '-' }}
          </p>
        </div>

        <!-- 版权与链接信息 -->
        <div class="mt-4 space-y-1 text-xs text-slate-500 dark:text-slate-400">
          <div>© {{ new Date().getFullYear() }} Pisces Platform.</div>
          <div class="space-x-2">
            <a href="javascript:void(0)" class="text-sky-500 dark:text-sky-400 hover:underline">Privacy Policy</a>
            <span class="text-slate-400 dark:text-slate-500">•</span>
            <a href="javascript:void(0)" class="text-sky-500 dark:text-sky-400 hover:underline">Terms of Service</a>
          </div>
        </div>

        <!-- 底部提示和按钮 -->
        <div class="mt-6 flex items-center justify-between border-t border-slate-200 dark:border-slate-700 pt-3 text-xs text-slate-500 dark:text-slate-400">
          <span>
            Pisces {{ systemVersion || '-' }} is the latest version available.
          </span>
          <button
            @click="openChangelog"
            class="ml-4 inline-flex items-center rounded-full border border-slate-300 dark:border-slate-600 px-3 py-1 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
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
const showUserMenu = ref(false)
const showAboutDialog = ref(false)
const userMenuRef = ref(null)
const userMenuButtonRef = ref(null)
const systemVersion = ref('')
const isAuthenticated = computed(() => {
  return authStore.isAuthenticated
})

// 如果能获取到用户名就显示，否则显示 Guest
const displayName = computed(() => {
  return authStore.user?.cn || authStore.user?.username || authStore.user?.name || 'Guest'
})

const openAbout = () => {
  showAboutDialog.value = true
  showUserMenu.value = false
}

const openIssue = () => {
  showUserMenu.value = false
  window.open('https://codehub-g.huawei.com/csirt_hunting/Tianyan-WEB/issues', '_blank', 'noopener,noreferrer')
}

const openChangelog = () => {
  const changelogUrl = import.meta.env.VITE_CHANGELOG_URL
  if (changelogUrl) {
    window.open(changelogUrl, '_blank', 'noopener,noreferrer')
  }
}

const selectLanguage = (lang) => {
  currentLocale.value = lang
  locale.value = lang
  appStore.setLocale(lang)
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

const handleOpenAISidebar = () => {
  // 触发全局事件，让页面组件打开AI侧边栏
  window.dispatchEvent(new CustomEvent('open-ai-sidebar'))
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
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

  if (config.enableAuth) {
    authStore.fetchCurrentUser().catch(() => {})
  }

  getSystemInfo()
    .then((res) => {
      if (res?.data?.version) {
        systemVersion.value = res.data.version
      }
    })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

