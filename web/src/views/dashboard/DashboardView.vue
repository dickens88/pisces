<template>
  <div class="w-full">
    <!-- Page header -->
    <div class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-white text-3xl font-bold tracking-tight">
        {{ $t('dashboard.title') }}
      </h1>
      <div class="flex items-center gap-2">
        <button
          @click="handleRefresh"
          :disabled="isRefreshing"
          class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546] h-9"
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
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </div>

    <!-- Statistics cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <!-- Alert count -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.alertCount24h') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
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
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.incidentCount30d') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
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
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.vulnerabilityCount30d') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
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

      <!-- Average detection time -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.mttd') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
          {{ statistics.mttd || '0m 0s' }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            statistics.mttdTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ statistics.mttdTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ statistics.mttdTrend === 'up' ? '+' : '' }}{{ statistics.mttdChange }}%
        </p>
      </div>
    </div>

    <!-- Charts area -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Alert type statistics -->
      <div class="flex flex-col rounded-xl border border-[#324867]/50 bg-[#19222c] p-0">
        <div class="flex justify-between items-center p-3 pt-2">
          <p class="text-white text-lg font-semibold">{{ $t('dashboard.charts.alertTypeStats') }}</p>
          <span class="text-xs text-white/60">{{ dashboardTimeRangeLabel }}</span>
        </div>
        <div class="flex flex-col gap-1 px-3 pb-2">
          <span class="text-white/60 text-sm font-medium uppercase tracking-wide">{{ $t('common.totalAlerts') }}</span>
          <span class="text-white text-3xl font-bold tracking-tight">{{ alertSourceTotal.toLocaleString() }}</span>
        </div>
        <div class="relative h-80">
          <div 
            v-if="alertSourceLoading"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div 
            v-else-if="alertSourceValues.length === 0"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
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
      <div class="flex flex-col rounded-xl border border-[#324867]/50 bg-[#19222c] p-0">
        <div class="flex justify-between items-center p-3 pt-2">
          <p class="text-white text-lg font-semibold">{{ $t('dashboard.charts.aiAccuracy') }}</p>
          <span class="text-xs text-white/60">{{ dashboardTimeRangeLabel }}</span>
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
import { getDashboardStatistics } from '@/api/dashboard'
import { getAlertCountsBySource, getAlertTrend, getAiAccuracyByModel } from '@/api/alerts'
import { getIncidentTrend, getVulnerabilityTrend } from '@/api/incidents'

const { t } = useI18n()

/**
 * @brief 统计数据
 */
const statistics = ref({
  alertCount24h: 0,
  alertCount24hChange: 0,
  alertCount24hTrend: 'up',
  incidentCount24h: 0,
  incidentCount24hChange: 0,
  incidentCount24hTrend: 'down',
  vulnerabilityCount: 0,
  vulnerabilityCountChange: 0,
  vulnerabilityCountTrend: 'down',
  mttd: '0m 0s',
  mttdChange: 0,
  mttdTrend: 'down'
})


/**
 * @brief 选中的时间范围
 */
const selectedTimeRange = ref('last24Hours')

/**
 * @brief 自定义时间范围
 */
const customTimeRange = ref(null)

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

const aiAccuracyChartRef = ref(null)
const aiAccuracyData = ref([])
const aiAccuracyLoading = ref(false)
let aiAccuracyChartInstance = null
let aiAccuracyResizeListenerBound = false

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
    const now = new Date()
    const end24h = new Date(now)
    const start24h = new Date(now)
    start24h.setHours(start24h.getHours() - 24)
    
    const start48h = new Date(start24h)
    start48h.setHours(start48h.getHours() - 24)

    // Get last 24 hours data
    const response24h = await getAlertTrend(
      start24h,
      end24h
    )
    
    // Get previous 24 hours data (24-48 hours ago)
    const response48h = await getAlertTrend(
      start48h,
      start24h
    )

    const data24h = response24h?.data || []
    const data48h = response48h?.data || []

    // Calculate total counts
    const total24h = data24h.reduce((sum, item) => sum + (item.count || 0), 0)
    const total48h = data48h.reduce((sum, item) => sum + (item.count || 0), 0)

    alertCount24hTotal.value = total24h

    // Calculate percentage change
    if (total48h > 0) {
      const change = ((total24h - total48h) / total48h) * 100
      alertCount24hChange.value = Math.abs(change).toFixed(1)
      alertCount24hTrend.value = change >= 0 ? 'up' : 'down'
    } else {
      alertCount24hChange.value = total24h > 0 ? '100.0' : '0.0'
      alertCount24hTrend.value = total24h > 0 ? 'up' : 'down'
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
    const now = new Date()
    const end30d = new Date(now)
    const start30d = new Date(now)
    start30d.setDate(start30d.getDate() - 30)
    
    const start60d = new Date(start30d)
    start60d.setDate(start60d.getDate() - 30)

    // Get last 30 days data
    const response30d = await getIncidentTrend(
      start30d,
      end30d
    )
    
    // Get previous 30 days data (30-60 days ago)
    const response60d = await getIncidentTrend(
      start60d,
      start30d
    )

    const data30d = response30d?.data || []
    const data60d = response60d?.data || []

    // Calculate total counts
    const total30d = data30d.reduce((sum, item) => sum + (item.count || 0), 0)
    const total60d = data60d.reduce((sum, item) => sum + (item.count || 0), 0)

    incidentCount30dTotal.value = total30d

    // Calculate percentage change
    if (total60d > 0) {
      const change = ((total30d - total60d) / total60d) * 100
      incidentCount30dChange.value = Math.abs(change).toFixed(1)
      incidentCount30dTrend.value = change >= 0 ? 'up' : 'down'
    } else {
      incidentCount30dChange.value = total30d > 0 ? '100.0' : '0.0'
      incidentCount30dTrend.value = total30d > 0 ? 'up' : 'down'
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
    const now = new Date()
    const end30d = new Date(now)
    const start30d = new Date(now)
    start30d.setDate(start30d.getDate() - 30)
    
    const start60d = new Date(start30d)
    start60d.setDate(start60d.getDate() - 30)

    // Get last 30 days data
    const response30d = await getVulnerabilityTrend(
      start30d,
      end30d
    )
    
    // Get previous 30 days data (30-60 days ago)
    const response60d = await getVulnerabilityTrend(
      start60d,
      start30d
    )

    const data30d = response30d?.data || []
    const data60d = response60d?.data || []

    // Calculate total counts
    const total30d = data30d.reduce((sum, item) => sum + (item.count || 0), 0)
    const total60d = data60d.reduce((sum, item) => sum + (item.count || 0), 0)

    vulnerabilityCount30dTotal.value = total30d

    // Calculate percentage change
    if (total60d > 0) {
      const change = ((total30d - total60d) / total60d) * 100
      vulnerabilityCount30dChange.value = Math.abs(change).toFixed(1)
      vulnerabilityCount30dTrend.value = change >= 0 ? 'up' : 'down'
    } else {
      vulnerabilityCount30dChange.value = total30d > 0 ? '100.0' : '0.0'
      vulnerabilityCount30dTrend.value = total30d > 0 ? 'up' : 'down'
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
      top: 16,
      left: 36,
      right: 16,
      bottom: 36,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: '#cbd5f5',
        rotate: categories.length > 5 ? 20 : 0,
        fontSize: 10,
        margin: 8
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
 * @brief 加载统计数据
 */
const loadStatistics = async () => {
  try {
    const response = await getDashboardStatistics()
    if (response && response.data) {
      // Handle each field separately to avoid overwriting default values
      const data = response.data
      
      // Update basic statistics fields
      // Note: alertCount24h is now handled by loadAlertCount24hData()
      // Note: incidentCount30d is now handled by loadIncidentCount30dData()
      // Note: vulnerabilityCount30d is now handled by loadVulnerabilityCount30dData()
      
      if (data.mttd !== undefined) statistics.value.mttd = data.mttd
      if (data.mttdChange !== undefined) statistics.value.mttdChange = data.mttdChange
      if (data.mttdTrend !== undefined) statistics.value.mttdTrend = data.mttdTrend
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
    // Use default mock data when API call fails, but keep existing chart data
    // Note: alertCount24h is now handled by loadAlertCount24hData()
    // Note: incidentCount30d is now handled by loadIncidentCount30dData()
    // Note: vulnerabilityCount30d is now handled by loadVulnerabilityCount30dData()
    statistics.value.mttd = '12m 34s'
    statistics.value.mttdChange = -1.2
    statistics.value.mttdTrend = 'down'
    // Chart data remains at default values
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
    loadStatistics(),
    loadAlertSourceStatistics(),
    loadAlertCount24hData(),
    loadIncidentCount30dData(),
    loadVulnerabilityCount30dData(),
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
