<template>
  <router-view />
  <Toast />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import Toast from '@/components/common/Toast.vue'

const appStore = useAppStore()

onMounted(() => {
  // 应用保存的主题设置
  appStore.setTheme(appStore.theme)
})
</script>

