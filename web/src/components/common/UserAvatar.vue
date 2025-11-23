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

// Preset 5 colors (cool tones)
const colors = [
  '#1abc9c', // Turquoise
  '#3498db', // Blue
  '#9b59b6', // Purple
  '#16a085', // Dark cyan
  '#2980b9'  // Dark blue
]

/**
 * @brief 根据名称生成缩写
 * @description 只显示名字的第一个字符
 */
const abbreviation = computed(() => {
  if (!props.name) return ''
  return props.name.trim().charAt(0).toUpperCase()
})

/**
 * @brief 根据名称的哈希值选择一个颜色
 * @description 确保相同的名称总是得到相同的颜色
 */
const avatarColor = computed(() => {
  if (!props.name) return colors[0]
  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = props.name.charCodeAt(i) + ((hash << 5) - hash)
  }
  const index = Math.abs(hash % colors.length)
  return colors[index]
})
</script>
