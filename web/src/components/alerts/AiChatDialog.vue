<template>
  <div class="flex flex-col h-full min-h-0">
    <!-- AI对话历史 -->
    <div 
      ref="chatHistoryRef" 
      class="flex-1 overflow-y-auto custom-scrollbar min-h-0"
      :class="scrollToEdge ? '-mr-6 pr-6' : ''"
    >
      <div 
        class="space-y-4"
        :class="compact ? '' : 'space-y-6'"
      >
      <!-- 显示从后端返回的AI数据 -->
      <div
        v-for="(aiItem, index) in aiData || []"
        :key="`ai-${index}`"
        class="flex items-start gap-3 min-w-0"
        :class="compact ? 'gap-3' : 'gap-4'"
      >
        <div
          v-if="showAvatar"
          class="flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600"
          :class="compact ? 'h-8 w-8' : 'h-10 w-10'"
        >
          <span 
            class="material-symbols-outlined text-white"
            :class="compact ? 'text-xs' : 'text-sm'"
          >smart_toy</span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-baseline gap-2">
            <p 
              class="font-semibold text-white"
              :class="compact ? 'text-sm' : ''"
            >{{ aiItem.author || 'AI Agent' }}</p>
            <p 
              class="text-xs text-text-light"
            >{{ formatDateTime(aiItem.create_time || aiItem.time) }}</p>
          </div>

          <!-- 将节点下拉和回答内容放在同一个气泡容器中 -->
          <div 
            class="mt-1 text-[#c3d3e8] bg-[#2a3546] rounded-lg rounded-tl-none ai-chat__html overflow-x-hidden break-words"
            :class="compact ? 'text-xs p-2' : 'text-sm p-3'"
          >
            <!-- 执行节点下拉列表 -->
            <div 
              v-if="aiItem.nodes && aiItem.nodes.length"
              class="mb-2"
            >
              <details
                class="group rounded-md border border-[#3c4a60] bg-[#111827]/60 text-[11px] text-text-light"
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
                    <span class="text-[10px] text-text-light/70 shrink-0">
                      ({{ aiItem.nodes.length }})
                    </span>
                  </div>
                  <span 
                    class="material-symbols-outlined text-text-light text-sm transition-transform duration-200 group-open:rotate-180 shrink-0"
                  >
                    expand_more
                  </span>
                </summary>
                
                <div class="border-t border-[#3c4a60] px-2 py-1.5 space-y-1.5">
                  <div
                    v-for="(node, nIndex) in aiItem.nodes"
                    :key="`node-${nIndex}-${node.title || node.name || 'node'}`"
                    class="flex items-center justify-between gap-2"
                  >
                    <div class="flex items-center gap-1.5 min-w-0">
                      <span 
                        class="material-symbols-outlined text-sm shrink-0"
                        :class="node.status === 'running' ? 'text-amber-300 animate-pulse' : 'text-emerald-300'"
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
                      :class="node.status === 'running' ? 'text-amber-300/90' : 'text-emerald-300/90'"
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

            <!-- AI 回答内容 -->
            <div v-html="sanitizeHtml(aiItem.content || '')"></div>
          </div>
        </div>
      </div>
      
      <!-- 如果没有AI数据，显示提示 -->
      <div 
        v-if="!aiData || aiData.length === 0" 
        class="text-text-light text-center py-4"
        :class="compact ? 'text-xs' : 'text-sm'"
      >
        {{ $t('alerts.detail.noAiResponse') || '暂无AI分析结果' }}
      </div>
      </div>
    </div>
    
    <!-- AI 对话输入框 -->
    <div 
      class="border-t border-border-dark"
      :class="compact ? 'pt-4' : 'mt-6 pt-6'"
    >
      <div 
        class="flex items-start gap-3 min-w-0"
        :class="compact ? 'gap-3' : 'gap-4'"
      >

        <div class="flex-1 min-w-0">
          <!-- 输入框容器 -->
          <div 
            class="relative border-2 border-[#3c4a60] bg-[#1e293b] transition-all duration-200 focus-within:border-primary focus-within:shadow-lg focus-within:shadow-primary/20"
            :class="[
              compact ? 'rounded-lg' : 'rounded-xl',
              { 
                'border-primary shadow-lg shadow-primary/20 drag-active': isDragging,
                'border-primary/50': isDragging
              }
            ]"
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
          >
            <textarea
              v-model="message"
              class="w-full bg-transparent text-white placeholder:text-text-light/60 focus:outline-none resize-none"
              :class="[
                compact 
                  ? 'rounded-lg p-3 pr-24 text-xs min-h-[80px]' 
                  : 'rounded-xl p-4 pr-32 text-sm min-h-[100px]',
                compact ? 'rows-2' : 'rows-3'
              ]"
              :placeholder="$t('alerts.detail.aiAgentPlaceholder') || 'Ask AI about this alert...'"
              :rows="compact ? 2 : 3"
              @input="handleMessageInput"
            ></textarea>
            
            <!-- 工具栏 -->
            <div 
              class="absolute flex items-center gap-1"
              :class="compact ? 'bottom-2 left-2 gap-1' : 'bottom-3 left-4 gap-2'"
            >
              <!-- 文件上传按钮 -->
              <label class="cursor-pointer">
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  class="hidden"
                  @change="handleFileSelect"
                />
                <button
                  type="button"
                  class="flex items-center justify-center rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200"
                  :class="compact ? 'w-7 h-7' : 'w-8 h-8'"
                  title="Upload file"
                >
                  <span 
                    class="material-symbols-outlined"
                    :class="compact ? 'text-sm' : 'text-lg'"
                  >attach_file</span>
                </button>
              </label>
              
              <!-- 表情按钮（仅在非紧凑模式下显示） -->
              <button
                v-if="!compact"
                type="button"
                class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200"
                title="Add emoji"
              >
                <span class="material-symbols-outlined text-lg">mood</span>
              </button>
            </div>
            
            <!-- 提交按钮 -->
            <button
              @click="handleSend"
              :disabled="!canSubmit"
              class="absolute flex items-center justify-center gap-1 rounded-lg bg-gradient-to-r from-primary to-blue-600 px-3 py-1.5 text-xs font-semibold text-white transition-all duration-200 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl disabled:shadow-none"
              :class="compact ? 'bottom-2 right-2 gap-1 px-3 py-1.5' : 'bottom-3 right-3 gap-2 px-4 py-2'"
            >
              <span 
                class="material-symbols-outlined"
                :class="compact ? 'text-sm' : 'text-base'"
              >send</span>
              <span>{{ $t('common.submit') || 'Send' }}</span>
            </button>
          </div>
          
          <!-- 已上传文件列表 -->
          <div 
            v-if="files.length > 0" 
            class="flex flex-wrap gap-1.5 mt-2"
            :class="compact ? 'gap-1.5 mt-2' : 'gap-2 mt-3'"
          >
            <div
              v-for="(file, index) in files"
              :key="index"
              class="group relative flex items-center gap-1.5 rounded-lg bg-[#2a3546] border border-[#3c4a60] px-2 py-1 hover:bg-[#3c4a60] transition-colors"
              :class="compact ? 'gap-1.5 px-2 py-1' : 'gap-2 px-3 py-2'"
            >
              <span 
                class="material-symbols-outlined text-primary"
                :class="compact ? 'text-xs' : 'text-sm'"
              >
                {{ getFileIcon(file.type) }}
              </span>
              <span 
                class="text-xs text-text-light truncate"
                :class="compact ? 'max-w-[120px]' : 'max-w-[200px]'"
              >{{ file.name }}</span>
              <span class="text-xs text-text-light/60">{{ formatFileSize(file.size) }}</span>
              <button
                @click="removeFile(index)"
                class="ml-1 flex items-center justify-center rounded-full bg-[#1e293b] hover:bg-red-500/20 text-text-light hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                :class="compact ? 'w-4 h-4' : 'w-5 h-5 ml-2'"
                title="Remove file"
              >
                <span 
                  class="material-symbols-outlined"
                  :class="compact ? 'text-xs' : 'text-sm'"
                >close</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import { formatDateTime } from '@/utils/dateTime'

const props = defineProps({
  aiData: {
    type: Array,
    default: () => []
  },
  compact: {
    type: Boolean,
    default: false
  },
  autoScroll: {
    type: Boolean,
    default: true
  },
  scrollToEdge: {
    type: Boolean,
    default: false
  },
  showAvatar: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['send'])

const { t } = useI18n()

const chatHistoryRef = ref(null)
const message = ref('')
const files = ref([])
const fileInput = ref(null)
const isDragging = ref(false)

const canSubmit = computed(() => {
  return message.value.trim().length > 0 || files.value.length > 0
})

// 滚动到底部
const scrollToBottom = () => {
  if (!props.autoScroll) return
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

// 监听 AI 数据变化，自动滚动到底部
watch(() => props.aiData, () => {
  scrollToBottom()
}, { deep: true, immediate: true })

// 组件挂载时滚动到底部
onMounted(() => {
  // 延迟一下确保 DOM 已渲染
  setTimeout(() => {
    scrollToBottom()
  }, 100)
})

// 暴露方法供父组件调用
defineExpose({
  scrollToBottom
})

const handleMessageInput = () => {
  // 可以在这里添加自动调整高度的逻辑
}

const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files || [])
  addFiles(selectedFiles)
  // 清空input，以便可以再次选择相同文件
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const droppedFiles = Array.from(event.dataTransfer.files || [])
  addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
  newFiles.forEach(file => {
    // 检查文件大小（限制为10MB）
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return
    }
    // 检查是否已存在
    if (!files.value.find(f => f.name === file.name && f.size === file.size)) {
      files.value.push(file)
    }
  })
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const handleSend = () => {
  if (!canSubmit.value) return
  
  emit('send', {
    message: message.value,
    files: [...files.value]
  })
  
  // 清空输入
  message.value = ''
  files.value = []
  
  // 发送后滚动到底部
  scrollToBottom()
}

const getFileIcon = (mimeType) => {
  if (!mimeType) return 'attach_file'
  if (mimeType.includes('image')) return 'image'
  if (mimeType.includes('video')) return 'videocam'
  if (mimeType.includes('audio')) return 'audiotrack'
  if (mimeType.includes('pdf')) return 'picture_as_pdf'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'description'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'table_chart'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'folder_zip'
  return 'attach_file'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}
</script>

<style scoped>
.ai-chat__html {
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
}

.ai-chat__html :deep(pre) {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  overflow-x: auto;
  max-width: 100%;
  margin: 10px 0;
}

.ai-chat__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.ai-chat__html :deep(b) {
  color: #e2e8f0;
}

.ai-chat__html :deep(p) {
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
}
</style>

