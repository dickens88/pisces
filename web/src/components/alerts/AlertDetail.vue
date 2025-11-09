<template>
  <Teleport to="body">
    <div
      v-if="alert"
      class="fixed inset-0 z-50 flex items-center justify-end"
      @click.self="handleClose"
    >
      <!-- 遮罩层 - 直接显示，无动画 -->
      <div 
        class="fixed inset-0 bg-black/50"
        @click="handleClose"
      ></div>
      
      <!-- 详情面板 - 有滑入动画 -->
      <Transition name="slide">
        <div
          v-if="visible"
          class="relative w-screen max-w-4xl h-full bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- 头部 -->
          <div class="sticky top-0 z-20 bg-panel-dark/80 backdrop-blur-sm border-b border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <h2 class="text-xl font-bold text-white">{{ $t('alerts.detail.title') }}</h2>
              <div class="flex items-center gap-2">
                <button
                  @click="handleCloseAlert"
                  class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2"
                >
                  <span class="material-symbols-outlined text-base">archive</span>
                  {{ $t('alerts.detail.closeAlert') }}
                </button>
                <button
                  class="bg-primary hover:bg-blue-500 text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2"
                >
                  <span class="material-symbols-outlined text-base">shield</span>
                  {{ $t('alerts.detail.convertToIncident') }}
                </button>
                <button
                  @click="handleClose"
                  class="p-2 text-text-light hover:text-white transition-colors"
                >
                  <span class="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 内容区 -->
          <div class="flex flex-1 overflow-hidden">
            <main class="flex-1 p-6 space-y-8 overflow-y-auto">
              <!-- 标题和严重程度 -->
              <div v-if="alert">
                <span
                  :class="[
                    'inline-flex items-center rounded-full px-3 py-1 text-sm font-medium',
                    getSeverityClass(alert.severity)
                  ]"
                >
                  <svg class="-ml-0.5 mr-1.5 h-2 w-2" fill="currentColor" viewBox="0 0 8 8">
                    <circle cx="4" cy="4" r="3"></circle>
                  </svg>
                  {{ $t(`alerts.detail.severity.${alert.severity}`) }}
                </span>
                <h1 class="mt-2 text-3xl font-bold text-white">{{ alert.title }}</h1>
              </div>

              <!-- AI分析 -->
              <div v-if="alert?.aiAnalysis">
                <div class="flex items-center gap-2 mb-3">
                  <span class="material-symbols-outlined text-primary text-xl">auto_awesome</span>
                  <h3 class="text-lg font-semibold text-white">{{ $t('alerts.detail.aiAnalysis') }}</h3>
                </div>
                <div class="p-4 rounded-lg bg-primary/10 border border-primary/30 text-sm">
                  <p class="font-bold text-white">{{ alert.aiAnalysis.summary }}</p>
                  <p class="mt-1 text-text-light">
                    {{ alert.aiAnalysis.description }}
                    <span v-if="alert.aiAnalysis.recommendation" class="text-primary font-medium">
                      {{ alert.aiAnalysis.recommendation }}
                    </span>
                  </p>
                </div>
              </div>

              <!-- 标签页 -->
              <div class="border-b border-border-dark">
                <nav aria-label="Tabs" class="-mb-px flex space-x-6">
                  <button
                    v-for="tab in tabs"
                    :key="tab.key"
                    @click="activeTab = tab.key"
                    :class="[
                      'shrink-0 border-b-2 px-1 pb-3 text-sm font-medium transition-colors',
                      activeTab === tab.key
                        ? 'border-primary text-primary font-semibold'
                        : 'border-transparent text-text-light hover:border-text-dark hover:text-white'
                    ]"
                  >
                    {{ $t(tab.label) }}
                  </button>
                </nav>
              </div>

              <!-- 标签页内容 -->
              <div v-if="activeTab === 'overview'">
                <h3 class="text-lg font-semibold mb-3 text-white">{{ $t('alerts.detail.alertInfo') }}</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4 text-sm">
                  <div class="space-y-1">
                    <p class="text-text-light">{{ $t('alerts.detail.timestamp') }}</p>
                    <p class="font-medium text-white">{{ alert?.timestamp || '-' }}</p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-text-light">{{ $t('alerts.detail.status') }}</p>
                    <p class="font-medium text-white">{{ alert?.status || '-' }}</p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-text-light">{{ $t('alerts.detail.ruleName') }}</p>
                    <p class="font-medium text-white">{{ alert?.ruleName || '-' }}</p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-text-light">{{ $t('alerts.detail.owner') }}</p>
                    <p class="font-medium text-white">{{ alert?.owner || $t('alerts.detail.unassigned') }}</p>
                  </div>
                </div>
              </div>

              <div v-if="activeTab === 'comments'">
                <h3 class="text-lg font-semibold mb-4 text-white">{{ $t('alerts.detail.comments') }}</h3>
                <div class="space-y-6">
                  <div
                    v-for="comment in alert?.comments || []"
                    :key="comment.id"
                    class="flex items-start gap-4"
                  >
                    <div
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
                      :class="getAvatarColor(comment.authorInitials)"
                    >
                      <span class="font-bold text-white">{{ comment.authorInitials }}</span>
                    </div>
                    <div class="flex-1">
                      <div class="flex items-baseline gap-2">
                        <p class="font-semibold text-white">{{ comment.author }}</p>
                        <p class="text-xs text-text-light">{{ comment.time }}</p>
                      </div>
                      <div class="mt-1 text-sm text-[#c3d3e8] bg-[#2a3546] p-3 rounded-lg rounded-tl-none">
                        {{ comment.content }}
                      </div>
                    </div>
                  </div>
                  <div v-if="!alert?.comments || alert.comments.length === 0" class="text-text-light text-sm">
                    {{ $t('common.noComments') || 'No comments yet' }}
                  </div>
                </div>
              </div>
            </main>

            <!-- 侧边栏 -->
            <aside class="w-80 border-l border-border-dark p-6 space-y-8 bg-[#1f2937]/20 overflow-y-auto">
              <!-- 关联实体 -->
              <div class="space-y-4" v-if="alert?.associatedEntities">
                <h3 class="text-base font-semibold text-white">{{ $t('alerts.detail.associatedEntities') }}</h3>
                <div class="space-y-3">
                  <div
                    v-for="(entity, index) in alert.associatedEntities"
                    :key="index"
                    class="flex items-center gap-3 p-3 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] cursor-pointer transition-colors"
                  >
                    <span class="material-symbols-outlined text-primary">
                      {{ getEntityIcon(entity.type) }}
                    </span>
                    <div class="text-sm">
                      <p class="font-medium text-white">{{ entity.name }}</p>
                      <p class="text-text-light">{{ entity.label }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 事件时间线 -->
              <div class="space-y-4" v-if="alert?.timeline">
                <h3 class="text-base font-semibold text-white">{{ $t('alerts.detail.eventTimeline') }}</h3>
                <div class="relative pl-6">
                  <div class="absolute left-0 h-full w-0.5 bg-border-dark"></div>
                  <div class="relative space-y-6">
                    <div
                      v-for="(event, index) in alert.timeline"
                      :key="index"
                      class="relative"
                    >
                      <div
                        :class="[
                          'absolute -left-7 top-1.5 h-2 w-2 rounded-full ring-4 ring-panel-dark',
                          index === 0 ? 'bg-primary' : 'bg-border-dark'
                        ]"
                      ></div>
                      <p class="text-xs text-text-light">{{ event.time }}</p>
                      <p class="text-sm text-white">{{ event.event }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 自动化响应 -->
              <div class="space-y-4">
                <h3 class="text-base font-semibold text-white">{{ $t('alerts.detail.automatedResponse') }}</h3>
                <div class="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                  <div class="flex items-start gap-3">
                    <span class="material-symbols-outlined text-green-400 mt-0.5">task_alt</span>
                    <div>
                      <p class="font-semibold text-white text-sm">Block IP Address</p>
                      <p class="text-xs text-green-300/80">
                        Successfully blocked {{ alert?.associatedEntities?.find(e => e.type === 'ip')?.name || 'IP' }} at firewall.
                      </p>
                    </div>
                  </div>
                </div>
                <div class="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                  <div class="flex items-start gap-3">
                    <span class="material-symbols-outlined text-yellow-400 mt-0.5">hourglass_top</span>
                    <div>
                      <p class="font-semibold text-white text-sm">Threat Intel Scan</p>
                      <p class="text-xs text-yellow-300/80">Scan in progress for related indicators...</p>
                    </div>
                  </div>
                </div>
                <button
                  class="w-full bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2 justify-center"
                >
                  <span class="material-symbols-outlined text-base">play_circle</span>
                  {{ $t('alerts.detail.runPlaybook') }}
                </button>
              </div>
            </aside>
          </div>

          <!-- 底部评论输入 -->
          <div class="sticky bottom-0 bg-panel-dark/80 backdrop-blur-sm px-6 py-4 border-t border-border-dark">
            <div class="flex items-start gap-4">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500">
                <span class="font-bold text-white">ME</span>
              </div>
              <div class="relative flex-1">
                <textarea
                  v-model="newComment"
                  class="w-full rounded-lg border border-border-dark bg-[#2a3546] p-3 pr-28 text-white placeholder:text-text-light focus:border-primary focus:ring-primary text-sm resize-none"
                  :placeholder="$t('alerts.detail.addComment')"
                  rows="2"
                ></textarea>
                <button
                  @click="handleAddComment"
                  class="absolute bottom-2.5 right-3 flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-blue-500"
                >
                  <span class="material-symbols-outlined text-base">send</span>
                  <span>{{ $t('common.submit') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getAlertDetail } from '@/api/alerts'

const props = defineProps({
  alertId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['close'])

const { t } = useI18n()

const visible = ref(false)
const alert = ref(null)
const activeTab = ref('overview')
const newComment = ref('')

const tabs = [
  { key: 'overview', label: 'alerts.detail.overview' },
  { key: 'relatedLogs', label: 'alerts.detail.relatedLogs' },
  { key: 'threatIntelligence', label: 'alerts.detail.threatIntelligence' },
  { key: 'comments', label: 'alerts.detail.comments' }
]

const loadAlertDetail = async () => {
  try {
    const response = await getAlertDetail(props.alertId)
    alert.value = response.data
    // 延迟显示以触发动画
    setTimeout(() => {
      visible.value = true
    }, 10)
  } catch (error) {
    console.error('Failed to load alert detail:', error)
    emit('close')
  }
}

const handleClose = () => {
  visible.value = false
  setTimeout(() => {
    emit('close')
  }, 300)
}

const handleCloseAlert = () => {
  // TODO: 实现关闭告警的逻辑
  console.log('Close alert:', props.alertId)
  handleClose()
}

const handleAddComment = () => {
  if (!newComment.value.trim()) return
  
  // TODO: 实现添加评论的逻辑
  if (!alert.value.comments) {
    alert.value.comments = []
  }
  
  alert.value.comments.unshift({
    id: Date.now(),
    author: 'Current User',
    authorInitials: 'CU',
    time: 'Just now',
    content: newComment.value
  })
  
  newComment.value = ''
}

const getSeverityClass = (severity) => {
  const classes = {
    high: 'bg-red-500/10 text-red-400',
    medium: 'bg-orange-500/10 text-orange-400',
    low: 'bg-blue-500/10 text-blue-400'
  }
  return classes[severity] || classes.low
}

const getAvatarColor = (initials) => {
  const colors = ['bg-slate-500', 'bg-purple-500', 'bg-blue-500', 'bg-green-500']
  const index = initials.charCodeAt(0) % colors.length
  return colors[index]
}

const getEntityIcon = (type) => {
  const icons = {
    host: 'computer',
    ip: 'public',
    user: 'person'
  }
  return icons[type] || 'help'
}

watch(() => props.alertId, () => {
  if (props.alertId) {
    loadAlertDetail()
  }
}, { immediate: true })

onMounted(() => {
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
})

// 组件卸载时恢复滚动
onUnmounted(() => {
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
</style>

