<template>
  <div class="w-full">
    <!-- 页面头部 -->
    <header class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em]">
        {{ $t('alerts.title') }}
      </h1>
      <div class="flex gap-2">
        <button
          v-for="range in timeRanges"
          :key="range.key"
          @click="selectedTimeRange = range.key"
          :class="[
            'flex h-9 shrink-0 items-center justify-center gap-x-2 rounded-lg px-3 transition-colors',
            selectedTimeRange === range.key
              ? 'bg-primary/30 hover:bg-primary/50 text-primary border border-primary'
              : 'bg-[#233348] hover:bg-[#324867] text-white'
          ]"
        >
          <span class="material-symbols-outlined" style="font-size: 20px;">
            {{ range.icon }}
          </span>
          <p class="text-sm font-medium leading-normal">{{ $t(range.label) }}</p>
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.alertTypeStats') }}
        </p>
        <p class="text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ statistics.totalAlerts?.toLocaleString() || 0 }}
        </p>
        <div class="flex gap-1 items-center">
          <p class="text-gray-400 text-sm font-normal leading-normal">
            {{ $t('alerts.list.statistics.past7Days') }}
          </p>
          <p class="text-[#0bda5e] text-sm font-medium leading-normal flex items-center">
            <span class="material-symbols-outlined" style="font-size: 16px;">arrow_upward</span>
            +{{ statistics.trend }}%
          </p>
        </div>
        <div class="grid min-h-[90px] grid-flow-col gap-6 grid-rows-[1fr_auto] items-end justify-items-center px-3 pt-4">
          <template v-for="(stat, index) in statistics.typeStats" :key="index">
            <div
              class="bg-primary/30 hover:bg-primary/50 w-full rounded-t transition-colors"
              :style="{ height: stat.value + '%' }"
            ></div>
            <p class="text-gray-400 text-xs font-medium">{{ stat.name }}</p>
          </template>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.alertTrend') }}
        </p>
        <p class="text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ statistics.alertCount || 0 }}
        </p>
        <div class="flex gap-1 items-center">
          <p class="text-gray-400 text-sm font-normal leading-normal">
            {{ $t('alerts.list.statistics.past7Days') }}
          </p>
          <p
            :class="[
              'text-sm font-medium leading-normal flex items-center',
              statistics.alertTrend >= 0 ? 'text-[#fa6238]' : 'text-[#0bda5e]'
            ]"
          >
            <span class="material-symbols-outlined" style="font-size: 16px;">
              {{ statistics.alertTrend >= 0 ? 'arrow_upward' : 'arrow_downward' }}
            </span>
            {{ statistics.alertTrend >= 0 ? '+' : '' }}{{ statistics.alertTrend }}%
          </p>
        </div>
        <div class="flex min-h-[90px] flex-1 flex-col justify-end pt-4">
          <svg
            fill="none"
            height="100%"
            preserveAspectRatio="none"
            viewBox="0 0 420 120"
            width="100%"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M0 87.2C15.5556 87.2 15.5556 16.8 31.1111 16.8C46.6667 16.8 46.6667 32.8 62.2222 32.8C77.7778 32.8 77.7778 74.4 93.3333 74.4C108.889 74.4 108.889 26.4 124.444 26.4C140 26.4 140 80.8 155.556 80.8C171.111 80.8 171.111 48.8 186.667 48.8C202.222 48.8 202.222 36 217.778 36C233.333 36 233.333 96.8 248.889 96.8C264.444 96.8 264.444 119.2 280 119.2C295.556 119.2 295.556 0.800003 311.111 0.800003C326.667 0.800003 326.667 64.8 342.222 64.8C357.778 64.8 357.778 103.2 373.333 103.2C388.889 103.2 388.889 20 404.444 20C420 20 420 20 420 20V120H0V87.2Z"
              fill="url(#trend-gradient)"
            ></path>
            <path
              d="M0 87.2C15.5556 87.2 15.5556 16.8 31.1111 16.8C46.6667 16.8 46.6667 32.8 62.2222 32.8C77.7778 32.8 77.7778 74.4 93.3333 74.4C108.889 74.4 108.889 26.4 124.444 26.4C140 26.4 140 80.8 155.556 80.8C171.111 80.8 171.111 48.8 186.667 48.8C202.222 48.8 202.222 36 217.778 36C233.333 36 233.333 96.8 248.889 96.8C264.444 96.8 264.444 119.2 280 119.2C295.556 119.2 295.556 0.800003 311.111 0.800003C326.667 0.800003 326.667 64.8 342.222 64.8C357.778 64.8 357.778 103.2 373.333 103.2C388.889 103.2 388.889 20 404.444 20"
              stroke="#2b7cee"
              stroke-linecap="round"
              stroke-width="3"
            ></path>
            <defs>
              <linearGradient
                gradientUnits="userSpaceOnUse"
                id="trend-gradient"
                x1="210"
                x2="210"
                y1="0"
                y2="120"
              >
                <stop stop-color="#2b7cee" stop-opacity="0.4"></stop>
                <stop offset="1" stop-color="#2b7cee" stop-opacity="0"></stop>
              </linearGradient>
            </defs>
          </svg>
          <div class="flex justify-between mt-2">
            <p v-for="day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="day" class="text-gray-400 text-xs font-medium">
              {{ day }}
            </p>
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-[#324867] bg-[#111822] p-6">
        <p class="text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.mttd') }}
        </p>
        <p class="text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ statistics.mttd || '0 hours' }}
        </p>
        <div class="flex gap-1 items-center">
          <p class="text-gray-400 text-sm font-normal leading-normal">
            {{ $t('alerts.list.statistics.past7Days') }}
          </p>
          <p class="text-[#0bda5e] text-sm font-medium leading-normal flex items-center">
            <span class="material-symbols-outlined" style="font-size: 16px;">arrow_upward</span>
            +{{ statistics.mttdChange }} hours
          </p>
        </div>
        <div class="grid min-h-[90px] gap-x-4 gap-y-4 grid-cols-[auto_1fr] items-center pt-4">
          <template v-for="stage in mttdStages" :key="stage.name">
            <p class="text-gray-400 text-xs font-medium">{{ stage.name }}</p>
            <div class="h-2.5 w-full bg-[#233348] rounded-full">
              <div
                class="bg-primary h-2.5 rounded-full transition-all"
                :style="{ width: stage.percentage + '%' }"
              ></div>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- 告警列表表格 -->
    <section class="bg-[#111822] border border-[#324867] rounded-xl">
      <div class="flex flex-wrap items-center justify-between gap-4 p-4 border-b border-[#324867]">
        <div class="relative w-full max-w-sm">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="material-symbols-outlined text-gray-400" style="font-size: 20px;">search</span>
          </div>
          <input
            v-model="searchQuery"
            @input="handleSearch"
            class="block w-full rounded-lg border-0 bg-[#233348] py-2 pl-10 text-white placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm"
            :placeholder="$t('alerts.list.searchPlaceholder')"
            type="text"
          />
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
              <option value="pending">{{ $t('alerts.list.pending') }}</option>
              <option value="closed">{{ $t('alerts.list.closed') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>
          <button
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-600/50 text-gray-300 text-sm font-bold px-4 cursor-not-allowed"
          >
            <span>{{ $t('alerts.list.batchClose') }}</span>
          </button>
          <button
            :disabled="selectedAlerts.length === 0"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-slate-700/50 text-slate-300 text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600/50 transition-colors"
          >
            <span class="material-symbols-outlined text-base">link</span>
            <span>{{ $t('alerts.list.associateIncident') }}</span>
          </button>
          <button
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-primary/30 text-primary text-sm font-bold px-4 cursor-not-allowed"
          >
            <span>{{ $t('alerts.list.batchConvert') }}</span>
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-300" style="table-layout: fixed;">
          <thead class="text-xs text-white uppercase bg-[#1e293b]">
            <tr>
              <th class="p-4" scope="col" style="width: 50px;">
                <div class="flex items-center">
                  <input
                    v-model="selectAll"
                    @change="handleSelectAll"
                    class="w-4 h-4 text-primary bg-gray-700 border-gray-600 rounded focus:ring-primary focus:ring-2"
                    type="checkbox"
                  />
                </div>
              </th>
              <th
                v-for="(column, index) in columns"
                :key="column.key"
                :scope="'col'"
                :style="{ width: getColumnWidth(column.key) + 'px', minWidth: '80px' }"
                class="px-6 py-3 relative border-r border-[#324867]/50"
              >
                <div class="flex items-center">
                  {{ column.label }}
                </div>
                <!-- 调整列宽的手柄 -->
                <div
                  v-if="index < columns.length - 1"
                  @mousedown="startResize(column.key, $event)"
                  class="absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-primary/50 transition-colors z-10"
                  style="touch-action: none;"
                ></div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="alert in alerts"
              :key="alert.id"
              class="border-b border-[#324867] hover:bg-white/5"
            >
              <td class="w-4 p-4">
                <div class="flex items-center">
                  <input
                    v-model="selectedAlerts"
                    :value="alert.id"
                    class="w-4 h-4 text-primary bg-gray-700 border-gray-600 rounded focus:ring-primary focus:ring-2"
                    type="checkbox"
                  />
                </div>
              </td>
              <td class="px-6 py-4 border-r border-[#324867]/30">{{ alert.createTime }}</td>
              <th class="px-6 py-4 font-medium text-white overflow-hidden text-ellipsis whitespace-nowrap border-r border-[#324867]/30" scope="row" :title="alert.title">
                <a
                  @click="openAlertDetail(alert.id)"
                  class="text-primary hover:underline cursor-pointer"
                >
                  {{ alert.title }}
                </a>
              </th>
              <td class="px-6 py-4 border-r border-[#324867]/30">
                <span
                  :class="[
                    'text-xs font-medium me-2 px-2.5 py-0.5 rounded-full',
                    getRiskLevelClass(alert.riskLevel)
                  ]"
                >
                  {{ $t(`alerts.list.riskLevels.${alert.riskLevel}`) }}
                </span>
              </td>
              <td class="px-6 py-4 border-r border-[#324867]/30">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium',
                    getStatusClass(alert.status)
                  ]"
                >
                  <span :class="['size-1.5 rounded-full', getStatusDotClass(alert.status)]"></span>
                  {{ $t(`alerts.list.${alert.status}`) }}
                </span>
              </td>
              <td class="px-6 py-4 overflow-hidden text-ellipsis whitespace-nowrap" :title="alert.owner">
                {{ alert.owner }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav aria-label="Table navigation" class="flex items-center justify-between p-4">
        <span class="text-sm font-normal text-gray-400">
          Showing <span class="font-semibold text-white">1-{{ alerts.length }}</span> of
          <span class="font-semibold text-white">{{ total }}</span>
        </span>
        <ul class="inline-flex -space-x-px text-sm h-8">
          <li>
            <button
              @click="currentPage > 1 && currentPage--"
              :disabled="currentPage === 1"
              class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-400 bg-[#233348] border border-gray-700 rounded-s-lg hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
          </li>
          <li v-for="page in totalPages" :key="page">
            <button
              @click="currentPage = page"
              :class="[
                'flex items-center justify-center px-3 h-8 leading-tight border border-gray-700',
                currentPage === page
                  ? 'text-white bg-primary hover:bg-primary/90'
                  : 'text-gray-400 bg-[#233348] hover:bg-gray-700 hover:text-white'
              ]"
            >
              {{ page }}
            </button>
          </li>
          <li>
            <button
              @click="currentPage < totalPages && currentPage++"
              :disabled="currentPage === totalPages"
              class="flex items-center justify-center px-3 h-8 leading-tight text-gray-400 bg-[#233348] border border-gray-700 rounded-e-lg hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </li>
        </ul>
      </nav>
    </section>

    <!-- 告警详情抽屉 -->
    <AlertDetail
      v-if="selectedAlertId"
      :alert-id="selectedAlertId"
      @close="closeAlertDetail"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getAlerts, getAlertStatistics } from '@/api/alerts'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import { useResizableColumns } from '@/composables/useResizableColumns'

const { t } = useI18n()

// 定义列配置（使用computed确保响应式）
const columns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'owner', label: t('alerts.list.owner') }
])

// 默认列宽
const defaultWidths = {
  createTime: 180,
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  owner: 100
}

// 使用可调整列宽的composable
const { getColumnWidth, startResize } = useResizableColumns(
  'alerts-table-columns',
  defaultWidths
)

const alerts = ref([])
const statistics = ref({
  totalAlerts: 0,
  trend: 0,
  alertCount: 0,
  alertTrend: 0,
  mttd: '0 hours',
  mttdChange: 0,
  typeStats: []
})
const searchQuery = ref('')
const statusFilter = ref('all')
const selectedAlerts = ref([])
const selectAll = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTimeRange = ref('last7Days')
const selectedAlertId = ref(null)

const timeRanges = [
  { key: 'last24Hours', icon: 'update', label: 'alerts.list.timeRange.last24Hours' },
  { key: 'last7Days', icon: 'calendar_month', label: 'alerts.list.timeRange.last7Days' },
  { key: 'customRange', icon: 'date_range', label: 'alerts.list.timeRange.customRange' }
]

const mttdStages = [
  { name: 'Detection', percentage: 20 },
  { name: 'Triage', percentage: 35 },
  { name: 'Investigation', percentage: 80 },
  { name: 'Containment', percentage: 50 }
]

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadAlerts = async () => {
  try {
    const response = await getAlerts({
      search: searchQuery.value,
      status: statusFilter.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    alerts.value = response.data
    total.value = response.total
  } catch (error) {
    console.error('Failed to load alerts:', error)
  }
}

const loadStatistics = async () => {
  try {
    const response = await getAlertStatistics()
    statistics.value = response.data
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const handleSearch = () => {
  loadAlerts()
}

const handleFilter = () => {
  loadAlerts()
}

const handleSelectAll = () => {
  if (selectAll.value) {
    selectedAlerts.value = alerts.value.map(alert => alert.id)
  } else {
    selectedAlerts.value = []
  }
}

const getRiskLevelClass = (level) => {
  const classes = {
    high: 'bg-red-900 text-red-300',
    medium: 'bg-orange-900 text-orange-300',
    low: 'bg-blue-900 text-blue-300'
  }
  return classes[level] || classes.low
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-primary/20 text-primary',
    pending: 'bg-orange-500/20 text-orange-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || classes.open
}

const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-primary',
    pending: 'bg-orange-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.open
}

const openAlertDetail = (alertId) => {
  selectedAlertId.value = alertId
}

const closeAlertDetail = () => {
  selectedAlertId.value = null
}

watch([currentPage], () => {
  loadAlerts()
})

onMounted(() => {
  loadAlerts()
  loadStatistics()
})
</script>

