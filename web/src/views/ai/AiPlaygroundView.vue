<template>
  <div class="w-full">
    <!-- Page title and actions -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('aiPlayground.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 text-sm">
          {{ $t('aiPlayground.list.title') }}
        </p>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="handleRefresh"
          :disabled="loadingAlerts || aiAccuracyLoading"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingAlerts || aiAccuracyLoading }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="ai-playground"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </header>

    <!-- Charts -->
    <section
      v-if="showCharts"
      class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6"
    >
      <div class="flex flex-col gap-2 rounded-xl border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#111822] p-6">
        <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
          {{ $t('aiPlayground.charts.aiAccuracy') || $t('dashboard.charts.aiAccuracy') }}
        </p>
        <p class="text-gray-600 dark:text-gray-400 text-sm font-normal leading-normal">
          {{ timeRangeLabel }}
        </p>
        <div class="relative h-72 w-full">
          <div
            v-if="aiAccuracyLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="aiAccuracyData.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('dashboard.charts.noData') }}
          </div>
          <div
            v-show="!aiAccuracyLoading && aiAccuracyData.length > 0"
            ref="aiAccuracyChartRef"
            class="absolute inset-0"
          ></div>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-dashed border-gray-300 dark:border-[#324867] bg-white dark:bg-[#111822] p-6 items-start justify-between">
        <div>
          <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
            {{ $t('aiPlayground.charts.placeholder') }}
          </p>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            {{ $t('common.noData') }}
          </p>
        </div>
        <span class="material-symbols-outlined text-gray-300 dark:text-gray-600 text-5xl">upcoming</span>
      </div>
    </section>

    <!-- Alert list table -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl relative lg:col-span-2">
        <div
          v-if="loadingAlerts"
          class="absolute inset-0 bg-white/80 dark:bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
        >
          <div class="flex flex-col items-center gap-4">
            <div class="relative w-16 h-16">
              <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') }}</p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-3 p-4 border-b border-gray-200 dark:border-[#324867]">
          <div class="relative w-full max-w-xl" ref="searchContainerRef">
            <div
              class="flex items-start gap-2 rounded-lg border-0 bg-gray-100 dark:bg-[#233348] px-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary"
              @click="handleSearchContainerClick"
            >
              <div class="pointer-events-none flex items-center shrink-0 pt-[2px]">
                <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">search</span>
              </div>
              <div class="flex flex-1 flex-wrap items-center gap-2 max-h-32 overflow-y-auto pr-1">
                <div
                  v-for="(keywordObj, index) in searchKeywords"
                  :key="`${keywordObj.field}-${keywordObj.value}-${index}`"
                  class="flex items-center gap-1 px-2 py-1 bg-primary/20 text-primary rounded text-sm max-w-full min-w-0"
                >
                  <span class="min-w-0 break-all">{{ getFieldLabel(keywordObj.field) }}: {{ keywordObj.value }}</span>
                  <button
                    @click.stop="removeKeyword(index)"
                    class="flex items-center justify-center hover:text-primary/70 transition-colors ml-0.5"
                    type="button"
                    :aria-label="$t('common.delete')"
                  >
                    <span class="material-symbols-outlined" style="font-size: 16px;">close</span>
                  </button>
                </div>
                <input
                  v-model="displaySearchInput"
                  @keydown.enter.prevent="addKeyword"
                  @keydown.backspace="handleKeywordDeleteKey"
                  @focus="showFieldMenu = !currentField.value"
                  class="flex-1 min-w-[160px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
                  :placeholder="getSearchPlaceholder()"
                  type="text"
                  ref="searchInputRef"
                />
              </div>
            </div>
            <div
              v-if="showFieldMenu && !currentField"
              class="absolute left-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[200px]"
              @mousedown.prevent
            >
              <button
                v-for="field in searchFields"
                :key="field.value"
                @click="selectField(field.value)"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">{{ field.icon }}</span>
                <span>{{ field.label }}</span>
              </button>
            </div>
          </div>

          <div class="relative">
            <select
              v-model="statusFilter"
              @change="handleFilter"
              class="pl-4 pr-9 appearance-none block w-full rounded-lg border-0 bg-gray-100 dark:bg-[#233348] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm"
            >
              <option value="all">{{ $t('alerts.list.allStatus') }}</option>
              <option value="open">{{ $t('alerts.list.open') }}</option>
              <option value="block">{{ $t('alerts.list.block') }}</option>
              <option value="closed">{{ $t('alerts.list.closed') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>
        </div>

        <DataTable
          ref="dataTableRef"
          :columns="columns"
          :items="alerts"
          :selectable="false"
          :resizable="true"
          storage-key="ai-playground-alerts-table-columns"
          :default-widths="defaultWidths"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @update:current-page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          @row-click="handleRowClick"
        >
          <template #cell-createTime="{ value, item }">
            {{ formatDateTime(value || item?.create_time) }}
          </template>
          <template #cell-alertTitle="{ item }">
            <span
              class="text-primary hover:underline cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap block"
              :title="item.title"
            >
              {{ item.title }}
            </span>
          </template>
          <template #cell-riskLevel="{ item }">
            <span
              :class="[
                'text-xs font-medium px-2.5 py-0.5 rounded-full inline-flex items-center justify-center min-w-[70px]',
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
            >
              <span :class="['size-1.5 rounded-full', getStatusDotClass(item.status)]"></span>
              {{ getStatusText(item.status) }}
            </span>
          </template>
        </DataTable>
      </div>

      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl p-5 min-h-[300px]">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <span class="material-symbols-outlined text-base">smart_toy</span>
            {{ $t('alerts.detail.aiAgent') }}
          </h2>
          <span v-if="selectedAlert" class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[180px]" :title="selectedAlert.title">
            {{ selectedAlert.title }}
          </span>
        </div>
        <div v-if="selectedAlertLoading" class="text-sm text-gray-500 dark:text-gray-400 mb-4 flex items-center gap-2">
          <span class="material-symbols-outlined animate-spin text-base">refresh</span>
          {{ $t('common.loading') }}
        </div>
        <div v-else class="space-y-4 mb-4">
          <div
            v-if="aiItems.length"
            class="space-y-3"
          >
            <div
              v-for="(aiItem, index) in aiItems"
              :key="`ai-${aiItem.id || index}`"
              class="flex items-start gap-3"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600">
                <span class="material-symbols-outlined text-white text-sm">smart_toy</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <p class="font-semibold text-gray-900 dark:text-white">{{ aiItem.author || 'AI Agent' }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDateTime(aiItem.create_time || aiItem.time) }}</p>
                </div>
                <div class="mt-1 text-sm text-gray-700 dark:text-[#c3d3e8] bg-white dark:bg-[#2a3546] border border-gray-200 dark:border-transparent p-3 rounded-lg rounded-tl-none max-w-full overflow-hidden">
                  <div
                    :class="[
                      'bg-gray-50 dark:bg-transparent text-gray-800 dark:text-inherit rounded-md p-2 border border-gray-200 dark:border-transparent ai-agent__html',
                      { 'ai-agent__html--dark': isDarkMode() }
                    ]"
                  >
                    <div v-html="sanitizeHtml(aiItem.content || '')"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('alerts.detail.noAiResponse') }}
          </p>
        </div>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          disabled
        >
          <span class="material-symbols-outlined text-base">travel_explore</span>
          Retrieval test
        </button>

        <div class="mt-8">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Human conclusion</p>
          <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line min-h-[100px] bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-3">
            {{ selectedAlert?.close_comment || selectedAlertDetail?.close_comment || $t('alerts.detail.noAiResponse') || 'No conclusion available.' }}
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import DOMPurify from 'dompurify'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import DataTable from '@/components/common/DataTable.vue'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { getAiAccuracyByModel, getAlertDetail } from '@/api/alerts'
import service from '@/api/axios'

import { formatDateTime, formatDateTimeWithOffset } from '@/utils/dateTime'

const { t } = useI18n()

const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('ai-playground', 'last30Days')

const showCharts = ref(true)

// AI accuracy chart state
const aiAccuracyChartRef = ref(null)
const aiAccuracyData = ref([])
const aiAccuracyLoading = ref(false)
let aiAccuracyChartInstance = null
let aiAccuracyResizeListenerBound = false

// Alert list state
const alerts = ref([])
const loadingAlerts = ref(false)
const dataTableRef = ref(null)
const searchKeywords = ref([])
const currentSearchInput = ref('')
const currentField = ref('')
const showFieldMenu = ref(false)
const searchInputRef = ref(null)
const searchContainerRef = ref(null)
const selectedAlert = ref(null)
const selectedAlertDetail = ref(null)
const selectedAlertLoading = ref(false)
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const columns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'actor', label: t('alerts.list.actor') }
])

const defaultWidths = {
  createTime: 180,
  alertTitle: 360,
  riskLevel: 120,
  status: 140,
  actor: 160
}

const searchFields = computed(() => [
  { value: 'title', label: t('alerts.list.alertTitle'), icon: 'title' },
  { value: 'creator', label: t('alerts.list.owner'), icon: 'person' },
  { value: 'actor', label: t('alerts.list.actor'), icon: 'person_search' },
  { value: 'model_name', label: 'Model Name', icon: 'robot_2' }
])

const getFieldLabel = (field) => {
  const fieldObj = searchFields.value.find(f => f.value === field)
  return fieldObj ? fieldObj.label : field
}

const displaySearchInput = computed({
  get() {
    if (currentField.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      return prefix + currentSearchInput.value
    }
    return currentSearchInput.value
  },
  set(value) {
    if (currentField.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      if (value.startsWith(prefix)) {
        currentSearchInput.value = value.slice(prefix.length)
      } else {
        currentField.value = ''
        currentSearchInput.value = value
      }
    } else {
      currentSearchInput.value = value
    }
  }
})

const getSearchPlaceholder = () => {
  if (!currentField.value) {
    return searchKeywords.value.length === 0 ? (t('alerts.list.searchPlaceholder') || '点击选择搜索字段...') : ''
  }
  return ''
}

const timeRangeLabel = computed(() => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      const start = new Date(customTimeRange.value[0])
      const end = new Date(customTimeRange.value[1])
      return `${start.toLocaleDateString()} ~ ${end.toLocaleDateString()}`
    }
    return t('common.timeRange.customRange')
  }
  return t(`common.timeRange.${selectedTimeRange.value}`) || t('common.timeRange.last30Days')
})

const wrapAxisLabel = (label) => {
  if (!label) return ''
  const normalized = String(label)
  const chunkSize = normalized.length > 12 ? 12 : 8
  const segments = normalized.match(new RegExp(`.{1,${chunkSize}}`, 'g'))
  return segments ? segments.join('\n') : normalized
}

const ensureAiAccuracyChart = () => {
  if (!aiAccuracyChartInstance && aiAccuracyChartRef.value) {
    aiAccuracyChartInstance = echarts.init(aiAccuracyChartRef.value)
    if (!aiAccuracyResizeListenerBound) {
      window.addEventListener('resize', handleAiAccuracyResize)
      aiAccuracyResizeListenerBound = true
    }
  }
}

const handleAiAccuracyResize = () => {
  if (aiAccuracyChartInstance) {
    aiAccuracyChartInstance.resize()
  }
}

const disposeAiAccuracyChart = () => {
  if (aiAccuracyChartInstance) {
    aiAccuracyChartInstance.dispose()
    aiAccuracyChartInstance = null
  }
  if (aiAccuracyResizeListenerBound) {
    window.removeEventListener('resize', handleAiAccuracyResize)
    aiAccuracyResizeListenerBound = false
  }
}

const updateAiAccuracyChart = () => {
  ensureAiAccuracyChart()
  if (!aiAccuracyChartInstance) return

  aiAccuracyChartInstance.clear()

  const categories = aiAccuracyData.value.map((item) => item.name)
  const accuracies = aiAccuracyData.value.map((item) => item.accuracy)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderWidth: 0,
      textStyle: { color: '#e2e8f0' },
      padding: [10, 12],
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        const dataIndex = params[0].dataIndex
        const dataPoint = aiAccuracyData.value[dataIndex]
        if (!dataPoint) {
          return `${params[0].name}: ${params[0].value}%`
        }
        return `
          <div style="min-width:140px">
            <div style="font-weight:600;margin-bottom:4px;">${dataPoint.name}</div>
            <div>Accuracy: ${dataPoint.accuracy}%</div>
            <div>Correct: ${dataPoint.correct}/${dataPoint.total}</div>
          </div>
        `
      }
    },
    grid: {
      top: 10,
      right: 12,
      bottom: 6,
      left: 28,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: '#cbd5f5',
        fontSize: 11,
        lineHeight: 11,
        margin: 1,
        interval: 0,
        formatter: wrapAxisLabel
      },
      axisLine: { lineStyle: { color: '#334155' } },
      axisTick: { show: true, inside: true, alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#1f2a37' } },
      axisLine: { show: false }
    },
    series: [
      {
        name: t('aiPlayground.charts.aiAccuracy') || t('dashboard.charts.aiAccuracy'),
        type: 'bar',
        data: accuracies,
        barWidth: '45%',
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#34d399' },
            { offset: 0.7, color: '#10b981' },
            { offset: 1, color: '#059669' }
          ])
        }
      }
    ]
  }

  aiAccuracyChartInstance.setOption(option, true)
  nextTick(() => aiAccuracyChartInstance.resize())

  // Bind click to filter alerts by model name
  aiAccuracyChartInstance.off('click')
  aiAccuracyChartInstance.on('click', (params) => {
    if (!params?.name) return
    // Remove existing model/model_name filters before adding the new one
    searchKeywords.value = searchKeywords.value.filter(
      k => k.field !== 'model_name' && k.field !== 'model'
    )
    addKeywordIfMissing('model_name', params.name)
  })
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

const loadAiAccuracyStatistics = async () => {
  aiAccuracyLoading.value = true
  try {
    const { start, end } = computeSelectedRange()
    const response = await getAiAccuracyByModel(start, end, 10)
    const data = response?.data || []
    aiAccuracyData.value = data.map((item) => ({
      name: item.model_name || item.model || 'Unknown',
      accuracy: Number(item.accuracy) || 0,
      correct: item.correct || 0,
      total: item.total || 0
    }))
  } catch (error) {
    console.error('Failed to load AI accuracy statistics:', error)
    aiAccuracyData.value = []
  } finally {
    aiAccuracyLoading.value = false
    await nextTick()
    updateAiAccuracyChart()
  }
}

const getRiskLevelClass = (level) => {
  const classes = {
    fatal: 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-200',
    high: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    medium: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
    low: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    tips: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
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

const getStatusText = (status) => {
  if (!status) return t('alerts.list.open')
  const map = {
    open: t('alerts.list.open'),
    block: t('alerts.list.block'),
    closed: t('alerts.list.closed')
  }
  return map[status] || status
}

const handleSearchContainerClick = () => {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
  }
}

const addKeywordIfMissing = (field, value) => {
  if (!field || !value) return
  const exists = searchKeywords.value.some(k => k.field === field && k.value === value)
  if (!exists) {
    searchKeywords.value.push({ field, value })
  }
  currentField.value = ''
  currentSearchInput.value = ''
  currentPage.value = 1
  loadAlerts()
}

const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && currentField.value) {
    addKeywordIfMissing(currentField.value, keyword)
    showFieldMenu.value = false
  }
}

const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  currentPage.value = 1
  loadAlerts()
}

const handleKeywordDeleteKey = (event) => {
  if (!currentSearchInput.value && searchKeywords.value.length > 0 && event.key === 'Backspace') {
    searchKeywords.value.pop()
    currentPage.value = 1
    loadAlerts()
  }
}

const selectField = (field) => {
  currentField.value = field
  showFieldMenu.value = false
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

const handleClickOutside = (event) => {
  const target = event.target
  if (!searchContainerRef.value) return
  if (!searchContainerRef.value.contains(target)) {
    showFieldMenu.value = false
  }
}

const handleSearch = () => {
  addKeyword()
}

const clearSearch = () => {
  searchKeywords.value = []
  currentField.value = ''
  currentSearchInput.value = ''
  currentPage.value = 1
  loadAlerts()
}

const sanitizeHtml = (html = '') => DOMPurify.sanitize(html)

const handleRowClick = async (item) => {
  // Seed with list data (includes close_comment) to avoid stale values
  selectedAlert.value = {
    ...item,
    close_comment: item.close_comment || item.closeComment || item?.data_object?.close_comment || null
  }
  selectedAlertDetail.value = null
  selectedAlertLoading.value = true
  try {
    const detailId = item.alert_id || item.id
    const response = await getAlertDetail(detailId)
    const detail =
      response?.data?.data ||
      response?.data ||
      response ||
      null
    selectedAlertDetail.value = detail || null

    const closeComment =
      detail?.close_comment ||
      detail?.data?.close_comment ||
      detail?.data_object?.close_comment ||
      null

    selectedAlert.value = {
      ...selectedAlert.value,
      close_comment: closeComment ?? selectedAlert.value.close_comment ?? null
    }
  } catch (error) {
    console.error('Failed to load alert detail:', error)
  } finally {
    selectedAlertLoading.value = false
  }
}

const aiItems = computed(() => selectedAlertDetail.value?.ai || [])

const isDarkMode = () => document.documentElement.classList.contains('dark')

const handleFilter = () => {
  currentPage.value = 1
  loadAlerts()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadAlerts()
}

const handlePageSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadAlerts()
}

const buildConditions = () => {
  const fieldMap = {
    title: 'title',
    creator: 'creator',
    actor: 'actor',
    model_name: 'model_name',
    model: 'model_name'
  }
  const statusApiMap = {
    open: 'Open',
    block: 'Block',
    closed: 'Closed'
  }

  const conditions = []

  if (statusFilter.value && statusFilter.value !== 'all') {
    conditions.push({
      handle_status: statusApiMap[statusFilter.value] || statusFilter.value
    })
  }

  searchKeywords.value.forEach(k => {
    if (k.field && k.value) {
      const mappedField = fieldMap[k.field] || k.field
      conditions.push({ [mappedField]: k.value })
    }
  })

  return conditions
}

const loadAlerts = async () => {
  loadingAlerts.value = true
  try {
    const { start, end } = computeSelectedRange()
    const params = {
      action: 'list_local',
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      conditions: buildConditions(),
      start_time: formatDateTimeWithOffset(start),
      end_time: formatDateTimeWithOffset(end)
    }
    const response = await service.post('/alerts', params)
    const raw = response.data || []

    const normalizeSeverity = (value) => {
      if (value === undefined || value === null) return 'medium'
      const v = String(value).toLowerCase()
      const map = {
        'fatal': 'fatal',
        'critical': 'fatal',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'tips': 'tips',
        'info': 'tips',
        '1': 'fatal',
        '2': 'high',
        '3': 'medium',
        '4': 'low',
        '5': 'tips'
      }
      return map[v] || 'medium'
    }

    const normalizeStatus = (value) => {
      if (!value) return 'open'
      const v = String(value).toLowerCase()
      if (['open', 'block', 'closed'].includes(v)) return v
      return v
    }

    const normalized = raw.map(item => ({
      ...item,
      riskLevel: normalizeSeverity(item.riskLevel || item.severity),
      status: normalizeStatus(item.status || item.handle_status),
      model_name: item.model_name || item.model,
      close_comment: item.close_comment || item.closeComment || item?.data_object?.close_comment || null
    }))

    // Client-side fallback for model_name filter
    const modelKeyword = searchKeywords.value.find(k => k.field === 'model_name' || k.field === 'model')
    const filtered = modelKeyword
      ? normalized.filter(a => {
          const val = a.model_name || a.model || a?.extend_properties?.model_name || a?.extend_properties?.model
          return val ? String(val).toLowerCase() === String(modelKeyword.value).toLowerCase() : false
        })
      : normalized

    alerts.value = filtered
    total.value = response.total || filtered.length || 0
  } catch (error) {
    console.error('Failed to load alerts:', error)
    alerts.value = []
    total.value = 0
  } finally {
    loadingAlerts.value = false
  }
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    handleRefresh()
  }
}

const handleCustomRangeChange = (range) => {
  customTimeRange.value = range
  if (selectedTimeRange.value === 'customRange' && range && range.length === 2) {
    handleRefresh()
  }
}

const handleRefresh = async () => {
  await Promise.all([
    loadAiAccuracyStatistics(),
    loadAlerts()
  ])
}

watch([currentPage, pageSize], () => {
  loadAlerts()
})

onMounted(() => {
  ensureAiAccuracyChart()
  document.addEventListener('click', handleClickOutside)
  handleRefresh()
})

onBeforeUnmount(() => {
  disposeAiAccuracyChart()
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.ai-agent__html {
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

.ai-agent__html :deep(pre) {
  background: #f5f5f5;
  border: 1px solid #cccccc;
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  margin: 10px 0;
  max-width: 100%;
  overflow-x: auto;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

:global(.dark) .ai-agent__html :deep(pre),
.ai-agent__html--dark :deep(pre) {
  background: #0f172a !important;
  border: 1px solid rgba(94, 114, 164, 0.45) !important;
  color: #e2e8f0 !important;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.4);
}

.ai-agent__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
  color: #0f172a;
}

:global(.dark) .ai-agent__html :deep(code),
.ai-agent__html--dark :deep(code) {
  color: #f1f5f9;
  background: transparent;
  padding: 0;
  border: none;
}

.ai-agent__html :deep(b) {
  color: #0f172a;
}

:global(.dark) .ai-agent__html :deep(b),
.ai-agent__html--dark :deep(b) {
  color: #e2e8f0;
}
</style>

