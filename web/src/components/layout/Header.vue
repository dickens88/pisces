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
      <div class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#1a2332] transition-colors">
        <UserAvatar :name="userName" />
        <span class="text-white text-sm font-medium">{{ userName || 'Guest' }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import UserAvatar from '@/components/common/UserAvatar.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  }
})

const { locale } = useI18n()
const appStore = useAppStore()
const authStore = useAuthStore()

const currentLocale = ref(locale.value)
const showLanguageMenu = ref(false)
const languageMenuRef = ref(null)
const languageButtonRef = ref(null)

const userName = computed(() => {
  return authStore.user?.username || ''
})

const selectLanguage = (lang) => {
  currentLocale.value = lang
  locale.value = lang
  appStore.setLocale(lang)
  showLanguageMenu.value = false
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  if (showLanguageMenu.value && 
      languageButtonRef.value && 
      !languageButtonRef.value.contains(event.target) &&
      languageMenuRef.value && 
      !languageMenuRef.value.contains(event.target)) {
    showLanguageMenu.value = false
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

