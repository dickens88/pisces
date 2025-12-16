<template>
  <div class="relative inline-block w-full">
    <select
      :value="modelValue"
      @change="onChange"
      :class="[
        'appearance-none block w-full rounded-lg border border-gray-300 dark:border-[#324867] bg-gray-100 dark:bg-[#233348] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 sm:text-sm text-sm pl-4',
        showClear ? 'pr-16' : 'pr-9'
      ]"
    >
      <!-- 透传选项，由父组件自行定义 <option> 列表 -->
      <slot />
    </select>

    <!-- 清除按钮：只有在当前值不等于 clearValue 时显示 -->
    <button
      v-if="showClear"
      type="button"
      class="absolute inset-y-0 right-7 flex items-center px-1 text-gray-400 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-200"
      @click.stop="onClear"
      :aria-label="clearAriaLabel"
    >
      <span class="material-symbols-outlined" style="font-size: 18px;">close</span>
    </button>

    <!-- 下拉箭头图标 -->
    <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
      <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: ''
  },
  /**
   * 清除后恢复到的值（默认 'all'，兼容告警页面的筛选逻辑）
   */
  clearValue: {
    type: [String, Number, Boolean],
    default: 'all'
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'clear'])

const { t } = useI18n()

const showClear = computed(() => props.modelValue !== props.clearValue)

const clearAriaLabel = computed(() => {
  return t?.('common.clear') || 'Clear selection'
})

const onChange = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('change', value)
}

const onClear = () => {
  emit('update:modelValue', props.clearValue)
  emit('change', props.clearValue)
  emit('clear', props.clearValue)
}
</script>


