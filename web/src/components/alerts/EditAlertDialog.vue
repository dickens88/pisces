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
      
      <!-- 编辑告警面板 - 有滑入动画 -->
      <Transition name="slide">
        <div
          v-if="showPanel"
          class="relative w-[70vw] h-full bg-white dark:bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- 头部 -->
          <div class="sticky top-0 z-20 bg-white/90 dark:bg-panel-dark/80 backdrop-blur-sm border-b border-gray-200 dark:border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ $t('alerts.edit.title') }}</h2>
              <button
                @click="handleClose"
                class="p-2 text-gray-500 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>

          <!-- 内容区 -->
          <div class="flex-1 p-6 overflow-y-auto custom-scrollbar bg-gray-50 dark:bg-transparent">
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <!-- 告警标题 - 独占一行 -->
              <div>
                <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  {{ $t('alerts.create.alertTitle') }} <span class="text-red-400">*</span>
                </label>
                <input
                  v-model="formData.title"
                  type="text"
                  required
                  class="w-full bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                  :placeholder="$t('alerts.create.alertTitlePlaceholder')"
                />
              </div>

              <!-- 第一行：风险等级、状态和发生时间 -->
              <div class="grid grid-cols-3 gap-4">
                <!-- 风险等级 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('alerts.create.riskLevel') }} <span class="text-red-400">*</span>
                  </label>
                  <select
                    v-model="formData.riskLevel"
                    required
                    class="w-full bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">{{ $t('alerts.create.selectRiskLevel') }}</option>
                    <option value="fatal">{{ $t('common.severity.fatal') }}</option>
                    <option value="high">{{ $t('common.severity.high') }}</option>
                    <option value="medium">{{ $t('common.severity.medium') }}</option>
                    <option value="low">{{ $t('common.severity.low') }}</option>
                    <option value="tips">{{ $t('common.severity.tips') }}</option>
                  </select>
                </div>

                <!-- 状态 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('alerts.create.status') }} <span class="text-red-400">*</span>
                  </label>
                  <select
                    v-model="formData.status"
                    required
                    class="w-full bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="open">{{ $t('alerts.list.open') }}</option>
                    <option value="block">{{ $t('alerts.list.block') }}</option>
                    <option value="closed">{{ $t('alerts.list.closed') }}</option>
                  </select>
                </div>

                <!-- 发生时间 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('alerts.create.timestamp') }} <span class="text-red-400">*</span>
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
                    input-class-name="datepicker-input"
                  />
                </div>
              </div>

              <!-- 第二行：责任人和规则名称 -->
              <div class="grid grid-cols-2 gap-4">
                <!-- 责任人 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('alerts.create.owner') }} <span class="text-red-400">*</span>
                  </label>
                  <input
                    v-model="formData.owner"
                    type="text"
                    required
                    class="w-full bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    :placeholder="$t('alerts.create.ownerPlaceholder')"
                  />
                </div>

                <!-- 规则名称 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {{ $t('alerts.create.ruleName') }}
                  </label>
                  <input
                    v-model="formData.ruleName"
                    type="text"
                    class="w-full bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    :placeholder="$t('alerts.create.ruleNamePlaceholder')"
                  />
                </div>
              </div>

              <!-- 告警描述 - 独占一行 -->
              <div>
                <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  {{ $t('alerts.create.description') }} <span class="text-red-400">*</span>
                </label>
                <textarea
                  v-model="formData.description"
                  required
                  rows="6"
                  class="w-full bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary outline-none resize-none transition-colors"
                  :placeholder="$t('alerts.create.descriptionPlaceholder')"
                ></textarea>
              </div>

              <!-- 按钮组 -->
              <div class="flex items-center justify-end gap-4 pt-4 border-t border-gray-200 dark:border-border-dark">
                <button
                  type="button"
                  @click="handleClose"
                  class="px-6 py-2 text-sm font-medium text-gray-700 dark:text-white bg-gray-100 dark:bg-[#2a3546] border border-gray-200 dark:border-transparent rounded-md hover:bg-gray-200 dark:hover:bg-[#3c4a60] transition-colors"
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
import { updateAlert } from '@/api/alerts'
import { updateASMItem } from '@/api/asm'
import { useToast } from '@/composables/useToast'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import { useAppStore } from '@/stores/app'
import { zhCN, enUS } from 'date-fns/locale'
import '@vuepic/vue-datepicker/dist/main.css'
import { parseToDate } from '@/utils/dateTime'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  alertId: {
    type: [Number, String],
    required: true
  },
  initialData: {
    type: Object,
    default: null
  },
  workspace: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

const { t, locale } = useI18n()
const appStore = useAppStore()
const toast = useToast()

const showPanel = ref(false)
const isSubmitting = ref(false)

// 日期选择器的语言配置
const datePickerLocale = computed(() => {
  return locale.value === 'zh-CN' ? zhCN : enUS
})

const isDarkMode = computed(() => appStore.theme === 'dark')

// 初始化表单数据
const getInitialFormData = () => {
  const now = new Date()

  return {
    title: '',
    riskLevel: '',
    status: 'open',
    owner: '',
    ruleName: '',
    createTime: now,
    description: ''
  }
}

const formData = ref(getInitialFormData())

const fillFormData = () => {
  formData.value = getInitialFormData()
  

  if (props.initialData) {
    formData.value.title = props.initialData.title || ''
    formData.value.riskLevel = props.initialData.riskLevel || ''
    formData.value.status = props.initialData.status || 'open'
    
    formData.value.createTime =
      parseToDate(props.initialData.createTime)
      || parseToDate(props.initialData.create_time)
      || new Date()
    
    formData.value.owner = props.initialData.owner || ''
    formData.value.ruleName = props.initialData.ruleName || ''
    // 处理 description 字段：如果是对象，转换为 JSON 字符串；如果是字符串，直接使用
    if (props.initialData.description) {
      if (typeof props.initialData.description === 'object') {
        formData.value.description = JSON.stringify(props.initialData.description, null, 2)
      } else {
        formData.value.description = String(props.initialData.description)
      }
    } else {
      formData.value.description = ''
    }
  } else {
    console.warn('No initial data provided to EditAlertDialog')
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
    
    // 直接传递 Date 对象，让 formatTimestamp 统一处理时区转换
    const createTime = parseToDate(formData.value.createTime) || new Date()
    
    const alertData = {
      title: formData.value.title,
      riskLevel: formData.value.riskLevel,
      status: formData.value.status,
      owner: formData.value.owner,
      ruleName: formData.value.ruleName || undefined,
      createTime,
      description: formData.value.description
    }

    if (props.workspace === 'asm') {
      await updateASMItem(props.alertId, alertData)
    } else {
      await updateAlert(props.alertId, alertData)
    }
    
    // 显示成功提示
    toast.success(t('alerts.edit.success') || '告警更新成功', 'SUCCESS')
    
    // 触发更新成功事件
    emit('updated')
    handleClose()
  } catch (error) {
    console.error('Failed to update alert:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('alerts.edit.error') || '告警更新失败，请稍后重试'
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

/* 自定义日期选择器输入框样式 */
:deep(.datepicker-input) {
  width: 100%;
  background-color: #ffffff;
  color: #111827;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.dark :deep(.datepicker-input) {
  background-color: #1e293b;
  color: white;
  border: 1px solid #324867;
}

:deep(.datepicker-input:hover) {
  border-color: #9ca3af;
}

.dark :deep(.datepicker-input:hover) {
  border-color: #3c4a60;
}

:deep(.datepicker-input:focus) {
  border-color: #2b7cee;
  box-shadow: 0 0 0 3px rgba(43, 124, 238, 0.1);
  outline: none;
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
  background-color: #ffffff;
  color: #111827;
  padding: 0.5rem;
}

.dark select option {
  background-color: #1e293b;
  color: white;
}

/* 输入框和选择框的 hover 效果 */
input:hover:not(:focus),
select:hover:not(:focus),
textarea:hover:not(:focus) {
  border-color: #9ca3af;
}

.dark input:hover:not(:focus),
.dark select:hover:not(:focus),
.dark textarea:hover:not(:focus) {
  border-color: #3c4a60;
}

/* 输入框和选择框的 focus 效果增强 */
input:focus,
select:focus,
textarea:focus {
  border-color: #2b7cee;
  box-shadow: 0 0 0 3px rgba(43, 124, 238, 0.1);
}
</style>

