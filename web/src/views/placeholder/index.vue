<template>
  <div class="w-full">
    <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em] mb-6">
      {{ $t(`nav.${routeName}`) }}
    </h1>
    <div class="text-gray-400">
      This page is under development...
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const { t } = useI18n()

const routeName = computed(() => route.name?.toLowerCase() || '')
</script>

