<template>
  <div class="w-full relative">
    <!-- 加载遮罩层 -->
    <div
      v-if="loadingIncident"
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
          {{ incident?.name }}
        </h1>
        <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-slate-400 text-base font-normal leading-normal">
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.eventId') }}:</span>
            <span class="text-white">{{ incident?.eventId }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.createTime') }}:</span>
            <span class="text-white">{{ formatDateTime(incident?.createTime) }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.updateTime') }}:</span>
            <span class="text-white">{{ formatDateTime(incident?.updateTime) }}</span>
          </div>
        </div>
      </div>
      <div class="flex flex-1 gap-3 flex-wrap justify-start sm:justify-end min-w-max">
        <button
          @click="openEditDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">edit</span>
          <span class="truncate">{{ $t('incidents.detail.edit') }}</span>
        </button>
        <button
          @click="openCloseDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">archive</span>
          <span class="truncate">{{ $t('incidents.detail.closeIncident') }}</span>
        </button>
        <button
          @click="handleShare"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
          :title="$t('incidents.detail.share') || 'Share'"
        >
          <span class="material-symbols-outlined text-base">share</span>
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.status') }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getIncidentStatusDotClass(incident?.status)
            ]"
          ></span>
          <p class="text-white text-xl font-bold leading-tight">
            {{ getStatusText(incident?.status) }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.severity') }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getSeverityDotClass(incident?.severity)
            ]"
          ></span>
          <p
            :class="[
              'text-xl font-bold leading-tight',
              getSeverityTextClass(incident?.severity)
            ]"
          >
            {{ $t(`common.severity.${incident?.severity?.toLowerCase()}`) }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.affectedAssets') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.affectedAssets || 0 }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.responsibleDepartment') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.extendProperties?.dataspace_name || '-' }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.responsiblePerson') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.owner || incident?.responsiblePerson || '-' }}
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
      <!-- 时间线 -->
      <div v-if="activeTab === 'timeline'" class="bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex flex-col h-[600px] lg:h-auto">
        <h3 class="text-white font-bold text-lg mb-4">
          {{ $t('incidents.detail.timeline.title') }}
        </h3>
        <div class="flex-grow relative overflow-y-auto pr-2">
          <div
            v-for="(event, index) in incident?.timeline || []"
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
                v-if="index < (incident?.timeline?.length || 0) - 1"
                class="w-px h-full bg-slate-700 my-2"
              ></div>
            </div>
            <div class="pb-8 flex-1">
              <p class="text-sm text-slate-400">{{ event.time }}</p>
              <p class="font-medium text-white">{{ event.title }}</p>
              <p class="text-sm text-slate-300 mt-1">{{ event.description }}</p>
              <a
                v-if="event.alertId"
                @click="openAlertDetail(event.alertId)"
                class="text-primary text-sm font-semibold mt-2 inline-block cursor-pointer hover:underline"
              >
                View Alert #{{ event.alertId }}
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Overview 标签页 -->
      <div v-if="activeTab === 'overview'" class="flex flex-col gap-6">
        <!-- 事件描述 -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.eventDescription') }}
            </h3>
            <button
              v-if="!isEditingDescription"
              @click="handleStartEditDescription"
              class="flex items-center justify-center size-8 rounded-md text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
              :title="$t('common.edit')"
            >
              <span class="material-symbols-outlined text-base">edit</span>
            </button>
          </div>
          <div v-if="!isEditingDescription">
            <p class="text-slate-300 leading-relaxed whitespace-pre-wrap">
              {{ incident?.description || '-' }}
            </p>
            <p v-if="incident?.descriptionLastModified" class="text-slate-500 text-xs mt-3">
              {{ $t('incidents.detail.overview.lastModified') }} {{ formatLastModified(incident.descriptionLastModified) }} {{ $t('incidents.detail.overview.by') }} {{ incident.descriptionLastModifiedBy || '-' }}
            </p>
          </div>
          <div v-else class="flex flex-col gap-3">
            <textarea
              v-model="editingDescription"
              class="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-sm text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-primary focus:border-primary transition-colors resize-none"
              :placeholder="$t('incidents.detail.overview.eventDescription')"
              rows="6"
            ></textarea>
            <div class="flex items-center gap-2 justify-end">
              <button
                @click="handleCancelEditDescription"
                class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-9 px-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
              >
                <span>{{ $t('common.cancel') }}</span>
              </button>
              <button
                @click="handleSaveDescription"
                class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-9 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
              >
                <span>{{ $t('common.save') }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 关联告警 -->
        <div class="bg-[#111822] border border-[#324867] rounded-xl">
          <div class="p-6 border-b border-[#324867]">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.associatedAlerts') }}
            </h3>
          </div>
          <DataTable
            :columns="associatedAlertsColumns"
            :items="formattedAssociatedAlerts"
            :selectable="false"
            :resizable="true"
            storage-key="incident-associated-alerts-table-columns"
            :default-widths="associatedAlertsDefaultWidths"
            :pagination="false"
          >
            <template #cell-createTime="{ value }">
              {{ value }}
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
          </DataTable>
        </div>
      </div>

      <!-- Comments 标签页 -->
      <div v-if="activeTab === 'comments'" class="flex-grow">
        <div class="bg-slate-800/50 border border-slate-700 rounded-lg flex flex-col h-[70vh] max-h-[800px]">
          <!-- 评论列表 -->
          <div class="flex-grow p-6 overflow-y-auto">
            <div class="space-y-8">
              <div
                v-for="comment in incident?.comments || []"
                :key="comment.id"
                class="flex items-start gap-4"
              >
                <div
                  :class="[
                    'flex-shrink-0 size-10 rounded-full flex items-center justify-center font-bold text-white text-base',
                    comment.avatarColor || 'bg-teal-500'
                  ]"
                >
                  <span>{{ comment.authorInitials }}</span>
                </div>
                <div class="flex-1">
                  <div class="flex items-center justify-between">
                    <p class="font-semibold text-white">{{ comment.author }}</p>
                    <p class="text-xs text-slate-400">{{ comment.time }}</p>
                  </div>
                  <div class="mt-2 text-slate-300 bg-slate-800 p-3 rounded-lg border border-slate-700">
                    <p class="text-sm leading-relaxed">{{ comment.content }}</p>
                  </div>
                </div>
              </div>
              <div v-if="!incident?.comments || incident.comments.length === 0" class="text-slate-400 text-center py-8">
                {{ $t('incidents.detail.comments.noComments') }}
              </div>
            </div>
          </div>

          <!-- 评论输入框 -->
          <div class="p-4 border-t border-slate-700 bg-slate-800/80 rounded-b-lg">
            <div class="relative">
              <textarea
                v-model="newComment"
                class="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 pr-28 text-sm text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-primary focus:border-primary transition-colors resize-none"
                :placeholder="$t('incidents.detail.comments.addComment')"
                rows="3"
              ></textarea>
              <div class="absolute right-3 bottom-3 flex items-center gap-2">
                <button
                  class="flex items-center justify-center size-8 rounded-md text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
                  :title="$t('incidents.detail.comments.attachFile')"
                >
                  <span class="material-symbols-outlined text-lg">attach_file</span>
                </button>
                <button
                  @click="handlePostComment"
                  class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-9 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
                >
                  <span>{{ $t('incidents.detail.comments.post') }}</span>
                  <span class="material-symbols-outlined text-lg">send</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- 告警详情抽屉 -->
    <AlertDetail
      v-if="selectedAlertId"
      :alert-id="selectedAlertId"
      @close="closeAlertDetail"
    />

    <!-- 关闭事件对话框 -->
    <div
      v-if="showCloseDialog"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50"
      @click.self="closeCloseDialog"
    >
      <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">
            {{ $t('incidents.detail.closeDialog.title') }}
          </h2>
          <button
            @click="closeCloseDialog"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- 提示信息 -->
        <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('incidents.detail.closeDialog.confirmMessage') }}
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
            @click="closeCloseDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleCloseIncident"
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim()"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑事件对话框 -->
    <EditIncidentDialog
      :visible="showEditDialog"
      :incident-id="route.params.id"
      :initial-data="editIncidentInitialData"
      @close="closeEditDialog"
      @updated="handleIncidentUpdated"
    />

    <!-- 分享成功提示 -->
    <Transition name="fade">
      <div
        v-if="showShareSuccess"
        class="fixed top-4 right-4 z-[100] bg-green-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center gap-2"
      >
        <span class="material-symbols-outlined text-sm">check_circle</span>
        <span class="text-sm">{{ $t('incidents.detail.shareSuccess') || '已复制到剪切板' }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getIncidentDetail, batchCloseIncidents } from '@/api/incidents'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import EditIncidentDialog from '@/components/incidents/EditIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import { formatDateTime } from '@/utils/dateTime'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const incident = ref(null)
const loadingIncident = ref(false)
const activeTab = ref('overview')
const newComment = ref('')
const isEditingDescription = ref(false)
const editingDescription = ref('')
const selectedAlertId = ref(null)
const showShareSuccess = ref(false)
const showCloseDialog = ref(false)
const closeConclusion = ref({
  category: '',
  notes: ''
})
const showEditDialog = ref(false)
const editIncidentInitialData = ref(null)

const tabs = [
  { key: 'overview', label: 'incidents.detail.tabs.overview' },
  { key: 'timeline', label: 'incidents.detail.tabs.timeline' },
  { key: 'comments', label: 'incidents.detail.tabs.comments' }
]

// 关联告警表格列配置
const associatedAlertsColumns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') }
])

// 关联告警表格默认列宽
const associatedAlertsDefaultWidths = {
  createTime: 180,
  alertTitle: 400,
  riskLevel: 120,
  status: 120
}

// 格式化关联告警数据，将事件详情的数据格式转换为告警管理页面的格式
const formattedAssociatedAlerts = computed(() => {
  if (!incident.value?.associatedAlerts) {
    return []
  }
  return incident.value.associatedAlerts.map(alert => ({
    id: alert.id,
    createTime: alert.timestamp || '-',
    title: alert.description || '-',
    riskLevel: alert.severity || 'low', // severity 映射为 riskLevel
    status: alert.status || 'open',
    owner: '-' // 事件详情中的告警可能没有 owner 字段
  }))
})

const loadIncidentDetail = async () => {
  loadingIncident.value = true
  try {
    const incidentId = route.params.id
    const response = await getIncidentDetail(incidentId)
    const data = response.data
    
    // 格式化数据，将后端字段映射到前端使用的字段
    incident.value = {
      id: data.id,
      eventId: data.id,
      name: data.title,
      title: data.title,
      createTime: data.create_time,
      updateTime: data.update_time,
      closeTime: data.close_time,
      status: data.handle_status,
      severity: data.severity,
      owner: data.owner,
      responsiblePerson: data.owner,
      creator: data.creator,
      labels: data.labels,
      closeReason: data.close_reason,
      closeComment: data.close_comment,
      isAutoClosed: data.is_auto_closed,
      ttd: data.ttd,
      arriveTime: data.arrive_time,
      description: data.description || data.title, // 如果没有description，使用title
      extendProperties: data.extend_properties,
      dataSourceProductName: data.data_source_product_name,
      // 格式化评论数据
      comments: formatComments(data.comments || []),
      // 从评论生成时间线
      timeline: generateTimeline(data),
      // 关联告警（如果有）
      associatedAlerts: data.associatedAlerts || []
    }
  } catch (error) {
    console.error('Failed to load incident detail:', error)
    router.push('/incidents')
  } finally {
    loadingIncident.value = false
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
    const author = comment.author || 'Unknown'
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
      content: comment.content,
      create_time: comment.create_time
    }
  })
}

/**
 * @brief 从事件数据生成时间线
 */
const generateTimeline = (data) => {
  const timeline = []
  
  // 添加创建事件
  if (data.create_time) {
    timeline.push({
      time: formatDateTime(data.create_time),
      rawTime: data.create_time,
      title: t('incidents.detail.timeline.incidentCreated'),
      description: t('incidents.detail.timeline.incidentCreatedDesc'),
      icon: 'event',
      severity: data.severity?.toLowerCase() || 'low'
    })
  }
  
  // 从评论中提取重要事件
  if (data.comments && Array.isArray(data.comments)) {
    data.comments.forEach(comment => {
      const content = comment.content || ''
      
      // 检查是否是重要事件
      if (content.includes('transfer alert to incident')) {
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.timeline.alertConverted'),
          description: content,
          icon: 'transform',
          severity: 'medium'
        })
      } else if (content.includes('change severity')) {
        const severityMatch = content.match(/severity:(\w+)/i)
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.timeline.severityChanged'),
          description: content,
          icon: 'priority',
          severity: severityMatch ? severityMatch[1].toLowerCase() : 'low'
        })
      } else if (content.includes('change owner')) {
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.timeline.ownerChanged'),
          description: content,
          icon: 'person',
          severity: 'low'
        })
      } else if (content.includes('Resolved') || content.includes('Closed')) {
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.timeline.incidentClosed'),
          description: content,
          icon: 'archive',
          severity: 'low'
        })
      }
    })
  }
  
  // 添加关闭事件
  if (data.close_time) {
    timeline.push({
      time: formatDateTime(data.close_time),
      rawTime: data.close_time,
      title: t('incidents.detail.timeline.incidentClosed'),
      description: data.close_comment || t('incidents.detail.timeline.incidentClosedDesc'),
      icon: 'check_circle',
      severity: 'low'
    })
  }
  
  // 按时间排序（从旧到新），使用原始时间字段
  return timeline.sort((a, b) => {
    const timeA = a.rawTime ? new Date(a.rawTime) : new Date(a.time)
    const timeB = b.rawTime ? new Date(b.rawTime) : new Date(b.time)
    return timeA - timeB
  })
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

const handlePostComment = () => {
  if (!newComment.value.trim()) return
  
  // TODO: 实现发布评论的逻辑
  if (!incident.value.comments) {
    incident.value.comments = []
  }
  
  incident.value.comments.push({
    id: Date.now(),
    author: 'Current User',
    authorInitials: 'CU',
    avatarColor: 'bg-blue-500',
    time: 'Just now',
    content: newComment.value
  })
  
  newComment.value = ''
}

const handleStartEditDescription = () => {
  editingDescription.value = incident.value?.description || ''
  isEditingDescription.value = true
}

const handleCancelEditDescription = () => {
  isEditingDescription.value = false
  editingDescription.value = ''
}

const handleSaveDescription = async () => {
  // TODO: 实现保存描述到后端的逻辑
  if (incident.value) {
    incident.value.description = editingDescription.value
    // 更新最后修改时间和修改人
    incident.value.descriptionLastModified = new Date().toISOString()
    incident.value.descriptionLastModifiedBy = 'Current User' // TODO: 从用户上下文获取实际用户名
  }
  isEditingDescription.value = false
  
  // 这里可以添加 API 调用来保存描述
  // try {
  //   await updateIncidentDescription(route.params.id, editingDescription.value)
  // } catch (error) {
  //   console.error('Failed to save description:', error)
  // }
}

const formatLastModified = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) {
    return t('incidents.detail.overview.justNow')
  } else if (diffMins < 60) {
    return `${diffMins} ${t('incidents.detail.overview.minutesAgo')}`
  } else if (diffHours < 24) {
    return `${diffHours} ${t('incidents.detail.overview.hoursAgo')}`
  } else if (diffDays < 7) {
    return `${diffDays} ${t('incidents.detail.overview.daysAgo')}`
  } else {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
}

const getAlertSeverityDotClass = (severity) => {
  const classes = {
    critical: 'bg-red-500',
    high: 'bg-amber-400',
    medium: 'bg-yellow-400',
    low: 'bg-blue-500'
  }
  return classes[severity] || classes.medium
}

const getAlertSeverityTextClass = (severity) => {
  const classes = {
    critical: 'text-red-400',
    high: 'text-amber-400',
    medium: 'text-yellow-400',
    low: 'text-blue-400'
  }
  return classes[severity] || classes.medium
}

const getAlertSeverityLabel = (severity) => {
  const labels = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return labels[severity] || severity
}

// 复用告警管理页面的样式函数
const getRiskLevelClass = (level) => {
  const classes = {
    fatal: 'bg-red-950 text-red-200',
    high: 'bg-red-900 text-red-300',
    medium: 'bg-orange-900 text-orange-300',
    low: 'bg-blue-900 text-blue-300',
    tips: 'bg-gray-700 text-gray-300'
  }
  return classes[level] || classes.low
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-primary/20 text-primary',
    block: 'bg-yellow-500/20 text-yellow-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || classes.open
}

const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-primary',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.open
}

// 事件状态的样式函数（保留用于事件详情页面的其他部分）
const getIncidentStatusDotClass = (status) => {
  const statusLower = (status || '').toLowerCase()
  const classes = {
    open: 'bg-amber-400',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[statusLower] || classes.open
}

/**
 * @brief 获取状态文本
 */
const getStatusText = (status) => {
  if (!status) return t('incidents.list.open')
  const statusLower = status.toLowerCase()
  const statusMap = {
    'open': t('incidents.list.open'),
    'block': t('incidents.list.block'),
    'closed': t('incidents.list.closed')
  }
  return statusMap[statusLower] || status
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

/**
 * @brief 生成事件详情URL
 * @return {string} 事件的完整URL
 */
const getIncidentUrl = () => {
  const baseUrl = window.location.origin
  const incidentId = route.params.id
  return `${baseUrl}/incidents/${incidentId}`
}

/**
 * @brief 分享事件（复制标题和链接到剪切板）
 */
const handleShare = async () => {
  if (!incident.value) return
  
  const title = incident.value.name || ''
  const url = getIncidentUrl()
  const textToCopy = `${title}: ${url}`
  
  try {
    await navigator.clipboard.writeText(textToCopy)
    // 显示成功提示
    showShareSuccess.value = true
    setTimeout(() => {
      showShareSuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    // 降级方案：使用传统的复制方法
    const textArea = document.createElement('textarea')
    textArea.value = textToCopy
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      // 显示成功提示
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

const openCloseDialog = () => {
  showCloseDialog.value = true
}

const closeCloseDialog = () => {
  showCloseDialog.value = false
  // 重置表单
  closeConclusion.value = {
    category: '',
    notes: ''
  }
}

const handleCloseIncident = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim()) {
    return
  }

  try {
    await batchCloseIncidents({
      incidentIds: [parseInt(route.params.id)],
      category: closeConclusion.value.category,
      notes: closeConclusion.value.notes.trim()
    })
    
    // 关闭对话框并重置表单
    closeCloseDialog()
    
    // 重新加载事件详情
    await loadIncidentDetail()
  } catch (error) {
    console.error('Failed to close incident:', error)
  }
}

const openEditDialog = () => {
  if (!incident.value) {
    console.warn('Incident data not loaded')
    return
  }
  
  editIncidentInitialData.value = {
    title: incident.value.name || incident.value.title || '',
    category: incident.value.category || 'platform',
    status: incident.value.status || 'open',
    occurrenceTime: incident.value.occurrenceTime 
      ? (incident.value.occurrenceTime instanceof Date 
          ? incident.value.occurrenceTime 
          : new Date(incident.value.occurrenceTime))
      : new Date(),
    responsiblePerson: incident.value.responsiblePerson || '',
    responsibleDepartment: incident.value.responsibleDepartment || '',
    rootCause: incident.value.rootCause || '',
    description: incident.value.description || ''
  }
  

  nextTick(() => {
    showEditDialog.value = true
  })
}

const closeEditDialog = () => {
  showEditDialog.value = false
  editIncidentInitialData.value = null
}

const handleIncidentUpdated = async () => {
  // 事件更新成功后，关闭对话框并重新加载详情
  closeEditDialog()
  await loadIncidentDetail()
}

onMounted(() => {
  loadIncidentDetail()
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
</style>

