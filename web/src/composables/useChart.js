import { ref, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { useI18n } from 'vue-i18n'

// Common constants
const SEVERITY_COLORS = {
  'Critical': '#FF4D4F',
  'High': '#FF7A45',
  'Medium': '#FFA940',
  'Low': '#1890FF',
  'Tips': '#91D5FF',
  'Unknown': '#8C8C8C'
}

const SEVERITY_ORDER = ['Critical', 'High', 'Medium', 'Low', 'Tips']
const PIE_COLORS = [
  '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af',
  '#8b5cf6', '#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95',
  '#ec4899', '#db2777', '#be185d', '#9f1239', '#831843',
  '#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f'
]

const COMMON_TOOLTIP = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  borderWidth: 0,
  textStyle: { color: '#e2e8f0' },
  padding: [10, 12]
}

const isDarkMode = () => document.documentElement.classList.contains('dark')

/**
 * Composable for managing ECharts instances
 */
export function useChart(chartRef) {
  let chartInstance = null
  let resizeBound = false

  const handleResize = () => chartInstance?.resize()

  const ensureChart = () => {
    if (!chartInstance && chartRef.value) {
      chartInstance = echarts.init(chartRef.value)
      if (!resizeBound) {
        window.addEventListener('resize', handleResize)
        resizeBound = true
      }
    }
  }

  const disposeChart = () => {
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
    if (resizeBound) {
      window.removeEventListener('resize', handleResize)
      resizeBound = false
    }
  }

  const updateChart = (option) => {
    ensureChart()
    if (!chartInstance) return
    chartInstance.clear()
    chartInstance.setOption(option, true)
    nextTick(() => chartInstance.resize())
  }

  onBeforeUnmount(disposeChart)

  return { ensureChart, disposeChart, updateChart, getInstance: () => chartInstance }
}

// Helper functions
const formatDateLabel = (dateStr, index, daysDiff, totalDates) => {
  const date = new Date(dateStr)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const year = date.getFullYear()
  
  if (daysDiff <= 30) return `${month}/${day}`
  if (daysDiff <= 90) return `${month}/${day}`
  if (daysDiff <= 365) {
    if (day === '01' || index === 0) {
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      return `${monthNames[date.getMonth()]} ${day}`
    }
    return `${month}/${day}`
  }
  
  const isFirstOfMonth = day === '01'
  const isFirstDate = index === 0
  const isLastDate = index === totalDates - 1
  
  if (isFirstOfMonth) return `${year}-${month}`
  if (isFirstDate || isLastDate) return `${year}-${month}-${day}`
  return `${month}/${day}`
}

const calculateLabelInterval = (dataPoints, daysDiff) => {
  if (daysDiff <= 30) return 0
  if (daysDiff <= 90) return Math.max(0, Math.floor(dataPoints / 20))
  if (daysDiff <= 365) return Math.max(0, Math.floor(dataPoints / 15))
  return Math.max(0, Math.floor(dataPoints / 12))
}

const normalizeSeverity = (severity) => 
  severity ? (severity.charAt(0).toUpperCase() + severity.slice(1).toLowerCase()) : 'Unknown'

/**
 * Composable for trend chart by severity
 */
export function useTrendChartBySeverity(chartRef, loadDataFn) {
  const { t } = useI18n()
  const { updateChart, disposeChart, ensureChart } = useChart(chartRef)
  
  const chartDates = ref([])
  const chartData = ref({})
  const loading = ref(false)

  const updateTrendChart = (computeSelectedRange) => {
    const range = computeSelectedRange()
    const daysDiff = Math.ceil((range.end - range.start) / (1000 * 60 * 60 * 24))
    const dataPoints = chartDates.value.length
    const shouldRotateLabels = dataPoints > 10 || daysDiff > 7

    const series = SEVERITY_ORDER
      .filter(severity => chartData.value[severity])
      .map(severity => {
        const color = SEVERITY_COLORS[severity] || SEVERITY_COLORS['Unknown']
        return {
          name: t(`common.severity.${severity.toLowerCase()}`) || severity,
          type: 'line',
          data: chartDates.value.map(date => chartData.value[severity]?.[date] || 0),
          smooth: true,
          symbol: 'circle',
          symbolSize: 4,
          lineStyle: { color, width: 2 },
          itemStyle: { color },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: `${color}40` },
              { offset: 1, color: `${color}00` }
            ])
          }
        }
      })

    updateChart({
      backgroundColor: 'transparent',
      tooltip: { ...COMMON_TOOLTIP, trigger: 'axis', axisPointer: { type: 'line' } },
      legend: {
        data: SEVERITY_ORDER
          .filter(severity => severity !== 'Unknown' && chartData.value[severity])
          .map(severity => t(`common.severity.${severity.toLowerCase()}`) || severity),
        textStyle: { color: '#94a3b8', fontSize: 11 },
        top: 5,
        itemWidth: 12,
        itemHeight: 8
      },
      grid: {
        top: 40,
        right: 10,
        bottom: shouldRotateLabels ? 50 : 30,
        left: 40,
        containLabel: false
      },
      xAxis: {
        type: 'category',
        data: chartDates.value.map((date, index) => formatDateLabel(date, index, daysDiff, dataPoints)),
        boundaryGap: false,
        axisLabel: {
          color: '#94a3b8',
          fontSize: 10,
          rotate: shouldRotateLabels ? -45 : 0,
          interval: calculateLabelInterval(dataPoints, daysDiff),
          margin: shouldRotateLabels ? 12 : 8,
          showMinLabel: true,
          showMaxLabel: true
        },
        axisLine: { show: true, lineStyle: { color: '#334155' } },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#94a3b8', margin: 0, fontSize: 10 },
        splitLine: { lineStyle: { color: '#1f2a37' } },
        axisLine: { show: true, lineStyle: { color: '#334155' } },
        axisTick: { show: true, inside: true }
      },
      series
    })
  }

  const loadData = async (computeSelectedRangeFn) => {
    loading.value = true
    try {
      const range = computeSelectedRangeFn()
      const response = await loadDataFn(range.start, range.end)
      const trendData = response?.data || []

      chartDates.value = [...new Set(trendData.map(item => item.date))].sort()

      const dataBySeverity = {}
      trendData.forEach(item => {
        const severity = item.severity || 'Unknown'
        if (!dataBySeverity[severity]) dataBySeverity[severity] = {}
        dataBySeverity[severity][item.date] = Number(item.count) || 0
      })

      chartData.value = dataBySeverity
    } catch (error) {
      console.error('Failed to load trend data:', error)
      chartDates.value = []
      chartData.value = {}
    } finally {
      loading.value = false
      await nextTick()
      updateTrendChart(computeSelectedRangeFn)
    }
  }

  return { chartDates, chartData, loading, loadData, updateTrendChart, ensureChart, disposeChart }
}

/**
 * Composable for department distribution chart (bar chart by severity)
 */
export function useDepartmentChart(chartRef, loadDataFn, titleKey) {
  const { t } = useI18n()
  const { updateChart, disposeChart, ensureChart } = useChart(chartRef)
  
  const chartData = ref({})
  const loading = ref(false)

  const updateDepartmentChart = () => {
    if (Object.keys(chartData.value).length === 0) return

    const departments = Object.keys(chartData.value)
    const allSeverities = new Set()
    departments.forEach(dept => {
      Object.keys(chartData.value[dept] || {}).forEach(severity => allSeverities.add(severity))
    })
    
    const severityOrder = [...SEVERITY_ORDER, 'Unknown']
    const severities = [
      ...severityOrder.filter(s => allSeverities.has(s)),
      ...Array.from(allSeverities).filter(s => !severityOrder.includes(s))
    ]

    const series = severities.map(severity => ({
      name: t(`common.severity.${severity.toLowerCase()}`) || severity,
      type: 'bar',
      stack: 'total', // Enable stacked bar chart
      data: departments.map(dept => chartData.value[dept]?.[severity] || 0),
      itemStyle: { color: SEVERITY_COLORS[severity] || SEVERITY_COLORS['Unknown'] }
    }))

    const textColor = isDarkMode() ? '#94a3b8' : '#374151'
    const lineColor = isDarkMode() ? '#334155' : '#e5e7eb'
    const splitLineColor = isDarkMode() ? '#1f2a37' : '#f3f4f6'
    const shouldRotate = departments.length > 5

    updateChart({
      backgroundColor: 'transparent',
      tooltip: { ...COMMON_TOOLTIP, trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: {
        data: severities.map(severity => t(`common.severity.${severity.toLowerCase()}`) || severity),
        textStyle: { color: textColor, fontSize: 11 },
        top: 5,
        itemWidth: 12,
        itemHeight: 8
      },
      grid: { top: 40, right: 10, bottom: 30, left: 40, containLabel: false },
      xAxis: {
        type: 'category',
        data: departments,
        axisLabel: {
          color: textColor,
          fontSize: 10,
          rotate: shouldRotate ? -45 : 0,
          margin: shouldRotate ? 12 : 8
        },
        axisLine: { show: true, lineStyle: { color: lineColor } },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: textColor, margin: 0, fontSize: 10 },
        splitLine: { lineStyle: { color: splitLineColor } },
        axisLine: { show: true, lineStyle: { color: lineColor } },
        axisTick: { show: true, inside: true }
      },
      series
    })
  }

  const loadData = async (computeSelectedRangeFn) => {
    loading.value = true
    try {
      const range = computeSelectedRangeFn()
      const response = await loadDataFn(range.start, range.end)
      const distribution = response?.data || {}
      
      const normalized = {}
      Object.entries(distribution).forEach(([dept, severities]) => {
        normalized[dept || 'Unknown'] = {}
        Object.entries(severities || {}).forEach(([severity, count]) => {
          normalized[dept || 'Unknown'][normalizeSeverity(severity)] = Number(count) || 0
        })
      })

      chartData.value = normalized
    } catch (error) {
      console.error('Failed to load department data:', error)
      chartData.value = {}
    } finally {
      loading.value = false
      await nextTick()
      updateDepartmentChart()
    }
  }

  return { chartData, loading, loadData, updateDepartmentChart, ensureChart, disposeChart }
}

/**
 * Composable for root cause distribution chart (pie chart)
 */
export function useRootCauseChart(chartRef, loadDataFn, titleKey) {
  const { t } = useI18n()
  const { updateChart, disposeChart, ensureChart } = useChart(chartRef)
  
  const chartData = ref([])
  const loading = ref(false)

  const updateRootCauseChart = () => {
    if (chartData.value.length === 0) return

    const textColor = isDarkMode() ? '#e2e8f0' : '#374151'
    const legendColor = isDarkMode() ? '#94a3b8' : '#374151'
    const borderColor = isDarkMode() ? '#111822' : '#ffffff'
    const labelLineColor = isDarkMode() ? '#94a3b8' : '#9ca3af'

    updateChart({
      backgroundColor: 'transparent',
      tooltip: {
        ...COMMON_TOOLTIP,
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'middle',
        textStyle: { color: legendColor, fontSize: 11 },
        itemWidth: 12,
        itemHeight: 8,
        itemGap: 8
      },
      series: [{
        name: t(titleKey) || 'Root Cause Distribution',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        roseType: 'area',
        itemStyle: {
          borderRadius: 4,
          borderColor,
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          color: textColor,
          fontSize: 10
        },
        labelLine: {
          show: true,
          length: 10,
          length2: 5,
          lineStyle: { color: labelLineColor }
        },
        emphasis: {
          label: { show: true, fontSize: 12, fontWeight: 'bold' },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: chartData.value.map(item => ({
          name: item.name || 'Unknown',
          value: item.value || 0
        })),
        color: PIE_COLORS
      }]
    })
  }

  const loadData = async (computeSelectedRangeFn) => {
    loading.value = true
    try {
      const range = computeSelectedRangeFn()
      const response = await loadDataFn(range.start, range.end)
      const distribution = response?.data || {}
      
      chartData.value = Object.entries(distribution)
        .map(([name, value]) => ({ name: name || 'Unknown', value: Number(value) || 0 }))
        .filter(item => item.value > 0)
        .sort((a, b) => b.value - a.value)
    } catch (error) {
      console.error('Failed to load root cause data:', error)
      chartData.value = []
    } finally {
      loading.value = false
      await nextTick()
      updateRootCauseChart()
    }
  }

  return { chartData, loading, loadData, updateRootCauseChart, ensureChart, disposeChart }
}

