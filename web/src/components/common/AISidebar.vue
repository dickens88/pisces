<template>
  <Teleport to="body">
    <!-- 遮罩层 -->
    <Transition name="fade">
      <div
        v-if="visible && showOverlay"
        class="fixed inset-0 bg-black/50 z-40"
        @click="handleClose"
      ></div>
    </Transition>

    <!-- 侧边栏 -->
    <Transition name="slide">
      <aside
        v-if="visible"
        :class="[
          position === 'fixed' ? 'fixed' : 'absolute',
          'right-0 top-0 h-screen w-[400px] bg-gray-100 dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col z-50 shadow-none'
        ]"
      >
        <!-- Header -->
        <header class="flex items-center justify-between px-4 py-1.5 border-b border-gray-200 dark:border-gray-700 flex-shrink-0" :class="position === 'absolute' && 'gap-2'">
          <div :class="position === 'absolute' && 'flex-1 min-w-0'">
            <h2 class="text-xs font-medium text-gray-500 dark:text-gray-400 leading-tight">{{ $t('common.aiAssistantForSecurity') || 'AI Assistant for Security' }}</h2>
            <p v-if="alertTitle && position === 'absolute'" class="text-sm font-semibold text-gray-900 dark:text-white mt-0.5 truncate" :title="alertTitle">{{ alertTitle }}</p>
          </div>
          <div class="flex items-center space-x-2" :class="position === 'absolute' && 'flex-shrink-0'">
            <button
              @click="handleResetConversation"
              class="h-8 w-8 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
              :title="$t('common.reset') || '重置'"
            >
              <span class="material-symbols-outlined text-base">restart_alt</span>
            </button>
            <button
              @click="handleClose"
              class="h-8 w-8 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
              :title="$t('common.close') || '关闭'"
            >
              <span class="material-symbols-outlined text-base">close</span>
            </button>
          </div>
        </header>

        <!-- Content -->
        <div ref="contentScrollRef" class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
          <!-- Security Agent Initial Message -->
          <div class="min-w-0">
            <div class="flex items-center space-x-3 mb-1">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex-shrink-0 flex items-center justify-center">
                <span class="material-symbols-outlined text-white text-base">auto_awesome</span>
              </div>
              <div class="flex items-center justify-between flex-1">
                <span class="text-xs font-semibold text-gray-700 dark:text-slate-200">
                  {{ getSecurityAgentAssistantLabel() }}
                </span>
                <span class="text-xs text-gray-500 dark:text-slate-400">
                  {{ formatDateTime(new Date()) }}
                </span>
              </div>
            </div>
            <div class="ml-2">
              <div class="text-sm text-gray-900 dark:text-slate-200 bg-gray-100 dark:bg-slate-800/50 rounded-md p-2.5 security-agent__html overflow-x-hidden break-words">
              </div>
            </div>
          </div>

          <template v-if="showFindingSummary && findingSummary">
            <!-- Finding Summarization -->
            <div class="space-y-2">
              <details class="group bg-white dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden" open>
                <summary class="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <h3 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('common.findingSummarization') || 'Finding Summarization' }}</h3>
                  <span class="material-symbols-outlined text-base text-gray-500 dark:text-gray-400 transition-transform group-open:rotate-180">expand_more</span>
                </summary>
                <div class="p-4 border-t border-gray-200 dark:border-gray-700">
                  <div
                    v-if="findingSummary && findingSummary.trim()"
                    :class="[
                      'text-sm text-gray-700 dark:text-[#c3d3e8] ai-agent__html',
                      { 'ai-agent__html--dark': isDarkMode }
                    ]"
                    v-html="sanitizeHtml(findingSummary)"
                  ></div>
                  <div
                    v-else
                    class="text-sm text-gray-500 dark:text-gray-400 italic"
                  >
                    {{ $t('common.noAiResponse') || 'No AI analysis results' }}
                  </div>
                </div>
              </details>

            </div>
          </template>

          <!-- Suggested Tools -->
          <ToolkitSection
            :toolkits="toolkits"
            :loading-toolkits="loadingToolkits"
            :loading-toolkit-records="loadingToolkitRecords"
            :toolkit-params="toolkitParams"
            :executing-toolkit-id="executingToolkitId"
            :toolkit-records="toolkitRecords"
            :toolkit-execution-results="toolkitExecutionResults"
            :expanded-toolkit-ids="expandedToolkitIds"
            @execute="handleExecuteToolkit"
            @update-param="updateToolkitParam"
            @result-ref="(appId, el) => { toolkitResultRefs[appId] = el }"
          />

          <!-- Security Agent Messages -->
          <div 
            ref="chatHistoryRef" 
            :class="position === 'absolute' ? 'space-y-3' : 'space-y-1'"
          >
            <div
              v-for="(item, index) in securityAgentMessages || []"
              :key="`msg-${index}`"
              class="min-w-0"
            >
              <!-- 分割线 -->
              <div v-if="index > 0" class="border-t border-gray-200 dark:border-gray-700 mb-3 -mt-1"></div>
              <div class="flex items-center space-x-3 mb-1">
                <!-- User Avatar -->
                <UserAvatar 
                  v-if="item.role === 'user'"
                  :name="getMessageAuthorLabel(item)"
                  class="w-8 h-8 shrink-0"
                />
                <!-- Security Agent Avatar -->
                <div 
                  v-else
                  class="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex-shrink-0 flex items-center justify-center"
                >
                  <span class="material-symbols-outlined text-white text-base">auto_awesome</span>
                </div>
                <div class="flex items-center justify-between flex-1">
                  <span class="text-xs font-semibold text-gray-700 dark:text-slate-200">
                    {{ getMessageAuthorLabel(item) }}
                  </span>
                  <span class="text-xs text-gray-500 dark:text-slate-400">
                    {{ formatDateTime(item.create_time || item.time) }}
                  </span>
                </div>
              </div>
              <div class="ml-2">
                <div 
                  class="text-sm text-gray-900 dark:text-slate-200 bg-gray-100 dark:bg-slate-800/50 rounded-md p-2.5 security-agent__html overflow-x-hidden break-words"
                >
                <!-- 执行节点下拉列表（仅在存在节点时显示） -->
                <div
                  v-if="item.nodes && item.nodes.length"
                  class="mb-2"
                >
                  <details
                    open
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
                          {{ $t('common.executedNodes') || 'Executed nodes' }}
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
                        class="space-y-1.5"
                      >
                        <div class="flex items-center justify-between gap-2">
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

                        <!-- 嵌套工具调用列表（仅在存在工具时显示） -->
                        <div
                          v-if="node.tools && node.tools.length"
                          class="ml-5"
                        >
                          <details open class="group/tool text-[11px] text-slate-600 dark:text-slate-300">
                            <summary class="flex items-center gap-1 cursor-pointer select-none list-none">
                              <span class="material-symbols-outlined text-xs text-primary shrink-0">
                                build
                              </span>
                              <span class="truncate">
                                {{ $t('common.agentTools') || 'Tools called' }}
                              </span>
                              <span class="text-[10px] text-slate-500 dark:text-slate-400 shrink-0">
                                ({{ node.tools.length }})
                              </span>
                            </summary>
                            <div class="mt-1 pl-4 space-y-0.5">
                              <div
                                v-for="(tool, tIndex) in node.tools"
                                :key="`tool-${tIndex}-${tool.name || 'tool'}`"
                                class="flex items-center gap-1.5 text-[11px]"
                              >
                                <span class="material-symbols-outlined text-[13px] text-primary shrink-0">
                                  play_arrow
                                </span>
                                <span class="truncate">
                                  {{ tool.name || 'Tool' }}
                                </span>
                              </div>
                            </div>
                          </details>
                        </div>
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
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-2 border-t border-gray-200 dark:border-gray-700 flex-shrink-0 security-agent-input">
          <CommentInput
            v-model="inputMessage"
            :disabled="isSendingSecurityAgentMessage"
            :loading="isSendingSecurityAgentMessage"
            :enable-file-upload="false"
            :submit-on-enter="true"
            placeholder="Ask me anything about ..."
            prefix-icon="auto_awesome"
            @submit="handleSecurityAgentSend"
          />
          <div
            v-if="promptSuggestions.length"
            class="mt-2 flex flex-wrap gap-2"
          >
            <button
              v-for="(prompt, idx) in promptSuggestions"
              :key="`prompt-${idx}`"
              class="ai-prompt-chip"
              @click="applyPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </div>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { getToolkits, getToolkitRecords, executeToolkit } from '@/api/toolkits'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'
import { useDarkModeObserver } from '@/composables/useDarkModeObserver'
import CommentInput from '@/components/common/CommentInput.vue'
import { sendSecurityAgentMessage } from '@/api/securityAgent'
import { getAIPrompts } from '@/api/aiPrompts'
import UserAvatar from '@/components/common/UserAvatar.vue'
import ToolkitSection from '@/components/common/ToolkitSection.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  alertTitle: {
    type: String,
    default: ''
  },
  alertId: {
    type: [String, Number],
    default: null
  },
  findingSummary: {
    type: String,
    default: ''
  },
  showFindingSummary: {
    type: Boolean,
    default: false
  },
  showOverlay: {
    type: Boolean,
    default: true
  },
  position: {
    type: String,
    default: 'fixed', // 'fixed' 或 'absolute'
    validator: (value) => ['fixed', 'absolute'].includes(value)
  }
})

const emit = defineEmits(['close', 'open-in-new', 'send-message', 'tool-action'])

const { t, locale } = useI18n()
const route = useRoute()
const toast = useToast()
const { isDarkMode } = useDarkModeObserver()

const inputMessage = ref('')

// Toolkit related state
const toolkits = ref([])
const loadingToolkits = ref(false)
const toolkitParams = ref({})
const executingToolkitId = ref(null) // 正在执行的工具ID
const toolkitRecords = ref([])
const loadingToolkitRecords = ref(false)
const toolkitExecutionResults = ref({}) // 存储每个工具的执行结果 { app_id: { status, result } }
const expandedToolkitIds = ref(new Set()) // 存储展开的工具ID集合
const toolkitResultRefs = ref({}) // 存储每个工具结果区域的 ref

// Security Agent related state
const securityAgentMessages = ref([])
const isSendingSecurityAgentMessage = ref(false)
const conversationId = ref(null)
const chatHistoryRef = ref(null)
const contentScrollRef = ref(null)

// AI prompt suggestions state
const promptSuggestions = ref([])
const promptsLoading = ref(false)
const promptMeta = ref({
  fallbackUsed: false,
  count: 0
})
const promptError = ref('')

// Security Agent helper functions
const getSecurityAgentUserLabel = () => t('common.securityAgentUserLabel') || 'You'
const getSecurityAgentAssistantLabel = () =>
  t('common.securityAgentAssistantLabel') ||
  t('common.securityAgentTab') ||
  'Agent'

const formatSecurityAgentContent = (text = '') => {
  if (!text || typeof text !== 'string') return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br />')
}

const generateSecurityAgentMessageId = () =>
  `security-agent-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

const appendSecurityAgentMessage = (message) => {
  if (!message) return null
  const rawContent = message.content || ''
  const normalizedMessage = {
    id: message.id || generateSecurityAgentMessageId(),
    author: message.author || getSecurityAgentAssistantLabel(),
    rawContent,
    content: formatSecurityAgentContent(rawContent),
    create_time: message.create_time || new Date().toISOString(),
    role: message.role || 'assistant',
    isLocal: message.isLocal || false,
    nodes: Array.isArray(message.nodes) ? [...message.nodes] : []
  }
  securityAgentMessages.value = [...securityAgentMessages.value, normalizedMessage]
  nextTick(() => {
    scrollToBottom()
  })
  return normalizedMessage.id
}

const updateSecurityAgentMessageNodes = (messageId, nodeTitle, status) => {
  if (!messageId || !nodeTitle || !status) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message

    const nodes = Array.isArray(message.nodes) ? [...message.nodes] : []
    const existingIndex = nodes.findIndex(
      n => n.title === nodeTitle || n.name === nodeTitle || n?.data?.title === nodeTitle
    )

    if (existingIndex === -1) {
      nodes.push({
        title: nodeTitle,
        status
      })
    } else {
      nodes[existingIndex] = {
        ...nodes[existingIndex],
        title: nodes[existingIndex].title || nodeTitle,
        status
      }
    }

    return {
      ...message,
      nodes
    }
  })
}

const appendToolCallToCurrentNode = (messageId, toolName) => {
  if (!messageId || !toolName) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message

    const nodes = Array.isArray(message.nodes) ? [...message.nodes] : []
    if (!nodes.length) {
      nodes.push({
        title: 'Agent',
        status: 'running',
        tools: []
      })
    }

    let targetIndex = nodes.slice().reverse().findIndex(n => n.status === 'running')
    if (targetIndex !== -1) {
      targetIndex = nodes.length - 1 - targetIndex
    } else {
      targetIndex = nodes.length - 1
    }

    const targetNode = { ...(nodes[targetIndex] || {}), tools: Array.isArray(nodes[targetIndex]?.tools) ? [...nodes[targetIndex].tools] : [] }

    const alreadyExists = targetNode.tools.some(t => t.name === toolName)
    if (!alreadyExists) {
      targetNode.tools.push({ name: toolName })
    }

    nodes[targetIndex] = targetNode

    return {
      ...message,
      nodes
    }
  })
}

const setSecurityAgentMessageContent = (messageId, text) => {
  if (!messageId) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message
    const newRawContent = text || ''
    return {
      ...message,
      rawContent: newRawContent,
      content: formatSecurityAgentContent(newRawContent)
    }
  })
}

const appendToSecurityAgentMessage = (messageId, chunk) => {
  if (!messageId || !chunk) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message
    const newRawContent = (message.rawContent || '') + chunk
    return {
      ...message,
      rawContent: newRawContent,
      content: formatSecurityAgentContent(newRawContent)
    }
  })
  nextTick(() => {
    scrollToBottom()
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (contentScrollRef.value) {
      contentScrollRef.value.scrollTop = contentScrollRef.value.scrollHeight
    }
  })
}

const scrollToToolkitResult = async (appId) => {
  // 确保工具抽屉展开
  expandedToolkitIds.value.add(appId)
  
  // 等待 DOM 更新
  await nextTick()
  
  // 再次等待，确保结果区域已渲染
  await nextTick()
  
  // 滚动到结果区域
  const resultElement = toolkitResultRefs.value[appId]
  if (resultElement && contentScrollRef.value) {
    // 计算结果元素相对于滚动容器的位置
    const containerRect = contentScrollRef.value.getBoundingClientRect()
    const elementRect = resultElement.getBoundingClientRect()
    const scrollTop = contentScrollRef.value.scrollTop
    const targetScrollTop = scrollTop + elementRect.top - containerRect.top - 20 // 留20px的顶部间距
    
    // 平滑滚动到目标位置
    contentScrollRef.value.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    })
  }
}

const getMessageAuthorLabel = (item = {}) => {
  if (item.role === 'user') {
    return getSecurityAgentUserLabel()
  }
  return getSecurityAgentAssistantLabel()
}

const isLastMessageLoading = (item, index) => {
  if (!isSendingSecurityAgentMessage.value) return false
  if (!securityAgentMessages.value || securityAgentMessages.value.length === 0) return false
  const isLastMessage = index === securityAgentMessages.value.length - 1
  const isAssistant = item.role === 'assistant'
  const isEmptyContent = !item.rawContent || item.rawContent.trim() === ''
  return isLastMessage && isAssistant && isEmptyContent
}

const loadToolkits = async () => {
  loadingToolkits.value = true
  try {
    const response = await getToolkits()
    // 处理不同的响应格式：response.tools 或 response.data.tools
    const tools = response?.tools || response?.data?.tools || []
    toolkits.value = tools
    toolkits.value.forEach(tool => {
      if (!toolkitParams.value[tool.app_id]) {
        toolkitParams.value[tool.app_id] = {}
      }
    })
  } catch (error) {
    console.error('Failed to load toolkits:', error)
    toolkits.value = []
    toast.error(error?.response?.data?.error_message || error?.message || t('common.loadToolkitsError') || '加载工具列表失败')
  } finally {
    loadingToolkits.value = false
  }
}

const currentRoutePath = computed(() => route?.path || '/')

const resolveLang = () => {
  const raw = (locale?.value || '').toLowerCase()
  if (raw.startsWith('zh')) return 'zh'
  if (raw.startsWith('en')) return 'en'
  return 'zh'
}

const fetchPromptSuggestions = async () => {
  if (!props.visible) return
  promptsLoading.value = true
  promptError.value = ''
  try {
    const response = await getAIPrompts({
      route: currentRoutePath.value,
      lang: resolveLang()
    })
    // 后端直接返回字符串数组
    const data = response?.data || response || []
    const prompts = Array.isArray(data) ? data : []
    promptSuggestions.value = prompts.slice(0, 3)
    promptMeta.value = {
      fallbackUsed: false,
      count: prompts.length || 0
    }
    if (!promptSuggestions.value.length) {
      promptError.value = t('common.aiPromptEmpty') || 'No prompt available'
    }
  } catch (error) {
    promptSuggestions.value = []
    promptMeta.value = { fallbackUsed: false, count: 0 }
    promptError.value =
      error?.response?.data?.error_message ||
      error?.message ||
      t('common.aiPromptEmpty') ||
      'No prompt available'
  } finally {
    promptsLoading.value = false
  }
}

const loadToolkitRecords = async () => {
  loadingToolkitRecords.value = true
  try {
    const response = await getToolkitRecords(props.alertId)
    toolkitRecords.value = response.data || []
  } catch (error) {
    console.error('Failed to load toolkit records:', error)
    toolkitRecords.value = []
    if (error?.response?.status !== 400) {
      toast.error(error?.response?.data?.error_message || error?.message || t('common.loadToolkitRecordsError') || '加载执行记录失败')
    }
  } finally {
    loadingToolkitRecords.value = false
  }
}

// 监听visible变化，当侧边栏打开时总是加载工具列表
watch(
  () => [props.visible, currentRoutePath.value, locale?.value],
  ([visible], [prevVisible]) => {
    if (visible) {
      loadToolkits()
      loadToolkitRecords()
      fetchPromptSuggestions()
    } else if (prevVisible) {
      // 关闭时清空数据
      toolkits.value = []
      toolkitParams.value = {}
      toolkitRecords.value = []
      toolkitExecutionResults.value = {}
      expandedToolkitIds.value.clear()
      toolkitResultRefs.value = {}
      promptSuggestions.value = []
      promptMeta.value = { fallbackUsed: false, count: 0 }
      promptError.value = ''
    }
  }
)


const updateToolkitParam = (appId, paramName, value) => {
  if (!toolkitParams.value[appId]) {
    toolkitParams.value[appId] = {}
  }
  toolkitParams.value[appId][paramName] = value
}

const handleExecuteToolkit = async (tool) => {
  const params = toolkitParams.value[tool.app_id] || {}
  const allParams = tool.params || []
  const requiredParams = allParams.filter(p => p.required !== false)
  const missingParams = requiredParams.filter(p => {
    const value = params[p.name]
    return !value || (typeof value === 'string' && value.trim() === '')
  })
  
  if (missingParams.length > 0) {
    const paramNames = missingParams.map(p => p.label).join(', ')
    toast.error(t('common.toolkitParamsRequired', { params: paramNames }) || `请填写参数: ${paramNames}`)
    return
  }

  executingToolkitId.value = tool.app_id
  // 清空之前的结果
  toolkitExecutionResults.value[tool.app_id] = null

  try {
    const requestData = {
      title: tool.title,
      app_id: tool.app_id,
      app_type: tool.app_type,
      params: params
    }

    const response = await executeToolkit(props.alertId || null, requestData)
    // 存储执行结果
    const resultData = response?.data || response
    if (resultData) {
      toolkitExecutionResults.value[tool.app_id] = {
        status: resultData.status || 'completed',
        result: resultData.result || null
      }
    }
    toast.success(t('common.toolkitExecuteSuccess') || '工具执行成功')
    await loadToolkitRecords()
    // 确保工具抽屉展开并滚动到结果区域
    await scrollToToolkitResult(tool.app_id)
  } catch (error) {
    console.error('Failed to execute toolkit:', error)
    // 存储错误结果
    toolkitExecutionResults.value[tool.app_id] = {
      status: 'failed',
      result: error?.response?.data?.error_message || error?.message || t('common.toolkitExecuteError') || '工具执行失败'
    }
    toast.error(error?.response?.data?.error_message || error?.message || t('common.toolkitExecuteError') || '工具执行失败')
    // 确保工具抽屉展开并滚动到结果区域
    await scrollToToolkitResult(tool.app_id)
  } finally {
    executingToolkitId.value = null
  }
}


const handleResetConversation = () => {
  securityAgentMessages.value = []
  conversationId.value = null
  inputMessage.value = ''
}

const handleClose = () => emit('close')
const handleOpenInNew = () => emit('open-in-new')

const handleSecurityAgentSend = async (data) => {
  // CommentInput 发出的是 { comment, files }，需要映射为 { message, files }
  const message = data?.comment || data?.message || ''
  const files = data?.files || []

  if (!message.trim() && (!files || files.length === 0)) {
    return
  }

  if (isSendingSecurityAgentMessage.value) {
    return
  }

  const sanitizedUserMessage = message.trim()
  const payload = {
    alertId: props.alertId,
    message: sanitizedUserMessage,
    files: data.files,
    conversationId: conversationId.value
  }

  if (sanitizedUserMessage) {
    appendSecurityAgentMessage({
      author: getSecurityAgentUserLabel(),
      content: sanitizedUserMessage,
      role: 'user',
      isLocal: true
    })
  }

  let assistantMessageId = null

  try {
    isSendingSecurityAgentMessage.value = true
    assistantMessageId = appendSecurityAgentMessage({
      author: getSecurityAgentAssistantLabel(),
      content: '',
      role: 'assistant',
      isLocal: true
    })

    await sendSecurityAgentMessage({
      ...payload,
      onEvent: (event) => {
        if (!event) return

        const receivedConversationId = event?.conversation_id || event?.conversationId
        if (receivedConversationId) {
          conversationId.value = receivedConversationId
        }

        const eventType = event.event || event.type

        if (eventType === 'message' || eventType === 'message_end') {
          if (assistantMessageId && typeof event.answer === 'string') {
            appendToSecurityAgentMessage(assistantMessageId, event.answer)
          }

          // 当收到 message_end（或类似结束事件）时，提前结束发送中的 loading 状态
          if (eventType === 'message_end') {
            isSendingSecurityAgentMessage.value = false
          }
        } else if (eventType === 'node_started' || eventType === 'node_finished') {
          const nodeData = event.data || {}
          const nodeTitle =
            nodeData.title ||
            nodeData.name ||
            (typeof nodeData === 'string' ? nodeData : '') ||
            ''
          if (assistantMessageId && nodeTitle) {
            const status = eventType === 'node_started' ? 'running' : 'finished'
            updateSecurityAgentMessageNodes(assistantMessageId, nodeTitle, status)
          }
        } else if (eventType === 'agent_log') {
          const logData = event.data || {}
          const label = logData.label || ''

          let toolName = ''
          const match = label.match(/CALL\s+([^\s]+)(?:\s+|$)/i)
          if (match && match[1]) {
            toolName = match[1]
          }

          if (assistantMessageId && toolName) {
            appendToolCallToCurrentNode(assistantMessageId, toolName)
          }
        } else if (eventType === 'error') {
          const streamError = event?.message || t('common.securityAgentSendError') || 'Failed to send message to Security Agent'
          toast.error(streamError, 'ERROR')
          if (assistantMessageId) {
            setSecurityAgentMessageContent(assistantMessageId, streamError)
          } else {
            appendSecurityAgentMessage({
              author: getSecurityAgentAssistantLabel(),
              content: streamError,
              role: 'assistant',
              isLocal: true
            })
          }

          // 出错时也需要立刻结束 loading 状态
          isSendingSecurityAgentMessage.value = false
        }
      }
    })
  } catch (error) {
    const rawMessage = error?.message || ''
    const errorMsg = rawMessage.includes('VITE_AI_CHAT_API') || rawMessage.toLowerCase().includes('not configured')
      ? t('common.securityAgentMissingConfig') || 'Security Agent endpoint is not configured. Please set VITE_AI_CHAT_API.'
      : rawMessage || t('common.securityAgentSendError') || 'Failed to send message to Security Agent'
    toast.error(errorMsg, 'ERROR')
    if (assistantMessageId) {
      setSecurityAgentMessageContent(assistantMessageId, errorMsg)
    } else {
      appendSecurityAgentMessage({
        author: getSecurityAgentAssistantLabel(),
        content: errorMsg,
        role: 'assistant',
        isLocal: true
      })
    }
  } finally {
    isSendingSecurityAgentMessage.value = false
  }
}

const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  // 先将换行符转换为 <br> 标签，以便正确渲染换行
  const htmlWithBreaks = html.replace(/\n/g, '<br />')
  return DOMPurify.sanitize(htmlWithBreaks, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}

// 设置输入框的消息内容
const setMessage = (text) => {
  inputMessage.value = text || ''
}

const applyPrompt = (text) => {
  if (!text) return
  inputMessage.value = text
}

// 暴露方法供父组件调用
defineExpose({
  setMessage
})

// 组件挂载时，如果 visible 为 true，也加载工具列表
onMounted(() => {
  if (props.visible) {
    loadToolkits()
    loadToolkitRecords()
    fetchPromptSuggestions()
  }
})

</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active {
  transition: transform 0.3s ease-out;
}

.slide-leave-active {
  transition: transform 0.3s ease-in;
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

/* AI Agent HTML 样式 - 与 AlertDetail 保持一致 */
.ai-agent__html {
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

.ai-prompt-chip {
  border: 1px solid rgba(148, 163, 184, 0.6);
  color: #0f172a;
  background: #f8fafc;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 11px;
  line-height: 1.2;
  transition: all 0.2s ease;
}

.ai-prompt-chip:hover {
  border-color: rgba(59, 130, 246, 0.7);
  color: #1d4ed8;
  background: #e0ebff;
}

.dark .ai-prompt-chip {
  border-color: rgba(148, 163, 184, 0.25);
  color: #e2e8f0;
  background: rgba(15, 23, 42, 0.6);
}

.dark .ai-prompt-chip:hover {
  border-color: rgba(96, 165, 250, 0.7);
  color: #bfdbfe;
  background: rgba(59, 130, 246, 0.15);
}

.ai-agent__html :deep(pre) {
  background: rgba(226, 232, 240, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.5);
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  margin: 10px 0;
  max-width: 100%;
  overflow-x: auto;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

:global(.dark) .ai-agent__html :deep(pre),
.ai-agent__html--dark :deep(pre) {
  background: #111b2e;
  border: 1px solid rgba(94, 114, 164, 0.45);
  color: #f1f5f9;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.4);
}

.ai-agent__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
  color: #0f172a;
}

:global(.dark) .ai-agent__html :deep(code),
.ai-agent__html--dark :deep(code) {
  color: #f1f5f9;
  background: transparent;
  padding: 0;
  border: none;
}

.ai-agent__html :deep(b) {
  color: #0f172a;
}

:global(.dark) .ai-agent__html :deep(b),
.ai-agent__html--dark :deep(b) {
  color: #e2e8f0;
}

/* Security Agent 样式 */
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

/* 隐藏 Security Agent 输入框中的头像，并压缩整体布局 */
.security-agent-input :deep(.comment-input-container > div > .shrink-0) {
  display: none;
}

.security-agent-input :deep(.comment-input-container > div) {
  gap: 0;
  align-items: center;
}

.security-agent-input :deep(textarea) {
  min-height: 30px;
  max-height: 120px;
  padding-top: 4px;
  padding-bottom: 4px;
  line-height: 1.4;
}

.security-agent-input :deep(.comment-input-container .absolute.left-3) {
  top: 50%;
  transform: translateY(-50%);
}

.security-agent-input :deep(.comment-input-container .absolute.right-2) {
  top: 50%;
  bottom: auto;
  transform: translateY(-50%);
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

