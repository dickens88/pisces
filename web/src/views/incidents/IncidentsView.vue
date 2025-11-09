<template>
  <div class="w-full">
    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('incidents.title') }}
        </h1>
      </div>
      <div class="flex items-center gap-4">
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
        <button
          @click="showCreateDialog = true"
          class="flex items-center gap-2 px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 transition-colors"
        >
          <span class="material-symbols-outlined text-base">add</span>
          <span>{{ $t('incidents.list.createIncident') }}</span>
        </button>
      </div>
    </header>

    <!-- 搜索和筛选 -->
    <div class="bg-[#111822] border border-[#324867] rounded-lg p-4 mb-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="relative flex-1 min-w-[250px]">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#92a9c9]">
            search
          </span>
          <input
            v-model="searchQuery"
            @input="handleSearch"
            class="w-full bg-[#1e293b] text-white border-0 rounded-md pl-10 pr-4 py-2 focus:ring-2 focus:ring-primary"
            :placeholder="$t('incidents.list.searchPlaceholder')"
            type="text"
          />
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            @click="showSeverityFilter = !showSeverityFilter"
            class="flex items-center gap-2 px-4 py-2 text-sm text-white bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('incidents.list.severityLevel') }}
            <span class="material-symbols-outlined text-base">expand_more</span>
          </button>
          <button
            @click="showStatusFilter = !showStatusFilter"
            class="flex items-center gap-2 px-4 py-2 text-sm text-white bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('incidents.list.status') }}
            <span class="material-symbols-outlined text-base">expand_more</span>
          </button>
        </div>
        <div class="flex items-center gap-2">
          <button
            :disabled="selectedIncidents.length === 0"
            class="flex items-center gap-2 px-4 py-2 text-sm text-[#92a9c9] bg-[#1e293b] rounded-md disabled:opacity-50 cursor-not-allowed transition-colors"
          >
            <span class="material-symbols-outlined text-base">ios_share</span>
            {{ $t('incidents.list.export') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 事件列表表格 -->
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
      <template #cell-severity="{ item }">
        <span
          :class="[
            'px-2 py-1 text-xs font-medium rounded-full',
            getSeverityClass(item.severity)
          ]"
        >
          {{ $t(`incidents.list.${item.severity}`) }}
        </span>
      </template>
      <template #cell-incidentName="{ item }">
        <router-link
          :to="`/incidents/${item.id}`"
          class="text-primary hover:underline font-medium overflow-hidden text-ellipsis whitespace-nowrap block"
          :title="item.name"
        >
          {{ item.name }}
        </router-link>
      </template>
      <template #cell-responsibleDepartment="{ value }">
        {{ value || '-' }}
      </template>
      <template #cell-rootCause="{ value }">
        {{ value || '-' }}
      </template>
      <template #cell-occurrenceTime="{ value }">
        {{ value }}
      </template>
      <template #cell-status="{ item }">
        <span :class="getStatusClass(item.status)">
          {{ $t(`incidents.list.${item.status}`) }}
        </span>
      </template>
    </DataTable>

    <!-- 创建事件对话框 -->
    <CreateIncidentDialog
      :visible="showCreateDialog"
      @close="showCreateDialog = false"
      @created="handleIncidentCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getIncidents } from '@/api/incidents'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'

const { t } = useI18n()

// 定义列配置（使用computed确保响应式）
const columns = computed(() => [
  { key: 'severity', label: t('incidents.list.severity') },
  { key: 'incidentName', label: t('incidents.list.incidentName') },
  { key: 'responsibleDepartment', label: t('incidents.list.responsibleDepartment') },
  { key: 'rootCause', label: t('incidents.list.rootCause') },
  { key: 'occurrenceTime', label: t('incidents.list.occurrenceTime') },
  { key: 'status', label: t('incidents.list.status') }
])

// 默认列宽
const defaultWidths = {
  severity: 100,
  incidentName: 300,
  responsibleDepartment: 150,
  rootCause: 150,
  occurrenceTime: 180,
  status: 100
}

const incidents = ref([])
const dataTableRef = ref(null)
const searchQuery = ref('')
const severityFilter = ref('all')
const statusFilter = ref('all')
const selectedIncidents = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showSeverityFilter = ref(false)
const showStatusFilter = ref(false)
const showCreateDialog = ref(false)

// 时间范围选择器
const selectedTimeRange = ref('last24Hours')
const customTimeRange = ref(null)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadIncidents = async () => {
  try {
    const params = {
      search: searchQuery.value,
      severity: severityFilter.value,
      status: statusFilter.value,
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
        // 默认24小时
        start.setHours(start.getHours() - 24)
      }
      
      params.startTime = start.toISOString()
      params.endTime = end.toISOString()
    }
    
    const response = await getIncidents(params)
    incidents.value = response.data
    total.value = response.total
  } catch (error) {
    console.error('Failed to load incidents:', error)
  }
}

const handleSearch = () => {
  loadIncidents()
}

const handleSelect = (items) => {
  selectedIncidents.value = items.map(incident => incident.id)
}

const handleSelectAll = (items) => {
  selectedIncidents.value = items.map(incident => incident.id)
}

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = newPageSize
  currentPage.value = 1
  loadIncidents()
}

const getSeverityClass = (severity) => {
  const classes = {
    high: 'text-white bg-[#E57373]',
    medium: 'text-black bg-[#FFB74D]',
    low: 'text-white bg-[#64B5F6]'
  }
  return classes[severity] || classes.low
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'text-amber-400',
    inProgress: 'text-blue-400',
    closed: 'text-gray-400'
  }
  return classes[status] || classes.pending
}

const handleIncidentCreated = () => {
  // 重新加载事件列表
  loadIncidents()
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    // 根据选择的时间范围加载数据
    loadIncidents()
  }
}

const handleCustomRangeChange = (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    loadIncidents()
  }
}

watch([currentPage, severityFilter, statusFilter, pageSize], () => {
  loadIncidents()
})

onMounted(() => {
  loadIncidents()
})
</script>


