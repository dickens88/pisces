<template>
  <div
    v-if="name"
    class="flex items-center justify-center w-8 h-8 rounded-full text-white text-sm font-bold select-none"
    :style="{ backgroundColor: avatarColor }"
    :title="name"
  >
    {{ abbreviation }}
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  }
})

/**
 * @brief 根据名称生成缩写
 * @description 只显示名字的第一个字符
 */
const abbreviation = computed(() => {
  if (!props.name) return ''
  return props.name.trim().charAt(0).toUpperCase()
})

/**
 * @brief 根据账号类型返回颜色
 * @description 机器人账号使用蓝色，其他账号使用橙色
 */
const avatarColor = computed(() => {
  if (!props.name) return '#ee9b00' // Orange-500

  // Robot accounts use blue, others use orange
  const lowerName = props.name.toLowerCase()
  if (lowerName.includes('robot') || lowerName.includes('secmaster') || lowerName.includes('autoclosed')) {
    return '#3b82f6' // Blue-500 for robot accounts
  }

  return '#f97316' // Orange-500 for other accounts
})
</script>
