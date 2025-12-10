<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="handleClose"
  >
    <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-2xl max-h-[80vh] flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
          {{ dialogTitle }}
        </h2>
        <button
          @click="handleClose"
          class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <span class="material-symbols-outlined text-base">close</span>
        </button>
      </div>

      <!-- 提示信息 -->
      <div class="mb-4 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md border border-gray-200 dark:border-[#324867]">
        <p class="text-sm text-gray-700 dark:text-gray-400">
          {{ confirmMessage }}
        </p>
      </div>

      <!-- 事件列表 -->
      <div class="flex-1 overflow-y-auto mb-4 relative">
        <!-- Loading overlay -->
        <div
          v-if="loadingIncidents"
          class="absolute inset-0 bg-white/80 dark:bg-[#1e293b]/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-md"
        >
          <div class="flex flex-col items-center gap-4">
            <div class="relative w-16 h-16">
              <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
            </div>
            <p class="text-gray-700 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
          </div>
        </div>
        <div class="bg-white dark:bg-[#1e293b] rounded-md border border-gray-200 dark:border-[#324867]">
          <table class="w-full text-sm text-left text-gray-700 dark:text-[#92a9c9]">
            <thead class="text-xs text-gray-600 dark:text-white uppercase bg-gray-100 dark:bg-[#111822] sticky top-0">
              <tr>
                <th class="px-4 py-3" scope="col" style="width: 50px;"></th>
                <th class="px-4 py-3" scope="col">{{ titleColumnLabel }}</th>
                <th class="px-4 py-3" scope="col">{{ createTimeLabel }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="incident in incidentsList"
                :key="incident.id"
                @click="selectIncident(incident.id)"
                :class="[
                  'border-b border-gray-200 dark:border-[#324867] hover:bg-gray-100 dark:hover:bg-primary/10 transition-colors cursor-pointer',
                  selectedIncidentId === incident.id ? 'bg-gray-100 dark:bg-primary/20' : ''
                ]"
              >
                <td class="px-4 py-3">
                  <input
                    type="radio"
                    :checked="selectedIncidentId === incident.id"
                    @click.stop="selectIncident(incident.id)"
                    class="bg-transparent border-gray-300 dark:border-[#324867] text-primary focus:ring-primary"
                  />
                </td>
                <td class="px-4 py-3">
                  <div class="max-w-xs break-words" :title="incident.title || incident.name">
                    {{ incident.title || incident.name }}
                  </div>
                </td>
                <td class="px-4 py-3 text-gray-600 dark:text-[#92a9c9]">{{ formatDateTime(incident.occurrenceTime || incident.arrive_time || incident.create_time) }}</td>
              </tr>
              <tr v-if="!loadingIncidents && incidentsList.length === 0">
                <td colspan="3" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  {{ emptyStateText }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 分页 -->
      <nav v-if="incidentsTotal > 0" aria-label="Incidents table navigation" class="flex items-center justify-between mb-6">
        <span class="text-sm font-normal text-gray-600 dark:text-gray-400">
          {{ $t('common.pagination.showing', { 
            start: pageSize * (page - 1) + 1, 
            end: Math.min(pageSize * page, incidentsTotal),
            total: incidentsTotal 
          }) }}
        </span>
        <ul class="inline-flex -space-x-px text-sm h-8">
          <li>
            <button
              @click="handlePreviousPage"
              :disabled="page === 1"
              class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] border border-gray-300 dark:border-gray-700 rounded-s-lg hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ $t('common.pagination.previous') }}
            </button>
          </li>
          <template v-for="(item, index) in displayPages" :key="index">
            <li v-if="item.type === 'page'">
              <button
                @click="page = item.value; loadIncidents()"
                :class="[
                  'flex items-center justify-center px-3 h-8 leading-tight border border-gray-300 dark:border-gray-700',
                  page === item.value
                    ? 'text-white bg-primary hover:bg-primary/90'
                    : 'text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                ]"
              >
                {{ item.value }}
              </button>
            </li>
            <li v-else-if="item.type === 'ellipsis'" class="flex items-center justify-center px-2 h-8 text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] border border-gray-300 dark:border-gray-700">
              <span class="material-symbols-outlined" style="font-size: 18px;">more_horiz</span>
            </li>
          </template>
          <li>
            <button
              @click="handleNextPage"
              :disabled="page === totalPages"
              class="flex items-center justify-center px-3 h-8 leading-tight text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] border border-gray-300 dark:border-gray-700 rounded-e-lg hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ $t('common.pagination.next') }}
            </button>
          </li>
        </ul>
      </nav>

      <!-- 操作按钮 -->
      <div class="flex items-center justify-end gap-3">
        <button
          @click="handleClose"
          class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md border border-gray-200 dark:border-[#324867] hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="handleAssociate"
          :disabled="!selectedIncidentId || isAssociating"
          class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <span v-if="isAssociating" class="material-symbols-outlined animate-spin text-base">sync</span>
          {{ $t('common.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getIncidents, associateAlertsToIncident } from '@/api/incidents'
import { formatDateTime, formatDateTimeWithOffset } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  alertIds: {
    type: Array,
    default: () => []
  },
  mode: {
    type: String,
    default: 'incident' // incident | vulnerability
  }
})

const emit = defineEmits(['close', 'associated'])

const { t } = useI18n()
const toast = useToast()

const incidentsList = ref([])
const selectedIncidentId = ref(null)
const page = ref(1)
const pageSize = ref(10)
const incidentsTotal = ref(0)
const loadingIncidents = ref(false)
const isAssociating = ref(false)
const totalPages = computed(() => Math.ceil(incidentsTotal.value / pageSize.value))
const isVulnerabilityMode = computed(() => props.mode === 'vulnerability')

const dialogTitle = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.title') || '关联漏洞'
    : t('alerts.list.associateIncidentDialog.title')
)

const confirmMessage = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.confirmMessage', { count: props.alertIds.length }) ||
      `请确认是否关联选中的 ${props.alertIds.length} 条告警到漏洞？`
    : t('alerts.list.associateIncidentDialog.confirmMessage', { count: props.alertIds.length })
)

const titleColumnLabel = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.vulnerabilityTitle') || '漏洞标题'
    : t('alerts.list.associateIncidentDialog.incidentTitle')
)

const createTimeLabel = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.createTime') || t('incidents.list.createTime') || '发现时间'
    : t('alerts.list.associateIncidentDialog.createTime')
)

const emptyStateText = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.noVulnerabilities') || '暂无漏洞'
    : t('alerts.list.associateIncidentDialog.noIncidents')
)

const successMessage = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.success') || '关联漏洞成功'
    : t('alerts.list.associateIncidentDialog.success') || '关联事件成功'
)

const associateErrorMessage = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.associateError') || '关联漏洞失败，请稍后重试'
    : t('alerts.list.associateIncidentDialog.associateError') || '关联事件失败，请稍后重试'
)

const loadErrorMessage = computed(() =>
  isVulnerabilityMode.value
    ? t('alerts.list.associateVulnerabilityDialog.loadError') || '加载漏洞列表失败，请稍后重试'
    : t('alerts.list.associateIncidentDialog.loadError') || '加载事件列表失败，请稍后重试'
)

// 计算要显示的页码数组
const displayPages = computed(() => {
  const total = totalPages.value
  const current = page.value
  const pages = []
  
  // 如果总页数少于等于 5，显示所有页码
  if (total <= 5) {
    for (let i = 1; i <= total; i++) {
      pages.push({ type: 'page', value: i })
    }
    return pages
  }
  
  // 总是显示第一页
  pages.push({ type: 'page', value: 1 })
  
  // 计算当前页附近的页码
  let start = Math.max(2, current - 1)
  let end = Math.min(total - 1, current + 1)
  
  // 如果当前页在开头附近，显示前几页
  if (current <= 3) {
    start = 2
    end = Math.min(4, total - 1)
  }
  // 如果当前页在结尾附近，显示后几页
  else if (current >= total - 2) {
    start = Math.max(2, total - 3)
    end = total - 1
  }
  
  // 如果 start > 2，添加省略号
  if (start > 2) {
    pages.push({ type: 'ellipsis' })
  }
  
  // 添加当前页附近的页码
  for (let i = start; i <= end; i++) {
    pages.push({ type: 'page', value: i })
  }
  
  // 如果 end < total - 1，添加省略号
  if (end < total - 1) {
    pages.push({ type: 'ellipsis' })
  }
  
  // 总是显示最后一页（如果不是第一页）
  if (total > 1) {
    pages.push({ type: 'page', value: total })
  }
  
  return pages
})

// 监听 visible 变化，打开时加载事件列表
watch(() => props.visible, (newVal) => {
  if (newVal) {
    selectedIncidentId.value = null
    page.value = 1
    loadIncidents()
  }
})

const loadIncidents = async () => {
  loadingIncidents.value = true
  try {
    // Build parameters in the format expected by the backend
    const end = new Date()
    const start = new Date()
    start.setMonth(start.getMonth() - 3)

    const params = {
      action: 'list',
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
      start_time: formatDateTimeWithOffset(start),
      end_time: formatDateTimeWithOffset(end),
      conditions: [] // No filters, show all
    }
    if (isVulnerabilityMode.value) {
      params.search_vulscan = true
    }
    
    const response = await getIncidents(params)
    incidentsList.value = response.data || []
    incidentsTotal.value = response.total || 0
  } catch (error) {
    console.error('Failed to load incidents:', error)
    incidentsList.value = []
    incidentsTotal.value = 0
    // Show error toast
    const errorMessage = error?.response?.data?.message || error?.message || loadErrorMessage.value
    toast.error(errorMessage, t('common.operationError') || '操作失败')
  } finally {
    loadingIncidents.value = false
  }
}

const handlePreviousPage = () => {
  if (page.value > 1) {
    page.value--
    loadIncidents()
  }
}

const handleNextPage = () => {
  if (page.value < totalPages.value) {
    page.value++
    loadIncidents()
  }
}

const selectIncident = (incidentId) => {
  selectedIncidentId.value = incidentId
}

const handleClose = () => {
  selectedIncidentId.value = null
  page.value = 1
  incidentsList.value = []
  incidentsTotal.value = 0
  emit('close')
}

const handleAssociate = async () => {
  if (!selectedIncidentId.value || props.alertIds.length === 0 || isAssociating.value) {
    return
  }

  try {
    isAssociating.value = true
    const workspace = isVulnerabilityMode.value ? 'asm' : null
    await associateAlertsToIncident(selectedIncidentId.value, props.alertIds, workspace)
    
    // Show success message
    toast.success(successMessage.value, t('common.operationSuccess') || '操作成功')
    
    handleClose()
    emit('associated')
  } catch (error) {
    console.error('Failed to associate alerts to incident:', error)
    // Show error toast
    const errorMessage = error?.response?.data?.message || error?.message || associateErrorMessage.value
    toast.error(errorMessage, t('common.operationError') || '操作失败')
  } finally {
    isAssociating.value = false
  }
}
</script>

