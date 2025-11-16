<template>
  <div class="w-full relative overflow-x-hidden">
    <!-- 加载遮罩层 -->
    <div
      v-if="loadingVulnerability"
      class="absolute inset-0 bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
    >
      <div class="flex flex-col items-center gap-4">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
        </div>
        <p class="text-gray-400 text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
      </div>
    </div>

    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap justify-between items-start gap-4 mb-6">
      <div class="flex flex-col gap-2">
        <h1 class="text-white text-3xl font-black leading-tight tracking-tight">
          {{ vulnerability?.title || vulnerability?.name || 'CVE-' + route.params.id }}
        </h1>
        <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-slate-400 text-base font-normal leading-normal">
          <div class="flex items-center gap-1.5">
            <span>{{ $t('vulnerabilities.detail.assignee') || 'Assignee' }}:</span>
            <span class="text-white">{{ vulnerability?.owner || '-' }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('vulnerabilities.detail.discoveredTime') || 'Discovered Time' }}:</span>
            <span class="text-white">{{ formatDateTime(vulnerability?.arrive_time || vulnerability?.create_time || vulnerability?.occurrenceTime || vulnerability?.occurrence_time) }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- 左侧主要内容 -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        <!-- Overview 部分 -->
        <section class="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 class="text-white font-bold text-lg mb-4">
            {{ $t('vulnerabilities.detail.overview') || 'Overview' }}
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
            <div class="flex flex-col gap-1">
              <p class="text-slate-400 text-sm font-normal leading-normal">
                {{ $t('vulnerabilities.detail.discoveredTime') || 'Discovered Time' }}
              </p>
              <p class="text-slate-300 text-sm font-normal leading-normal">
                {{ formatDateTime(vulnerability?.arrive_time || vulnerability?.create_time || vulnerability?.occurrenceTime || vulnerability?.occurrence_time) }}
              </p>
            </div>
            <div class="flex flex-col gap-1">
              <p class="text-slate-400 text-sm font-normal leading-normal">
                {{ $t('vulnerabilities.detail.assignee') || 'Assignee' }}
              </p>
              <p class="text-slate-300 text-sm font-normal leading-normal">
                {{ vulnerability?.owner || '-' }}
              </p>
            </div>
            <div class="flex flex-col gap-1">
              <p class="text-slate-400 text-sm font-normal leading-normal">
                {{ $t('vulnerabilities.detail.assigneeDepartment') || "Assignee's Department" }}
              </p>
              <p class="text-slate-300 text-sm font-normal leading-normal">
                {{ vulnerability?.responsible_dept || vulnerability?.responsibleDepartment || '-' }}
              </p>
            </div>
            <div class="flex flex-col gap-1">
              <p class="text-slate-400 text-sm font-normal leading-normal">
                {{ $t('vulnerabilities.detail.riskLevel') || 'Risk Level' }}
              </p>
              <div class="flex items-center">
                <span
                  :class="[
                    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
                    getRiskLevelClass(vulnerability?.severity || vulnerability?.riskLevel)
                  ]"
                >
                  {{ $t(`common.severity.${(vulnerability?.severity || vulnerability?.riskLevel || 'low').toLowerCase()}`) }}
                </span>
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <p class="text-slate-400 text-sm font-normal leading-normal">
                {{ $t('vulnerabilities.detail.rootCause') || 'Root Cause' }}
              </p>
              <p class="text-slate-300 text-sm font-normal leading-normal">
                {{ vulnerability?.root_cause || vulnerability?.rootCause || '-' }}
              </p>
            </div>
            <div class="flex flex-col gap-1">
              <p class="text-slate-400 text-sm font-normal leading-normal">
                {{ $t('vulnerabilities.detail.fixStatus') || 'Fix Status' }}
              </p>
              <div class="flex items-center gap-2">
                <span
                  :class="[
                    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
                    getFixStatusClass(vulnerability?.handle_status || vulnerability?.status)
                  ]"
                >
                  {{ getFixStatusText(vulnerability?.handle_status || vulnerability?.status) }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Description 部分 -->
        <section class="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 class="text-white font-bold text-lg mb-4">
            {{ $t('vulnerabilities.detail.description') || 'Description' }}
          </h3>
          <div class="overflow-x-hidden">
            <p class="text-slate-300 leading-relaxed whitespace-pre-wrap break-all">
              {{ vulnerability?.description || vulnerability?.aiAnalysis?.description || $t('vulnerabilities.detail.noDescription') || 'No description available.' }}
            </p>
          </div>
        </section>
      </div>

      <!-- 右侧时间线 -->
      <div class="lg:col-span-1">
        <section class="bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex flex-col h-[600px] lg:h-auto">
          <h3 class="text-white font-bold text-lg mb-4">
            {{ $t('vulnerabilities.detail.lifecycle') || 'Vulnerability Lifecycle' }}
          </h3>
          <div class="flex-grow relative overflow-y-auto pr-2">
            <div
              v-for="(event, index) in lifecycleEvents"
              :key="index"
              class="flex gap-4"
            >
              <div class="flex flex-col items-center">
                <div
                  :class="[
                    'flex items-center justify-center size-8 rounded-full',
                    getTimelineIconBgClass(event.severity)
                  ]"
                >
                  <span
                    :class="[
                      'material-symbols-outlined text-base',
                      getTimelineIconColorClass(event.severity)
                    ]"
                  >
                    {{ event.icon }}
                  </span>
                </div>
                <div
                  v-if="index < lifecycleEvents.length - 1"
                  class="w-px h-full bg-slate-700 my-2"
                ></div>
              </div>
              <div class="pb-8 flex-1">
                <p class="text-sm text-slate-400">{{ formatDateTime(event.time) }}</p>
                <p class="font-medium text-white">{{ event.title }}</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Comments 部分 -->
    <div class="mt-6">
      <div class="bg-slate-800/50 border border-slate-700 rounded-lg flex flex-col">
        <div class="p-6 pt-4 overflow-x-hidden">
          <CommentSection
            :comments="formattedComments"
            :title="$t('vulnerabilities.detail.comments') || 'Comments'"
            @submit="handlePostComment"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { getIncidentDetail } from '@/api/incidents'
import { postComment } from '@/api/comments'
import CommentSection from '@/components/common/CommentSection.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const vulnerability = ref(null)
const loadingVulnerability = ref(false)
const comments = ref([])
const newComment = ref('')
const isPostingComment = ref(false)

// 加载漏洞详情
const loadVulnerabilityDetail = async () => {
  loadingVulnerability.value = true
  try {
    const response = await getIncidentDetail(route.params.id)
    const data = response.data
    
    // 格式化数据，将后端字段映射到前端使用的字段
    vulnerability.value = {
      id: data.id,
      title: data.title,
      name: data.title,
      create_time: data.create_time,
      update_time: data.update_time,
      arrive_time: data.arrive_time,
      handle_status: data.handle_status,
      status: data.handle_status,
      severity: data.severity,
      riskLevel: data.severity,
      owner: data.owner,
      responsible_dept: data.responsible_dept,
      responsibleDepartment: data.responsible_dept,
      root_cause: data.root_cause,
      rootCause: data.root_cause,
      description: data.description || data.title,
      aiAnalysis: data.ai_analysis || data.aiAnalysis
    }
    
    // 格式化评论数据
    comments.value = formatComments(data.comments || [])
  } catch (error) {
    console.error('Failed to load vulnerability detail:', error)
    toast.error(
      t('vulnerabilities.detail.loadError') || '加载漏洞详情失败',
      '错误'
    )
  } finally {
    loadingVulnerability.value = false
  }
}

/**
 * @brief 格式化评论数据
 */
const formatComments = (comments) => {
  if (!comments || !Array.isArray(comments)) {
    return []
  }
  
  return comments.map((comment, index) => {
    const author = comment.author || comment.owner || 'Unknown'
    const authorWords = author.trim().split(/\s+/)
    const authorInitials = authorWords.length > 1
      ? authorWords.slice(0, 3).map(word => word.charAt(0).toUpperCase()).join('')
      : author.charAt(0).toUpperCase()
    
    // 根据作者名称生成头像颜色
    let hash = 0
    for (let i = 0; i < author.length; i++) {
      hash = author.charCodeAt(i) + ((hash << 5) - hash)
    }
    const colors = ['bg-teal-500', 'bg-blue-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500']
    const avatarColor = colors[Math.abs(hash % colors.length)]
    
    return {
      id: comment.id || index,
      author: author,
      authorInitials: authorInitials,
      avatarColor: avatarColor,
      time: formatDateTime(comment.create_time),
      content: comment.content || comment.comment || '',
      create_time: comment.create_time,
      file: comment.file || null  // 保留文件信息
    }
  })
}

// 格式化后的评论列表
const formattedComments = computed(() => comments.value)

// 生命周期事件
const lifecycleEvents = computed(() => {
  const events = []
  if (!vulnerability.value) return events

  // 添加创建事件
  if (vulnerability.value.create_time) {
    events.push({
      icon: 'event',
      title: t('vulnerabilities.detail.vulnerabilityCreated') || 'Vulnerability Created',
      time: vulnerability.value.create_time,
      severity: (vulnerability.value.severity || 'low').toLowerCase()
    })
  }

  // 如果有负责人，添加分配事件
  if (vulnerability.value.owner && vulnerability.value.arrive_time) {
    events.push({
      icon: 'person',
      title: t('vulnerabilities.detail.assignedTo') || `Assigned to ${vulnerability.value.owner}`,
      time: vulnerability.value.arrive_time,
      severity: 'low'
    })
  }

  // 如果状态是进行中，添加状态变更事件
  if (vulnerability.value.handle_status === 'Block' || vulnerability.value.status === 'block') {
    events.push({
      icon: 'priority',
      title: t('vulnerabilities.detail.statusChanged') || "Status changed to 'In Progress'",
      time: vulnerability.value.update_time || vulnerability.value.create_time,
      severity: 'medium'
    })
  }

  // 如果已关闭，添加关闭事件
  if (vulnerability.value.handle_status === 'Closed' || vulnerability.value.status === 'closed') {
    events.push({
      icon: 'check_circle',
      title: t('vulnerabilities.detail.remediationVerified') || 'Remediation Verified',
      time: vulnerability.value.update_time || vulnerability.value.create_time,
      severity: 'low'
    })
  }

  // 按时间排序（从旧到新）
  return events.sort((a, b) => {
    const timeA = new Date(a.time)
    const timeB = new Date(b.time)
    return timeA - timeB
  })
})

// 风险等级样式
const getRiskLevelClass = (level) => {
  const levelLower = (level || 'low').toLowerCase()
  const classes = {
    critical: 'bg-[#FF4D4F]/20 text-[#FF4D4F]',
    high: 'bg-red-500/20 text-red-400',
    medium: 'bg-orange-500/20 text-orange-400',
    low: 'bg-blue-500/20 text-blue-400'
  }
  return classes[levelLower] || classes.low
}

// 修复状态样式
const getFixStatusClass = (status) => {
  const statusLower = (status || 'open').toLowerCase()
  const classes = {
    closed: 'bg-green-500/20 text-green-400',
    patched: 'bg-green-500/20 text-green-400',
    open: 'bg-amber-500/20 text-amber-400',
    block: 'bg-yellow-500/20 text-yellow-400',
    inprogress: 'bg-yellow-500/20 text-yellow-400'
  }
  return classes[statusLower] || classes.open
}

// 修复状态文本
const getFixStatusText = (status) => {
  const statusLower = (status || 'open').toLowerCase()
  const statusMap = {
    closed: t('vulnerabilities.detail.status.patched') || 'Patched',
    patched: t('vulnerabilities.detail.status.patched') || 'Patched',
    open: t('vulnerabilities.detail.status.open') || 'Open',
    block: t('vulnerabilities.detail.status.inProgress') || 'In Progress',
    inprogress: t('vulnerabilities.detail.status.inProgress') || 'In Progress'
  }
  return statusMap[statusLower] || statusMap.open
}

const getTimelineIconBgClass = (severity) => {
  const classes = {
    high: 'bg-red-500/20 ring-1 ring-inset ring-red-500/30',
    medium: 'bg-amber-500/20 ring-1 ring-inset ring-amber-500/30',
    low: 'bg-slate-700'
  }
  return classes[severity] || classes.low
}

const getTimelineIconColorClass = (severity) => {
  const classes = {
    high: 'text-red-400',
    medium: 'text-amber-400',
    low: 'text-slate-300'
  }
  return classes[severity] || classes.low
}

const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}

// Note: File handling functions (getFileIcon, formatFileSize, openImageModal, downloadFile) 
// have been moved to CommentSection component

// 处理状态变更
const handleChangeStatus = () => {
  // TODO: 实现状态变更功能
  console.log('Change status')
}

// 处理分配
const handleAssign = () => {
  // TODO: 实现分配功能
  console.log('Assign')
}

// 提交评论
const handlePostComment = async ({ comment, files }) => {
  if (!vulnerability.value?.id) {
    toast.error(t('vulnerabilities.detail.commentError') || '无法提交评论：漏洞ID不存在', '操作失败')
    return
  }
  
  try {
    const commentText = comment.trim()
    // 允许只有文件没有文本的情况
    if (!commentText && (!files || files.length === 0)) {
      return
    }
    
    // 调用 API 提交评论（包含文件）
    await postComment(vulnerability.value.id, commentText, files || [])
    
    // 清空输入框（组件会自动清空）
    newComment.value = ''
    
    // 重新加载漏洞详情以获取最新评论
    await loadVulnerabilityDetail()
    
    // 显示成功提示
    toast.success(t('vulnerabilities.detail.commentSuccess') || '评论提交成功', '操作成功')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('vulnerabilities.detail.commentError') || '评论提交失败，请稍后重试'
    toast.error(errorMessage, '操作失败')
  }
}

onMounted(() => {
  loadVulnerabilityDetail()
})
</script>

<style scoped>
/* 隐藏评论输入框中的滚动条 */
.comment-input-wrapper :deep(textarea) {
  overflow-y: hidden !important;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.comment-input-wrapper :deep(textarea)::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>


