<template>
  <div class="w-full">
    <!-- Page header -->
    <header class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em]">
        {{ $t('alerts.title') }}
      </h1>
      <div class="flex gap-2 items-center">
        <button
          @click="handleRefresh"
          :disabled="isRefreshing"
          class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': isRefreshing }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="alerts"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
        <button
          @click="openCreateAlertDialog"
          class="flex items-center justify-center gap-2 rounded-lg h-10 bg-primary text-white text-sm font-bold px-4 hover:bg-blue-500 transition-colors"
        >
          <span class="material-symbols-outlined text-base">add</span>
          <span>{{ $t('alerts.list.createAlert') }}</span>
        </button>
      </div>
    </header>

    <!-- Statistics cards -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.alertTypeStats') }}
        </p>
        <p class="text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ alertTypeChartTotal.toLocaleString() }}
        </p>
        <p class="text-gray-400 text-sm font-normal leading-normal">
          {{ alertsTimeRangeLabel }}
        </p>
        <div class="relative h-40 w-full">
          <div
            v-if="alertTypeChartLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="alertTypeChartValues.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
          >
            {{ $t('common.noData') }}
          </div>
          <div
            v-show="!alertTypeChartLoading && alertTypeChartValues.length > 0"
            ref="alertTypeChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.alertTrend') }}
        </p>
        <p class="text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ statistics.alertCount || 0 }}
        </p>
        <p class="text-gray-400 text-sm font-normal leading-normal">
          {{ alertsTimeRangeLabel }}
        </p>
        <div class="relative h-40 w-full">
          <div
            v-if="alertTrendChartLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="alertTrendChartValues.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
          >
            {{ $t('common.noData') }}
          </div>
          <div
            v-show="!alertTrendChartLoading && alertTrendChartValues.length > 0"
            ref="alertTrendChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.automationClosureRate') }}
        </p>
        <p class="text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ statistics.automationRate || '0' }}%
        </p>
        <p class="text-gray-400 text-sm font-normal leading-normal">
          {{ alertsTimeRangeLabel }}
        </p>
        <div class="relative h-40 w-full">
          <div
            v-if="automationRateLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="!statistics.totalClosed && !statistics.autoClosed"
            class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
          >
            {{ $t('common.noData') }}
          </div>
          <div
            v-show="!automationRateLoading && (statistics.totalClosed || statistics.autoClosed)"
            class="absolute inset-0 flex flex-col justify-between py-3"
          >
            <!-- Progress bar -->
            <div class="relative h-6 w-full bg-[#233348] rounded-full mt-4">
              <div
                class="bg-primary h-6 rounded-full transition-all"
                :style="{ width: (statistics.automationRate || 0) + '%' }"
              ></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-white text-sm font-medium">{{ statistics.automationRate || '0' }}%</span>
              </div>
            </div>
            <!-- Two metrics -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-gray-400 text-xs font-medium mb-1">{{ $t('alerts.list.statistics.autoClosed') }}</p>
                <p class="text-white text-2xl font-bold">{{ (statistics.autoClosed || 0).toLocaleString() }}</p>
              </div>
              <div class="text-right">
                <p class="text-gray-400 text-xs font-medium mb-1">{{ $t('alerts.list.statistics.totalAlerts') }}</p>
                <p class="text-white text-2xl font-bold">{{ (statistics.totalClosed || 0).toLocaleString() }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Alert list table -->
    <section class="bg-[#111822] border border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingAlerts"
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
              :placeholder="searchKeywords.length === 0 ? $t('alerts.list.searchPlaceholder') : ''"
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
              <option value="all">{{ $t('alerts.list.allStatus') }}</option>
              <option value="open">{{ $t('alerts.list.open') }}</option>
              <option value="block">{{ $t('alerts.list.block') }}</option>
              <option value="closed">{{ $t('alerts.list.closed') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>
          <button
            :disabled="selectedAlerts.length === 0"
            @click="openBatchCloseDialog"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
            <span>{{ $t('alerts.list.batchClose') }}</span>
          </button>
          <button
            :disabled="selectedAlerts.length === 0"
            @click="openAssociateIncidentDialog"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">link</span>
            <span>{{ $t('alerts.list.associateIncident') }}</span>
          </button>
          <button
            :disabled="selectedAlerts.length === 0"
            @click="openCreateIncidentDialog"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">transform</span>
            <span>{{ $t('alerts.list.batchConvert') }}</span>
          </button>
          <!-- More actions button -->
          <div class="relative">
            <button
              @click="showMoreMenu = !showMoreMenu"
              class="more-menu-button flex items-center justify-center rounded-lg h-10 w-10 bg-[#233348] text-white hover:bg-[#324867] transition-colors"
              :title="$t('common.more')"
            >
              <span class="material-symbols-outlined text-base">more_vert</span>
            </button>
            <!-- Dropdown menu -->
            <div
              v-if="showMoreMenu"
              class="more-menu-dropdown absolute right-0 top-full mt-2 bg-[#233348] border border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
            >
              <button
                @click="handleToggleWordWrap"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-white hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">
                  {{ isWordWrap ? 'wrap_text' : 'text_fields' }}
                </span>
                <span>{{ isWordWrap ? $t('common.wordWrap') : $t('common.singleLine') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <DataTable
        ref="dataTableRef"
        :columns="columns"
        :items="alerts"
        :selectable="true"
        :resizable="true"
        storage-key="alerts-table-columns"
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
        <template #cell-createTime="{ value, item }">
          {{ formatDateTime(value || item?.createTime || item?.create_time) }}
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
    </section>

    <!-- Alert detail drawer -->
    <AlertDetail
      v-if="currentAlertId"
      :alert-id="currentAlertId"
      @close="closeAlertDetail"
      @closed="handleAlertClosed"
      @created="handleAlertConvertedToIncident"
    />

    <!-- Create incident dialog -->
    <CreateIncidentDialog
      :visible="showCreateIncidentDialog"
      :initial-data="createIncidentInitialData"
      :alert-ids="selectedAlerts"
      @close="closeCreateIncidentDialog"
      @created="handleIncidentCreated"
    />

    <!-- Create alert dialog -->
    <CreateAlertDialog
      :visible="showCreateAlertDialog"
      @close="closeCreateAlertDialog"
      @created="handleAlertCreated"
    />

    <!-- Associate incident dialog -->
    <AssociateIncidentDialog
      :visible="showAssociateIncidentDialog"
      :alert-ids="selectedAlerts"
      @close="closeAssociateIncidentDialog"
      @associated="handleAssociateIncidentSuccess"
    />

    <!-- Batch close dialog -->
    <div
      v-if="showBatchCloseDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeBatchCloseDialog"
    >
      <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">
            {{ $t('alerts.list.batchCloseDialog.title') }}
          </h2>
          <button
            @click="closeBatchCloseDialog"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('alerts.list.batchCloseDialog.confirmMessage', { count: selectedAlerts.length }) }}
          </p>
        </div>

        <!-- Conclusion category dropdown -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusionCategory') }}
          </label>
          <select
            v-model="closeConclusion.category"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">{{ $t('alerts.list.batchCloseDialog.selectCategory') }}</option>
            <option value="falsePositive">{{ $t('alerts.list.batchCloseDialog.categories.falsePositive') }}</option>
            <option value="resolved">{{ $t('alerts.list.batchCloseDialog.categories.resolved') }}</option>
            <option value="repeated">{{ $t('alerts.list.batchCloseDialog.categories.repeated') }}</option>
            <option value="other">{{ $t('alerts.list.batchCloseDialog.categories.other') }}</option>
          </select>
        </div>

        <!-- Investigation conclusion input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusion') }}
          </label>
          <textarea
            v-model="closeConclusion.notes"
            rows="4"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
            :placeholder="$t('alerts.list.batchCloseDialog.conclusionPlaceholder')"
          ></textarea>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchCloseDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchClose"
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim() || isBatchClosing"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isBatchClosing" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getAlerts, getAlertStatistics, batchCloseAlerts, batchCloseAlertsByPut, getAlertCountsBySource, getAlertTrend, closeAlert } from '@/api/alerts'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import CreateAlertDialog from '@/components/alerts/CreateAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const toast = useToast()



// Define column configuration (using computed to ensure reactivity)
const columns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'owner', label: t('alerts.list.owner') }
])

// Default column widths
const defaultWidths = {
  createTime: 200, // Adjusted to 200 to fit yyyy-MM-dd HH:mm:ss format
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  owner: 50
}

const alerts = ref([])
const loadingAlerts = ref(false)
const isRefreshing = ref(false)
const dataTableRef = ref(null)
const statistics = ref({
  totalAlerts: 0,
  trend: 0,
  alertCount: 0,
  alertTrend: 0,
  automationRate: 0,
  automationRateChange: 0,
  automationRateTrend: 'down',
  totalClosed: 0,
  autoClosed: 0,
  typeStats: []
})

// 从 localStorage 读取保存的搜索关键词
const getStoredSearchKeywords = () => {
  try {
    const stored = localStorage.getItem('alerts-searchKeywords')
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
// 从localStorage读取保存的status筛选器设置，如果没有则默认为'all'
const getStoredStatusFilter = () => {
  try {
    const stored = localStorage.getItem('alerts-status-filter')
    // 验证存储的值是否有效
    if (stored && ['all', 'open', 'block', 'closed'].includes(stored)) {
      return stored
    }
  } catch (error) {
    console.warn('Failed to read status filter from localStorage:', error)
  }
  return 'all'
}
const statusFilter = ref(getStoredStatusFilter())
const selectedAlerts = ref([])
const currentPage = ref(1)

// 从 localStorage 读取保存的分页大小
const getStoredPageSize = () => {
  try {
    const stored = localStorage.getItem('alerts-pageSize')
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
// 从 localStorage 读取保存的时间范围
const getStoredTimeRange = () => {
  try {
    const stored = localStorage.getItem('alerts-timeRange')
    if (stored && ['last24Hours', 'last3Days', 'last7Days', 'last30Days', 'last3Months', 'customRange'].includes(stored)) {
      return stored
    }
  } catch (error) {
    console.warn('Failed to read time range from localStorage:', error)
  }
  return 'last24Hours'
}

// 从 localStorage 读取保存的自定义时间范围
const getStoredCustomRange = () => {
  try {
    const stored = localStorage.getItem('alerts-customTimeRange')
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
const showBatchCloseDialog = ref(false)
const isBatchClosing = ref(false)
const closeConclusion = ref({
  category: '',
  notes: ''
})
const showAssociateIncidentDialog = ref(false)
const showCreateIncidentDialog = ref(false)
const createIncidentInitialData = ref(null)
const showCreateAlertDialog = ref(false)
const showMoreMenu = ref(false)

const alertTypeChartRef = ref(null)
const alertTypeChartCategories = ref([])
const alertTypeChartValues = ref([])
const alertTypeChartLoading = ref(false)
const alertTypeChartTotal = ref(0)

let alertTypeChartInstance = null
let alertTypeChartResizeBound = false

const alertTrendChartRef = ref(null)
const alertTrendChartDates = ref([])
const alertTrendChartValues = ref([])
const alertTrendChartLoading = ref(false)

let alertTrendChartInstance = null
let alertTrendChartResizeBound = false

const automationRateLoading = ref(false)

const formatDateForBackend = (date) => {
  const isoString = date.toISOString()
  return isoString.includes('.') ? isoString.split('.')[0] : isoString.replace('Z', '')
}

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
      start.setHours(start.getHours() - 24)
      break
  }

  return { start, end }
}

const handleAlertTypeResize = () => {
  if (alertTypeChartInstance) {
    alertTypeChartInstance.resize()
  }
}

const handleAlertTrendResize = () => {
  if (alertTrendChartInstance) {
    alertTrendChartInstance.resize()
  }
}

const ensureAlertTypeChart = () => {
  if (!alertTypeChartInstance && alertTypeChartRef.value) {
    alertTypeChartInstance = echarts.init(alertTypeChartRef.value)
    if (!alertTypeChartResizeBound) {
      window.addEventListener('resize', handleAlertTypeResize)
      alertTypeChartResizeBound = true
    }
  }
}

const disposeAlertTypeChart = () => {
  if (alertTypeChartInstance) {
    alertTypeChartInstance.dispose()
    alertTypeChartInstance = null
  }
  if (alertTypeChartResizeBound) {
    window.removeEventListener('resize', handleAlertTypeResize)
    alertTypeChartResizeBound = false
  }
}

const ensureAlertTrendChart = () => {
  if (!alertTrendChartInstance && alertTrendChartRef.value) {
    alertTrendChartInstance = echarts.init(alertTrendChartRef.value)
    if (!alertTrendChartResizeBound) {
      window.addEventListener('resize', handleAlertTrendResize)
      alertTrendChartResizeBound = true
    }
  }
}

const disposeAlertTrendChart = () => {
  if (alertTrendChartInstance) {
    alertTrendChartInstance.dispose()
    alertTrendChartInstance = null
  }
  if (alertTrendChartResizeBound) {
    window.removeEventListener('resize', handleAlertTrendResize)
    alertTrendChartResizeBound = false
  }
}

const updateAlertTypeChart = () => {
  ensureAlertTypeChart()
  if (!alertTypeChartInstance) {
    return
  }

  // Clear previous option to ensure new settings take effect
  alertTypeChartInstance.clear()

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderWidth: 0,
      textStyle: { color: '#e2e8f0' },
      padding: [10, 12]
    },
    grid: {
      top: 5,
      right: 5,
      bottom: 25,
      left: 20,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: alertTypeChartCategories.value,
      boundaryGap: true,
      axisLabel: {
        color: '#cbd5f5',
        rotate: alertTypeChartCategories.value.length > 5 ? 20 : 0,
        margin: 8,
        fontSize: 10
      },
      axisLine: {
        show: true,
        lineStyle: { color: '#334155' }
      },
      axisTick: { show: true, inside: true, alignWithLabel: true }
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
    series: [
      {
        name: t('alerts.title'),
        type: 'bar',
        data: alertTypeChartValues.value,
        barWidth: '45%',
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#60a5fa' },
            { offset: 0.7, color: '#3b82f6' },
            { offset: 1, color: '#2563eb' }
          ])
        }
      }
    ]
  }

  alertTypeChartInstance.setOption(option, true)
  // Force resize to ensure grid changes take effect
  nextTick(() => {
    alertTypeChartInstance.resize()
  })
}

const loadAlertTypeDistribution = async () => {
  alertTypeChartLoading.value = true
  alertTypeChartTotal.value = 0
  try {
    const range = computeSelectedRange()
    const response = await getAlertCountsBySource(
      range.start,
      range.end,
      statusFilter.value
    )
    const counts = response?.data || {}
    const entries = Object.entries(counts).map(([name, value]) => [name, Number(value) || 0])
    entries.sort((a, b) => b[1] - a[1])
    alertTypeChartCategories.value = entries.map(([name]) => name)
    alertTypeChartValues.value = entries.map(([, value]) => value)
    alertTypeChartTotal.value = alertTypeChartValues.value.reduce((sum, value) => sum + value, 0)
  } catch (error) {
    console.error('Failed to load alert type distribution:', error)
    alertTypeChartCategories.value = []
    alertTypeChartValues.value = []
    alertTypeChartTotal.value = 0
  } finally {
    alertTypeChartLoading.value = false
    await nextTick()
    updateAlertTypeChart()
  }
}

const updateAlertTrendChart = () => {
  ensureAlertTrendChart()
  if (!alertTrendChartInstance) {
    return
  }

  // Clear previous option to ensure new settings take effect
  alertTrendChartInstance.clear()

  // Format dates for display (show date)
  const formatDateLabel = (dateStr) => {
    const date = new Date(dateStr)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${month}/${day}`
  }

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
    grid: {
      top: 5,
      right: 5,
      bottom: 25,
      left: 20,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: alertTrendChartDates.value.map(formatDateLabel),
      boundaryGap: false,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10
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
    series: [
      {
        name: t('alerts.title'),
        type: 'line',
        data: alertTrendChartValues.value,
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: {
          color: '#2b7cee',
          width: 3
        },
        itemStyle: {
          color: '#2b7cee'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(43, 124, 238, 0.4)' },
            { offset: 1, color: 'rgba(43, 124, 238, 0)' }
          ])
        }
      }
    ]
  }

  alertTrendChartInstance.setOption(option, true)
  // Force resize to ensure grid changes take effect
  nextTick(() => {
    alertTrendChartInstance.resize()
  })
}

const loadAlertTrend = async () => {
  alertTrendChartLoading.value = true
  try {
    const range = computeSelectedRange()
    const response = await getAlertTrend(
      range.start,
      range.end
    )
    const trendData = response?.data || []
    alertTrendChartDates.value = trendData.map(item => item.date)
    alertTrendChartValues.value = trendData.map(item => Number(item.count) || 0)
    // Calculate total alert count from trend data
    statistics.value.alertCount = alertTrendChartValues.value.reduce((sum, count) => sum + count, 0)
  } catch (error) {
    console.error('Failed to load alert trend:', error)
    alertTrendChartDates.value = []
    alertTrendChartValues.value = []
    statistics.value.alertCount = 0
  } finally {
    alertTrendChartLoading.value = false
    await nextTick()
    updateAlertTrendChart()
  }
}


const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadAlerts = async () => {
  loadingAlerts.value = true
  try {
    const params = {
      searchKeywords: searchKeywords.value,
      status: statusFilter.value,
      page: currentPage.value,
      pageSize: pageSize.value
    }
    
    const range = computeSelectedRange()
    if (range) {
      params.startTime = range.start
      params.endTime = range.end
    }
    
    const response = await getAlerts(params)
    alerts.value = response.data
    total.value = response.total
    
  } catch (error) {
    console.error('Failed to load alerts:', error)
  } finally {
    loadingAlerts.value = false
  }
}

const handleRefresh = async () => {
  if (isRefreshing.value) return
  
  isRefreshing.value = true
  try {
    await Promise.all([
      loadAlerts(),
      loadStatistics()
    ])
  } catch (error) {
    console.error('Failed to refresh:', error)
  } finally {
    isRefreshing.value = false
  }
}

const loadStatistics = async () => {
  automationRateLoading.value = true
  try {
    const response = await getAlertStatistics()
    // Merge response data instead of completely replacing to preserve alertCount set by loadAlertTrend
    if (response && response.data) {
      // Map API response fields to frontend statistics fields
      if (response.data.automation_rate !== undefined) {
        statistics.value.automationRate = response.data.automation_rate
      }
      if (response.data.total_closed !== undefined) {
        statistics.value.totalClosed = response.data.total_closed
      }
      if (response.data.auto_closed !== undefined) {
        statistics.value.autoClosed = response.data.auto_closed
      }
      // For now, set default trend values (can be enhanced later to calculate from historical data)
      if (statistics.value.automationRateChange === 0) {
        statistics.value.automationRateChange = 0
        statistics.value.automationRateTrend = 'down'
      }
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    automationRateLoading.value = false
  }
}

// 保存搜索关键词到 localStorage
const saveSearchKeywords = () => {
  try {
    localStorage.setItem('alerts-searchKeywords', JSON.stringify(searchKeywords.value))
  } catch (error) {
    console.warn('Failed to save search keywords to localStorage:', error)
  }
}

/**
 * @brief 添加搜索关键字
 * @details 当用户按回车时，将当前输入添加到关键字列表
 */
const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && !searchKeywords.value.includes(keyword)) {
    searchKeywords.value.push(keyword)
    currentSearchInput.value = ''
    saveSearchKeywords()
    loadAlerts()
  }
}

/**
 * @brief 删除搜索关键字
 * @param {number} index - 要删除的关键字索引
 */
const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  saveSearchKeywords()
  loadAlerts()
}

/**
 * @brief 处理搜索输入
 * @details 实时搜索功能（可选，如果需要实时搜索可以启用）
 */
const handleSearchInput = () => {
  // If real-time search is needed, call loadAlerts() here
  // Currently only searches when adding/removing keywords
}

const handleFilter = () => {
  // 保存status筛选器设置到localStorage
  try {
    localStorage.setItem('alerts-status-filter', statusFilter.value)
  } catch (error) {
    console.warn('Failed to save status filter to localStorage:', error)
  }
  loadAlerts()
  loadAlertTypeDistribution()  // Reload chart data when status filter changes
  // Note: Alert trend chart doesn't use status filter, only time range
}

const handlePageSizeChange = () => {
  pageSize.value = Number(pageSize.value) // Ensure it's a number type
  currentPage.value = 1 // Reset to first page
  // 保存到 localStorage
  try {
    localStorage.setItem('alerts-pageSize', String(pageSize.value))
  } catch (error) {
    console.warn('Failed to save page size to localStorage:', error)
  }
  loadAlerts()
}

const handleSelect = (items) => {
  selectedAlerts.value = items.map(alert => alert.id)
}

const handleSelectAll = (items) => {
  selectedAlerts.value = items.map(alert => alert.id)
}

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

const router = useRouter()
const route = useRoute()
const currentAlertId = computed(() => route.params.id ?? null)

const openAlertDetail = (alertId) => {
  // Update URL without triggering page navigation
  router.push({ path: `/alerts/${alertId}`, replace: true })
}

const openAlertDetailInNewWindow = (alertId) => {
  // Open alert detail in a new window
  const route = router.resolve({ path: `/alerts/${alertId}` })
  // Build complete URL
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const closeAlertDetail = () => {
  // Clear alert ID from URL
  router.push({ path: '/alerts', replace: true })
}

const handleAlertClosed = () => {
  // Reload alert list after alert is closed
  loadAlerts()
  // Clear selection
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const handleAlertConvertedToIncident = () => {
  // Reload alert list after alert is converted to incident
  loadAlerts()
  // Clear selection
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

// Word wrap state
const isWordWrap = computed(() => {
  return dataTableRef.value?.wordWrap?.value ?? true
})

// Toggle word wrap
const handleToggleWordWrap = () => {
  if (dataTableRef.value) {
    dataTableRef.value.toggleWordWrap()
    showMoreMenu.value = false
  }
}

// Close dropdown menu when clicking outside
const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.more-menu-dropdown')
  const button = event.target.closest('.more-menu-button')
  if (!dropdown && !button) {
    showMoreMenu.value = false
  }
}

const openBatchCloseDialog = () => {
  if (selectedAlerts.value.length === 0) {
    console.warn('No alerts selected')
    return
  }

  showBatchCloseDialog.value = true
}

const closeBatchCloseDialog = () => {
  showBatchCloseDialog.value = false
  // Reset form
  closeConclusion.value = {
    category: '',
    notes: ''
  }
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim() || isBatchClosing.value) {
    return
  }

  if (selectedAlerts.value.length === 0) {
    toast.warn('请至少选择一个告警', '提示')
    return
  }

  try {
    isBatchClosing.value = true
    
    // 调用批量关闭接口
    await batchCloseAlertsByPut(
      selectedAlerts.value,
      closeConclusion.value.category,
      closeConclusion.value.notes.trim()
    )
    
    // 显示成功提示
    toast.success(
      t('alerts.list.batchCloseSuccess', { count: selectedAlerts.value.length }) || 
      `成功关闭 ${selectedAlerts.value.length} 个告警`, 
      '操作成功'
    )
    
    // Close dialog and reset form
    closeBatchCloseDialog()
    selectedAlerts.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    // Reload alert list
    loadAlerts()
  } catch (error) {
    console.error('Failed to batch close alerts:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('alerts.list.batchCloseError') || '批量关闭告警失败，请稍后重试'
    toast.error(errorMessage, '操作失败')
  } finally {
    isBatchClosing.value = false
  }
}

const openAssociateIncidentDialog = () => {
  if (selectedAlerts.value.length === 0) {
    console.warn('No alerts selected')
    return
  }
  showAssociateIncidentDialog.value = true
}

const closeAssociateIncidentDialog = () => {
  showAssociateIncidentDialog.value = false
}

const handleAssociateIncidentSuccess = () => {
  // Close dialog and reset after successful association
  closeAssociateIncidentDialog()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
  
  // Reload alert list
  loadAlerts()
}

const openCreateIncidentDialog = () => {
  // Find selected alerts
  const selectedAlertObjects = alerts.value.filter(alert => selectedAlerts.value.includes(alert.id))

  
  // Use the first alert's data for initial form data
  const firstAlert = selectedAlertObjects[0]
  
  // Use browser current time for occurrence time
  const occurrenceTime = new Date()
  
  // Get title and description from first alert only
  const incidentTitle = firstAlert.title || ''
  
  // Get description - handle both string and object types
  let alertDescription = ''
  if (firstAlert.aiAnalysis?.description) {
    // If aiAnalysis.description exists, use it (convert to string if object)
    alertDescription = typeof firstAlert.aiAnalysis.description === 'string' 
      ? firstAlert.aiAnalysis.description 
      : JSON.stringify(firstAlert.aiAnalysis.description)
  } else if (firstAlert.description) {
    // If description exists, use it (convert to string if object)
    alertDescription = typeof firstAlert.description === 'string' 
      ? firstAlert.description 
      : JSON.stringify(firstAlert.description)
  }
  
  // Set initial data - use first alert's title and description, current time for occurrence
  createIncidentInitialData.value = {
    title: incidentTitle,
    occurrenceTime: occurrenceTime,
    description: alertDescription
  }
  
  // Open dialog
  showCreateIncidentDialog.value = true
}

const closeCreateIncidentDialog = () => {
  showCreateIncidentDialog.value = false
  createIncidentInitialData.value = null
}

const handleIncidentCreated = () => {
  // Reload alert list after incident is created
  loadAlerts()
  // Clear selection
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const openCreateAlertDialog = () => {
  showCreateAlertDialog.value = true
}

const closeCreateAlertDialog = () => {
  showCreateAlertDialog.value = false
}

const handleAlertCreated = async () => {
  // Reload alert list after alert is created
  loadAlerts()
  await loadStatistics()
  loadAlertTypeDistribution()
  await loadAlertTrend() // Load after loadStatistics to ensure alertCount is set correctly
}

const handleTimeRangeChange = async (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    // Load data based on selected time range
    loadAlerts()
    loadAlertTypeDistribution()
    await loadAlertTrend() // Ensure alertCount is updated when time range changes
  }
}

const handleCustomRangeChange = async (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    loadAlerts()
    loadAlertTypeDistribution()
    await loadAlertTrend() // Ensure alertCount is updated when custom range changes
  }
}

watch([currentPage], () => {
  loadAlerts()
})

onMounted(async () => {
  ensureAlertTypeChart()
  ensureAlertTrendChart()
  loadAlerts()
  await loadStatistics()
  loadAlertTypeDistribution()
  await loadAlertTrend() // Load after loadStatistics to ensure alertCount is set correctly
  // Add click outside listener to close dropdown menu
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // Remove click outside listener
  document.removeEventListener('click', handleClickOutside)
  disposeAlertTypeChart()
  disposeAlertTrendChart()
})

const alertsTimeRangeLabel = computed(() => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      return `${formatDateTime(customTimeRange.value[0])} ~ ${formatDateTime(customTimeRange.value[1])}`
    }
    return t('common.timeRange.customRange')
  }
  return t(`common.timeRange.${selectedTimeRange.value}`) || t('common.timeRange.last24Hours')
})
</script>


