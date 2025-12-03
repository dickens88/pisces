<template>
  <div class="w-full">
    <!-- Page title and actions -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('vulnerabilities.title') }}
        </h1>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="handleRefresh"
          :disabled="loadingVulnerabilities"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingVulnerabilities }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="vulnerabilities"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </header>

    <!-- Statistics charts -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <!-- Vulnerability trend statistics -->
      <div class="flex flex-col gap-2 rounded-xl border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#111822] p-6">
        <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
          {{ $t('vulnerabilities.statistics.trend') || 'Vulnerability Trend Statistics' }}
        </p>
        <div class="flex h-64 w-full flex-col justify-end relative">
          <!-- Loading state -->
          <div
            v-if="vulnerabilityTrendChartLoading"
            class="absolute inset-0 flex items-center justify-center"
          >
            <div class="flex flex-col items-center gap-2">
              <div class="relative w-8 h-8">
                <div class="absolute inset-0 border-2 border-primary/20 rounded-full"></div>
                <div class="absolute inset-0 border-2 border-transparent border-t-primary rounded-full animate-spin"></div>
              </div>
              <p class="text-gray-600 dark:text-gray-400 text-xs">{{ $t('common.loading') || '加载中...' }}</p>
            </div>
          </div>
          <!-- Empty state -->
          <div
            v-else-if="vulnerabilityTrendChartDates.length === 0"
            class="absolute inset-0 flex items-center justify-center"
          >
            <p class="text-gray-600 dark:text-gray-400 text-sm">{{ $t('common.noData') }}</p>
          </div>
          <!-- Chart container -->
          <div
            v-show="!vulnerabilityTrendChartLoading && vulnerabilityTrendChartDates.length > 0"
            ref="vulnerabilityTrendChartRef"
            class="w-full h-full min-h-[200px]"
          ></div>
        </div>
      </div>

      <!-- Vulnerability department distribution -->
      <div class="flex flex-col gap-2 rounded-xl border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#111822] p-6">
        <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
          {{ $t('vulnerabilities.statistics.departmentDistribution') }}
        </p>
        <div class="flex h-64 w-full flex-col justify-end relative">
          <!-- Loading state -->
          <div
            v-if="departmentChartLoading"
            class="absolute inset-0 flex items-center justify-center"
          >
            <div class="flex flex-col items-center gap-2">
              <div class="relative w-8 h-8">
                <div class="absolute inset-0 border-2 border-primary/20 rounded-full"></div>
                <div class="absolute inset-0 border-2 border-transparent border-t-primary rounded-full animate-spin"></div>
              </div>
              <p class="text-gray-600 dark:text-gray-400 text-xs">{{ $t('common.loading') || '加载中...' }}</p>
            </div>
          </div>
          <!-- Empty state -->
          <div
            v-else-if="departmentChartData.length === 0"
            class="absolute inset-0 flex items-center justify-center"
          >
            <p class="text-gray-600 dark:text-gray-400 text-sm">{{ $t('common.noData') }}</p>
          </div>
          <!-- Chart container -->
          <div
            v-show="!departmentChartLoading && departmentChartData.length > 0"
            ref="departmentChartRef"
            class="w-full h-full min-h-[200px]"
          ></div>
        </div>
      </div>
    </section>

    <!-- Vulnerability list table -->
    <section class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingVulnerabilities"
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
            :disabled="selectedVulnerabilities.length === 0"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
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
                @click="handleCreateVulnerability"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">add</span>
                <span>{{ $t('vulnerabilities.create.title') }}</span>
              </button>
              <button
                @click="openCloseVulnerabilityDialog"
                :disabled="selectedVulnerabilities.length !== 1"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">archive</span>
                <span>{{ $t('vulnerabilities.detail.closeVulnerability') }}</span>
              </button>
              <button
                @click="openBatchDeleteDialog"
                :disabled="selectedVulnerabilities.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">delete</span>
                <span>{{ $t('vulnerabilities.list.batchDelete') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      <DataTable
        ref="dataTableRef"
        :columns="columns"
        :items="vulnerabilities"
        :selectable="true"
        :resizable="true"
        storage-key="vulnerabilities-table-columns"
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
              @click.stop="openVulnerabilityDetailInNewWindow(item.id)"
              class="flex-shrink-0 text-gray-400 hover:text-primary transition-colors p-1"
              :title="$t('incidents.list.openInNewWindow') || '在新窗口打开'"
            >
              <span class="material-symbols-outlined text-base">open_in_new</span>
            </button>
            <router-link
              :to="`/vulnerabilities/${item.id}`"
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
      </DataTable>
    </section>

    <!-- Create vulnerability dialog -->
    <CreateVulnerabilityDialog
      :visible="showCreateDialog"
      @close="showCreateDialog = false"
      @created="handleVulnerabilityCreated"
    />

    <!-- Close vulnerability dialog -->
    <CloseIncidentDialog
      ref="closeVulnerabilityDialogRef"
      :visible="showCloseVulnerabilityDialog"
      :title="$t('vulnerabilities.detail.closeDialog.title') || '关闭漏洞'"
      :confirm-message="$t('vulnerabilities.detail.closeDialog.confirmMessage') || '确认要关闭此漏洞吗？'"
      @close="closeCloseVulnerabilityDialog"
      @submit="handleCloseVulnerability"
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
            {{ $t('vulnerabilities.list.batchDeleteDialog.title') }}
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
            {{ $t('vulnerabilities.list.batchDeleteDialog.confirmMessage', { count: selectedVulnerabilities.length }) }}
          </p>
        </div>

        <!-- Confirmation input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('vulnerabilities.list.batchDeleteDialog.confirmInputLabel') }}
          </label>
          <input
            v-model="deleteConfirmInput"
            @keydown.enter.prevent="handleBatchDelete"
            type="text"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
            :placeholder="$t('vulnerabilities.list.batchDeleteDialog.confirmInputPlaceholder')"
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getIncidents, getVulnerabilityTrendBySeverity, deleteIncidents } from '@/api/incidents'
import { 
  getVulnerabilityTrend, 
  getVulnerabilityDepartmentDistribution
} from '@/api/vulnerabilities'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import { formatDateTime, formatDateTimeWithOffset } from '@/utils/dateTime'
import { severityToNumber } from '@/utils/severity'
import { useToast } from '@/composables/useToast'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const toast = useToast()

// Dark mode detection
const isDarkMode = () => document.documentElement.classList.contains('dark')

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

const vulnerabilities = ref([])
const trendData = ref([])
const departmentData = ref([])
const dataTableRef = ref(null)
const loadingVulnerabilities = ref(false)
const showCreateDialog = ref(false)
const showMoreMenu = ref(false)
const showBatchDeleteDialog = ref(false)
const deleteConfirmInput = ref('')
const isBatchDeleting = ref(false)
const showCloseVulnerabilityDialog = ref(false)
const closeVulnerabilityDialogRef = ref(null)
const isClosingVulnerability = ref(false)
const authStore = useAuthStore()

// 从 localStorage 读取保存的搜索关键词
const getStoredSearchKeywords = () => {
  try {
    const stored = localStorage.getItem('vulnerabilities-searchKeywords')
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
const selectedVulnerabilities = ref([])
const currentPage = ref(1)

// 从 localStorage 读取保存的分页大小
const getStoredPageSize = () => {
  try {
    const stored = localStorage.getItem('vulnerabilities-pageSize')
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

// Time range picker
// Time range picker
const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('vulnerabilities', 'last30Days')

// Vulnerability trend chart
const vulnerabilityTrendChartRef = ref(null)
const vulnerabilityTrendChartDates = ref([])
const vulnerabilityTrendChartData = ref({})
const vulnerabilityTrendChartLoading = ref(false)
let vulnerabilityTrendChartInstance = null
let vulnerabilityTrendChartResizeBound = false

// Department distribution chart
const departmentChartRef = ref(null)
const departmentChartData = ref([])
const departmentChartLoading = ref(false)
let departmentChartInstance = null
let departmentChartResizeBound = false

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadVulnerabilities = async () => {
  loadingVulnerabilities.value = true
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
    // Add search_vulscan: true to indicate this is a vulnerability scan query
    const params = {
      action: 'list',
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      conditions,
      search_vulscan: true
    }

    if (range) {
      params.start_time = formatDateTimeWithOffset(range.start)
      params.end_time = formatDateTimeWithOffset(range.end)
    }
    
    const response = await getIncidents(params)
    vulnerabilities.value = response.data || []
    total.value = response.total || 0
  } catch (error) {
    console.error('Failed to load vulnerabilities:', error)
    vulnerabilities.value = []
    total.value = 0
  } finally {
    loadingVulnerabilities.value = false
  }
}

// Chart initialization and management
const handleVulnerabilityTrendResize = () => {
  if (vulnerabilityTrendChartInstance) {
    vulnerabilityTrendChartInstance.resize()
  }
}

const ensureVulnerabilityTrendChart = () => {
  if (!vulnerabilityTrendChartInstance && vulnerabilityTrendChartRef.value) {
    vulnerabilityTrendChartInstance = echarts.init(vulnerabilityTrendChartRef.value)
    if (!vulnerabilityTrendChartResizeBound) {
      window.addEventListener('resize', handleVulnerabilityTrendResize)
      vulnerabilityTrendChartResizeBound = true
    }
  }
}

const disposeVulnerabilityTrendChart = () => {
  if (vulnerabilityTrendChartInstance) {
    vulnerabilityTrendChartInstance.dispose()
    vulnerabilityTrendChartInstance = null
  }
  if (vulnerabilityTrendChartResizeBound) {
    window.removeEventListener('resize', handleVulnerabilityTrendResize)
    vulnerabilityTrendChartResizeBound = false
  }
}

const updateVulnerabilityTrendChart = () => {
  ensureVulnerabilityTrendChart()
  if (!vulnerabilityTrendChartInstance) {
    return
  }

  vulnerabilityTrendChartInstance.clear()

  // Calculate time range to determine label format
  const range = computeSelectedRange()
  const daysDiff = Math.ceil((range.end - range.start) / (1000 * 60 * 60 * 24))
  
  // Format dates for display based on time range
  const formatDateLabel = (dateStr, index) => {
    const date = new Date(dateStr)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const year = date.getFullYear()
    
    // Adjust format based on time range
    if (daysDiff <= 30) {
      // Show day: MM/DD
      return `${month}/${day}`
    } else if (daysDiff <= 90) {
      // Show day: MM/DD (but with interval to reduce clutter)
      return `${month}/${day}`
    } else if (daysDiff <= 365) {
      // Show month-day: MM/DD (but with interval)
      // For longer ranges, show month abbreviation for first day of month
      if (day === '01' || index === 0) {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return `${monthNames[date.getMonth()]} ${day}`
      }
      return `${month}/${day}`
    } else {
      // Show year-month: YYYY-MM (for data spanning more than a year)
      // Show month label on the 1st of each month, or first/last date
      const isFirstOfMonth = day === '01'
      const isFirstDate = index === 0
      const isLastDate = index === vulnerabilityTrendChartDates.value.length - 1
      
      if (isFirstOfMonth) {
        // For first of month, show YYYY-MM
        return `${year}-${month}`
      } else if (isFirstDate || isLastDate) {
        // For first/last date, show full date
        return `${year}-${month}-${day}`
      } else {
        // For other dates, show month/day but interval will control visibility
        return `${month}/${day}`
      }
    }
  }
  
  // Get data points count
  const dataPoints = vulnerabilityTrendChartDates.value.length
  
  // Calculate interval for x-axis labels based on data points
  const calculateLabelInterval = () => {
    if (daysDiff <= 30) {
      // Show every day if <= 30 days
      return 0
    } else if (daysDiff <= 90) {
      // Show every 3-5 days (about 20 labels max)
      return Math.max(0, Math.floor(dataPoints / 20))
    } else if (daysDiff <= 365) {
      // Show every week or so (about 15 labels max)
      return Math.max(0, Math.floor(dataPoints / 15))
    } else {
      // Show monthly (about 12 labels max)
      return Math.max(0, Math.floor(dataPoints / 12))
    }
  }
  
  const labelInterval = calculateLabelInterval()
  
  // Determine if labels should be rotated based on data points count
  // Rotate when there are many data points to prevent overlap
  const shouldRotateLabels = dataPoints > 10 || daysDiff > 7
  const labelRotation = shouldRotateLabels ? -45 : 0  // -45 degrees for downward rotation
  const bottomMargin = shouldRotateLabels ? 50 : 30  // Increase bottom margin for rotated labels

  // Severity colors mapping
  const severityColors = {
    'Critical': '#FF4D4F',
    'High': '#FF7A45',
    'Medium': '#FFA940',
    'Low': '#1890FF',
    'Unknown': '#8C8C8C'
  }

  // Severity order (exclude Unknown from legend)
  const severityOrder = ['Critical', 'High', 'Medium', 'Low']

  // Build series data for each severity (exclude Unknown)
  const series = severityOrder
    .filter(severity => vulnerabilityTrendChartData.value[severity])
    .map(severity => ({
      name: t(`common.severity.${severity.toLowerCase()}`) || severity,
      type: 'line',
      data: vulnerabilityTrendChartDates.value.map(date => {
        return vulnerabilityTrendChartData.value[severity]?.[date] || 0
      }),
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: {
        color: severityColors[severity] || severityColors['Unknown'],
        width: 2
      },
      itemStyle: {
        color: severityColors[severity] || severityColors['Unknown']
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: `${severityColors[severity] || severityColors['Unknown']}40` },
          { offset: 1, color: `${severityColors[severity] || severityColors['Unknown']}00` }
        ])
      }
    }))

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderWidth: 0,
      textStyle: { color: '#e2e8f0' },
      padding: [10, 12]
    },
    legend: {
      data: severityOrder
        .filter(severity => severity !== 'Unknown' && vulnerabilityTrendChartData.value[severity])
        .map(severity => t(`common.severity.${severity.toLowerCase()}`) || severity),
      textStyle: {
        color: '#94a3b8',
        fontSize: 11
      },
      top: 5,
      itemWidth: 12,
      itemHeight: 8
    },
    grid: {
      top: 40,
      right: 10,
      bottom: bottomMargin,
      left: 40,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: vulnerabilityTrendChartDates.value.map((date, index) => formatDateLabel(date, index)),
      boundaryGap: false,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        rotate: labelRotation,
        interval: labelInterval,
        margin: shouldRotateLabels ? 12 : 8,
        // Auto hide labels if too many
        showMinLabel: true,
        showMaxLabel: true
      },
      axisLine: {
        show: true,
        lineStyle: { color: '#334155' }
      },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#94a3b8', margin: 0, fontSize: 10 },
      splitLine: {
        lineStyle: { color: '#1f2a37' }
      },
      axisLine: { show: true, lineStyle: { color: '#334155' } },
      axisTick: { show: true, inside: true }
    },
    series: series
  }

  vulnerabilityTrendChartInstance.setOption(option, true)
  nextTick(() => {
    vulnerabilityTrendChartInstance.resize()
  })
}

// Format dates for backend (ISO format without Z)
const formatDateForBackend = (date) => {
  const isoString = date.toISOString()
  return isoString.includes('.') ? isoString.split('.')[0] : isoString.replace('Z', '')
}

// Compute selected time range
const computeSelectedRange = () => {
  if (selectedTimeRange.value === 'customRange' && customTimeRange.value && customTimeRange.value.length === 2) {
    return {
      start: new Date(customTimeRange.value[0]),
      end: new Date(customTimeRange.value[1])
    }
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
      start.setDate(start.getDate() - 30)
      break
  }

  return { start, end }
}

// Load vulnerability trend data by severity
const loadVulnerabilityTrendBySeverity = async () => {
  vulnerabilityTrendChartLoading.value = true
  try {
    // Calculate date range from time picker
    const range = computeSelectedRange()

    const response = await getVulnerabilityTrendBySeverity(
      range.start,
      range.end
    )

    const trendData = response?.data || []

    // Extract unique dates
    const dates = [...new Set(trendData.map(item => item.date))].sort()
    vulnerabilityTrendChartDates.value = dates

    // Group data by severity
    const dataBySeverity = {}
    trendData.forEach(item => {
      const severity = item.severity || 'Unknown'
      if (!dataBySeverity[severity]) {
        dataBySeverity[severity] = {}
      }
      dataBySeverity[severity][item.date] = Number(item.count) || 0
    })

    vulnerabilityTrendChartData.value = dataBySeverity
  } catch (error) {
    console.error('Failed to load vulnerability trend by severity:', error)
    vulnerabilityTrendChartDates.value = []
    vulnerabilityTrendChartData.value = {}
  } finally {
    vulnerabilityTrendChartLoading.value = false
    await nextTick()
    updateVulnerabilityTrendChart()
  }
}

// Load trend data (deprecated, kept for compatibility)
const loadTrendData = async () => {
  try {
    const response = await getVulnerabilityTrend()
    trendData.value = response.data
  } catch (error) {
    console.error('Failed to load trend data:', error)
  }
}

// Department distribution chart management
const handleDepartmentChartResize = () => {
  if (departmentChartInstance) {
    departmentChartInstance.resize()
  }
}

const ensureDepartmentChart = () => {
  if (!departmentChartInstance && departmentChartRef.value) {
    departmentChartInstance = echarts.init(departmentChartRef.value)
    if (!departmentChartResizeBound) {
      window.addEventListener('resize', handleDepartmentChartResize)
      departmentChartResizeBound = true
    }
  }
}

const disposeDepartmentChart = () => {
  if (departmentChartInstance) {
    departmentChartInstance.dispose()
    departmentChartInstance = null
  }
  if (departmentChartResizeBound) {
    window.removeEventListener('resize', handleDepartmentChartResize)
    departmentChartResizeBound = false
  }
}

const updateDepartmentChart = () => {
  ensureDepartmentChart()
  if (!departmentChartInstance) {
    return
  }

  departmentChartInstance.clear()

  if (departmentChartData.value.length === 0) {
    return
  }

  // Prepare data for Nightingale Chart
  const chartData = departmentChartData.value.map(item => ({
    name: item.name || 'Unknown',
    value: item.value || 0
  }))

  // Color palette matching the theme
  const colors = [
    '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af',
    '#8b5cf6', '#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95',
    '#ec4899', '#db2777', '#be185d', '#9f1239', '#831843',
    '#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f'
  ]

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderWidth: 0,
      textStyle: { color: '#e2e8f0' },
      padding: [10, 12]
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        color: isDarkMode() ? '#94a3b8' : '#374151',
        fontSize: 11
      },
      itemWidth: 12,
      itemHeight: 8,
      itemGap: 8
    },
    series: [
      {
        name: t('vulnerabilities.statistics.departmentDistribution') || 'Department Distribution',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        roseType: 'area',
        itemStyle: {
          borderRadius: 4,
          borderColor: isDarkMode() ? '#111822' : '#ffffff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          color: isDarkMode() ? '#e2e8f0' : '#374151',
          fontSize: 10
        },
        labelLine: {
          show: true,
          length: 10,
          length2: 5,
          lineStyle: {
            color: isDarkMode() ? '#94a3b8' : '#9ca3af'
          }
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 12,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: chartData,
        color: colors
      }
    ]
  }

  departmentChartInstance.setOption(option, true)
  nextTick(() => {
    departmentChartInstance.resize()
  })
}

// Load department distribution data
const loadDepartmentData = async () => {
  departmentChartLoading.value = true
  try {
    // Calculate date range from time picker
    const range = computeSelectedRange()

    const response = await getVulnerabilityDepartmentDistribution(
      range.start,
      range.end
    )

    const distribution = response?.data || {}
    
    // Convert dictionary to array format for chart
    const entries = Object.entries(distribution)
      .map(([name, value]) => ({
        name: name || 'Unknown',
        value: Number(value) || 0
      }))
      .filter(item => item.value > 0) // Filter out zero values
      .sort((a, b) => b.value - a.value) // Sort by value descending

    departmentChartData.value = entries
    departmentData.value = entries // Keep for backward compatibility if needed
  } catch (error) {
    console.error('Failed to load department data:', error)
    departmentChartData.value = []
    departmentData.value = []
  } finally {
    departmentChartLoading.value = false
    await nextTick()
    updateDepartmentChart()
  }
}

/**
 * @brief 刷新漏洞列表
 */
const handleRefresh = async () => {
  await Promise.all([
    loadVulnerabilities(),
    loadVulnerabilityTrendBySeverity(),
    loadDepartmentData()
  ])
}

// 保存搜索关键词到 localStorage
const saveSearchKeywords = () => {
  try {
    localStorage.setItem('vulnerabilities-searchKeywords', JSON.stringify(searchKeywords.value))
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
    loadVulnerabilities()
  }
}

/**
 * @brief 删除搜索关键字
 * @param {number} index - 要删除的关键字索引
 */
const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  saveSearchKeywords()
  loadVulnerabilities()
}

/**
 * @brief 处理搜索输入
 * @details 实时搜索功能（可选，如果需要实时搜索可以启用）
 */
const handleSearchInput = () => {
  // If real-time search is needed, call loadVulnerabilities() here
  // Currently only searches when adding/removing keywords
}

/**
 * @brief 处理筛选器变化
 */
const handleFilter = () => {
  loadVulnerabilities()
}

const handleSelect = (items) => {
  selectedVulnerabilities.value = items.map(vulnerability => vulnerability.id)
}

const handleSelectAll = (items) => {
  selectedVulnerabilities.value = items.map(vulnerability => vulnerability.id)
}

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = newPageSize
  currentPage.value = 1
  // 保存到 localStorage
  try {
    localStorage.setItem('vulnerabilities-pageSize', String(newPageSize))
  } catch (error) {
    console.warn('Failed to save page size to localStorage:', error)
  }
  loadVulnerabilities()
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

const openVulnerabilityDetailInNewWindow = (vulnerabilityId) => {
  // Open vulnerability detail in a new window
  const route = router.resolve({ path: `/vulnerabilities/${vulnerabilityId}` })
  // Build complete URL
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    // Load data based on selected time range
    loadVulnerabilities()
    loadVulnerabilityTrendBySeverity()
    loadDepartmentData()
  }
}

const handleCustomRangeChange = (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    loadVulnerabilities()
    loadVulnerabilityTrendBySeverity()
    loadDepartmentData()
  }
}

const handleVulnerabilityCreated = () => {
  // 刷新漏洞列表
  loadVulnerabilities()
  loadVulnerabilityTrendBySeverity()
  loadDepartmentData()
}

// Delete confirmation validation
const isDeleteConfirmValid = computed(() => {
  return deleteConfirmInput.value.toLowerCase() === 'delete'
})

const openBatchDeleteDialog = () => {
  if (selectedVulnerabilities.value.length === 0) {
    console.warn('No vulnerabilities selected')
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

  if (selectedVulnerabilities.value.length === 0) {
    toast.warn('请至少选择一个漏洞', '提示')
    return
  }

  try {
    isBatchDeleting.value = true
    
    // 调用删除接口（使用和删除事件相同的接口）
    await deleteIncidents(selectedVulnerabilities.value, 'asm')
    
    // 显示成功提示
    toast.success(
      t('vulnerabilities.list.batchDeleteDialog.deleteSuccess', { count: selectedVulnerabilities.value.length }) || 
      `成功删除 ${selectedVulnerabilities.value.length} 条漏洞`, 
      'SUCCESS'
    )
    
    // Close dialog and reset form
    closeBatchDeleteDialog()
    selectedVulnerabilities.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    // Reload vulnerability list
    loadVulnerabilities()
    loadVulnerabilityTrendBySeverity()
    loadDepartmentData()
  } catch (error) {
    console.error('Failed to delete vulnerabilities:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('vulnerabilities.list.batchDeleteDialog.deleteError') || '删除漏洞失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isBatchDeleting.value = false
  }
}

const handleCreateVulnerability = () => {
  showMoreMenu.value = false
  showCreateDialog.value = true
}

const openCloseVulnerabilityDialog = () => {
  if (selectedVulnerabilities.value.length !== 1) {
    toast.warn('请选择一个漏洞', '提示')
    return
  }
  showMoreMenu.value = false
  showCloseVulnerabilityDialog.value = true
}

const closeCloseVulnerabilityDialog = () => {
  showCloseVulnerabilityDialog.value = false
}

const handleCloseVulnerability = async (data) => {
  if (isClosingVulnerability.value) {
    return
  }

  if (selectedVulnerabilities.value.length !== 1) {
    toast.warn('请选择一个漏洞', '提示')
    return
  }

  try {
    isClosingVulnerability.value = true
    if (closeVulnerabilityDialogRef.value) {
      closeVulnerabilityDialogRef.value.setSubmitting(true)
    }
    
    const vulnerabilityId = selectedVulnerabilities.value[0]
    const body = {
      handle_status: 'Closed',
      close_reason: data.close_reason,
      close_comment: data.close_comment,
      search_vulscan: true
    }

    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/vulnerabilities/${vulnerabilityId}` : `/api/vulnerabilities/${vulnerabilityId}`
    
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    await axios.put(url, body, { headers })
    
    toast.success(t('vulnerabilities.detail.closeSuccess') || '漏洞关闭成功', 'SUCCESS')
    
    closeCloseVulnerabilityDialog()
    
    // 清除选择并刷新列表
    selectedVulnerabilities.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    await loadVulnerabilities()
    loadVulnerabilityTrendBySeverity()
    loadDepartmentData()
  } catch (error) {
    console.error('Failed to close vulnerability:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('vulnerabilities.detail.closeError') || '漏洞关闭失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isClosingVulnerability.value = false
    if (closeVulnerabilityDialogRef.value) {
      closeVulnerabilityDialogRef.value.setSubmitting(false)
    }
  }
}

// Close more menu when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.more-menu-button') && !event.target.closest('.more-menu-dropdown')) {
    showMoreMenu.value = false
  }
}

watch([currentPage, pageSize], () => {
  loadVulnerabilities()
})

onMounted(() => {
  loadVulnerabilities()
  loadVulnerabilityTrendBySeverity()
  loadDepartmentData()
  ensureVulnerabilityTrendChart()
  ensureDepartmentChart()
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  disposeVulnerabilityTrendChart()
  disposeDepartmentChart()
  // Clean up event listener
  document.removeEventListener('click', handleClickOutside)
})
</script>


