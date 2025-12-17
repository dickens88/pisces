<template>
  <div class="w-full relative overflow-x-hidden">
    <!-- 加载遮罩层 -->
    <div
      v-if="loadingVulnerability"
      class="absolute inset-0 bg-white/80 dark:bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
    >
      <div class="flex flex-col items-center gap-4">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
        </div>
        <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
      </div>
    </div>
    <!-- 面包屑导航和操作按钮 -->
    <nav class="mb-5 flex items-center justify-between gap-4 flex-wrap">
      <ol class="flex items-center gap-2.5 text-sm">
        <li>
          <router-link
            to="/vulnerabilities"
            class="inline-flex items-center gap-1.5 text-gray-500 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors duration-200 font-medium"
          >
            <span class="material-symbols-outlined text-base">folder</span>
            <span>{{ $t('vulnerabilities.title') || '漏洞管理' }}</span>
          </router-link>
        </li>
        <li class="flex items-center text-gray-300 dark:text-gray-600">
          <span class="material-symbols-outlined text-lg">chevron_right</span>
        </li>
        <li class="flex items-center gap-2">
          <span class="text-gray-400 dark:text-gray-500 font-medium">ID:</span>
          <span class="text-gray-900 dark:text-white font-semibold font-mono text-sm bg-gray-100 dark:bg-slate-700/50 px-2.5 py-1 rounded-md border border-gray-200 dark:border-slate-600">
            {{ route.params.id || '--' }}
          </span>
        </li>
      </ol>
      <div class="flex gap-3 flex-wrap justify-end min-w-max">
        <button
          @click="openEditDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 text-gray-700 dark:text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">edit</span>
          <span class="truncate">{{ $t('vulnerabilities.detail.edit') || '编辑' }}</span>
        </button>
        <button
          @click="openCloseDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">archive</span>
          <span class="truncate">{{ $t('vulnerabilities.detail.closeVulnerability') || '关闭' }}</span>
        </button>
        <button
          @click="handleRefresh"
          :disabled="loadingVulnerability"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingVulnerability }"
          >
            refresh
          </span>
        </button>
        <button
          @click="handleShare"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center h-10"
          :title="$t('vulnerabilities.detail.share') || 'Share'"
        >
          <span class="material-symbols-outlined text-base">share</span>
        </button>
      </div>
    </nav>
    <!-- 页面标题 -->
    <header class="flex flex-col gap-2 mb-6">
      <h1 class="text-gray-900 dark:text-white text-xl font-bold leading-tight tracking-tight">
        {{ vulnerability?.title || vulnerability?.name || 'CVE-' + route.params.id }}
      </h1>
      <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-gray-600 dark:text-slate-400 text-sm font-normal leading-normal">
        <div class="flex items-center gap-1.5">
          <span>{{ $t('vulnerabilities.detail.actor') }}:</span>
          <span class="text-gray-900 dark:text-white">{{ vulnerability?.actor || '-' }}</span>
        </div>
        <div class="h-4 w-px bg-slate-600/50"></div>
        <div class="flex items-center gap-1.5">
          <span>{{ $t('vulnerabilities.detail.createTime') || 'Create Time' }}:</span>
          <span class="text-gray-900 dark:text-white">{{ formatDateTime(vulnerability?.createTime || vulnerability?.create_time) }}</span>
        </div>
        <div class="h-4 w-px bg-slate-600/50"></div>
        <div class="flex items-center gap-1.5">
          <span>{{ $t('vulnerabilities.detail.closeTime') }}:</span>
          <span class="text-gray-900 dark:text-white">{{ formatDateTime(vulnerability?.closeTime || vulnerability?.close_time) }}</span>
        </div>
        <div class="h-4 w-px bg-slate-600/50"></div>
        <div class="flex items-center gap-1.5">
          <span>{{ $t('vulnerabilities.detail.updateTime') || 'Update Time' }}:</span>
          <span class="text-gray-900 dark:text-white">{{ formatDateTime(vulnerability?.updateTime || vulnerability?.update_time) }}</span>
        </div>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700">
        <p class="text-gray-600 dark:text-slate-300 text-sm font-medium leading-normal">
          {{ $t('vulnerabilities.detail.statusLabel') || 'Status' }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getStatusDotClass(vulnerability?.status || vulnerability?.handle_status)
            ]"
          ></span>
          <p class="text-gray-900 dark:text-white text-xl font-bold leading-tight">
            {{ getStatusText(vulnerability?.status || vulnerability?.handle_status) }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700">
        <p class="text-gray-600 dark:text-slate-300 text-sm font-medium leading-normal">
          {{ $t('vulnerabilities.detail.riskLevel') || 'Risk Level' }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getSeverityDotClass(vulnerability?.severity || vulnerability?.riskLevel)
            ]"
          ></span>
          <p
            :class="[
              'text-xl font-bold leading-tight',
              getSeverityTextClass(vulnerability?.severity || vulnerability?.riskLevel)
            ]"
          >
            {{ severityToNumber(vulnerability?.severity || vulnerability?.riskLevel) || '-' }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700">
        <p class="text-gray-600 dark:text-slate-300 text-sm font-medium leading-normal">
          {{ $t('vulnerabilities.detail.responsibleDepartment') || 'Responsible Department' }}
        </p>
        <p class="text-gray-900 dark:text-white text-xl font-bold leading-tight">
          {{ vulnerability?.responsibleDept || vulnerability?.responsible_dept || '-' }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700">
        <p class="text-gray-600 dark:text-slate-300 text-sm font-medium leading-normal">
          {{ $t('vulnerabilities.edit.cloudService') || 'Cloud Service' }}
        </p>
        <p class="text-gray-900 dark:text-white text-xl font-bold leading-tight">
          {{ vulnerability?.cloudService || vulnerability?.cloud_service || '-' }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700">
        <p class="text-gray-600 dark:text-slate-300 text-sm font-medium leading-normal">
          {{ $t('vulnerabilities.detail.responsiblePerson') || 'Responsible Person' }}
        </p>
        <p class="text-gray-900 dark:text-white text-xl font-bold leading-tight">
          {{ vulnerability?.owner || vulnerability?.responsiblePerson || '-' }}
        </p>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="mt-8 border-b border-slate-700">
      <nav aria-label="Tabs" class="flex -mb-px space-x-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.key
              ? 'text-primary border-primary'
              : 'text-slate-400 hover:text-white border-transparent'
          ]"
        >
          {{ $t(tab.label) }}
        </button>
      </nav>
    </div>

    <!-- 标签页内容 -->
    <div class="mt-6 flex-grow">
      <!-- Overview 标签页 -->
      <div v-if="activeTab === 'overview'" class="flex flex-col gap-6">
        <!-- 漏洞描述 -->
        <div class="bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-gray-900 dark:text-white font-bold text-lg">
              {{ $t('vulnerabilities.detail.description') || 'Description' }}
            </h3>
          </div>
          <div class="overflow-x-hidden">
            <p class="text-gray-600 dark:text-slate-300 leading-relaxed whitespace-pre-wrap break-all vulnerability-description-text">
              {{ vulnerability?.description || vulnerability?.aiAnalysis?.description || $t('vulnerabilities.detail.noDescription') || 'No description available.' }}
            </p>
          </div>
        </div>

        <!-- 关联告警 -->
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl">
          <div class="p-6 border-b border-gray-200 dark:border-[#324867] flex items-center justify-between">
            <h3 class="text-gray-900 dark:text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.associatedAlerts') || 'Associated Alerts' }}
            </h3>
            <button
              :disabled="selectedAlerts.length === 0"
              @click="openDisassociateDialog"
              class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-200 dark:bg-[#233348] text-gray-700 dark:text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 dark:hover:bg-[#324867] transition-colors"
            >
              <span class="material-symbols-outlined text-base">link_off</span>
              <span>{{ $t('incidents.detail.disassociate') || 'Disassociate' }}</span>
            </button>
          </div>
          <DataTable
            ref="associatedAlertsTableRef"
            :columns="associatedAlertsColumns"
            :items="formattedAssociatedAlerts"
            :selectable="true"
            :resizable="true"
            storage-key="vulnerability-associated-alerts-table-columns"
            :default-widths="associatedAlertsDefaultWidths"
            :pagination="false"
            @select="handleSelectAlerts"
            @select-all="handleSelectAlerts"
          >
            <template #cell-createTime="{ value }">
              {{ formatDateTime(value) }}
            </template>
            <template #cell-alertTitle="{ item }">
              <div class="flex items-center gap-2">
                <button
                  @click.stop="openAlertDetailInNewWindow(item.id)"
                  class="flex-shrink-0 text-gray-400 hover:text-primary transition-colors p-1"
                  :title="$t('alerts.list.openInNewWindow') || '在新窗口打开'"
                >
                  <span class="material-symbols-outlined text-base">open_in_new</span>
                </button>
                <a
                  @click="openAlertDetail(item.id)"
                  class="text-primary hover:underline cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap flex-1 font-medium"
                  :title="item.title"
                >
                  {{ item.title }}
                </a>
              </div>
            </template>
            <template #cell-riskLevel="{ item }">
              <span
                :class="[
                  'text-xs font-medium me-2 px-2.5 py-0.5 rounded-full inline-block',
                  getRiskLevelClass(item.riskLevel)
                ]"
                :title="$t(`common.severity.${item.riskLevel}`)"
              >
                {{ $t(`common.severity.${item.riskLevel}`) }}
              </span>
            </template>
            <template #cell-status="{ item }">
              <span
                :class="[
                  'inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium',
                  getStatusClass(item.status)
                ]"
                :title="$t(`alerts.list.${item.status}`)"
              >
                <span :class="['size-1.5 rounded-full', getStatusDotClass(item.status)]"></span>
                {{ $t(`alerts.list.${item.status}`) }}
              </span>
            </template>
            <template #cell-owner="{ value }">
              <div class="flex justify-center w-full">
                <UserAvatar :name="value" />
              </div>
            </template>
          </DataTable>
        </div>
      </div>

      <!-- Comments 标签页 -->
      <div v-if="activeTab === 'comments'" class="flex-grow">
        <div class="bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 rounded-lg flex flex-col">
          <div class="p-6 pt-4 overflow-x-hidden">
            <CommentSection
              :comments="vulnerability?.comments || []"
              @submit="handlePostComment"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 关闭漏洞对话框 -->
    <CloseIncidentDialog
      ref="closeDialogRef"
      :visible="showCloseDialog"
      :title="$t('vulnerabilities.detail.closeDialog.title') || '关闭漏洞'"
      :confirm-message="$t('vulnerabilities.detail.closeDialog.confirmMessage') || '确认要关闭此漏洞吗？'"
      @close="closeCloseDialog"
      @submit="handleCloseVulnerability"
    />

    <!-- 编辑漏洞对话框 -->
    <EditVulnerabilityDialog
      :visible="showEditDialog"
      :vulnerability-id="route.params.id"
      :initial-data="editVulnerabilityInitialData"
      @close="closeEditDialog"
      @updated="handleVulnerabilityUpdated"
    />

    <!-- ASM 告警详情抽屉（关联漏洞的告警使用 ASM 风格详情） -->
    <ASMDetail
      v-if="selectedAlertId"
      :alert-id="selectedAlertId"
      @close="closeAlertDetail"
    />

    <!-- 解关联确认对话框 -->
    <div
      v-if="showDisassociateDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeDisassociateDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('incidents.detail.disassociateDialog.title') || 'Disassociate Alerts' }}
          </h2>
          <button
            @click="closeDisassociateDialog"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-6 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('incidents.detail.disassociateDialog.confirmMessage', { count: selectedAlerts.length }) || `确认要解关联 ${selectedAlerts.length} 个告警吗？` }}
          </p>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeDisassociateDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleDisassociate"
            :disabled="isDisassociating"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isDisassociating" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('incidents.detail.disassociate') || 'Disassociate' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 分享成功提示 -->
    <Transition name="fade">
      <div
        v-if="showShareSuccess"
        class="fixed top-4 right-4 z-[100] bg-green-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center gap-2"
      >
        <span class="material-symbols-outlined text-sm">check_circle</span>
        <span class="text-sm">{{ $t('vulnerabilities.detail.shareSuccess') || '已复制到剪切板' }}</span>
      </div>
    </Transition>

    <!-- AI Sidebar -->
    <AISidebar
      :visible="showAISidebar"
      :alert-title="currentTitle"
      :finding-summary="findingSummary"
      :alert-id="route.params.id"
      @close="showAISidebar = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { getVulnerabilityDetail } from '@/api/vulnerabilities'
import { postComment } from '@/api/comments'
import { disassociateAlertsFromIncident } from '@/api/incidents'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import EditVulnerabilityDialog from '@/components/vulnerabilities/EditVulnerabilityDialog.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import ASMDetail from '@/components/asm/ASMDetail.vue'
import DataTable from '@/components/common/DataTable.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import AISidebar from '@/components/common/AISidebar.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import { severityToNumber } from '@/utils/severity'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const toast = useToast()
const authStore = useAuthStore()

const vulnerability = ref(null)
const loadingVulnerability = ref(false)
const activeTab = ref('overview')
const showCloseDialog = ref(false)
const isClosingVulnerability = ref(false)
const closeDialogRef = ref(null)
const showEditDialog = ref(false)
const editVulnerabilityInitialData = ref(null)
const showShareSuccess = ref(false)
const selectedAlerts = ref([])
const associatedAlertsTableRef = ref(null)
const showDisassociateDialog = ref(false)
const isDisassociating = ref(false)
const selectedAlertId = ref(null)
const showAISidebar = ref(false)
const currentTitle = ref('')
const findingSummary = ref('')

const tabs = [
  { key: 'overview', label: 'vulnerabilities.detail.tabs.overview' },
  { key: 'comments', label: 'vulnerabilities.detail.tabs.comments' }
]

const loadVulnerabilityDetail = async ({ silent = false } = {}) => {
  if (!silent) {
    loadingVulnerability.value = true
  }
  try {
    const vulnerabilityId = route.params.id
    const response = await getVulnerabilityDetail(vulnerabilityId)
    const data = response.data
    
    // 格式化数据，将后端字段映射到前端使用的字段
    vulnerability.value = {
      id: data.id,
      title: data.title,
      name: data.title,
      createTime: data.create_time,
      updateTime: data.update_time,
      closeTime: data.close_time,
      create_time: data.create_time,
      update_time: data.update_time,
      close_time: data.close_time,
      arrive_time: data.arrive_time,
      handle_status: data.handle_status,
      status: data.handle_status,
      severity: data.severity,
      riskLevel: data.severity,
      owner: data.owner,
      actor: data.actor,
      responsiblePerson: data.owner,
      responsibleDept: data.responsible_dept || '',
      responsible_dept: data.responsible_dept,
      cloudService: data.cloud_service,
      cloud_service: data.cloud_service,
      rootCause: data.root_cause,
      root_cause: data.root_cause,
      description: data.description || data.title,
      aiAnalysis: data.ai_analysis || data.aiAnalysis,
      // 格式化评论数据
      comments: formatComments(data.comments || []),
      // 关联告警（如果有）
      associatedAlerts: data.associated_alerts || data.associatedAlerts || []
    }
  } catch (error) {
    console.error('Failed to load vulnerability detail:', error)
    router.push('/vulnerabilities')
  } finally {
    if (!silent) {
      loadingVulnerability.value = false
    }
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
      file: comment.file || null
    }
  })
}

const handlePostComment = async ({ comment, files }) => {
  if (!vulnerability.value?.id) {
    toast.error(t('vulnerabilities.detail.commentError') || '无法提交评论：漏洞ID不存在', 'ERROR')
    return
  }
  
  try {
    const commentText = comment.trim()
    if (!commentText && (!files || files.length === 0)) {
      return
    }
    
    await postComment(vulnerability.value.id, commentText, files || [], 'asm')
    
    await loadVulnerabilityDetail()
    
    toast.success(t('vulnerabilities.detail.commentSuccess') || '评论提交成功', 'SUCCESS')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('vulnerabilities.detail.commentError') || '评论提交失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  }
}

const getStatusText = (status) => {
  if (!status) return t('vulnerabilities.detail.status.open') || 'Open'
  const statusLower = status.toLowerCase()
  const statusMap = {
    'open': t('vulnerabilities.detail.status.open') || 'Open',
    'block': t('vulnerabilities.detail.status.inProgress') || 'In Progress',
    'closed': t('vulnerabilities.detail.status.patched') || 'Patched'
  }
  return statusMap[statusLower] || status
}

const getStatusDotClass = (status) => {
  const statusLower = (status || '').toLowerCase()
  const classes = {
    open: 'bg-amber-400',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[statusLower] || classes.open
}

const getStatusClass = (status) => {
  const statusLower = (status || '').toLowerCase()
  const classes = {
    open: 'bg-primary/20 text-primary',
    block: 'bg-yellow-500/20 text-yellow-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[statusLower] || classes.open
}

const getSeverityDotClass = (severity) => {
  const classes = {
    high: 'bg-red-500',
    medium: 'bg-orange-500',
    low: 'bg-blue-500'
  }
  return classes[severity] || classes.low
}

const getSeverityTextClass = (severity) => {
  const classes = {
    high: 'text-red-400',
    medium: 'text-orange-400',
    low: 'text-blue-400'
  }
  return classes[severity] || classes.low
}

const getVulnerabilityUrl = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  let basePath = '/'
  if (raw && raw !== '/') {
    basePath = raw.startsWith('/') ? raw : `/${raw}`
    basePath = basePath.replace(/\/$/, '')
  }
  const origin = window.location.origin
  const vulnerabilityId = route.params.id
  const path = basePath === '/' ? '/vulnerabilities' : `${basePath}/vulnerabilities`
  return `${origin}${path}/${vulnerabilityId}`
}

const handleShare = async () => {
  if (!vulnerability.value) return
  
  const title = vulnerability.value.title || vulnerability.value.name || ''
  const url = getVulnerabilityUrl()
  const textToCopy = `${title}: ${url}`
  
  try {
    await navigator.clipboard.writeText(textToCopy)
    showShareSuccess.value = true
    setTimeout(() => {
      showShareSuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    const textArea = document.createElement('textarea')
    textArea.value = textToCopy
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      showShareSuccess.value = true
      setTimeout(() => {
        showShareSuccess.value = false
      }, 2000)
    } catch (fallbackErr) {
      console.error('Fallback copy failed:', fallbackErr)
    }
    document.body.removeChild(textArea)
  }
}

const handleRefresh = async () => {
  await loadVulnerabilityDetail()
}

const openCloseDialog = () => {
  showCloseDialog.value = true
}

const closeCloseDialog = () => {
  showCloseDialog.value = false
}

const handleCloseVulnerability = async (data) => {
  if (isClosingVulnerability.value) {
    return
  }

  try {
    isClosingVulnerability.value = true
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(true)
    }
    
    const body = {
      handle_status: 'Closed',
      close_reason: data.close_reason,
      close_comment: data.close_comment,
      search_vulscan: true
    }

    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/vulnerabilities/${route.params.id}?workspace=asm` : `/api/vulnerabilities/${route.params.id}?workspace=asm`
    
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    await axios.put(url, body, { headers })
    
    toast.success(t('vulnerabilities.detail.closeSuccess') || '漏洞关闭成功', 'SUCCESS')
    
    closeCloseDialog()
    
    await loadVulnerabilityDetail()
  } catch (error) {
    console.error('Failed to close vulnerability:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('vulnerabilities.detail.closeError') || '漏洞关闭失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isClosingVulnerability.value = false
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(false)
    }
  }
}

const openEditDialog = () => {
  if (!vulnerability.value) {
    console.warn('Vulnerability data not loaded')
    return
  }
  
  editVulnerabilityInitialData.value = {
    title: vulnerability.value.title || vulnerability.value.name || '',
    status: vulnerability.value.status || vulnerability.value.handle_status || 'Open',
    severity: vulnerability.value.severity || 'low',
    create_time: vulnerability.value.createTime || vulnerability.value.create_time || null,
    close_time: vulnerability.value.closeTime || vulnerability.value.close_time || null,
    owner: vulnerability.value.owner || '',
    responsibleDepartment: vulnerability.value.responsibleDept || vulnerability.value.responsible_dept || '',
    cloud_service: vulnerability.value.cloudService || vulnerability.value.cloud_service || null,
    actor: vulnerability.value.actor || '',
    description: vulnerability.value.description || ''
  }
  
  nextTick(() => {
    showEditDialog.value = true
  })
}

const closeEditDialog = () => {
  showEditDialog.value = false
  editVulnerabilityInitialData.value = null
}

const handleVulnerabilityUpdated = async () => {
  closeEditDialog()
  await loadVulnerabilityDetail()
}

// Associated Alerts 相关函数
const associatedAlertsColumns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'owner', label: t('alerts.list.owner') }
])

const associatedAlertsDefaultWidths = {
  createTime: 180,
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  owner: 50
}

const formattedAssociatedAlerts = computed(() => {
  if (!vulnerability.value?.associatedAlerts) {
    return []
  }
  return vulnerability.value.associatedAlerts.map(alert => {
    // 转换 severity 为 riskLevel (需要转换为小写)
    const severityMap = {
      'Critical': 'fatal',
      'High': 'high',
      'Medium': 'medium',
      'Low': 'low',
      'Tips': 'tips'
    }
    const riskLevel = alert.severity 
      ? (severityMap[alert.severity] || alert.severity.toLowerCase())
      : 'low'
    
    // 转换 handle_status 为 status (需要转换为小写)
    const statusMap = {
      'Open': 'open',
      'Block': 'block',
      'Closed': 'closed'
    }
    const status = alert.handle_status
      ? (statusMap[alert.handle_status] || alert.handle_status.toLowerCase())
      : 'open'
    
    return {
      id: alert.id,
      createTime: alert.create_time || alert.createTime || '-',
      title: alert.title || '-',
      riskLevel: riskLevel,
      status: status,
      owner: alert.owner || '-'
    }
  })
})

const getRiskLevelClass = (level) => {
  const classes = {
    fatal: 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-200',
    high: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    medium: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
    low: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    tips: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
  }
  return classes[level] || classes.low
}

const handleSelectAlerts = (items) => {
  selectedAlerts.value = items.map(alert => alert.id)
}

const openDisassociateDialog = () => {
  showDisassociateDialog.value = true
}

const closeDisassociateDialog = () => {
  showDisassociateDialog.value = false
}

const handleDisassociate = async () => {
  if (selectedAlerts.value.length === 0 || isDisassociating.value) {
    return
  }

  try {
    isDisassociating.value = true
    
    // 调用解关联接口（使用事件解关联接口，因为漏洞和事件使用相同的关联机制）
    await disassociateAlertsFromIncident(route.params.id, selectedAlerts.value)
    
    toast.success(
      t('incidents.detail.disassociateSuccess', { count: selectedAlerts.value.length }) || 
      `成功解关联 ${selectedAlerts.value.length} 个告警`,
      'SUCCESS'
    )
    
    closeDisassociateDialog()
    selectedAlerts.value = []
    associatedAlertsTableRef.value?.clearSelection()
    await loadVulnerabilityDetail()
  } catch (error) {
    console.error('Failed to disassociate alerts:', error)
    const errorMessage = error?.response?.data?.message || 
                        error?.response?.data?.error_message || 
                        error?.message || 
                        t('incidents.detail.disassociateError') || '解关联失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isDisassociating.value = false
  }
}

const openAlertDetail = (alertId) => {
  selectedAlertId.value = alertId
}

const openAlertDetailInNewWindow = (alertId) => {
  // 在新窗口打开告警详情
  const route = router.resolve({ path: `/alerts/${alertId}` })
  // 构建完整的 URL
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const closeAlertDetail = () => {
  selectedAlertId.value = null
}

const handleOpenAISidebar = () => {
  if (vulnerability.value) {
    currentTitle.value = vulnerability.value.title || vulnerability.value.name || ''
    findingSummary.value = vulnerability.value.description || vulnerability.value.aiAnalysis?.description || ''
  } else {
    currentTitle.value = ''
    findingSummary.value = ''
  }
  showAISidebar.value = true
}

onMounted(() => {
  loadVulnerabilityDetail()
  // 监听Header发出的打开AI侧边栏事件
  window.addEventListener('open-ai-sidebar', handleOpenAISidebar)
})

onBeforeUnmount(() => {
  window.removeEventListener('open-ai-sidebar', handleOpenAISidebar)
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

.vulnerability-description-text {
  word-break: break-all;
  overflow-wrap: anywhere;
  max-width: 100%;
}
</style>
