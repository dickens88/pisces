<template>
  <div class="w-full">
    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em] min-w-72">
        {{ $t('vulnerabilities.title') }}
      </h1>
      <div class="flex items-center gap-2">
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          @change="handleTimeRangeChange"
          @customRangeChange="handleCustomRangeChange"
        />
        <button
          @click="handleExportReport"
          class="flex items-center gap-2 px-4 py-2 h-10 text-sm text-white bg-[#233348] rounded-lg hover:bg-[#324867] transition-colors"
        >
          <span class="truncate">{{ $t('vulnerabilities.list.exportReport') }}</span>
        </button>
        <button
          @click="showCreateScanDialog = true"
          class="flex items-center gap-2 px-4 py-2 h-10 text-sm text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
        >
          <span class="truncate">{{ $t('vulnerabilities.list.createScanTask') }}</span>
        </button>
      </div>
    </header>

    <!-- 统计图表 -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <!-- 漏洞趋势统计 -->
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

      <!-- 漏洞责任部门分布 -->
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

    <!-- 搜索和筛选 -->
    <section class="flex flex-col gap-4 rounded-xl border border-[#324867] bg-[#111822] p-4 mb-6">
      <div class="flex flex-wrap items-center justify-between gap-2 px-2 py-1">
        <div class="flex items-center gap-2">
          <div class="relative w-64">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#92a9c9]">
              search
            </span>
            <input
              v-model="searchQuery"
              @input="handleSearch"
              class="w-full h-10 rounded-lg border border-[#324867] bg-transparent pl-10 pr-4 text-white placeholder:text-[#92a9c9] focus:border-primary focus:ring-primary"
              :placeholder="$t('vulnerabilities.list.searchPlaceholder')"
              type="text"
            />
          </div>
          <button
            @click="showFilterDialog = !showFilterDialog"
            class="flex items-center justify-center rounded-lg p-2 text-white hover:bg-[#233348] transition-colors"
          >
            <span class="material-symbols-outlined">filter_list</span>
          </button>
          <button
            @click="handleDownload"
            class="flex items-center justify-center rounded-lg p-2 text-white hover:bg-[#233348] transition-colors"
          >
            <span class="material-symbols-outlined">download</span>
          </button>
        </div>
        <button
          @click="showBatchOperateDialog = true"
          :disabled="selectedVulnerabilities.length === 0"
          class="flex items-center gap-2 px-4 py-2 h-10 text-sm text-white bg-primary rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span class="material-symbols-outlined text-base">apps</span>
          <span class="truncate">{{ $t('vulnerabilities.list.batchOperate') }}</span>
        </button>
      </div>

      <!-- 数据表格 -->
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
        <template #cell-name="{ item }">
          <div class="text-white font-normal">
            {{ item.name }}
          </div>
        </template>
        <template #cell-riskLevel="{ item }">
          <span :class="getRiskLevelClass(item.riskLevel)">
            {{ $t(`vulnerabilities.list.riskLevels.${item.riskLevel}`) }}
          </span>
        </template>
        <template #cell-affectedAsset="{ value }">
          <span class="text-[#92a9c9]">{{ value }}</span>
        </template>
        <template #cell-firstDiscoveryTime="{ value }">
          <span class="text-[#92a9c9]">{{ value }}</span>
        </template>
        <template #cell-status="{ item }">
          <span :class="getStatusClass(item.status)">
            {{ $t(`vulnerabilities.list.status.${item.status}`) }}
          </span>
        </template>
        <template #cell-action="{ item }">
          <button
            @click.stop="handleViewDetail(item)"
            class="text-sm font-medium text-primary cursor-pointer hover:underline"
          >
            {{ $t('vulnerabilities.list.detail') }}
          </button>
        </template>
      </DataTable>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { 
  getVulnerabilities, 
  getVulnerabilityTrend, 
  getVulnerabilityDepartmentDistribution,
  exportVulnerabilityReport 
} from '@/api/vulnerabilities'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'

const { t } = useI18n()

// 定义列配置
const columns = computed(() => [
  { key: 'name', label: t('vulnerabilities.list.nameCve') },
  { key: 'riskLevel', label: t('vulnerabilities.list.riskLevel') },
  { key: 'affectedAsset', label: t('vulnerabilities.list.affectedAsset') },
  { key: 'firstDiscoveryTime', label: t('vulnerabilities.list.firstDiscoveryTime') },
  { key: 'status', label: t('vulnerabilities.list.status') },
  { key: 'action', label: t('vulnerabilities.list.action') }
])

// 默认列宽
const defaultWidths = {
  name: 400,
  riskLevel: 120,
  affectedAsset: 150,
  firstDiscoveryTime: 150,
  status: 100,
  action: 100
}

const vulnerabilities = ref([])
const trendData = ref([])
const departmentData = ref([])
const dataTableRef = ref(null)
const searchQuery = ref('')
const selectedVulnerabilities = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showFilterDialog = ref(false)
const showBatchOperateDialog = ref(false)
const showCreateScanDialog = ref(false)

// 时间范围选择器
const selectedTimeRange = ref('last30Days')
const customTimeRange = ref(null)

// 加载漏洞列表
const loadVulnerabilities = async () => {
  try {
    const params = {
      search: searchQuery.value,
      page: currentPage.value,
      pageSize: pageSize.value
    }
    
    // 根据选择的时间范围添加时间参数
    if (selectedTimeRange.value === 'customRange' && customTimeRange.value && customTimeRange.value.length === 2) {
      params.startTime = customTimeRange.value[0].toISOString()
      params.endTime = customTimeRange.value[1].toISOString()
    } else {
      const end = new Date()
      const start = new Date()
      
      if (selectedTimeRange.value === 'last24Hours') {
        start.setHours(start.getHours() - 24)
      } else if (selectedTimeRange.value === 'last3Days') {
        start.setDate(start.getDate() - 3)
      } else if (selectedTimeRange.value === 'last7Days') {
        start.setDate(start.getDate() - 7)
      } else if (selectedTimeRange.value === 'last30Days') {
        start.setDate(start.getDate() - 30)
      } else if (selectedTimeRange.value === 'last3Months') {
        start.setMonth(start.getMonth() - 3)
      } else {
        // 默认30天
        start.setDate(start.getDate() - 30)
      }
      
      params.startTime = start.toISOString()
      params.endTime = end.toISOString()
    }
    
    const response = await getVulnerabilities(params)
    vulnerabilities.value = response.data
    total.value = response.total
  } catch (error) {
    console.error('Failed to load vulnerabilities:', error)
  }
}

// 加载趋势数据
const loadTrendData = async () => {
  try {
    const response = await getVulnerabilityTrend()
    trendData.value = response.data
  } catch (error) {
    console.error('Failed to load trend data:', error)
  }
}

// 加载部门分布数据
const loadDepartmentData = async () => {
  try {
    const response = await getVulnerabilityDepartmentDistribution()
    departmentData.value = response.data
  } catch (error) {
    console.error('Failed to load department data:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadVulnerabilities()
}

const handleSelect = (items) => {
  selectedVulnerabilities.value = items.map(vuln => vuln.id)
}

const handleSelectAll = (items) => {
  selectedVulnerabilities.value = items.map(vuln => vuln.id)
}

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = newPageSize
  currentPage.value = 1
  loadVulnerabilities()
}

const getRiskLevelClass = (riskLevel) => {
  const classes = {
    critical: 'inline-block rounded-full bg-red-500/10 px-3 py-1 text-xs font-medium text-red-500',
    high: 'inline-block rounded-full bg-orange-500/10 px-3 py-1 text-xs font-medium text-orange-500',
    medium: 'inline-block rounded-full bg-yellow-500/10 px-3 py-1 text-xs font-medium text-yellow-500',
    low: 'inline-block rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-500'
  }
  return classes[riskLevel] || classes.low
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'text-[#92a9c9]',
    inProgress: 'text-yellow-500',
    fixed: 'text-green-500',
    ignored: 'text-[#92a9c9]'
  }
  return classes[status] || classes.pending
}

const handleViewDetail = (item) => {
  // TODO: 实现详情查看功能
  console.log('View detail:', item)
}

const handleExportReport = async () => {
  try {
    await exportVulnerabilityReport({
      timeRange: selectedTimeRange.value,
      customRange: customTimeRange.value
    })
  } catch (error) {
    console.error('Failed to export report:', error)
  }
}

const handleDownload = () => {
  handleExportReport()
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
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

