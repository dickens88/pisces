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

// Preset 5 colors (warm tones for general users)
const colors = [
  '#e67e22', // Carrot (orange)
  '#e74c3c', // Alizarin (red)
  '#f39c12', // Orange
  '#d35400', // Pumpkin (deep orange)
  '#c0392b'  // Pomegranate (deep red)
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

  // Special rule: accounts containing "robot" or "SecMaster" (case-insensitive) use blue background
  const lowerName = props.name.toLowerCase()
  if (lowerName.includes('robot') || lowerName.includes('secmaster') || lowerName.includes('autoclosed')) {
    return '#3498db' // consistent blue
  }

  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = props.name.charCodeAt(i) + ((hash << 5) - hash)
  }
  const index = Math.abs(hash % colors.length)
  return colors[index]
})
</script>
