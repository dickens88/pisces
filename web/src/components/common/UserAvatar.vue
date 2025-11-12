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

// 预设的5种颜色
const colors = [
  '#1abc9c', // 绿松石
  '#3498db', // 蓝色
  '#9b59b6', // 紫色
  '#e67e22', // 橙色
  '#e74c3c'  // 红色
]

/**
 * @brief 根据名称生成缩写
 * @description 最多显示3个字母的缩写
 */
const abbreviation = computed(() => {
  if (!props.name) return ''
  const words = props.name.trim().split(/\s+/)
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  return words
    .slice(0, 3)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
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
