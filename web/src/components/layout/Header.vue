<template>
  <header class="flex items-center justify-end px-6 py-4 border-b border-[#324867] bg-[#111822]">
    <div class="flex items-center gap-4">
      <!-- 语言切换 -->
      <div class="relative">
        <select
          v-model="currentLocale"
          @change="handleLocaleChange"
          class="appearance-none bg-[#233348] text-white px-4 py-2 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:outline-none cursor-pointer"
        >
          <option value="zh-CN">中文</option>
          <option value="en-US">English</option>
        </select>
      </div>
      
      <!-- 用户信息（后续SSO集成时使用） -->
      <div class="flex items-center gap-2">
        <div class="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
          <span class="text-white text-sm font-medium">U</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'

const props = defineProps({
  title: {
    type: String,
    default: ''
  }
})

const { locale } = useI18n()
const appStore = useAppStore()

const currentLocale = ref(locale.value)

const handleLocaleChange = () => {
  locale.value = currentLocale.value
  appStore.setLocale(currentLocale.value)
}

onMounted(() => {
  currentLocale.value = appStore.locale
  locale.value = appStore.locale
})
</script>

