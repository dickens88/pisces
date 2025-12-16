<template>
  <div class="w-full">
    <!-- Page title and actions -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('incidents.title') }}
        </h1>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="handleRefresh"
          :disabled="loadingIncidents"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
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
      </div>
    </header>

    <!-- Incident list table -->
    <section class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingIncidents"
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
      <div class="flex flex-wrap items-center justify-between gap-4 p-4 border-b border-gray-200 dark:border-[#324867]">
        <div class="flex flex-wrap items-center gap-3 flex-1">
          <div class="relative w-full max-w-sm">
            <div class="flex flex-wrap items-center gap-2 min-h-[42px] rounded-lg border-0 bg-gray-100 dark:bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary">
              <div class="pointer-events-none flex items-center shrink-0">
                <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">search</span>
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
                class="flex-1 min-w-[120px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
                :placeholder="searchKeywords.length === 0 ? $t('incidents.list.searchPlaceholder') : ''"
                type="text"
              />
            </div>
          </div>
          <div class="relative">
            <select
              v-model="statusFilter"
              @change="handleFilter"
              class="pl-4 pr-9 appearance-none block w-full rounded-lg border-0 bg-gray-100 dark:bg-[#233348] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm"
            >
              <option value="all">{{ $t('incidents.list.allStatus') }}</option>
              <option value="Open">{{ $t('incidents.list.open') }}</option>
              <option value="Block">{{ $t('incidents.list.block') }}</option>
              <option value="Closed">{{ $t('incidents.list.closed') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button
            :disabled="selectedIncidents.length === 0"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">ios_share</span>
            <span>{{ $t('incidents.list.export') }}</span>
          </button>
          <!-- More actions button -->
          <div class="relative">
            <button
              @click="showMoreMenu = !showMoreMenu"
              class="more-menu-button flex items-center justify-center rounded-lg h-10 w-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
              :title="$t('common.more')"
            >
              <span class="material-symbols-outlined text-base">more_vert</span>
            </button>
            <!-- Dropdown menu -->
            <div
              v-if="showMoreMenu"
              class="more-menu-dropdown absolute right-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
            >
              <button
                @click="handleCreateIncident"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">add</span>
                <span>{{ $t('incidents.list.createIncident') }}</span>
              </button>
              <button
                @click="handleCloseSelectedIncident"
                :disabled="!canCloseSelectedIncident"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">archive</span>
                <span>{{ $t('incidents.detail.closeIncident') }}</span>
              </button>
              <button
                @click="openBatchDeleteDialog"
                :disabled="selectedIncidents.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">delete</span>
                <span>{{ $t('incidents.list.batchDelete') }}</span>
              </button>
            </div>
          </div>
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
      @update:current-page="handlePageChange"
      @update:page-size="handlePageSizeChange"
      @select="handleSelect"
      @select-all="handleSelectAll"
      @page-size-change="handlePageSizeChange"
    >
      <template #cell-occurrenceTime="{ value, item }">
        {{ formatDateTime(value || item?.arrive_time || item?.create_time || item?.occurrenceTime || item?.occurrence_time) }}
      </template>
      <template #cell-category="{ item }">
        {{ $t(`incidents.create.category${item?.category ? item.category.charAt(0).toUpperCase() + item.category.slice(1) : 'Platform'}`) }}
      </template>
      <template #cell-incidentName="{ item }">
        <div class="flex items-center gap-2">
          <button
            @click.stop="openIncidentDetailInNewWindow(item.id)"
            class="flex-shrink-0 text-gray-500 dark:text-gray-400 hover:text-primary transition-colors p-1"
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
          {{ severityToNumber(item.severity) || '-' }}
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
      <template #cell-actor="{ value, item }">
        <div class="flex justify-center w-full">
          <UserAvatar :name="item.actor || value || ''" />
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

    <!-- Batch delete dialog -->
    <div
      v-if="showBatchDeleteDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeBatchDeleteDialog"
    >
      <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">
            {{ $t('incidents.list.batchDeleteDialog.title') }}
          </h2>
          <button
            @click="closeBatchDeleteDialog"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('incidents.list.batchDeleteDialog.confirmMessage', { count: selectedIncidents.length }) }}
          </p>
        </div>

        <!-- Confirmation input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('incidents.list.batchDeleteDialog.confirmInputLabel') }}
          </label>
          <input
            v-model="deleteConfirmInput"
            @keydown.enter.prevent="handleBatchDelete"
            type="text"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
            :placeholder="$t('incidents.list.batchDeleteDialog.confirmInputPlaceholder')"
            autocomplete="off"
          />
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchDeleteDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchDelete"
            :disabled="!isDeleteConfirmValid || isBatchDeleting"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isBatchDeleting" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- AI Sidebar -->
    <AISidebar
      :visible="showAISidebar"
      :alert-title="currentTitle"
      :finding-summary="findingSummary"
      :alert-id="currentIncidentId"
      @close="showAISidebar = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { getIncidents, deleteIncidents } from '@/api/incidents'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import AISidebar from '@/components/common/AISidebar.vue'
import { formatDateTime, formatDateTimeWithOffset } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { useAuthStore } from '@/stores/auth'
import { severityToNumber } from '@/utils/severity'
import axios from 'axios'

const { t } = useI18n()
const toast = useToast()
const authStore = useAuthStore()

// Define column configuration (using computed to ensure reactivity)
const columns = computed(() => [
  { key: 'occurrenceTime', label: t('incidents.list.occurrenceTime') },
  { key: 'category', label: t('incidents.detail.category') },
  { key: 'incidentName', label: t('incidents.list.incidentName') },
  { key: 'severity', label: t('incidents.list.severity') },
  { key: 'status', label: t('incidents.list.status') },
  { key: 'responsibleDepartment', label: t('incidents.list.responsibleDepartment') },
  { key: 'owner', label: t('incidents.list.owner') },
  { key: 'actor', label: t('incidents.list.actor') }
])

// Default column widths
const defaultWidths = {
  occurrenceTime: 200,
  category: 120,
  incidentName: 400,
  severity: 120,
  status: 120,
  responsibleDepartment: 150,
  owner: 50,
  actor: 50
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
const showMoreMenu = ref(false)
const showBatchDeleteDialog = ref(false)
const deleteConfirmInput = ref('')
const isBatchDeleting = ref(false)
const showAISidebar = ref(false)
const currentIncidentId = ref(null)
const currentTitle = ref('')
const findingSummary = ref('')

// Time range picker
// Time range picker
const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('incidents', 'last3Months')

const computeSelectedRange = () => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      return {
        start: new Date(customTimeRange.value[0]),
        end: new Date(customTimeRange.value[1])
      }
    }
    const end = new Date()
    const start = new Date(end)
    start.setDate(start.getDate() - 7)
    return { start, end }
  }

  const end = new Date()
  const start = new Date(end)

  switch (selectedTimeRange.value) {
    case 'last24Hours':
      start.setHours(start.getHours() - 24)
      break
    case 'last3Days':
      start.setDate(start.getDate() - 3)
      break
    case 'last7Days':
      start.setDate(start.getDate() - 7)
      break
    case 'last30Days':
      start.setDate(start.getDate() - 30)
      break
    case 'last3Months':
      start.setMonth(start.getMonth() - 3)
      break
    default:
      start.setMonth(start.getMonth() - 3)
      break
  }

  return { start, end }
}

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadIncidents = async () => {
  loadingIncidents.value = true
  try {
    const range = computeSelectedRange()

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
      conditions
    }

    if (range) {
      params.start_time = formatDateTimeWithOffset(range.start)
      params.end_time = formatDateTimeWithOffset(range.end)
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

const handlePageChange = (page) => {
  currentPage.value = page
  return loadIncidents()
}

const reloadIncidentsFromFirstPage = () => {
  if (currentPage.value === 1) {
    return loadIncidents()
  }
  return handlePageChange(1)
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
    reloadIncidentsFromFirstPage()
  }
}

/**
 * @brief 删除搜索关键字
 * @param {number} index - 要删除的关键字索引
 */
const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  saveSearchKeywords()
  reloadIncidentsFromFirstPage()
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
  reloadIncidentsFromFirstPage()
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
 * @brief 处理创建事件
 */
const handleCreateIncident = () => {
  showMoreMenu.value = false
  showCreateDialog.value = true
}

/**
 * @brief 处理关闭选中的事件
 */
const handleCloseSelectedIncident = () => {
  if (!canCloseSelectedIncident.value) {
    return
  }
  showMoreMenu.value = false
  const selectedId = selectedIncidents.value[0]
  openCloseDialog(selectedId)
}

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = Number(newPageSize)
  // 保存到 localStorage
  try {
    localStorage.setItem('incidents-pageSize', String(pageSize.value))
  } catch (error) {
    console.warn('Failed to save page size to localStorage:', error)
  }
  handlePageChange(1)
}

const router = useRouter()

const getSeverityClass = (severity) => {
  if (!severity) return 'text-white bg-gray-500'
  const severityLower = String(severity).toLowerCase().trim()
  const classes = {
    fatal: 'text-white bg-red-600',
    critical: 'text-white bg-red-600',
    high: 'text-white bg-[#E57373]',
    medium: 'text-black bg-[#FFB74D]',
    low: 'text-white bg-[#64B5F6]',
    tips: 'text-white bg-gray-400'
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
    reloadIncidentsFromFirstPage()
  }
}

const handleCustomRangeChange = (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    reloadIncidentsFromFirstPage()
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
    toast.success(t('incidents.detail.closeSuccess') || '事件关闭成功', 'SUCCESS')
    
    // 关闭对话框
    closeCloseDialog()
    
    // 重新加载事件列表
    loadIncidents()
  } catch (error) {
    console.error('Failed to close incident:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.closeError') || '事件关闭失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isClosingIncident.value = false
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(false)
    }
  }
}

// Delete confirmation validation
const isDeleteConfirmValid = computed(() => {
  return deleteConfirmInput.value.toLowerCase() === 'delete'
})

const openBatchDeleteDialog = () => {
  if (selectedIncidents.value.length === 0) {
    console.warn('No incidents selected')
    return
  }
  showMoreMenu.value = false
  showBatchDeleteDialog.value = true
  deleteConfirmInput.value = ''
}

const closeBatchDeleteDialog = () => {
  showBatchDeleteDialog.value = false
  deleteConfirmInput.value = ''
}

const handleBatchDelete = async () => {
  if (!isDeleteConfirmValid.value || isBatchDeleting.value) {
    return
  }

  if (selectedIncidents.value.length === 0) {
    toast.warn('请至少选择一个事件', '提示')
    return
  }

  try {
    isBatchDeleting.value = true
    
    // 调用删除接口
    await deleteIncidents(selectedIncidents.value)
    
    // 显示成功提示
    toast.success(
      t('incidents.list.batchDeleteDialog.deleteSuccess', { count: selectedIncidents.value.length }) || 
      `成功删除 ${selectedIncidents.value.length} 条事件`, 
      'SUCCESS'
    )
    
    // Close dialog and reset form
    closeBatchDeleteDialog()
    selectedIncidents.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    // Reload incident list
    loadIncidents()
  } catch (error) {
    console.error('Failed to delete incidents:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('incidents.list.batchDeleteDialog.deleteError') || '删除事件失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isBatchDeleting.value = false
  }
}

const openAISidebarFromList = () => {
  if (!incidents.value.length) {
    currentIncidentId.value = null
    currentTitle.value = ''
    findingSummary.value = ''
    showAISidebar.value = true
    return
  }

  const selectedId = selectedIncidents.value[0]
  const target =
    incidents.value.find(inc => inc.id === selectedId) ||
    incidents.value[0]

  currentIncidentId.value = target?.id ?? null
  currentTitle.value = target?.title || target?.name || ''
  findingSummary.value = target?.description || ''
  showAISidebar.value = true
}

// Close more menu when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.more-menu-button') && !event.target.closest('.more-menu-dropdown')) {
    showMoreMenu.value = false
  }
}

onMounted(() => {
  loadIncidents()
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
  // 监听 Header 发出的打开 AI 侧边栏事件
  window.addEventListener('open-ai-sidebar', openAISidebarFromList)
})

// Clean up event listener
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('open-ai-sidebar', openAISidebarFromList)
})
</script>


