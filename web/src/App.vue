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
  // 设置暗色主题
  document.documentElement.classList.add('dark')
})
</script>

