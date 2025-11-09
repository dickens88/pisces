<template>
  <div class="w-full">
    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-white text-3xl font-bold leading-tight tracking-tight">
          {{ $t('incidents.title') }}
        </h1>
      </div>
      <div class="flex items-center gap-4">
        <button
          class="flex items-center gap-2 px-4 py-2 text-sm text-white bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
        >
          <span class="material-symbols-outlined text-base">calendar_today</span>
          <span>{{ $t('incidents.list.timeRange.last24Hours') }}</span>
          <span class="material-symbols-outlined text-base">expand_more</span>
        </button>
        <button
          class="flex items-center gap-2 px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 transition-colors"
        >
          <span class="material-symbols-outlined text-base">add</span>
          <span>{{ $t('incidents.list.createManually') }}</span>
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
            <span class="material-symbols-outlined text-base">assignment_turned_in</span>
            {{ $t('incidents.list.batchClose') }}
          </button>
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
    <div class="bg-[#111822] border border-[#324867] rounded-lg overflow-x-auto">
      <table class="w-full text-sm text-left text-[#92a9c9]" style="table-layout: fixed;">
        <thead class="text-xs text-white uppercase bg-[#1e293b]">
          <tr>
            <th class="p-4" scope="col" style="width: 50px;">
              <input
                v-model="selectAll"
                @change="handleSelectAll"
                class="bg-transparent border-[#324867] rounded text-primary focus:ring-primary"
                type="checkbox"
              />
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
            v-for="incident in incidents"
            :key="incident.id"
            class="border-b border-[#324867] hover:bg-primary/10 transition-colors"
          >
            <td class="w-4 p-4">
              <input
                v-model="selectedIncidents"
                :value="incident.id"
                class="bg-transparent border-[#324867] rounded text-primary focus:ring-primary"
                type="checkbox"
              />
            </td>
            <td class="px-6 py-4 border-r border-[#324867]/30">
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getSeverityClass(incident.severity)
                ]"
              >
                {{ $t(`incidents.list.${incident.severity}`) }}
              </span>
            </td>
            <td class="px-6 py-4 border-r border-[#324867]/30">
              <router-link
                :to="`/incidents/${incident.id}`"
                class="text-primary hover:underline font-medium overflow-hidden text-ellipsis whitespace-nowrap block"
                :title="incident.name"
              >
                {{ incident.name }}
              </router-link>
            </td>
            <td class="px-6 py-4 overflow-hidden text-ellipsis whitespace-nowrap border-r border-[#324867]/30" :title="incident.sourceIp">
              {{ incident.sourceIp }}
            </td>
            <td class="px-6 py-4 overflow-hidden text-ellipsis whitespace-nowrap border-r border-[#324867]/30" :title="incident.targetIp">
              {{ incident.targetIp }}
            </td>
            <td class="px-6 py-4 border-r border-[#324867]/30">{{ incident.occurrenceTime }}</td>
            <td class="px-6 py-4">
              <span :class="getStatusClass(incident.status)">
                {{ $t(`incidents.list.${incident.status}`) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <nav aria-label="Table navigation" class="flex items-center justify-between p-4">
        <span class="text-sm font-normal text-[#92a9c9]">
          显示 <span class="font-semibold text-white">1-{{ incidents.length }}</span> of
          <span class="font-semibold text-white">{{ total }}</span>
        </span>
        <ul class="inline-flex -space-x-px text-sm h-8">
          <li>
            <button
              @click="currentPage > 1 && currentPage--"
              :disabled="currentPage === 1"
              class="flex items-center justify-center px-3 h-8 ml-0 leading-tight text-[#92a9c9] bg-[#1e293b] border border-[#324867] rounded-l-lg hover:bg-primary/30 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              上一页
            </button>
          </li>
          <li v-for="page in totalPages" :key="page">
            <button
              @click="currentPage = page"
              :class="[
                'flex items-center justify-center px-3 h-8 leading-tight border border-[#324867] transition-colors',
                currentPage === page
                  ? 'text-white bg-primary/40'
                  : 'text-[#92a9c9] bg-[#1e293b] hover:bg-primary/30 hover:text-white'
              ]"
            >
              {{ page }}
            </button>
          </li>
          <li>
            <button
              @click="currentPage < totalPages && currentPage++"
              :disabled="currentPage === totalPages"
              class="flex items-center justify-center px-3 h-8 leading-tight text-[#92a9c9] bg-[#1e293b] border border-[#324867] rounded-r-lg hover:bg-primary/30 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              下一页
            </button>
          </li>
        </ul>
      </nav>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getIncidents } from '@/api/incidents'
import { useResizableColumns } from '@/composables/useResizableColumns'

const { t } = useI18n()

// 定义列配置（使用computed确保响应式）
const columns = computed(() => [
  { key: 'severity', label: t('incidents.list.severity') },
  { key: 'incidentName', label: t('incidents.list.incidentName') },
  { key: 'sourceIp', label: t('incidents.list.sourceIp') },
  { key: 'targetIp', label: t('incidents.list.targetIp') },
  { key: 'occurrenceTime', label: t('incidents.list.occurrenceTime') },
  { key: 'status', label: t('incidents.list.status') }
])

// 默认列宽
const defaultWidths = {
  severity: 100,
  incidentName: 300,
  sourceIp: 150,
  targetIp: 150,
  occurrenceTime: 180,
  status: 100
}

// 使用可调整列宽的composable
const { getColumnWidth, startResize } = useResizableColumns(
  'incidents-table-columns',
  defaultWidths
)

const incidents = ref([])
const searchQuery = ref('')
const severityFilter = ref('all')
const statusFilter = ref('all')
const selectedIncidents = ref([])
const selectAll = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showSeverityFilter = ref(false)
const showStatusFilter = ref(false)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadIncidents = async () => {
  try {
    const response = await getIncidents({
      search: searchQuery.value,
      severity: severityFilter.value,
      status: statusFilter.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    incidents.value = response.data
    total.value = response.total
  } catch (error) {
    console.error('Failed to load incidents:', error)
  }
}

const handleSearch = () => {
  loadIncidents()
}

const handleSelectAll = () => {
  if (selectAll.value) {
    selectedIncidents.value = incidents.value.map(incident => incident.id)
  } else {
    selectedIncidents.value = []
  }
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


watch([currentPage, severityFilter, statusFilter], () => {
  loadIncidents()
})

watch(selectedIncidents, (newVal) => {
  selectAll.value = newVal.length === incidents.value.length && incidents.value.length > 0
})

onMounted(() => {
  loadIncidents()
})
</script>

