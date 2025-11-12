<template>
  <div class="w-full">
    <!-- 页面头部 -->
    <header class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em]">
        {{ $t('alerts.title') }}
      </h1>
      <div class="flex gap-2 items-center">
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
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
          <div class="flex flex-wrap items-center gap-2 min-h-[42px] rounded-lg border-0 bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary">
            <div class="pointer-events-none flex items-center shrink-0">
              <span class="material-symbols-outlined text-gray-400" style="font-size: 20px;">search</span>
            </div>
            <!-- 搜索关键字标签 -->
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
            <!-- 输入框 -->
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
            :disabled="selectedAlerts.length !== 1"
            @click="openCreateIncidentDialog"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">transform</span>
            <span>{{ $t('alerts.list.batchConvert') }}</span>
          </button>
          <!-- 更多操作按钮 -->
          <div class="relative">
            <button
              @click="showMoreMenu = !showMoreMenu"
              class="more-menu-button flex items-center justify-center rounded-lg h-10 w-10 bg-[#233348] text-white hover:bg-[#324867] transition-colors"
              :title="$t('common.more') || '更多'"
            >
              <span class="material-symbols-outlined text-base">more_vert</span>
            </button>
            <!-- 下拉菜单 -->
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
          <UserAvatar :name="value" />
        </template>
      </DataTable>
    </section>

    <!-- 告警详情抽屉 -->
    <AlertDetail
      v-if="currentAlertId"
      :alert-id="currentAlertId"
      @close="closeAlertDetail"
      @closed="handleAlertClosed"
      @created="handleAlertConvertedToIncident"
    />

    <!-- 创建事件对话框 -->
    <CreateIncidentDialog
      :visible="showCreateIncidentDialog"
      :initial-data="createIncidentInitialData"
      @close="closeCreateIncidentDialog"
      @created="handleIncidentCreated"
    />

    <!-- 创建告警对话框 -->
    <CreateAlertDialog
      :visible="showCreateAlertDialog"
      @close="closeCreateAlertDialog"
      @created="handleAlertCreated"
    />

    <!-- 关联事件对话框 -->
    <AssociateIncidentDialog
      :visible="showAssociateIncidentDialog"
      :alert-ids="selectedAlerts"
      @close="closeAssociateIncidentDialog"
      @associated="handleAssociateIncidentSuccess"
    />

    <!-- 批量关闭对话框 -->
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

        <!-- 提示信息 -->
        <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('alerts.list.batchCloseDialog.confirmMessage', { count: selectedAlerts.length }) }}
          </p>
        </div>

        <!-- 结论分类下拉框 -->
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
            <option value="convertedToIncident">{{ $t('alerts.list.batchCloseDialog.categories.convertedToIncident') }}</option>
            <option value="other">{{ $t('alerts.list.batchCloseDialog.categories.other') }}</option>
          </select>
        </div>

        <!-- 调查结论输入框 -->
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

        <!-- 操作按钮 -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchCloseDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchClose"
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim()"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { getAlerts, getAlertStatistics, batchCloseAlerts } from '@/api/alerts'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import CreateAlertDialog from '@/components/alerts/CreateAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatDateTime } from '@/utils/dateTime'

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
  createTime: 200, // 调整为200以适应 yyyy-MM-dd HH:mm:ss 格式
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  owner: 100
}

const alerts = ref([])
const dataTableRef = ref(null)
const statistics = ref({
  totalAlerts: 0,
  trend: 0,
  alertCount: 0,
  alertTrend: 0,
  mttd: '0 hours',
  mttdChange: 0,
  typeStats: []
})
const searchKeywords = ref([])
const currentSearchInput = ref('')
const statusFilter = ref('all')
const selectedAlerts = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTimeRange = ref('last24Hours')
const customTimeRange = ref(null)
const showBatchCloseDialog = ref(false)
const closeConclusion = ref({
  category: '',
  notes: ''
})
const showAssociateIncidentDialog = ref(false)
const showCreateIncidentDialog = ref(false)
const createIncidentInitialData = ref(null)
const showCreateAlertDialog = ref(false)
const showMoreMenu = ref(false)


const mttdStages = [
  { name: 'Detection', percentage: 20 },
  { name: 'Triage', percentage: 35 },
  { name: 'Investigation', percentage: 80 },
  { name: 'Containment', percentage: 50 }
]

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadAlerts = async () => {
  try {
    const params = {
      searchKeywords: searchKeywords.value,
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
    
    const response = await getAlerts(params)
    alerts.value = response.data
    total.value = response.total
    
    // 调试：检查第一条数据的时间字段
    if (response.data && response.data.length > 0) {
      console.log('First alert data:', response.data[0])
      console.log('createTime field:', response.data[0].createTime)
      console.log('create_time field:', response.data[0].create_time)
    }
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

/**
 * @brief 添加搜索关键字
 * @details 当用户按回车时，将当前输入添加到关键字列表
 */
const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && !searchKeywords.value.includes(keyword)) {
    searchKeywords.value.push(keyword)
    currentSearchInput.value = ''
    loadAlerts()
  }
}

/**
 * @brief 删除搜索关键字
 * @param {number} index - 要删除的关键字索引
 */
const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  loadAlerts()
}

/**
 * @brief 处理搜索输入
 * @details 实时搜索功能（可选，如果需要实时搜索可以启用）
 */
const handleSearchInput = () => {
  // 如果需要实时搜索，可以在这里调用 loadAlerts()
  // 目前只在添加/删除关键字时搜索
}

const handleFilter = () => {
  loadAlerts()
}

const handlePageSizeChange = () => {
  pageSize.value = Number(pageSize.value) // 确保是数字类型
  currentPage.value = 1 // 重置到第一页
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
  // 更新URL，但不触发页面跳转
  router.push({ path: `/alerts/${alertId}`, replace: true })
}

const openAlertDetailInNewWindow = (alertId) => {
  // 在新窗口打开告警详情
  const route = router.resolve({ path: `/alerts/${alertId}` })
  // 构建完整的 URL
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const closeAlertDetail = () => {
  // 清除URL中的告警ID
  router.push({ path: '/alerts', replace: true })
}

const handleAlertClosed = () => {
  // 告警关闭后，重新加载告警列表
  loadAlerts()
  // 清空选中状态
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const handleAlertConvertedToIncident = () => {
  // 告警转事件后，重新加载告警列表
  loadAlerts()
  // 清空选中状态
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

// 自动换行状态
const isWordWrap = computed(() => {
  return dataTableRef.value?.wordWrap?.value ?? true
})

// 切换自动换行
const handleToggleWordWrap = () => {
  if (dataTableRef.value) {
    dataTableRef.value.toggleWordWrap()
    showMoreMenu.value = false
  }
}

// 点击外部关闭下拉菜单
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
  // 重置表单
  closeConclusion.value = {
    category: '',
    notes: ''
  }
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim()) {
    return
  }

  try {
    await batchCloseAlerts({
      alertIds: selectedAlerts.value,
      category: closeConclusion.value.category,
      notes: closeConclusion.value.notes.trim()
    })
    
    // 关闭对话框并重置表单
    closeBatchCloseDialog()
    selectedAlerts.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    // 重新加载告警列表
    loadAlerts()
  } catch (error) {
    console.error('Failed to batch close alerts:', error)
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
  // 关联成功后，关闭对话框并重置
  closeAssociateIncidentDialog()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
  
  // 重新加载告警列表
  loadAlerts()
}

const openCreateIncidentDialog = () => {
  if (selectedAlerts.value.length !== 1) {
    console.warn('Please select exactly one alert')
    return
  }
  
  // 找到选中的告警
  const selectedAlert = alerts.value.find(alert => alert.id === selectedAlerts.value[0])
  if (!selectedAlert) {
    console.warn('Selected alert not found')
    return
  }
  
  // 解析告警的创建时间
  let occurrenceTime = new Date()
  try {
    // 尝试解析告警的创建时间
    if (selectedAlert.createTime) {
      occurrenceTime = new Date(selectedAlert.createTime)
      // 如果解析失败，使用当前时间
      if (isNaN(occurrenceTime.getTime())) {
        occurrenceTime = new Date()
      }
    }
  } catch (error) {
    console.warn('Failed to parse alert create time:', error)
    occurrenceTime = new Date()
  }
  
  // 获取告警描述（优先使用 aiAnalysis.description，否则使用 description）
  const alertDescription = selectedAlert.aiAnalysis?.description || selectedAlert.description || ''
  
  // 设置初始数据
  createIncidentInitialData.value = {
    title: selectedAlert.title || '',
    occurrenceTime: occurrenceTime,
    description: alertDescription
  }
  
  // 打开对话框
  showCreateIncidentDialog.value = true
}

const closeCreateIncidentDialog = () => {
  showCreateIncidentDialog.value = false
  createIncidentInitialData.value = null
}

const handleIncidentCreated = () => {
  // 事件创建成功后，重新加载告警列表
  loadAlerts()
  // 清空选中状态
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

const handleAlertCreated = () => {
  // 告警创建成功后，重新加载告警列表
  loadAlerts()
  loadStatistics()
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    // 根据选择的时间范围加载数据
    loadAlerts()
  }
}

const handleCustomRangeChange = (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    loadAlerts()
  }
}

watch([currentPage], () => {
  loadAlerts()
})

onMounted(() => {
  loadAlerts()
  loadStatistics()
  // 添加点击外部关闭下拉菜单的监听器
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // 移除点击外部关闭下拉菜单的监听器
  document.removeEventListener('click', handleClickOutside)
})
</script>


