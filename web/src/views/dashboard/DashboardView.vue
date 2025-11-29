<template>
  <div class="w-full">
    <!-- Page header -->
    <div class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
        {{ $t('dashboard.title') }}
      </h1>
      <div class="flex items-center gap-2">
        <button
          @click="handleRefresh"
          :disabled="isRefreshing"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-9"
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
          storage-key="dashboard"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </div>

    <!-- Statistics cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <!-- Alert count -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#19222c] border border-gray-200 dark:border-[#324867]/50">
        <p class="text-gray-600 dark:text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.alertCount24h') }}</p>
        <p class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
          {{ alertCount24hTotal?.toLocaleString() || 0 }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            alertCount24hTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ alertCount24hTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ alertCount24hTrend === 'up' ? '+' : '' }}{{ alertCount24hChange }}%
        </p>
      </div>

      <!-- Incident count -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#19222c] border border-gray-200 dark:border-[#324867]/50">
        <p class="text-gray-600 dark:text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.incidentCount30d') }}</p>
        <p class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
          {{ incidentCount30dTotal?.toLocaleString() || 0 }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            incidentCount30dTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ incidentCount30dTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ incidentCount30dTrend === 'up' ? '+' : '' }}{{ incidentCount30dChange }}%
        </p>
      </div>

      <!-- Vulnerability count -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#19222c] border border-gray-200 dark:border-[#324867]/50">
        <p class="text-gray-600 dark:text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.vulnerabilityCount30d') }}</p>
        <p class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
          {{ vulnerabilityCount30dTotal?.toLocaleString() || 0 }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            vulnerabilityCount30dTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ vulnerabilityCount30dTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ vulnerabilityCount30dTrend === 'up' ? '+' : '' }}{{ vulnerabilityCount30dChange }}%
        </p>
      </div>

      <!-- Automation Closure Rate -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#19222c] border border-gray-200 dark:border-[#324867]/50">
        <p class="text-gray-600 dark:text-white/70 text-sm font-medium">
          {{ $t('alerts.list.statistics.automationClosureRate') || 'Automation Closure Rate' }}
        </p>
        <p class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
          {{ automationClosureRate }}%
        </p>
        <p class="text-sm text-gray-600 dark:text-white/60">
          {{ dashboardTimeRangeLabel }}
        </p>
      </div>
    </div>

    <!-- Charts area -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Alert type statistics -->
      <div class="flex flex-col rounded-xl border border-gray-200 dark:border-[#324867]/50 bg-white dark:bg-[#19222c] p-0">
        <div class="flex justify-between items-center p-3 pt-2">
          <p class="text-gray-900 dark:text-white text-lg font-semibold">{{ $t('dashboard.charts.alertTypeStats') }}</p>
          <span class="text-xs text-gray-600 dark:text-white/60">{{ dashboardTimeRangeLabel }}</span>
        </div>
        <div class="flex flex-col gap-1 px-3 pb-2">
          <span class="text-gray-600 dark:text-white/60 text-sm font-medium uppercase tracking-wide">{{ $t('common.totalAlerts') }}</span>
          <span class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">{{ alertSourceTotal.toLocaleString() }}</span>
        </div>
        <div class="relative h-80">
          <div 
            v-if="alertSourceLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-white/50 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div 
            v-else-if="alertSourceValues.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-white/50 text-sm"
          >
            {{ $t('dashboard.charts.noData') }}
          </div>
          <div 
            v-show="!alertSourceLoading && alertSourceValues.length > 0"
            ref="alertSourceChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>

      <!-- AI accuracy rate -->
      <div class="flex flex-col rounded-xl border border-gray-200 dark:border-[#324867]/50 bg-white dark:bg-[#19222c] p-0">
        <div class="flex justify-between items-center p-3 pt-2">
          <p class="text-gray-900 dark:text-white text-lg font-semibold">{{ $t('dashboard.charts.aiAccuracy') }}</p>
          <span class="text-xs text-gray-600 dark:text-white/60">{{ dashboardTimeRangeLabel }}</span>
        </div>
        <div class="flex flex-col gap-1 px-3 pb-2">
          <span class="text-gray-600 dark:text-white/60 text-sm font-medium uppercase tracking-wide">
            {{ $t('common.averageAccuracy') || 'Average Accuracy' }}
          </span>
          <span class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
            {{ aiAccuracyAverage }}%
          </span>
        </div>
        <div class="relative h-80">
          <div 
            v-if="aiAccuracyLoading"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div 
            v-else-if="aiAccuracyData.length === 0"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('dashboard.charts.noData') }}
          </div>
          <div 
            v-show="!aiAccuracyLoading && aiAccuracyData.length > 0"
            ref="aiAccuracyChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { getAlertCountsBySource, getAlertTrend, getAiAccuracyByModel, getAlertStatistics } from '@/api/alerts'
import { getIncidentTrend, getVulnerabilityTrend } from '@/api/incidents'

const { t } = useI18n()

/**
 * @brief 时间范围存储
 */
const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('dashboard', 'last24Hours')

/**
 * @brief 是否正在刷新
 */
const isRefreshing = ref(false)

const alertSourceChartRef = ref(null)
const alertSourceCategories = ref([])
const alertSourceValues = ref([])
const alertSourceTotal = ref(0)
const alertSourceLoading = ref(false)

let alertSourceChartInstance = null
let alertSourceResizeListenerBound = false

// Automation Closure Rate
const automationClosureRate = ref('0.0')
const automationClosureRateLoading = ref(false)

const aiAccuracyChartRef = ref(null)
const aiAccuracyData = ref([])
const aiAccuracyLoading = ref(false)
let aiAccuracyChartInstance = null
let aiAccuracyResizeListenerBound = false
const aiAccuracyAverage = computed(() => {
  if (!aiAccuracyData.value.length) {
    return '0.0'
  }
  const sum = aiAccuracyData.value.reduce((total, item) => total + (Number(item.accuracy) || 0), 0)
  return (sum / aiAccuracyData.value.length).toFixed(1)
})
const wrapAxisLabel = (label) => {
  if (!label) {
    return ''
  }
  const normalized = String(label)
  const chunkSize = normalized.length > 12 ? 12 : 8
  const segments = normalized.match(new RegExp(`.{1,${chunkSize}}`, 'g'))
  return segments ? segments.join('\n') : normalized
}

// Alert Count 24h
const alertCount24hTotal = ref(0)
const alertCount24hChange = ref(0)
const alertCount24hTrend = ref('down')

// Incident Count 30d
const incidentCount30dTotal = ref(0)
const incidentCount30dChange = ref(0)
const incidentCount30dTrend = ref('down')

// Vulnerability Count 30d
const vulnerabilityCount30dTotal = ref(0)
const vulnerabilityCount30dChange = ref(0)
const vulnerabilityCount30dTrend = ref('down')

const formatDateForBackend = (date) => {
  const isoString = date.toISOString()
  return isoString.includes('.') ? isoString.split('.')[0] : isoString.replace('Z', '')
}

const handleAlertSourceResize = () => {
  if (alertSourceChartInstance) {
    alertSourceChartInstance.resize()
  }
}

const handleAiAccuracyResize = () => {
  if (aiAccuracyChartInstance) {
    aiAccuracyChartInstance.resize()
  }
}

const ensureAlertSourceChart = () => {
  if (!alertSourceChartInstance && alertSourceChartRef.value) {
    alertSourceChartInstance = echarts.init(alertSourceChartRef.value)
    if (!alertSourceResizeListenerBound) {
      window.addEventListener('resize', handleAlertSourceResize)
      alertSourceResizeListenerBound = true
    }
  }
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

const disposeAlertSourceChart = () => {
  if (alertSourceChartInstance) {
    alertSourceChartInstance.dispose()
    alertSourceChartInstance = null
  }
  if (alertSourceResizeListenerBound) {
    window.removeEventListener('resize', handleAlertSourceResize)
    alertSourceResizeListenerBound = false
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

const loadAlertCount24hData = async () => {
  try {
    const { start, end } = getDashboardTimeRange()
    const timeRange = end.getTime() - start.getTime()
    const previousStart = new Date(start.getTime() - timeRange)
    const previousEnd = new Date(start)
    
    // Fetch data for current period
    const currentResponse = await getAlertTrend(start, end)
    const currentData = currentResponse?.data || []
    
    // Fetch data for previous period
    const previousResponse = await getAlertTrend(previousStart, previousEnd)
    const previousData = previousResponse?.data || []

    let currentTotal = 0
    let previousTotal = 0

    currentData.forEach((item) => {
      const count = Number(item.count) || 0
      currentTotal += count
    })

    previousData.forEach((item) => {
      const count = Number(item.count) || 0
      previousTotal += count
    })

    alertCount24hTotal.value = currentTotal

    // Calculate percentage change
    if (previousTotal > 0) {
      const change = ((currentTotal - previousTotal) / previousTotal) * 100
      alertCount24hChange.value = Math.abs(change).toFixed(1)
      alertCount24hTrend.value = change >= 0 ? 'up' : 'down'
    } else {
      alertCount24hChange.value = currentTotal > 0 ? '100.0' : '0.0'
      alertCount24hTrend.value = currentTotal > 0 ? 'up' : 'down'
    }
  } catch (error) {
    console.error('Failed to load alert count 24h data:', error)
    alertCount24hTotal.value = 0
    alertCount24hChange.value = 0
    alertCount24hTrend.value = 'down'
  }
}

const loadIncidentCount30dData = async () => {
  try {
    const { start, end } = getDashboardTimeRange()
    const timeRange = end.getTime() - start.getTime()
    const previousStart = new Date(start.getTime() - timeRange)
    const previousEnd = new Date(start)
    
    // Fetch data for current period
    const currentResponse = await getIncidentTrend(start, end)
    const currentData = currentResponse?.data || []
    
    // Fetch data for previous period
    const previousResponse = await getIncidentTrend(previousStart, previousEnd)
    const previousData = previousResponse?.data || []

    let currentTotal = 0
    let previousTotal = 0

    currentData.forEach((item) => {
      const count = Number(item.count) || 0
      currentTotal += count
    })

    previousData.forEach((item) => {
      const count = Number(item.count) || 0
      previousTotal += count
    })

    incidentCount30dTotal.value = currentTotal

    if (previousTotal > 0) {
      const change = ((currentTotal - previousTotal) / previousTotal) * 100
      incidentCount30dChange.value = Math.abs(change).toFixed(1)
      incidentCount30dTrend.value = change >= 0 ? 'up' : 'down'
    } else {
      incidentCount30dChange.value = currentTotal > 0 ? '100.0' : '0.0'
      incidentCount30dTrend.value = currentTotal > 0 ? 'up' : 'down'
    }
  } catch (error) {
    console.error('Failed to load incident count 30d data:', error)
    incidentCount30dTotal.value = 0
    incidentCount30dChange.value = 0
    incidentCount30dTrend.value = 'down'
  }
}

const loadVulnerabilityCount30dData = async () => {
  try {
    const { start, end } = getDashboardTimeRange()
    const timeRange = end.getTime() - start.getTime()
    const previousStart = new Date(start.getTime() - timeRange)
    const previousEnd = new Date(start)
    
    // Fetch data for current period
    const currentResponse = await getVulnerabilityTrend(start, end)
    const currentData = currentResponse?.data || []
    
    // Fetch data for previous period
    const previousResponse = await getVulnerabilityTrend(previousStart, previousEnd)
    const previousData = previousResponse?.data || []

    let currentTotal = 0
    let previousTotal = 0

    currentData.forEach((item) => {
      const count = Number(item.count) || 0
      currentTotal += count
    })

    previousData.forEach((item) => {
      const count = Number(item.count) || 0
      previousTotal += count
    })

    vulnerabilityCount30dTotal.value = currentTotal

    if (previousTotal > 0) {
      const change = ((currentTotal - previousTotal) / previousTotal) * 100
      vulnerabilityCount30dChange.value = Math.abs(change).toFixed(1)
      vulnerabilityCount30dTrend.value = change >= 0 ? 'up' : 'down'
    } else {
      vulnerabilityCount30dChange.value = currentTotal > 0 ? '100.0' : '0.0'
      vulnerabilityCount30dTrend.value = currentTotal > 0 ? 'up' : 'down'
    }
  } catch (error) {
    console.error('Failed to load vulnerability count 30d data:', error)
    vulnerabilityCount30dTotal.value = 0
    vulnerabilityCount30dChange.value = 0
    vulnerabilityCount30dTrend.value = 'down'
  }
}

const updateAlertSourceChart = () => {
  ensureAlertSourceChart()
  if (!alertSourceChartInstance) {
    return
  }

  // Clear previous option to ensure new settings take effect
  alertSourceChartInstance.clear()

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
      top: 8,
      right: 8,
      bottom: 20,
      left: 28,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: alertSourceCategories.value,
      boundaryGap: true,
      axisLabel: {
        color: '#cbd5f5',
        rotate: alertSourceCategories.value.length > 5 ? 20 : 0,
        margin: 2,
        fontSize: 10
      },
      axisLine: {
        lineStyle: { color: '#334155' }
      },
      axisTick: { show: true, inside: true, alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#94a3b8' },
      splitLine: {
        lineStyle: { color: '#1f2a37' }
      },
      axisLine: { show: false }
    },
    series: [
      {
        name: t('alerts.title'),
        type: 'bar',
        data: alertSourceValues.value,
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

  alertSourceChartInstance.setOption(option, true)
  // Force resize to ensure grid changes take effect
  setTimeout(() => {
    alertSourceChartInstance.resize()
  }, 0)
}

const updateAiAccuracyChart = () => {
  ensureAiAccuracyChart()
  if (!aiAccuracyChartInstance) {
    return
  }

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
        if (!params || params.length === 0) {
          return ''
        }
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
      axisLine: {
        lineStyle: { color: '#334155' }
      },
      axisTick: {
        show: true,
        inside: true,
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        color: '#94a3b8',
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: { color: '#1f2a37' }
      },
      axisLine: { show: false }
    },
    series: [
      {
        name: t('dashboard.charts.aiAccuracy'),
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
  setTimeout(() => {
    aiAccuracyChartInstance?.resize()
  }, 0)
}

const getDashboardTimeRange = () => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      return {
        start: new Date(customTimeRange.value[0]),
        end: new Date(customTimeRange.value[1])
      }
    }
    // Fallback to last 24 hours if custom range incomplete
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

const loadAlertSourceStatistics = async () => {
  alertSourceLoading.value = true
  alertSourceTotal.value = 0
  try {
    const { start, end } = getDashboardTimeRange()
    const response = await getAlertCountsBySource(start, end)
    const counts = response?.data || {}
    const entries = Object.entries(counts).map(([name, value]) => [name, Number(value) || 0])
    entries.sort((a, b) => b[1] - a[1])
    alertSourceCategories.value = entries.map(([name]) => name)
    alertSourceValues.value = entries.map(([, value]) => value)
    alertSourceTotal.value = alertSourceValues.value.reduce((sum, value) => sum + value, 0)
  } catch (error) {
    console.error('Failed to load alert source statistics:', error)
    alertSourceCategories.value = []
    alertSourceValues.value = []
    alertSourceTotal.value = 0
  } finally {
    alertSourceLoading.value = false
    await nextTick()
    updateAlertSourceChart()
  }
}

const loadAutomationClosureRate = async () => {
  automationClosureRateLoading.value = true
  try {
    const { start, end } = getDashboardTimeRange()
    const response = await getAlertStatistics(start, end)
    const rate = response?.data?.automation_rate
    if (rate !== undefined && rate !== null) {
      automationClosureRate.value = Number(rate).toFixed(1)
    } else {
      automationClosureRate.value = '0.0'
    }
  } catch (error) {
    console.error('Failed to load automation closure rate:', error)
    automationClosureRate.value = '0.0'
  } finally {
    automationClosureRateLoading.value = false
  }
}

const loadAiAccuracyStatistics = async () => {
  aiAccuracyLoading.value = true
  try {
    const { start, end } = getDashboardTimeRange()
    const response = await getAiAccuracyByModel(
      start,
      end,
      10
    )
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

/**
 * @brief 处理时间范围变化
 * @param {String} rangeKey 时间范围键
 */
const handleTimeRangeChange = (rangeKey) => {
  // Reload data when time range changes
  loadData()
}

/**
 * @brief 处理自定义时间范围变化
 * @param {Array} range 自定义时间范围数组
 */
const handleCustomRangeChange = (range) => {
  // Reload data when custom time range changes
  if (range && range.length === 2) {
    loadData()
  }
}

/**
 * @brief 处理刷新
 */
const handleRefresh = async () => {
  if (isRefreshing.value) return
  
  isRefreshing.value = true
  try {
    await loadData()
  } catch (error) {
    console.error('Failed to refresh:', error)
  } finally {
    isRefreshing.value = false
  }
}

/**
 * @brief 加载所有数据
 */
const loadData = async () => {
  await Promise.all([
    loadAlertSourceStatistics(),
    loadAlertCount24hData(),
    loadIncidentCount30dData(),
    loadVulnerabilityCount30dData(),
    loadAutomationClosureRate(),
    loadAiAccuracyStatistics()
  ])
}


/**
 * @brief 组件挂载时加载数据
 */
onMounted(() => {
  ensureAlertSourceChart()
  ensureAiAccuracyChart()
  loadData()
})

onBeforeUnmount(() => {
  disposeAlertSourceChart()
  disposeAiAccuracyChart()
})

const dashboardTimeRangeLabel = computed(() => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      const start = new Date(customTimeRange.value[0])
      const end = new Date(customTimeRange.value[1])
      return `${start.toLocaleDateString()} ~ ${end.toLocaleDateString()}`
    }
    return t('common.timeRange.customRange')
  }
  return t(`common.timeRange.${selectedTimeRange.value}`) || t('common.timeRange.last24Hours')
})
</script>
