<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-end"
    >
      <!-- 遮罩层 -->
      <div 
        class="fixed inset-0 bg-black/50"
      ></div>
      
      <!-- 编辑事件面板 - 有滑入动画 -->
      <Transition name="slide">
        <div
          v-if="showPanel"
          class="relative w-[70vw] h-full bg-white dark:bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- 头部 -->
          <div class="sticky top-0 z-20 bg-white/80 dark:bg-panel-dark/80 backdrop-blur-sm border-b border-gray-200 dark:border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ $t('incidents.edit.title') }}</h2>
              <button
                @click="handleClose"
                class="p-2 text-gray-500 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>

          <!-- 内容区 -->
          <div class="flex-1 p-6 overflow-y-auto custom-scrollbar">
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <!-- 事件标题 - 独占一行 -->
              <div>
                <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  {{ $t('incidents.create.incidentTitle') }} <span class="text-red-400">*</span>
                </label>
                <input
                  v-model="formData.title"
                  type="text"
                  required
                  class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                  :placeholder="$t('incidents.create.incidentTitlePlaceholder')"
                />
              </div>

              <!-- 第一行：事件分类、当前状态和发生时间 -->
              <div class="grid grid-cols-3 gap-4">
                <!-- 事件分类 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.create.category') }} <span class="text-red-400">*</span>
                  </label>
                  <select
                    v-model="formData.category"
                    required
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">{{ $t('incidents.create.selectCategory') }}</option>
                    <option value="platform">{{ $t('incidents.create.categoryPlatform') }}</option>
                    <option value="tenant">{{ $t('incidents.create.categoryTenant') }}</option>
                  </select>
                </div>

                <!-- 当前状态 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.create.currentStatus') }} <span class="text-red-400">*</span>
                  </label>
                  <select
                    v-model="formData.status"
                    required
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="Open">{{ $t('incidents.list.open') }}</option>
                    <option value="Block">{{ $t('incidents.list.block') }}</option>
                    <option value="Closed">{{ $t('incidents.list.closed') }}</option>
                  </select>
                </div>

                <!-- 事件创建时间 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.create.occurrenceTime') }} <span class="text-red-400">*</span>
                  </label>
                  <VueDatePicker
                    v-model="formData.createTime"
                    :enable-time-picker="true"
                    :dark="isDarkMode"
                    format="yyyy-MM-dd HH:mm"
                    :locale="datePickerLocale"
                    :teleport="true"
                    :auto-apply="true"
                    :required="true"
                    class="w-full"
                    :input-class-name="isDarkMode ? 'datepicker-input-dark' : 'datepicker-input-light'"
                  />
                </div>
              </div>

              <!-- 第三行：责任人和责任部门 -->
              <div class="grid grid-cols-2 gap-4">
                <!-- 责任人 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.create.responsiblePerson') }} <span class="text-red-400">*</span>
                  </label>
                  <input
                    v-model="formData.responsiblePerson"
                    type="text"
                    required
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    :placeholder="$t('incidents.create.responsiblePersonPlaceholder')"
                  />
                </div>

                <!-- 责任部门 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.create.responsibleDepartment') }}
                  </label>
                  <input
                    v-model="formData.responsibleDepartment"
                    type="text"
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    :placeholder="$t('incidents.create.responsibleDepartmentPlaceholder')"
                  />
                </div>
              </div>

              <!-- 第四行：Actor、事件根因和严重程度 -->
              <div class="grid grid-cols-3 gap-4">
                <!-- Actor -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.detail.actor') }}
                  </label>
                  <input
                    v-model="formData.actor"
                    type="text"
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    :placeholder="$t('incidents.detail.actor') || '请输入调查员'"
                  />
                </div>

                <!-- 事件根因 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.create.rootCause') }}
                  </label>
                  <select
                    v-model="formData.rootCause"
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">{{ $t('incidents.create.selectRootCause') }}</option>
                    <option value="exposedPort">{{ $t('incidents.create.rootCauseExposedPort') }}</option>
                    <option value="weakPassword">{{ $t('incidents.create.rootCauseWeakPassword') }}</option>
                    <option value="weakConfig">{{ $t('incidents.create.rootCauseWeakConfig') }}</option>
                    <option value="unauthorizedApi">{{ $t('incidents.create.rootCauseUnauthorizedApi') }}</option>
                    <option value="penetrationTest">{{ $t('incidents.create.rootCausePenetrationTest') }}</option>
                    <option value="vulnerabilityExploit">{{ $t('incidents.create.rootCauseVulnerabilityExploit') }}</option>
                  </select>
                </div>

                <!-- 严重程度 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('incidents.detail.severity') }}
                  </label>
                  <select
                    v-model="formData.severity"
                    class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">{{ $t('incidents.create.selectSeverity') || '请选择严重程度' }}</option>
                    <option
                      v-for="option in severityOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- 事件描述 - 独占一行 -->
              <div>
                <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  {{ $t('incidents.create.description') }} <span class="text-red-400">*</span>
                </label>
                <textarea
                  v-model="formData.description"
                  required
                  rows="6"
                  class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none resize-none transition-colors"
                  :placeholder="$t('incidents.create.descriptionPlaceholder')"
                ></textarea>
              </div>

              <!-- 按钮组 -->
              <div class="flex items-center justify-end gap-4 pt-4 border-t border-gray-200 dark:border-border-dark">
                <button
                  type="button"
                  @click="handleClose"
                  class="px-6 py-2 text-sm font-medium text-gray-700 dark:text-white bg-gray-200 dark:bg-[#2a3546] rounded-md hover:bg-gray-300 dark:hover:bg-[#3c4a60] transition-colors"
                >
                  {{ $t('common.cancel') }}
                </button>
                <button
                  type="submit"
                  :disabled="isSubmitting"
                  class="px-6 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <span v-if="isSubmitting" class="material-symbols-outlined animate-spin text-base">sync</span>
                  {{ $t('common.submit') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import { zhCN, enUS } from 'date-fns/locale'
import '@vuepic/vue-datepicker/dist/main.css'
import { formatDateTimeWithOffset, parseToDate } from '@/utils/dateTime'
import { severityToNumber, numberToSeverity } from '@/utils/severity'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  incidentId: {
    type: [Number, String],
    required: true
  },
  initialData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

const { t, locale } = useI18n()
const toast = useToast()
const authStore = useAuthStore()

const isDarkMode = computed(() => document.documentElement.classList.contains('dark'))

const showPanel = ref(false)
const isSubmitting = ref(false)

// 日期选择器的语言配置
const datePickerLocale = computed(() => {
  return locale.value === 'zh-CN' ? zhCN : enUS
})

const severityOptions = computed(() => ([
  { value: '1', label: `1 - ${t('common.severity.fatal')}` },
  { value: '2', label: `2 - ${t('common.severity.high')}` },
  { value: '3', label: `3 - ${t('common.severity.medium')}` },
  { value: '4', label: `4 - ${t('common.severity.low')}` },
  { value: '5', label: `5 - ${t('common.severity.tips')}` }
]))

// 初始化表单数据
const getInitialFormData = () => {
  const now = new Date()

  return {
    title: '',
    category: '',
    createTime: now,
    responsiblePerson: '',
    responsibleDepartment: '',
    actor: '',
    rootCause: '',
    severity: '',
    status: 'Open',
    description: ''
  }
}

const formData = ref(getInitialFormData())

/**
 * @brief 将时间戳转换为后端期望的格式
 * @param {Date|string|undefined} timestamp - 时间戳（Date对象、ISO字符串或undefined）
 * @returns {string} 格式化后的时间字符串，使用统一的 formatDateTimeWithOffset 函数
 */
const formatTimestamp = (timestamp) => {
  return formatDateTimeWithOffset(timestamp) || formatDateTimeWithOffset(new Date())
}

// 填充表单数据的函数
const fillFormData = () => {
  formData.value = getInitialFormData()
  
  if (props.initialData) {
    formData.value.title = props.initialData.title || ''
    formData.value.category = props.initialData.category || 'platform'
    formData.value.status = props.initialData.status || 'Open'
    
    formData.value.createTime =
      parseToDate(props.initialData.createTime)
      || parseToDate(props.initialData.create_time)
      || parseToDate(props.initialData.occurrenceTime)
      || new Date()
    
    formData.value.responsiblePerson = props.initialData.responsiblePerson || ''
    formData.value.responsibleDepartment = props.initialData.responsibleDepartment || ''
    formData.value.actor = props.initialData.actor || ''
    const initialRootCause = props.initialData.rootCause
    formData.value.rootCause = initialRootCause || ''
    const rawSeverity = props.initialData.severity
    const severityNumber = typeof rawSeverity === 'number'
      ? rawSeverity
      : severityToNumber(rawSeverity)
    formData.value.severity = severityNumber ? String(severityNumber) : ''
    // 处理 description 字段：如果是对象，转换为 JSON 字符串；如果是字符串，直接使用
    if (props.initialData.description) {
      if (typeof props.initialData.description === 'object' && props.initialData.description !== null) {
        formData.value.description = JSON.stringify(props.initialData.description, null, 2)
      } else {
        formData.value.description = String(props.initialData.description)
      }
    } else {
      formData.value.description = ''
    }
  } else {
    console.warn('No initial data provided to EditIncidentDialog')
  }
}

// 监听 visible 变化，控制动画和表单填充
watch(() => props.visible, (newVal) => {
  if (newVal) {
    // 填充表单数据
    fillFormData()
    
    // 延迟显示面板以触发动画
    setTimeout(() => {
      showPanel.value = true
    }, 10)
  } else {
    showPanel.value = false
  }
})

// 同时监听 initialData 变化，确保数据更新时表单也会更新
watch(() => props.initialData, (newData) => {
  if (props.visible && newData) {
    fillFormData()
  }
}, { deep: true })

const handleClose = () => {
  showPanel.value = false
  setTimeout(() => {
    emit('close')
  }, 300)
}

const handleSubmit = async () => {
  if (isSubmitting.value) return

  try {
    isSubmitting.value = true
    
    // 构建符合 /api/incidents 接口格式的请求体
    const body = {
      action: 'update',
      title: formData.value.title,
      description: formData.value.description,
      create_time: formatTimestamp(formData.value.createTime),
      severity: numberToSeverity(Number(formData.value.severity)) || '',
      actor: formData.value.actor || '',
      resource_list: [{
        owner: formData.value.responsiblePerson,
        responsible_person: formData.value.responsiblePerson,
        responsible_dept: formData.value.responsibleDepartment || '',
        root_cause: formData.value.rootCause || '',
        category: formData.value.category || ''
      }]
    }

    // 直接调用 PUT /api/incidents/<incident_id> 接口
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/incidents/${props.incidentId}` : `/api/incidents/${props.incidentId}`
    
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    await axios.put(url, body, { headers })
    
    // 显示成功提示
    toast.success(t('incidents.edit.success') || '事件更新成功', 'SUCCESS')
    
    // 触发更新成功事件
    emit('updated')
    handleClose()
  } catch (error) {
    console.error('Failed to update incident:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.edit.error') || '事件更新失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isSubmitting.value = false
  }
}

// 监听 visible 变化，控制 body 滚动
watch(() => props.visible, (newVal) => {
  if (newVal) {
    // 阻止背景滚动
    document.body.style.overflow = 'hidden'
  } else {
    // 恢复滚动
    document.body.style.overflow = ''
  }
}, { immediate: true })

onMounted(() => {
  if (props.visible) {
    setTimeout(() => {
      showPanel.value = true
    }, 10)
  }
})

onUnmounted(() => {
  // 确保组件卸载时恢复滚动
  document.body.style.overflow = ''
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease-in-out;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* 自定义滚动条样式 */
.custom-scrollbar {
  /* Firefox */
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
}

/* WebKit 浏览器 (Chrome, Safari, Edge) */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 2px;
  transition: background-color 0.2s ease;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(59, 130, 246, 0.5);
}

/* 自定义日期选择器输入框样式 - 深色模式 */
:deep(.datepicker-input-dark) {
  width: 100%;
  background-color: #1e293b;
  color: white;
  border: 1px solid #324867;
  border-radius: 0.375rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

:deep(.datepicker-input-dark:hover) {
  border-color: #3c4a60;
}

:deep(.datepicker-input-dark:focus) {
  border-color: #2b7cee;
  box-shadow: 0 0 0 3px rgba(43, 124, 238, 0.1);
  outline: none;
}

/* 自定义日期选择器输入框样式 - 浅色模式 */
:deep(.datepicker-input-light) {
  width: 100%;
  background-color: #f3f4f6;
  color: #111827;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

:deep(.datepicker-input-light:hover) {
  border-color: #9ca3af;
}

:deep(.datepicker-input-light:focus) {
  border-color: #2b7cee;
  box-shadow: 0 0 0 3px rgba(43, 124, 238, 0.1);
  outline: none;
}

/* 日期选择器弹窗深色主题样式 */
:deep(.dp__theme_dark) {
  --dp-background-color: #1e293b;
  --dp-text-color: #ffffff;
  --dp-hover-color: #2a3546;
  --dp-hover-text-color: #ffffff;
  --dp-hover-icon-color: #ffffff;
  --dp-primary-color: #2b7cee;
  --dp-primary-text-color: #ffffff;
  --dp-secondary-color: #324867;
  --dp-border-color: #324867;
  --dp-menu-border-color: #324867;
  --dp-border-color-hover: #3c4a60;
  --dp-disabled-color: #1a1f2e;
  --dp-scroll-bar-background: #2a3546;
  --dp-scroll-bar-color: #3c4a60;
  --dp-success-color: #10b981;
  --dp-success-color-disabled: #065f46;
  --dp-icon-color: #9ca3af;
  --dp-danger-color: #ef4444;
  --dp-highlight-color: rgba(43, 124, 238, 0.1);
}

/* 美化 select 下拉框 */
select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1.25rem;
  padding-right: 2.75rem !important;
}

select:focus {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%232b7cee' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
}

select option {
  padding: 0.5rem;
}

:root select option {
  background-color: #f3f4f6;
  color: #111827;
}

:root.dark select option {
  background-color: #1e293b;
  color: white;
}

/* 输入框和选择框的 hover 效果 */
:root.dark input:hover:not(:focus),
:root.dark select:hover:not(:focus),
:root.dark textarea:hover:not(:focus) {
  border-color: #3c4a60;
}

:root:not(.dark) input:hover:not(:focus),
:root:not(.dark) select:hover:not(:focus),
:root:not(.dark) textarea:hover:not(:focus) {
  border-color: #9ca3af;
}

/* 输入框和选择框的 focus 效果增强 */
input:focus,
select:focus,
textarea:focus {
  border-color: #2b7cee;
  box-shadow: 0 0 0 3px rgba(43, 124, 238, 0.1);
}
</style>

