<template>
  <div class="flex items-center gap-2">
    <!-- 时间范围下拉选择器 -->
    <div class="relative">
      <button
        @click.stop="showTimeRangeDropdown = !showTimeRangeDropdown"
        class="time-range-button flex h-9 shrink-0 items-center justify-center gap-x-2 rounded-lg px-3 transition-colors bg-[#233348] hover:bg-[#324867] text-white border border-[#324867]"
      >
        <span class="material-symbols-outlined" style="font-size: 20px;">schedule</span>
        <p class="text-sm font-medium leading-normal">{{ getCurrentTimeRangeLabel() }}</p>
        <span class="material-symbols-outlined" style="font-size: 16px;">arrow_drop_down</span>
      </button>
      <!-- 下拉菜单 -->
      <div
        v-if="showTimeRangeDropdown"
        @click.stop
        class="time-range-dropdown absolute top-full left-0 mt-2 bg-[#233348] border border-[#324867] rounded-lg shadow-lg z-50 min-w-[140px]"
      >
        <button
          v-for="range in presetTimeRanges"
          :key="range.key"
          @click="handleTimeRangeChange(range.key)"
          :class="[
            'w-full flex items-center gap-x-2 px-4 py-2 text-sm font-medium transition-colors text-left',
            selectedTimeRange === range.key
              ? 'bg-primary/30 text-primary'
              : 'text-white hover:bg-[#324867]'
          ]"
        >
          <span class="material-symbols-outlined" style="font-size: 18px;">{{ range.icon }}</span>
          <span>{{ $t(`${i18nPrefix}.${range.key}`) }}</span>
        </button>
        <div class="border-t border-[#324867] my-1"></div>
        <button
          @click="handleTimeRangeChange('customRange')"
          :class="[
            'w-full flex items-center gap-x-2 px-4 py-2 text-sm font-medium transition-colors text-left',
            selectedTimeRange === 'customRange'
              ? 'bg-primary/30 text-primary'
              : 'text-white hover:bg-[#324867]'
          ]"
        >
          <span class="material-symbols-outlined" style="font-size: 18px;">date_range</span>
          <span>{{ $t(`${i18nPrefix}.customRange`) }}</span>
        </button>
      </div>
    </div>
    <!-- 自定义时间范围选择器 -->
    <div v-if="selectedTimeRange === 'customRange'" class="flex items-center gap-2">
      <VueDatePicker
        v-model="customTimeRange"
        :enable-time-picker="true"
        :dark="true"
        range
        format="yyyy-MM-dd HH:mm"
        :locale="datePickerLocale"
        :teleport="true"
        :auto-apply="true"
        class="custom-date-picker"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import { zhCN, enUS } from 'date-fns/locale'
import '@vuepic/vue-datepicker/dist/main.css'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'last24Hours'
  },
  customRange: {
    type: Array,
    default: null
  },
  i18nPrefix: {
    type: String,
    default: 'common.timeRange'
  },
  storageKey: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'customRangeChange'])

const { locale, t } = useI18n()

// 从 localStorage 读取保存的时间范围
const getStoredTimeRange = () => {
  if (!props.storageKey) return props.modelValue
  try {
    const stored = localStorage.getItem(`${props.storageKey}-timeRange`)
    if (stored && ['last24Hours', 'last3Days', 'last7Days', 'last30Days', 'last3Months', 'customRange'].includes(stored)) {
      return stored
    }
  } catch (error) {
    console.warn('Failed to read time range from localStorage:', error)
  }
  return props.modelValue
}

// 从 localStorage 读取保存的自定义时间范围
const getStoredCustomRange = () => {
  if (!props.storageKey) return props.customRange
  try {
    const stored = localStorage.getItem(`${props.storageKey}-customTimeRange`)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length === 2) {
        return [new Date(parsed[0]), new Date(parsed[1])]
      }
    }
  } catch (error) {
    console.warn('Failed to read custom time range from localStorage:', error)
  }
  return props.customRange
}

const selectedTimeRange = ref(getStoredTimeRange())
const showTimeRangeDropdown = ref(false)
const customTimeRange = ref(getStoredCustomRange())

// 日期选择器的语言配置
const datePickerLocale = computed(() => {
  return locale.value === 'zh-CN' ? zhCN : enUS
})

const presetTimeRanges = [
  { key: 'last24Hours', icon: 'schedule' },
  { key: 'last3Days', icon: 'calendar_today' },
  { key: 'last7Days', icon: 'calendar_month' },
  { key: 'last30Days', icon: 'event' },
  { key: 'last3Months', icon: 'calendar_view_month' }
]

const getCurrentTimeRangeLabel = () => {
  if (selectedTimeRange.value === 'customRange') {
    return t(`${props.i18nPrefix}.customRange`)
  }
  return t(`${props.i18nPrefix}.${selectedTimeRange.value}`)
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  showTimeRangeDropdown.value = false
  
  // 保存到 localStorage
  if (props.storageKey) {
    try {
      localStorage.setItem(`${props.storageKey}-timeRange`, rangeKey)
    } catch (error) {
      console.warn('Failed to save time range to localStorage:', error)
    }
  }
  
  emit('update:modelValue', rangeKey)
  emit('change', rangeKey)
  
  if (rangeKey === 'customRange') {
    // 如果已有保存的自定义时间范围，使用它；否则初始化自定义时间范围为最近7天
    if (!customTimeRange.value || customTimeRange.value.length !== 2) {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() - 7)
      customTimeRange.value = [start, end]
    }
    emit('customRangeChange', customTimeRange.value)
  } else {
    customTimeRange.value = null
    // 清除自定义时间范围的缓存
    if (props.storageKey) {
      try {
        localStorage.removeItem(`${props.storageKey}-customTimeRange`)
      } catch (error) {
        console.warn('Failed to remove custom time range from localStorage:', error)
      }
    }
    emit('customRangeChange', null)
  }
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.time-range-dropdown')
  const button = event.target.closest('.time-range-button')
  if (!dropdown && !button) {
    showTimeRangeDropdown.value = false
  }
}

// 监听自定义时间范围变化
watch(customTimeRange, (newRange) => {
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    // 保存到 localStorage
    if (props.storageKey) {
      try {
        const serialized = JSON.stringify([newRange[0].toISOString(), newRange[1].toISOString()])
        localStorage.setItem(`${props.storageKey}-customTimeRange`, serialized)
      } catch (error) {
        console.warn('Failed to save custom time range to localStorage:', error)
      }
    }
    emit('customRangeChange', newRange)
  }
})

// 监听 props 变化
watch(() => props.modelValue, (newValue) => {
  // 只有当新值与当前值不同时才更新（避免循环更新）
  if (newValue !== selectedTimeRange.value) {
    selectedTimeRange.value = newValue
  }
})

watch(() => props.customRange, (newValue) => {
  // 只有当新值与当前值不同时才更新（避免循环更新）
  if (JSON.stringify(newValue) !== JSON.stringify(customTimeRange.value)) {
    customTimeRange.value = newValue
  }
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 自定义日期选择器样式 */
:deep(.custom-date-picker .dp__input_wrap) {
  width: 100%;
}

:deep(.custom-date-picker .dp__input) {
  background-color: #1e293b;
  color: white;
  border: 1px solid #324867;
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  min-width: 280px;
}

:deep(.custom-date-picker .dp__input:hover) {
  border-color: #3c4a60;
}

:deep(.custom-date-picker .dp__input:focus) {
  border-color: #2b7cee;
  box-shadow: 0 0 0 3px rgba(43, 124, 238, 0.1);
  outline: none;
}
</style>

