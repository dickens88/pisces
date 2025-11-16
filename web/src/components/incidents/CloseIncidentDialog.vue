<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50"
    @click.self="handleClose"
  >
    <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-white">
          {{ title }}
        </h2>
        <button
          @click="handleClose"
          class="text-gray-400 hover:text-white transition-colors"
        >
          <span class="material-symbols-outlined text-base">close</span>
        </button>
      </div>

      <!-- 提示信息 -->
      <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
        <p class="text-sm text-gray-400">
          {{ confirmMessage }}
        </p>
      </div>

      <!-- 结论分类下拉框 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-white mb-2">
          {{ $t('incidents.detail.closeDialog.conclusionCategory') }}
        </label>
        <select
          v-model="closeConclusion.category"
          class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
        >
          <option value="">{{ $t('incidents.detail.closeDialog.selectCategory') }}</option>
          <option value="falsePositive">{{ $t('incidents.detail.closeDialog.categories.falsePositive') }}</option>
          <option value="resolved">{{ $t('incidents.detail.closeDialog.categories.resolved') }}</option>
          <option value="convertedToIncident">{{ $t('incidents.detail.closeDialog.categories.convertedToIncident') }}</option>
          <option value="other">{{ $t('incidents.detail.closeDialog.categories.other') }}</option>
        </select>
      </div>

      <!-- 调查结论输入框 -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-white mb-2">
          {{ $t('incidents.detail.closeDialog.conclusion') }}
        </label>
        <textarea
          v-model="closeConclusion.notes"
          rows="4"
          class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
          :placeholder="$t('incidents.detail.closeDialog.conclusionPlaceholder')"
        ></textarea>
      </div>

      <!-- 操作按钮 -->
      <div class="flex items-center justify-end gap-3">
        <button
          @click="handleClose"
          class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="handleSubmit"
          :disabled="!closeConclusion.category || !closeConclusion.notes.trim() || isSubmitting"
          class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <span v-if="isSubmitting" class="material-symbols-outlined animate-spin text-base">sync</span>
          {{ $t('common.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  confirmMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'submit'])

const { t } = useI18n()

const isSubmitting = ref(false)
const closeConclusion = ref({
  category: '',
  notes: ''
})

// 监听 visible 变化，重置表单
watch(() => props.visible, (newVal) => {
  if (!newVal) {
    closeConclusion.value = {
      category: '',
      notes: ''
    }
    isSubmitting.value = false
  }
})

const handleClose = () => {
  emit('close')
}

const handleSubmit = () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim() || isSubmitting.value) {
    return
  }
  
  // 设置提交状态，防止重复提交
  isSubmitting.value = true
  
  // 将category映射到close_reason
  const reasonMap = {
    'falsePositive': 'False detection',
    'resolved': 'Resolved',
    'convertedToIncident': 'Converted to Incident',
    'other': 'Other'
  }
  const closeReason = reasonMap[closeConclusion.value.category] || closeConclusion.value.category || 'Other'
  
  emit('submit', {
    close_reason: closeReason,
    close_comment: closeConclusion.value.notes.trim()
  })
}

// 暴露方法供父组件调用
defineExpose({
  setSubmitting: (value) => {
    isSubmitting.value = value
  }
})
</script>

