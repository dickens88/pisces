<template>
  <div class="flex flex-col h-full min-h-0">
    <!-- 消息历史 -->
    <div 
      ref="chatHistoryRef" 
      class="flex-1 overflow-y-auto custom-scrollbar min-h-0"
    >
      <div class="space-y-3">
        <!-- 显示消息 -->
        <div
          v-for="(item, index) in messages || []"
          :key="`msg-${index}`"
          class="min-w-0"
        >
          <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span class="font-semibold text-slate-200">
              {{ getMessageAuthorLabel(item) }}
            </span>
            <span>
              {{ formatDateTime(item.create_time || item.time) }}
            </span>
          </div>
          <div 
            class="text-sm text-slate-200 bg-slate-800/50 rounded-md p-2.5 security-agent__html overflow-x-hidden break-words"
            v-html="sanitizeHtml(item.content || '')"
          ></div>
        </div>
        
        <!-- 如果没有消息，显示提示 -->
        <div 
          v-if="!messages || messages.length === 0" 
          class="text-slate-400 text-center py-8 text-sm"
        >
          {{ $t('alerts.detail.noAiResponse') || '暂无消息' }}
        </div>
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="border-t border-slate-700 pt-3 mt-3 security-agent-input">
      <CommentInput
        v-model="message"
        :placeholder="$t('alerts.detail.aiAgentPlaceholder') || '输入消息...'"
        :disabled="disabled"
        :loading="loading"
        :enable-file-upload="false"
        :submit-on-enter="true"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import { formatDateTime } from '@/utils/dateTime'
import CommentInput from '@/components/common/CommentInput.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  autoScroll: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

const { t } = useI18n()

const chatHistoryRef = ref(null)
const message = ref('')

// 滚动到底部
const scrollToBottom = () => {
  if (!props.autoScroll) return
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动到底部
watch(() => props.messages, () => {
  scrollToBottom()
}, { deep: true, immediate: true })

// 组件挂载时滚动到底部
onMounted(() => {
  setTimeout(() => {
    scrollToBottom()
  }, 100)
})

// 设置输入框的值
const setMessage = (text) => {
  message.value = text || ''
}

// 暴露方法供父组件调用
defineExpose({
  scrollToBottom,
  setMessage
})

const handleSubmit = ({ comment, files }) => {
  emit('send', {
    message: comment || '',
    files: files || []
  })
  
  // 发送后滚动到底部
  scrollToBottom()
}

const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}

const getMessageAuthorLabel = (item = {}) => {
  if (item.role === 'user') {
    return t('alerts.detail.securityAgentUserLabel') || 'Me'
  }
  return t('alerts.detail.securityAgentAssistantLabel') || 'Agent'
}
</script>

<style scoped>
.security-agent__html {
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
}

.security-agent__html :deep(pre) {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 8px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  overflow-x: auto;
  max-width: 100%;
  margin: 8px 0;
  font-size: 12px;
}

.security-agent__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 12px;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.security-agent__html :deep(b) {
  color: #e2e8f0;
  font-weight: 600;
}

.security-agent__html :deep(p) {
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
  margin: 4px 0;
}

/* 自定义滚动条样式 */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
}

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

/* 隐藏 Security Agent 输入框中的头像 */
.security-agent-input :deep(.comment-input-container > div > .shrink-0) {
  display: none;
}

.security-agent-input :deep(.comment-input-container > div) {
  gap: 0;
}
</style>

