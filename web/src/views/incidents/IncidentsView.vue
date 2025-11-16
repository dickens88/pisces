<template>
  <div class="w-full">
    <!-- Page title and actions -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('incidents.title') }}
        </h1>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="handleRefresh"
          :disabled="loadingIncidents"
          class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingIncidents }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="incidents"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
        <button
          @click="handleCloseSelectedIncident"
          :disabled="!canCloseSelectedIncident"
          class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
        >
          <span class="material-symbols-outlined text-base">archive</span>
          <span>{{ $t('incidents.detail.closeIncident') }}</span>
        </button>
        <button
          @click="showCreateDialog = true"
          class="flex items-center justify-center gap-2 rounded-lg h-10 bg-primary text-white text-sm font-bold px-4 hover:bg-blue-500 transition-colors"
        >
          <span class="material-symbols-outlined text-base">add</span>
          <span>{{ $t('incidents.list.createIncident') }}</span>
        </button>
      </div>
    </header>

    <!-- Incident list table -->
    <section class="bg-[#111822] border border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingIncidents"
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
      <div class="flex flex-wrap items-center justify-between gap-4 p-4 border-b border-[#324867]">
        <div class="relative w-full max-w-sm">
          <div class="flex flex-wrap items-center gap-2 min-h-[42px] rounded-lg border-0 bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary">
            <div class="pointer-events-none flex items-center shrink-0">
              <span class="material-symbols-outlined text-gray-400" style="font-size: 20px;">search</span>
            </div>
            <!-- Search keyword tags -->
            <div
              v-for="(keyword, index) in searchKeywords"
              :key="index"
              class="flex items-center gap-1 px-2 py-1 bg-primary/20 text-primary rounded text-sm shrink-0"
            >
              <span>{{ keyword }}</span>
              <button
                @click="removeKeyword(index)"
                class="flex items-center justify-center hover:text-primary/70 transition-colors ml-0.5"
                type="button"
                :aria-label="$t('common.delete')"
              >
                <span class="material-symbols-outlined" style="font-size: 16px;">close</span>
              </button>
            </div>
            <!-- Input field -->
            <input
              v-model="currentSearchInput"
              @keydown.enter.prevent="addKeyword"
              @input="handleSearchInput"
              class="flex-1 min-w-[120px] border-0 bg-transparent text-white placeholder:text-gray-400 focus:outline-none sm:text-sm"
              :placeholder="searchKeywords.length === 0 ? $t('incidents.list.searchPlaceholder') : ''"
              type="text"
            />
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="relative">
            <select
              v-model="statusFilter"
              @change="handleFilter"
              class="pl-4 pr-9 appearance-none block w-full rounded-lg border-0 bg-[#233348] h-10 text-white placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm"
            >
              <option value="all">{{ $t('incidents.list.allStatus') }}</option>
              <option value="Open">{{ $t('incidents.list.open') }}</option>
              <option value="Block">{{ $t('incidents.list.block') }}</option>
              <option value="Closed">{{ $t('incidents.list.closed') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>
          <button
            :disabled="selectedIncidents.length === 0"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">ios_share</span>
            <span>{{ $t('incidents.list.export') }}</span>
          </button>
        </div>
      </div>
      <DataTable
      ref="dataTableRef"
      :columns="columns"
      :items="incidents"
      :selectable="true"
      :resizable="true"
      storage-key="incidents-table-columns"
      :default-widths="defaultWidths"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      @update:current-page="currentPage = $event"
      @update:page-size="pageSize = $event"
      @select="handleSelect"
      @select-all="handleSelectAll"
      @page-size-change="handlePageSizeChange"
    >
      <template #cell-occurrenceTime="{ value, item }">
        {{ formatDateTime(value || item?.arrive_time || item?.create_time || item?.occurrenceTime || item?.occurrence_time) }}
      </template>
      <template #cell-incidentName="{ item }">
        <div class="flex items-center gap-2">
          <button
            @click.stop="openIncidentDetailInNewWindow(item.id)"
            class="flex-shrink-0 text-gray-400 hover:text-primary transition-colors p-1"
            :title="$t('incidents.list.openInNewWindow') || '在新窗口打开'"
          >
            <span class="material-symbols-outlined text-base">open_in_new</span>
          </button>
          <router-link
            :to="`/incidents/${item.id}`"
            class="text-primary hover:underline cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap flex-1 font-medium"
            :title="item.title || item.name"
          >
            {{ item.title || item.name }}
          </router-link>
        </div>
      </template>
      <template #cell-severity="{ item }">
        <span
          :class="[
            'text-xs font-medium me-2 px-2.5 py-0.5 rounded-full inline-block',
            getSeverityClass(item.severity)
          ]"
          :title="$t(`common.severity.${item.severity?.toLowerCase()}`)"
        >
          {{ $t(`common.severity.${item.severity?.toLowerCase()}`) }}
        </span>
      </template>
      <template #cell-status="{ item }">
        <span
          :class="[
            'inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium',
            getStatusClass(item.handle_status || item.status)
          ]"
          :title="getStatusText(item.handle_status || item.status)"
        >
          <span :class="['size-1.5 rounded-full', getStatusDotClass(item.handle_status || item.status)]"></span>
          {{ getStatusText(item.handle_status || item.status) }}
        </span>
      </template>
      <template #cell-responsibleDepartment="{ value, item }">
        {{ item.responsible_dept || value || '-' }}
      </template>
      <template #cell-owner="{ value, item }">
        <div class="flex justify-center w-full">
          <UserAvatar :name="item.owner || value || ''" />
        </div>
      </template>
      </DataTable>
    </section>

    <!-- Create incident dialog -->
    <CreateIncidentDialog
      :visible="showCreateDialog"
      @close="showCreateDialog = false"
      @created="handleIncidentCreated"
    />

    <!-- Close incident dialog -->
    <CloseIncidentDialog
      ref="closeDialogRef"
      :visible="showCloseDialog"
      :title="$t('incidents.detail.closeDialog.title')"
      :confirm-message="$t('incidents.detail.closeDialog.confirmMessage')"
      @close="closeCloseDialog"
      @submit="handleCloseIncident"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { getIncidents } from '@/api/incidents'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const { t } = useI18n()
const toast = useToast()
const authStore = useAuthStore()

// Define column configuration (using computed to ensure reactivity)
const columns = computed(() => [
  { key: 'occurrenceTime', label: t('incidents.list.occurrenceTime') },
  { key: 'incidentName', label: t('incidents.list.incidentName') },
  { key: 'severity', label: t('incidents.list.severity') },
  { key: 'status', label: t('incidents.list.status') },
  { key: 'responsibleDepartment', label: t('incidents.list.responsibleDepartment') },
  { key: 'owner', label: t('incidents.list.owner') }
])

// Default column widths
const defaultWidths = {
  occurrenceTime: 200,
  incidentName: 400,
  severity: 120,
  status: 120,
  responsibleDepartment: 150,
  owner: 50
}

const incidents = ref([])
const dataTableRef = ref(null)
const loadingIncidents = ref(false)

// 从 localStorage 读取保存的搜索关键词
const getStoredSearchKeywords = () => {
  try {
    const stored = localStorage.getItem('incidents-searchKeywords')
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.every(k => typeof k === 'string')) {
        return parsed
      }
    }
  } catch (error) {
    console.warn('Failed to read search keywords from localStorage:', error)
  }
  return []
}

const searchKeywords = ref(getStoredSearchKeywords())
const currentSearchInput = ref('')
const severityFilter = ref('all')
const statusFilter = ref('all')
const selectedIncidents = ref([])
const currentPage = ref(1)

// 从 localStorage 读取保存的分页大小
const getStoredPageSize = () => {
  try {
    const stored = localStorage.getItem('incidents-pageSize')
    if (stored) {
      const size = Number(stored)
      if (size && [10, 20, 50, 100].includes(size)) {
        return size
      }
    }
  } catch (error) {
    console.warn('Failed to read page size from localStorage:', error)
  }
  return 10
}

const pageSize = ref(getStoredPageSize())
const total = ref(0)
const showCreateDialog = ref(false)
const showCloseDialog = ref(false)
const isClosingIncident = ref(false)
const closeDialogRef = ref(null)
const closingIncidentId = ref(null)

// Time range picker
// 从 localStorage 读取保存的时间范围
const getStoredTimeRange = () => {
  try {
    const stored = localStorage.getItem('incidents-timeRange')
    if (stored && ['last24Hours', 'last3Days', 'last7Days', 'last30Days', 'last3Months', 'customRange'].includes(stored)) {
      return stored
    }
  } catch (error) {
    console.warn('Failed to read time range from localStorage:', error)
  }
  return 'last3Months'
}

// 从 localStorage 读取保存的自定义时间范围
const getStoredCustomRange = () => {
  try {
    const stored = localStorage.getItem('incidents-customTimeRange')
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length === 2) {
        return [new Date(parsed[0]), new Date(parsed[1])]
      }
    }
  } catch (error) {
    console.warn('Failed to read custom time range from localStorage:', error)
  }
  return null
}

const selectedTimeRange = ref(getStoredTimeRange())
const customTimeRange = ref(getStoredCustomRange())

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadIncidents = async () => {
  loadingIncidents.value = true
  try {
    // Calculate time range (in days)
    let timeRange = 1 // Default 1 day
    if (selectedTimeRange.value === 'customRange' && customTimeRange.value && customTimeRange.value.length === 2) {
      // Custom time range: calculate day difference
      const diffTime = Math.abs(customTimeRange.value[1] - customTimeRange.value[0])
      timeRange = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) || 1
    } else {
      // Predefined time range
      if (selectedTimeRange.value === 'last24Hours') {
        timeRange = 1
      } else if (selectedTimeRange.value === 'last3Days') {
        timeRange = 3
      } else if (selectedTimeRange.value === 'last7Days') {
        timeRange = 7
      } else if (selectedTimeRange.value === 'last30Days') {
        timeRange = 30
      } else if (selectedTimeRange.value === 'last3Months') {
        timeRange = 90
      }
    }
    
    // Build conditions array
    const conditions = []
    // Add search keyword conditions
    searchKeywords.value.forEach(keyword => {
      conditions.push({ title: keyword })
    })
    if (severityFilter.value && severityFilter.value !== 'all') {
      conditions.push({ severity: severityFilter.value })
    }
    if (statusFilter.value && statusFilter.value !== 'all') {
      conditions.push({ handle_status: statusFilter.value })
    }
    
    // Build parameters in the format expected by the backend
    const params = {
      action: 'list',
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      time_range: timeRange,
      conditions: conditions
    }
    
    const response = await getIncidents(params)
    incidents.value = response.data || []
    total.value = response.total || 0
  } catch (error) {
    console.error('Failed to load incidents:', error)
    incidents.value = []
    total.value = 0
  } finally {
    loadingIncidents.value = false
  }
}

/**
 * @brief 刷新事件列表
 */
const handleRefresh = async () => {
  await loadIncidents()
}

// 保存搜索关键词到 localStorage
const saveSearchKeywords = () => {
  try {
    localStorage.setItem('incidents-searchKeywords', JSON.stringify(searchKeywords.value))
  } catch (error) {
    console.warn('Failed to save search keywords to localStorage:', error)
  }
}

/**
 * @brief 添加搜索关键字
 */
const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && !searchKeywords.value.includes(keyword)) {
    searchKeywords.value.push(keyword)
    currentSearchInput.value = ''
    saveSearchKeywords()
    loadIncidents()
  }
}

/**
 * @brief 删除搜索关键字
 * @param {number} index - 要删除的关键字索引
 */
const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  saveSearchKeywords()
  loadIncidents()
}

/**
 * @brief 处理搜索输入
 * @details 实时搜索功能（可选，如果需要实时搜索可以启用）
 */
const handleSearchInput = () => {
  // If real-time search is needed, call loadIncidents() here
  // Currently only searches when adding/removing keywords
}

/**
 * @brief 处理筛选器变化
 */
const handleFilter = () => {
  loadIncidents()
}

const handleSelect = (items) => {
  selectedIncidents.value = items.map(incident => incident.id)
}

const handleSelectAll = (items) => {
  selectedIncidents.value = items.map(incident => incident.id)
}

/**
 * @brief 计算是否可以关闭选中的事件
 * @details 必须选中一个事件，且该事件未关闭
 */
const canCloseSelectedIncident = computed(() => {
  if (selectedIncidents.value.length !== 1) {
    return false
  }
  const selectedId = selectedIncidents.value[0]
  const selectedIncident = incidents.value.find(inc => inc.id === selectedId)
  if (!selectedIncident) {
    return false
  }
  const status = (selectedIncident.handle_status || selectedIncident.status)?.toLowerCase()
  return status !== 'closed'
})

/**
 * @brief 处理关闭选中的事件
 */
const handleCloseSelectedIncident = () => {
  if (!canCloseSelectedIncident.value) {
    return
  }
  const selectedId = selectedIncidents.value[0]
  openCloseDialog(selectedId)
}

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = newPageSize
  currentPage.value = 1
  // 保存到 localStorage
  try {
    localStorage.setItem('incidents-pageSize', String(newPageSize))
  } catch (error) {
    console.warn('Failed to save page size to localStorage:', error)
  }
  loadIncidents()
}

const router = useRouter()

const getSeverityClass = (severity) => {
  const severityLower = (severity || '').toLowerCase()
  const classes = {
    high: 'text-white bg-[#E57373]',
    medium: 'text-black bg-[#FFB74D]',
    low: 'text-white bg-[#64B5F6]'
  }
  return classes[severityLower] || classes.low
}

const getStatusClass = (status) => {
  const statusLower = (status || '').toLowerCase()
  const classes = {
    open: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    block: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20',
    closed: 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
  }
  return classes[statusLower] || classes.open
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

const openIncidentDetailInNewWindow = (incidentId) => {
  // Open incident detail in a new window
  const route = router.resolve({ path: `/incidents/${incidentId}` })
  // Build complete URL
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const handleIncidentCreated = () => {
  // Reload incident list
  loadIncidents()
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    // Load data based on selected time range
    loadIncidents()
  }
}

const handleCustomRangeChange = (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    loadIncidents()
  }
}

/**
 * @brief 打开关闭事件对话框
 */
const openCloseDialog = (incidentId) => {
  closingIncidentId.value = incidentId
  showCloseDialog.value = true
}

/**
 * @brief 关闭关闭事件对话框
 */
const closeCloseDialog = () => {
  showCloseDialog.value = false
  closingIncidentId.value = null
}

/**
 * @brief 处理关闭事件
 */
const handleCloseIncident = async (data) => {
  if (!closingIncidentId.value || isClosingIncident.value) {
    return
  }

  try {
    isClosingIncident.value = true
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(true)
    }
    
    // 构建请求体
    const body = {
      handle_status: 'Closed',
      close_reason: data.close_reason,
      close_comment: data.close_comment
    }

    // 调用 PUT /api/incidents/<incident_id> 接口
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/incidents/${closingIncidentId.value}` : `/api/incidents/${closingIncidentId.value}`
    
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    await axios.put(url, body, { headers })
    
    // 显示成功提示
    toast.success(t('incidents.detail.closeSuccess') || '事件关闭成功', '操作成功')
    
    // 关闭对话框
    closeCloseDialog()
    
    // 重新加载事件列表
    loadIncidents()
  } catch (error) {
    console.error('Failed to close incident:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.closeError') || '事件关闭失败，请稍后重试'
    toast.error(errorMessage, '操作失败')
  } finally {
    isClosingIncident.value = false
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(false)
    }
  }
}

watch([currentPage, pageSize], () => {
  loadIncidents()
})

onMounted(() => {
  loadIncidents()
})
</script>


