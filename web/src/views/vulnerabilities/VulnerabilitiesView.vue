<template>
  <div class="w-full">
    <!-- Page title and actions -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('vulnerabilities.title') }}
        </h1>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="handleRefresh"
          :disabled="loadingVulnerabilities"
          class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546] h-10"
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
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </header>

    <!-- Statistics charts -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <!-- Vulnerability trend statistics -->
      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('vulnerabilities.statistics.trend') }}
        </p>
        <div class="flex h-40 w-full flex-col justify-end">
          <div class="grid h-full grid-cols-6 items-end gap-2">
            <div
              v-for="(data, index) in trendData"
              :key="index"
              class="flex h-full flex-col justify-end gap-px"
            >
              <div
                :style="{ height: `${data.critical}%` }"
                class="w-full bg-red-500"
              ></div>
              <div
                :style="{ height: `${data.high}%` }"
                class="w-full bg-orange-500"
              ></div>
              <div
                :style="{ height: `${data.medium}%` }"
                class="w-full bg-yellow-500"
              ></div>
              <div
                :style="{ height: `${data.low}%` }"
                class="w-full bg-blue-500"
              ></div>
            </div>
          </div>
          <div class="mt-2 grid grid-cols-6 text-center">
            <p
              v-for="(data, index) in trendData"
              :key="index"
              class="text-[13px] font-medium text-[#92a9c9]"
            >
              {{ data.month }}
            </p>
          </div>
        </div>
      </div>

      <!-- Vulnerability department distribution -->
      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('vulnerabilities.statistics.departmentDistribution') }}
        </p>
        <div class="flex h-40 w-full flex-col justify-end">
          <div class="grid h-full grid-cols-5 items-end gap-2">
            <div
              v-for="(data, index) in departmentData"
              :key="index"
              class="flex h-full flex-col justify-end gap-px"
            >
              <div
                :style="{ height: `${data.critical}%` }"
                class="w-full bg-red-500"
              ></div>
              <div
                :style="{ height: `${data.high}%` }"
                class="w-full bg-orange-500"
              ></div>
              <div
                :style="{ height: `${data.medium}%` }"
                class="w-full bg-yellow-500"
              ></div>
              <div
                :style="{ height: `${data.low}%` }"
                class="w-full bg-blue-500"
              ></div>
            </div>
          </div>
          <div class="mt-2 grid grid-cols-5 text-center">
            <p
              v-for="(data, index) in departmentData"
              :key="index"
              class="text-xs font-medium text-[#92a9c9]"
            >
              {{ data.department }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Vulnerability list table -->
    <section class="bg-[#111822] border border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingVulnerabilities"
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
            :disabled="selectedVulnerabilities.length === 0"
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { getIncidents } from '@/api/incidents'
import { 
  getVulnerabilityTrend, 
  getVulnerabilityDepartmentDistribution
} from '@/api/vulnerabilities'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatDateTime } from '@/utils/dateTime'

const { t } = useI18n()

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
const searchKeywords = ref([])
const currentSearchInput = ref('')
const severityFilter = ref('all')
const statusFilter = ref('all')
const selectedVulnerabilities = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Time range picker
const selectedTimeRange = ref('last3Months')
const customTimeRange = ref(null)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadVulnerabilities = async () => {
  loadingVulnerabilities.value = true
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
    // Add search_vulscan: true to indicate this is a vulnerability scan query
    const params = {
      action: 'list',
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      time_range: timeRange,
      conditions: conditions,
      search_vulscan: true
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

// Load trend data
const loadTrendData = async () => {
  try {
    const response = await getVulnerabilityTrend()
    trendData.value = response.data
  } catch (error) {
    console.error('Failed to load trend data:', error)
  }
}

// Load department distribution data
const loadDepartmentData = async () => {
  try {
    const response = await getVulnerabilityDepartmentDistribution()
    departmentData.value = response.data
  } catch (error) {
    console.error('Failed to load department data:', error)
  }
}

/**
 * @brief 刷新漏洞列表
 */
const handleRefresh = async () => {
  await Promise.all([
    loadVulnerabilities(),
    loadTrendData(),
    loadDepartmentData()
  ])
}

/**
 * @brief 添加搜索关键字
 */
const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && !searchKeywords.value.includes(keyword)) {
    searchKeywords.value.push(keyword)
    currentSearchInput.value = ''
    loadVulnerabilities()
  }
}

/**
 * @brief 删除搜索关键字
 * @param {number} index - 要删除的关键字索引
 */
const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
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
    loadTrendData()
    loadDepartmentData()
  }
}

const handleCustomRangeChange = (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    loadVulnerabilities()
    loadTrendData()
    loadDepartmentData()
  }
}

watch([currentPage, pageSize], () => {
  loadVulnerabilities()
})

onMounted(() => {
  loadVulnerabilities()
  loadTrendData()
  loadDepartmentData()
})
</script>


