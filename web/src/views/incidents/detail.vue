<template>
  <div class="w-full">
    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap justify-between items-start gap-4 mb-6">
      <div class="flex flex-col gap-2">
        <h1 class="text-white text-3xl font-black leading-tight tracking-tight">
          {{ incident?.name }}
        </h1>
        <p class="text-slate-400 text-base font-normal leading-normal">
          {{ $t('incidents.detail.eventId') }}: {{ incident?.eventId }}
        </p>
      </div>
      <div class="flex flex-1 gap-3 flex-wrap justify-start sm:justify-end min-w-max">
        <button
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">person_add</span>
          <span class="truncate">{{ $t('incidents.detail.assign') }}</span>
        </button>
        <button
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">task_alt</span>
          <span class="truncate">{{ $t('incidents.detail.changeStatus') }}</span>
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.status') }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getStatusDotClass(incident?.status)
            ]"
          ></span>
          <p class="text-white text-xl font-bold leading-tight">
            {{ $t(`incidents.list.${incident?.status}`) }}
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
            {{ $t(`incidents.list.${incident?.severity}`) }}
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
          {{ $t('incidents.detail.mitreTactic') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.mitreTactic || '-' }}
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
      <!-- 时间线与告警 -->
      <div v-if="activeTab === 'timeline'" class="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <!-- 左侧时间线 -->
        <div class="lg:col-span-2 bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex flex-col h-[600px] lg:h-auto">
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

        <!-- 右侧攻击链 -->
        <div class="lg:col-span-3 bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex flex-col h-[600px] lg:h-auto">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.attackChain.title') }}
            </h3>
            <div class="flex items-center gap-2">
              <button
                class="flex items-center justify-center size-8 rounded-md bg-slate-700 hover:bg-slate-600 transition-colors"
                :title="$t('incidents.detail.attackChain.zoomIn')"
              >
                <span class="material-symbols-outlined text-base">zoom_in</span>
              </button>
              <button
                class="flex items-center justify-center size-8 rounded-md bg-slate-700 hover:bg-slate-600 transition-colors"
                :title="$t('incidents.detail.attackChain.zoomOut')"
              >
                <span class="material-symbols-outlined text-base">zoom_out</span>
              </button>
              <button
                class="flex items-center justify-center size-8 rounded-md bg-slate-700 hover:bg-slate-600 transition-colors"
                :title="$t('incidents.detail.attackChain.fullscreen')"
              >
                <span class="material-symbols-outlined text-base">fullscreen</span>
              </button>
            </div>
          </div>
          <div
            class="mt-4 flex-grow rounded-md flex items-center justify-center"
            style="--dot-bg: #101822; --dot-color: #2E4057; background-image: radial-gradient(var(--dot-color) 1px, var(--dot-bg) 1px); background-size: 20px 20px;"
          >
            <div
              v-if="incident?.attackChainImage"
              class="w-full h-full bg-contain bg-no-repeat bg-center"
              :style="{ backgroundImage: `url('${incident.attackChainImage}')` }"
            ></div>
            <div v-else class="text-slate-400 text-sm">
              {{ $t('incidents.detail.attackChain.title') }}
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
        <div class="bg-slate-800/50 border border-slate-700 rounded-lg flex-grow flex flex-col">
          <div class="p-6">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.associatedAlerts') }}
            </h3>
          </div>
          <div class="overflow-x-auto">
            <div class="min-w-full align-middle">
              <table class="min-w-full divide-y divide-slate-700">
                <thead class="bg-slate-800/30">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" scope="col">
                      {{ $t('incidents.detail.overview.alertId') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" scope="col">
                      {{ $t('incidents.detail.overview.timestamp') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" scope="col">
                      {{ $t('incidents.detail.overview.description') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" scope="col">
                      {{ $t('incidents.detail.overview.severity') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider" scope="col">
                      {{ $t('incidents.detail.overview.status') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-700">
                  <tr
                    v-for="alert in incident?.associatedAlerts || []"
                    :key="alert.id"
                    class="hover:bg-slate-700/30 transition-colors"
                  >
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <a
                        @click="openAlertDetail(alert.id)"
                        class="text-primary hover:underline cursor-pointer"
                      >
                        {{ alert.id }}
                      </a>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      {{ alert.timestamp }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      {{ alert.description }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                      <div class="flex items-center gap-2">
                        <span
                          :class="[
                            'h-2 w-2 rounded-full',
                            getAlertSeverityDotClass(alert.severity)
                          ]"
                        ></span>
                        <span :class="getAlertSeverityTextClass(alert.severity)">
                          {{ getAlertSeverityLabel(alert.severity) }}
                        </span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      {{ alert.status }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
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

      <!-- Attack Chain 标签页 -->
      <div v-if="activeTab === 'attackChain'" class="text-slate-400">
        Attack Chain content coming soon...
      </div>
    </div>

    <!-- 告警详情抽屉 -->
    <AlertDetail
      v-if="selectedAlertId"
      :alert-id="selectedAlertId"
      @close="closeAlertDetail"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getIncidentDetail } from '@/api/incidents'
import AlertDetail from '@/components/alerts/AlertDetail.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const incident = ref(null)
const activeTab = ref('overview')
const newComment = ref('')
const isEditingDescription = ref(false)
const editingDescription = ref('')
const selectedAlertId = ref(null)

const tabs = [
  { key: 'overview', label: 'incidents.detail.tabs.overview' },
  { key: 'timeline', label: 'incidents.detail.tabs.timeline' },
  { key: 'attackChain', label: 'incidents.detail.tabs.attackChain' },
  { key: 'comments', label: 'incidents.detail.tabs.comments' }
]

const loadIncidentDetail = async () => {
  try {
    const incidentId = route.params.id
    const response = await getIncidentDetail(incidentId)
    incident.value = response.data
  } catch (error) {
    console.error('Failed to load incident detail:', error)
    router.push('/incidents')
  }
}

const openAlertDetail = (alertId) => {
  selectedAlertId.value = alertId
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

const getStatusDotClass = (status) => {
  const classes = {
    pending: 'bg-amber-400',
    inProgress: 'bg-blue-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.pending
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

onMounted(() => {
  loadIncidentDetail()
})
</script>

