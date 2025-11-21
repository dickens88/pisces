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
      <div class="mb-6 relative">
        <label class="block text-sm font-medium text-white mb-2">
          {{ $t('incidents.detail.closeDialog.conclusion') }}
        </label>
        <div class="relative">
          <textarea
            v-model="closeConclusion.notes"
            @focus="showHistoryDropdown = true"
            @blur="handleTextareaBlur"
            rows="4"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
            :placeholder="$t('incidents.detail.closeDialog.conclusionPlaceholder')"
          ></textarea>
          <!-- 历史记录下拉菜单 -->
          <div
            v-if="showHistoryDropdown && commentHistory.length > 0"
            class="absolute z-10 w-full mt-1 bg-[#1e293b] border border-[#324867] rounded-md shadow-lg max-h-48 overflow-y-auto"
            @mousedown.prevent
          >
            <div
              v-for="(item, index) in commentHistory"
              :key="index"
              @click="selectHistoryItem(item)"
              class="px-4 py-2 text-sm text-white hover:bg-[#324867] cursor-pointer border-b border-[#324867] last:border-b-0"
            >
              <div class="truncate">{{ item }}</div>
            </div>
          </div>
        </div>
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
import { saveCloseComment, getCloseCommentHistory } from '@/utils/closeCommentHistory'

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
const showHistoryDropdown = ref(false)
const commentHistory = ref([])
const closeConclusion = ref({
  category: '',
  notes: ''
})

// 加载历史记录
const loadHistory = () => {
  commentHistory.value = getCloseCommentHistory('incident')
}

// 监听 visible 变化，重置表单并加载历史记录
watch(() => props.visible, (newVal) => {
  if (newVal) {
    // 弹窗打开时加载历史记录
    loadHistory()
  } else {
    // 弹窗关闭时重置表单
    closeConclusion.value = {
      category: '',
      notes: ''
    }
    isSubmitting.value = false
    showHistoryDropdown.value = false
  }
})

// 处理输入框失焦事件（延迟关闭下拉菜单，以便点击选项时能触发）
const handleTextareaBlur = () => {
  // 延迟关闭，让点击事件先触发
  setTimeout(() => {
    showHistoryDropdown.value = false
  }, 200)
}

// 选择历史记录项
const selectHistoryItem = (item) => {
  closeConclusion.value.notes = item
  showHistoryDropdown.value = false
}

const handleClose = () => {
  emit('close')
}

const handleSubmit = () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim() || isSubmitting.value) {
    return
  }
  
  // 设置提交状态，防止重复提交
  isSubmitting.value = true
  
  // 保存评论到历史记录
  saveCloseComment(closeConclusion.value.notes.trim(), 'incident')
  
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

