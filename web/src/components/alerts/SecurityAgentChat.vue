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
          <div class="flex items-center justify-between text-xs text-gray-500 dark:text-slate-400 mb-1">
            <span class="font-semibold text-gray-700 dark:text-slate-200">
              {{ getMessageAuthorLabel(item) }}
            </span>
            <span>
              {{ formatDateTime(item.create_time || item.time) }}
            </span>
          </div>

          <!-- 将节点下拉和回答内容放在同一个气泡容器中 -->
          <div 
            class="text-sm text-gray-900 dark:text-slate-200 bg-gray-100 dark:bg-slate-800/50 rounded-md p-2.5 security-agent__html overflow-x-hidden break-words"
          >
            <!-- 执行节点下拉列表（仅在存在节点时显示） -->
            <div
              v-if="item.nodes && item.nodes.length"
              class="mb-2"
            >
              <details
                class="group rounded-md border border-slate-200 dark:border-slate-700 bg-slate-50/80 dark:bg-slate-900/40 text-[11px] text-slate-600 dark:text-slate-300"
              >
                <summary
                  class="flex items-center justify-between px-2 py-1 cursor-pointer select-none list-none"
                >
                  <div class="flex items-center gap-1.5 min-w-0">
                    <span class="material-symbols-outlined text-primary text-sm shrink-0">
                      route
                    </span>
                    <span class="truncate">
                      {{ $t('alerts.detail.executedNodes') || 'Executed nodes' }}
                    </span>
                    <span class="text-[10px] text-slate-500 dark:text-slate-400 shrink-0">
                      ({{ item.nodes.length }})
                    </span>
                  </div>
                  <span 
                    class="material-symbols-outlined text-slate-500 dark:text-slate-300 text-sm transition-transform duration-200 group-open:rotate-180 shrink-0"
                  >
                    expand_more
                  </span>
                </summary>
                
                <div class="border-t border-slate-200 dark:border-slate-700 px-2 py-1.5 space-y-1.5">
                  <div
                    v-for="(node, nIndex) in item.nodes"
                    :key="`node-${nIndex}-${node.title || node.name || 'node'}`"
                    class="flex items-center justify-between gap-2"
                  >
                    <div class="flex items-center gap-1.5 min-w-0">
                      <span 
                        class="material-symbols-outlined text-sm shrink-0"
                        :class="node.status === 'running' ? 'text-amber-400 animate-pulse' : 'text-emerald-400'"
                      >
                        {{ node.status === 'running' ? 'autorenew' : 'check_circle' }}
                      </span>
                      <span 
                        class="truncate text-[11px]"
                      >
                        {{ node.title || node.name || (node.data && node.data.title) || 'Unnamed node' }}
                      </span>
                    </div>
                    <span
                      class="text-[10px] shrink-0"
                      :class="node.status === 'running' ? 'text-amber-500/90' : 'text-emerald-400/90'"
                    >
                      {{ node.status === 'running'
                        ? ($t('common.running') || 'Running')
                        : ($t('common.finished') || 'Finished')
                      }}
                    </span>
                  </div>
                </div>
              </details>
            </div>

            <!-- 如果是最后一条消息且是assistant且内容为空且正在loading，显示loading动画 -->
            <div 
              v-if="isLastMessageLoading(item, index)"
            >
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <div 
              v-else
              v-html="sanitizeHtml(item.content || '')"
            ></div>
          </div>
        </div>
        
        <!-- 如果没有消息，显示提示 -->
        <div 
          v-if="!messages || messages.length === 0" 
          class="text-gray-500 dark:text-slate-400 text-center py-8 text-sm"
        >
          {{ $t('alerts.detail.noAiResponse') || '暂无消息' }}
        </div>
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="border-t border-gray-200 dark:border-slate-700 pt-3 mt-3 security-agent-input">
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

// 判断是否是最后一条消息且正在loading
const isLastMessageLoading = (item, index) => {
  if (!props.loading) return false
  if (!props.messages || props.messages.length === 0) return false
  const isLastMessage = index === props.messages.length - 1
  const isAssistant = item.role === 'assistant'
  const isEmptyContent = !item.content || item.content.trim() === ''
  return isLastMessage && isAssistant && isEmptyContent
}
</script>

<style scoped>
.security-agent__html {
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
}

.security-agent__html :deep(pre) {
  background: rgba(249, 250, 251, 0.9);
  border: 1px solid rgba(209, 213, 219, 0.8);
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

.dark .security-agent__html :deep(pre) {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
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

/* 打字指示器动画 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #94a3b8;
  display: inline-block;
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0;
}

@keyframes typing-bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>

