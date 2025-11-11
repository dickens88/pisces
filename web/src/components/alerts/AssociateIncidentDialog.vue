<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="handleClose"
  >
    <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-2xl max-h-[80vh] flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-white">
          {{ $t('alerts.list.associateIncidentDialog.title') }}
        </h2>
        <button
          @click="handleClose"
          class="text-gray-400 hover:text-white transition-colors"
        >
          <span class="material-symbols-outlined text-base">close</span>
        </button>
      </div>

      <!-- 提示信息 -->
      <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
        <p class="text-sm text-gray-400">
          {{ $t('alerts.list.associateIncidentDialog.confirmMessage', { count: alertIds.length }) }}
        </p>
      </div>

      <!-- 事件列表 -->
      <div class="flex-1 overflow-y-auto mb-4">
        <div class="bg-[#1e293b] rounded-md border border-[#324867]">
          <table class="w-full text-sm text-left text-[#92a9c9]">
            <thead class="text-xs text-white uppercase bg-[#111822] sticky top-0">
              <tr>
                <th class="px-4 py-3" scope="col" style="width: 50px;"></th>
                <th class="px-4 py-3" scope="col">{{ $t('alerts.list.associateIncidentDialog.incidentId') }}</th>
                <th class="px-4 py-3" scope="col">{{ $t('alerts.list.associateIncidentDialog.incidentTitle') }}</th>
                <th class="px-4 py-3" scope="col">{{ $t('alerts.list.associateIncidentDialog.createTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="incident in incidentsList"
                :key="incident.id"
                @click="selectIncident(incident.id)"
                :class="[
                  'border-b border-[#324867] hover:bg-primary/10 transition-colors cursor-pointer',
                  selectedIncidentId === incident.id ? 'bg-primary/20' : ''
                ]"
              >
                <td class="px-4 py-3">
                  <input
                    type="radio"
                    :checked="selectedIncidentId === incident.id"
                    @click.stop="selectIncident(incident.id)"
                    class="bg-transparent border-[#324867] text-primary focus:ring-primary"
                  />
                </td>
                <td class="px-4 py-3">{{ incident.id }}</td>
                <td class="px-4 py-3">
                  <div class="max-w-xs overflow-hidden text-ellipsis whitespace-nowrap" :title="incident.name">
                    {{ incident.name }}
                  </div>
                </td>
                <td class="px-4 py-3">{{ incident.occurrenceTime }}</td>
              </tr>
              <tr v-if="incidentsList.length === 0">
                <td colspan="4" class="px-4 py-8 text-center text-gray-400">
                  {{ $t('alerts.list.associateIncidentDialog.noIncidents') }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 分页 -->
      <nav v-if="incidentsTotal > 0" aria-label="Incidents table navigation" class="flex items-center justify-between mb-6">
        <span class="text-sm font-normal text-gray-400">
          {{ $t('common.pagination.showing', { 
            start: pageSize * (page - 1) + 1, 
            end: Math.min(pageSize * page, incidentsTotal),
            total: incidentsTotal 
          }) }}
        </span>
        <ul class="inline-flex -space-x-px text-sm h-8">
          <li>
            <button
              @click="handlePreviousPage"
              :disabled="page === 1"
              class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-400 bg-[#233348] border border-gray-700 rounded-s-lg hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ $t('common.pagination.previous') }}
            </button>
          </li>
          <template v-for="(item, index) in displayPages" :key="index">
            <li v-if="item.type === 'page'">
              <button
                @click="page = item.value; loadIncidents()"
                :class="[
                  'flex items-center justify-center px-3 h-8 leading-tight border border-gray-700',
                  page === item.value
                    ? 'text-white bg-primary hover:bg-primary/90'
                    : 'text-gray-400 bg-[#233348] hover:bg-gray-700 hover:text-white'
                ]"
              >
                {{ item.value }}
              </button>
            </li>
            <li v-else-if="item.type === 'ellipsis'" class="flex items-center justify-center px-2 h-8 text-gray-400 bg-[#233348] border border-gray-700">
              <span class="material-symbols-outlined" style="font-size: 18px;">more_horiz</span>
            </li>
          </template>
          <li>
            <button
              @click="handleNextPage"
              :disabled="page === totalPages"
              class="flex items-center justify-center px-3 h-8 leading-tight text-gray-400 bg-[#233348] border border-gray-700 rounded-e-lg hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ $t('common.pagination.next') }}
            </button>
          </li>
        </ul>
      </nav>

      <!-- 操作按钮 -->
      <div class="flex items-center justify-end gap-3">
        <button
          @click="handleClose"
          class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="handleAssociate"
          :disabled="!selectedIncidentId"
          class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ $t('common.submit') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getIncidents } from '@/api/incidents'
import { associateAlertsToIncident } from '@/api/alerts'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  alertIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'associated'])

const { t } = useI18n()

const incidentsList = ref([])
const selectedIncidentId = ref(null)
const page = ref(1)
const pageSize = ref(10)
const incidentsTotal = ref(0)
const totalPages = computed(() => Math.ceil(incidentsTotal.value / pageSize.value))

// 计算要显示的页码数组
const displayPages = computed(() => {
  const total = totalPages.value
  const current = page.value
  const pages = []
  
  // 如果总页数少于等于 5，显示所有页码
  if (total <= 5) {
    for (let i = 1; i <= total; i++) {
      pages.push({ type: 'page', value: i })
    }
    return pages
  }
  
  // 总是显示第一页
  pages.push({ type: 'page', value: 1 })
  
  // 计算当前页附近的页码
  let start = Math.max(2, current - 1)
  let end = Math.min(total - 1, current + 1)
  
  // 如果当前页在开头附近，显示前几页
  if (current <= 3) {
    start = 2
    end = Math.min(4, total - 1)
  }
  // 如果当前页在结尾附近，显示后几页
  else if (current >= total - 2) {
    start = Math.max(2, total - 3)
    end = total - 1
  }
  
  // 如果 start > 2，添加省略号
  if (start > 2) {
    pages.push({ type: 'ellipsis' })
  }
  
  // 添加当前页附近的页码
  for (let i = start; i <= end; i++) {
    pages.push({ type: 'page', value: i })
  }
  
  // 如果 end < total - 1，添加省略号
  if (end < total - 1) {
    pages.push({ type: 'ellipsis' })
  }
  
  // 总是显示最后一页（如果不是第一页）
  if (total > 1) {
    pages.push({ type: 'page', value: total })
  }
  
  return pages
})

// 监听 visible 变化，打开时加载事件列表
watch(() => props.visible, (newVal) => {
  if (newVal) {
    selectedIncidentId.value = null
    page.value = 1
    loadIncidents()
  }
})

const loadIncidents = async () => {
  try {
    const response = await getIncidents({
      page: page.value,
      pageSize: pageSize.value
    })
    incidentsList.value = response.data
    incidentsTotal.value = response.total
  } catch (error) {
    console.error('Failed to load incidents:', error)
    incidentsList.value = []
    incidentsTotal.value = 0
  }
}

const handlePreviousPage = () => {
  if (page.value > 1) {
    page.value--
    loadIncidents()
  }
}

const handleNextPage = () => {
  if (page.value < totalPages.value) {
    page.value++
    loadIncidents()
  }
}

const selectIncident = (incidentId) => {
  selectedIncidentId.value = incidentId
}

const handleClose = () => {
  selectedIncidentId.value = null
  page.value = 1
  incidentsList.value = []
  incidentsTotal.value = 0
  emit('close')
}

const handleAssociate = async () => {
  if (!selectedIncidentId.value || props.alertIds.length === 0) {
    return
  }

  try {
    await associateAlertsToIncident({
      alertIds: props.alertIds,
      incidentId: selectedIncidentId.value
    })
    
    handleClose()
    emit('associated')
  } catch (error) {
    console.error('Failed to associate alerts to incident:', error)
  }
}
</script>

