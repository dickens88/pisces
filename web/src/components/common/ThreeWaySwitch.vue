<template>
  <div class="flex items-center bg-gray-100 dark:bg-[#233348] p-0.5 rounded-lg h-10">
    <span v-if="label" class="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap px-2">
      {{ label }}
    </span>
    <button
      v-for="(option, index) in options"
      :key="option.value"
      @click="handleChange(option.value)"
      :class="[
        'group relative px-2.5 py-1 rounded-md transition-all duration-300 h-full flex items-center justify-center',
        modelValue === option.value
          ? 'text-primary bg-white dark:bg-[#111822] shadow-sm'
          : 'text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
      ]"
      :title="getOptionLabel(option)"
    >
      <span class="material-symbols-outlined !text-lg">{{ option.icon }}</span>
      <div class="absolute top-[-28px] left-1/2 -translate-x-1/2 w-max pointer-events-none z-10">
        <span class="text-xs font-medium text-gray-600 dark:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap bg-white dark:bg-[#111822] px-2 py-1 rounded shadow-sm border border-gray-200 dark:border-[#324867]">
          {{ getOptionLabel(option) }}
        </span>
      </div>
    </button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  options: {
    type: Array,
    required: true,
    validator: (options) => {
      return options.every(opt => 
        opt && typeof opt.value === 'string' && typeof opt.icon === 'string'
      )
    }
  },
  i18nPrefix: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const { t } = useI18n()

const handleChange = (value) => {
  if (value !== props.modelValue) {
    emit('update:modelValue', value)
    emit('change', value)
  }
}

// 计算选项的标签（支持国际化）
const getOptionLabel = (option) => {
  if (option.label) {
    return option.label
  }
  if (props.i18nPrefix && option.i18nKey) {
    return t(`${props.i18nPrefix}.${option.i18nKey}`)
  }
  return option.value
}
</script>

