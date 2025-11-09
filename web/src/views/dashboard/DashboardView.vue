<template>
  <div class="w-full">
    <!-- 页面头部 -->
    <div class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-white text-3xl font-bold tracking-tight">
        {{ $t('dashboard.title') }}
      </h1>
      <div class="flex items-center gap-2">
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <!-- 告警数量 -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.alertCount24h') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
          {{ statistics.alertCount24h?.toLocaleString() || 0 }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            statistics.alertCount24hTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ statistics.alertCount24hTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ statistics.alertCount24hTrend === 'up' ? '+' : '' }}{{ statistics.alertCount24hChange }}%
        </p>
      </div>

      <!-- 事件数 -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.incidentCount24h') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
          {{ statistics.incidentCount24h?.toLocaleString() || 0 }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            statistics.incidentCount24hTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ statistics.incidentCount24hTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ statistics.incidentCount24hTrend === 'up' ? '+' : '' }}{{ statistics.incidentCount24hChange }}%
        </p>
      </div>

      <!-- 漏洞数 -->
      <div class="flex flex-col gap-2 rounded-xl p-6 bg-[#19222c] border border-[#324867]/50">
        <p class="text-white/70 text-sm font-medium">{{ $t('dashboard.statistics.vulnerabilityCount') }}</p>
        <p class="text-white text-3xl font-bold tracking-tight">
          {{ statistics.vulnerabilityCount || 0 }}
        </p>
        <p 
          :class="[
            'text-sm font-medium flex items-center gap-1',
            statistics.vulnerabilityCountTrend === 'up' ? 'text-red-400' : 'text-green-400'
          ]"
        >
          <span class="material-symbols-outlined text-base">
            {{ statistics.vulnerabilityCountTrend === 'up' ? 'arrow_upward' : 'arrow_downward' }}
          </span>
          {{ statistics.vulnerabilityCountTrend === 'up' ? '+' : '' }}{{ statistics.vulnerabilityCountChange }}
        </p>
      </div>

      <!-- 平均检测时间 -->
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

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- 告警类型统计 -->
      <div class="flex flex-col gap-4 rounded-xl border border-[#324867]/50 p-6 bg-[#19222c]">
        <div class="flex justify-between items-center">
          <p class="text-white text-lg font-semibold">{{ $t('dashboard.charts.alertTypeStats') }}</p>
          <div class="flex items-center gap-4 text-xs text-white/70">
            <div class="flex items-center gap-2">
              <div class="size-2.5 rounded-sm bg-primary/70"></div>
              <span>{{ $t('dashboard.charts.manual') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="size-2.5 rounded-sm bg-primary"></div>
              <span>{{ $t('dashboard.charts.auto') }}</span>
            </div>
          </div>
        </div>
        <div class="h-80 flex items-end gap-x-4 md:gap-x-6">
          <template v-if="statistics.alertTypeStats && statistics.alertTypeStats.length > 0">
            <div 
              v-for="(stat, index) in statistics.alertTypeStats" 
              :key="index"
              class="flex-1 h-full flex flex-col items-center gap-2"
            >
              <div class="w-full flex-1 flex items-end">
                <div class="w-full h-full flex flex-col justify-end rounded-t-sm hover:opacity-80 transition-opacity">
                  <div 
                    class="w-full bg-primary/70 rounded-t-sm"
                    :style="{ height: stat.manual + '%' }"
                  ></div>
                  <div 
                    class="w-full bg-primary rounded-t-sm"
                    :style="{ height: stat.auto + '%' }"
                  ></div>
                </div>
              </div>
              <span class="text-xs text-white/60">{{ stat.name }}</span>
            </div>
          </template>
          <div v-else class="w-full h-full flex items-center justify-center text-white/50 text-sm">
            {{ $t('dashboard.charts.noData') }}
          </div>
        </div>
      </div>

      <!-- AI研判正确率 -->
      <div class="flex flex-col gap-4 rounded-xl border border-[#324867]/50 p-6 bg-[#19222c]">
        <p class="text-white text-lg font-semibold">{{ $t('dashboard.charts.aiAccuracy') }}</p>
        <div class="h-80 flex items-end gap-x-4 md:gap-x-6">
          <template v-if="statistics.aiAccuracy && statistics.aiAccuracy.length > 0">
            <div 
              v-for="(item, index) in statistics.aiAccuracy" 
              :key="index"
              class="flex-1 h-full flex flex-col items-center gap-2 relative"
            >
              <span class="text-xs font-semibold absolute -top-5 text-primary">{{ item.accuracy }}%</span>
              <div class="w-full flex-1 flex items-end">
                <div 
                  class="w-full h-full bg-primary rounded-t-sm hover:opacity-80 transition-opacity"
                  :style="{ height: item.accuracy + '%' }"
                ></div>
              </div>
              <span class="text-xs text-white/60">{{ item.name }}</span>
            </div>
          </template>
          <div v-else class="w-full h-full flex items-center justify-center text-white/50 text-sm">
            {{ $t('dashboard.charts.noData') }}
          </div>
        </div>
      </div>
    </div>

    <!-- 表格区域 -->
    <!-- 最近未关闭的告警 -->
    <div class="rounded-xl border border-[#324867]/50 bg-[#19222c] mb-6">
      <div class="p-6">
        <h3 class="text-white text-lg font-semibold">{{ $t('dashboard.tables.recentOpenAlerts') }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-white/80">
          <thead class="text-xs text-white/60 uppercase bg-[#101822]/30">
            <tr>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.severity') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.alertName') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.time') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.sourceIp') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="alert in recentAlerts" 
              :key="alert.id"
              class="border-t border-[#324867]/50 hover:bg-white/5"
            >
              <td class="px-6 py-4">
                <span 
                  :class="[
                    'inline-flex items-center gap-2 font-medium',
                    getSeverityClass(alert.severity)
                  ]"
                >
                  <span 
                    :class="[
                      'w-2 h-2 rounded-full',
                      getSeverityDotClass(alert.severity)
                    ]"
                  ></span>
                  {{ $t(`dashboard.severity.${alert.severity}`) }}
                </span>
              </td>
              <td class="px-6 py-4 font-medium text-white/90">
                <button 
                  @click="handleInvestigateAlert(alert)"
                  class="text-primary hover:underline"
                >
                  {{ alert.name }}
                </button>
              </td>
              <td class="px-6 py-4">{{ alert.timestamp }}</td>
              <td class="px-6 py-4">{{ alert.sourceIp }}</td>
              <td class="px-6 py-4">
                <span 
                  :class="[
                    'text-xs font-medium px-2.5 py-0.5 rounded-full',
                    getStatusClass(alert.status)
                  ]"
                >
                  {{ $t(`dashboard.status.${alert.status}`) }}
                </span>
              </td>
            </tr>
            <tr v-if="recentAlerts.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-gray-400">
                {{ $t('common.noData') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 最近未关闭的漏洞 -->
    <div class="rounded-xl border border-[#324867]/50 bg-[#19222c]">
      <div class="p-6">
        <h3 class="text-white text-lg font-semibold">{{ $t('dashboard.tables.recentOpenVulnerabilities') }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-white/80">
          <thead class="text-xs text-white/60 uppercase bg-[#101822]/30">
            <tr>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.cvss') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.vulnerabilityName') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.affectedAsset') }}</th>
              <th class="px-6 py-3" scope="col">{{ $t('dashboard.tables.discoveryTime') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="vuln in recentVulnerabilities" 
              :key="vuln.id"
              class="border-t border-[#324867]/50 hover:bg-white/5"
            >
              <td class="px-6 py-4">
                <span 
                  :class="[
                    'inline-flex items-center gap-2 font-semibold',
                    getCvssClass(vuln.cvssLevel)
                  ]"
                >
                  {{ vuln.cvss }} {{ $t(`dashboard.severity.${vuln.cvssLevel}`) }}
                </span>
              </td>
              <td class="px-6 py-4 font-medium text-white/90">
                <button 
                  @click="handleViewVulnerabilityDetail(vuln)"
                  class="text-primary hover:underline"
                >
                  {{ vuln.name }}
                </button>
              </td>
              <td class="px-6 py-4">{{ vuln.affectedAsset }}</td>
              <td class="px-6 py-4">{{ vuln.discoveryTime }}</td>
            </tr>
            <tr v-if="recentVulnerabilities.length === 0">
              <td colspan="4" class="px-6 py-8 text-center text-gray-400">
                {{ $t('common.noData') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import { getDashboardStatistics, getRecentOpenAlerts, getRecentOpenVulnerabilities } from '@/api/dashboard'

const { t } = useI18n()
const router = useRouter()

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
  mttdTrend: 'down',
  alertTypeStats: [
    { name: 'IAM', manual: 75, auto: 40 },
    { name: 'HSS', manual: 60, auto: 60 },
    { name: 'NDR', manual: 90, auto: 30 },
    { name: 'COP', manual: 50, auto: 55 },
    { name: 'SA', manual: 70, auto: 45 },
    { name: 'SIEM', manual: 85, auto: 80 }
  ],
  aiAccuracy: [
    { name: 'IAM', accuracy: 99.8 },
    { name: 'HSS', accuracy: 99.5 },
    { name: 'NDR', accuracy: 98.2 },
    { name: 'COP', accuracy: 99.1 },
    { name: 'SA', accuracy: 97.5 },
    { name: 'SIEM', accuracy: 99.9 }
  ]
})

/**
 * @brief 最近未关闭的告警
 */
const recentAlerts = ref([])

/**
 * @brief 最近未关闭的漏洞
 */
const recentVulnerabilities = ref([])

/**
 * @brief 选中的时间范围
 */
const selectedTimeRange = ref('last24Hours')

/**
 * @brief 自定义时间范围
 */
const customTimeRange = ref(null)

/**
 * @brief 加载统计数据
 */
const loadStatistics = async () => {
  try {
    const response = await getDashboardStatistics()
    if (response && response.data) {
      // 分别处理各个字段，避免覆盖默认值
      const data = response.data
      
      // 更新基本统计字段
      if (data.alertCount24h !== undefined) statistics.value.alertCount24h = data.alertCount24h
      if (data.alertCount24hChange !== undefined) statistics.value.alertCount24hChange = data.alertCount24hChange
      if (data.alertCount24hTrend !== undefined) statistics.value.alertCount24hTrend = data.alertCount24hTrend
      
      if (data.incidentCount24h !== undefined) statistics.value.incidentCount24h = data.incidentCount24h
      if (data.incidentCount24hChange !== undefined) statistics.value.incidentCount24hChange = data.incidentCount24hChange
      if (data.incidentCount24hTrend !== undefined) statistics.value.incidentCount24hTrend = data.incidentCount24hTrend
      
      if (data.vulnerabilityCount !== undefined) statistics.value.vulnerabilityCount = data.vulnerabilityCount
      if (data.vulnerabilityCountChange !== undefined) statistics.value.vulnerabilityCountChange = data.vulnerabilityCountChange
      if (data.vulnerabilityCountTrend !== undefined) statistics.value.vulnerabilityCountTrend = data.vulnerabilityCountTrend
      
      if (data.mttd !== undefined) statistics.value.mttd = data.mttd
      if (data.mttdChange !== undefined) statistics.value.mttdChange = data.mttdChange
      if (data.mttdTrend !== undefined) statistics.value.mttdTrend = data.mttdTrend
      
      // 更新图表数据（只有在有有效数据时才更新）
      if (data.alertTypeStats && Array.isArray(data.alertTypeStats) && data.alertTypeStats.length > 0) {
        statistics.value.alertTypeStats = data.alertTypeStats
      }
      
      if (data.aiAccuracy && Array.isArray(data.aiAccuracy) && data.aiAccuracy.length > 0) {
        statistics.value.aiAccuracy = data.aiAccuracy
      }
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
    // API 调用失败时使用默认 mock 数据，但保留已有的图表数据
    statistics.value.alertCount24h = 1258
    statistics.value.alertCount24hChange = 12.5
    statistics.value.alertCount24hTrend = 'up'
    statistics.value.incidentCount24h = 1283594
    statistics.value.incidentCount24hChange = -2.1
    statistics.value.incidentCount24hTrend = 'down'
    statistics.value.vulnerabilityCount = 87
    statistics.value.vulnerabilityCountChange = -5
    statistics.value.vulnerabilityCountTrend = 'down'
    statistics.value.mttd = '12m 34s'
    statistics.value.mttdChange = -1.2
    statistics.value.mttdTrend = 'down'
    // 图表数据保持默认值不变
  }
}

/**
 * @brief 加载最近告警
 */
const loadRecentAlerts = async () => {
  try {
    const response = await getRecentOpenAlerts({ limit: 3 })
    recentAlerts.value = response.data
  } catch (error) {
    console.error('Failed to load recent alerts:', error)
  }
}

/**
 * @brief 加载最近漏洞
 */
const loadRecentVulnerabilities = async () => {
  try {
    const response = await getRecentOpenVulnerabilities({ limit: 3 })
    recentVulnerabilities.value = response.data
  } catch (error) {
    console.error('Failed to load recent vulnerabilities:', error)
  }
}

/**
 * @brief 处理时间范围变化
 * @param {String} rangeKey 时间范围键
 */
const handleTimeRangeChange = (rangeKey) => {
  // 当时间范围变化时，重新加载数据
  loadData()
}

/**
 * @brief 处理自定义时间范围变化
 * @param {Array} range 自定义时间范围数组
 */
const handleCustomRangeChange = (range) => {
  // 当自定义时间范围变化时，重新加载数据
  if (range && range.length === 2) {
    loadData()
  }
}

/**
 * @brief 加载所有数据
 */
const loadData = async () => {
  await Promise.all([
    loadStatistics(),
    loadRecentAlerts(),
    loadRecentVulnerabilities()
  ])
}

/**
 * @brief 获取严重性样式类
 * @param {String} severity 严重性级别
 * @return {String} CSS类名
 */
const getSeverityClass = (severity) => {
  const classes = {
    critical: 'text-red-400',
    high: 'text-orange-400',
    medium: 'text-yellow-400',
    low: 'text-blue-400'
  }
  return classes[severity] || 'text-gray-400'
}

/**
 * @brief 获取严重性点样式类
 * @param {String} severity 严重性级别
 * @return {String} CSS类名
 */
const getSeverityDotClass = (severity) => {
  const classes = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-blue-500'
  }
  return classes[severity] || 'bg-gray-500'
}

/**
 * @brief 获取状态样式类
 * @param {String} status 状态
 * @return {String} CSS类名
 */
const getStatusClass = (status) => {
  const classes = {
    new: 'bg-red-500/20 text-red-300',
    inProgress: 'bg-yellow-500/20 text-yellow-300'
  }
  return classes[status] || 'bg-gray-500/20 text-gray-300'
}

/**
 * @brief 获取CVSS样式类
 * @param {String} level CVSS级别
 * @return {String} CSS类名
 */
const getCvssClass = (level) => {
  const classes = {
    critical: 'text-red-400',
    high: 'text-orange-400',
    medium: 'text-yellow-400',
    low: 'text-blue-400'
  }
  return classes[level] || 'text-gray-400'
}

/**
 * @brief 处理调查告警
 * @param {Object} alert 告警对象
 */
const handleInvestigateAlert = (alert) => {
  router.push(`/alerts/${alert.id}`)
}

/**
 * @brief 处理查看漏洞详情
 * @param {Object} vuln 漏洞对象
 */
const handleViewVulnerabilityDetail = (vuln) => {
  // TODO: 实现漏洞详情页面路由
  console.log('View vulnerability detail:', vuln)
}

/**
 * @brief 组件挂载时加载数据
 */
onMounted(() => {
  loadData()
})
</script>
