<template>
  <Teleport to="body">
    <Transition name="slide">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-end"
        @click.self="handleClose"
      >
        <!-- 遮罩层 - 直接显示，无动画 -->
        <div 
          v-if="incident"
          class="fixed inset-0 bg-black/50"
          @click="handleClose"
        ></div>
        
        <!-- 详情面板 - 有滑入动画 -->
        <Transition name="slide">
          <div
            v-if="visible"
            class="relative w-screen max-w-6xl h-full bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
            @click.stop
          >
            <!-- 头部 -->
            <div class="sticky top-0 z-20 bg-panel-dark/80 backdrop-blur-sm border-b border-border-dark">
              <div class="flex items-center justify-between px-6 py-4">
                <div class="flex flex-col gap-1">
                  <h2 class="text-xl font-bold text-white">{{ $t('incidents.detail.title') }}</h2>
                  <p class="text-sm text-slate-400">
                    {{ $t('incidents.detail.eventId') }}: {{ incident?.eventId }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
                  >
                    <span class="material-symbols-outlined text-base">person_add</span>
                    <span class="truncate">{{ $t('incidents.detail.assign') }}</span>
                  </button>
                  <button
                    class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
                  >
                    <span class="material-symbols-outlined text-base">task_alt</span>
                    <span class="truncate">{{ $t('incidents.detail.changeStatus') }}</span>
                  </button>
                  <button
                    @click="handleClose"
                    class="p-2 text-text-light hover:text-white transition-colors"
                  >
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 主内容区 -->
            <main class="flex-1 p-6 overflow-y-auto">
              <!-- 页面标题 -->
              <div class="mb-6">
                <h1 class="text-white text-3xl font-black leading-tight tracking-tight mb-2">
                  {{ incident?.name }}
                </h1>
              </div>

            <!-- 统计卡片 -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
                <p class="text-slate-300 text-sm font-medium leading-normal">
                  {{ $t('incidents.detail.status') }}
                </p>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'w-2 h-2 rounded-full',
                      getStatusDotClass(incident.status)
                    ]"
                  ></span>
                  <p class="text-white text-xl font-bold leading-tight">
                    {{ $t(`incidents.list.${incident.status}`) }}
                  </p>
                </div>
              </div>
              <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
                <p class="text-slate-300 text-sm font-medium leading-normal">
                  {{ $t('incidents.detail.severity') }}
                </p>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'w-2 h-2 rounded-full',
                      getSeverityDotClass(incident.severity)
                    ]"
                  ></span>
                  <p
                    :class="[
                      'text-xl font-bold leading-tight',
                      getSeverityTextClass(incident.severity)
                    ]"
                  >
                    {{ $t(`incidents.list.${incident.severity}`) }}
                  </p>
                </div>
              </div>
              <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
                <p class="text-slate-300 text-sm font-medium leading-normal">
                  {{ $t('incidents.detail.affectedAssets') }}
                </p>
                <p class="text-white text-xl font-bold leading-tight">
                  {{ incident.affectedAssets || 0 }}
                </p>
              </div>
              <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
                <p class="text-slate-300 text-sm font-medium leading-normal">
                  {{ $t('incidents.detail.mitreTactic') }}
                </p>
                <p class="text-white text-xl font-bold leading-tight">
                  {{ incident.mitreTactic || '-' }}
                </p>
              </div>
            </div>

            <!-- 标签页导航 -->
            <div class="mt-8 border-b border-slate-700">
              <nav aria-label="Tabs" class="flex -mb-px space-x-6">
                <button
                  v-for="tab in tabs"
                  :key="tab.key"
                  @click="activeTab = tab.key"
                  :class="[
                    'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors',
                    activeTab === tab.key
                      ? 'text-primary border-primary'
                      : 'text-slate-400 hover:text-white border-transparent'
                  ]"
                >
                  {{ $t(tab.label) }}
                </button>
              </nav>
            </div>

            <!-- 标签页内容 -->
            <div class="mt-6 flex-grow">
              <!-- 时间线与告警 -->
              <div v-if="activeTab === 'timeline'" class="grid grid-cols-1 lg:grid-cols-5 gap-6">
                <!-- 左侧时间线 -->
                <div class="lg:col-span-2 bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex flex-col h-[600px] lg:h-auto">
                  <h3 class="text-white font-bold text-lg mb-4">
                    {{ $t('incidents.detail.timeline.title') }}
                  </h3>
                  <div class="flex-grow relative overflow-y-auto pr-2">
                    <div
                      v-for="(event, index) in incident.timeline || []"
                      :key="index"
                      class="flex gap-4"
                    >
                      <div class="flex flex-col items-center">
                        <div
                          :class="[
                            'flex items-center justify-center size-8 rounded-full',
                            getTimelineIconBgClass(event.severity)
                          ]"
                        >
                          <span
                            :class="[
                              'material-symbols-outlined text-base',
                              getTimelineIconColorClass(event.severity)
                            ]"
                          >
                            {{ event.icon }}
                          </span>
                        </div>
                        <div
                          v-if="index < (incident.timeline?.length || 0) - 1"
                          class="w-px h-full bg-slate-700 my-2"
                        ></div>
                      </div>
                      <div class="pb-8 flex-1">
                        <p class="text-sm text-slate-400">{{ event.time }}</p>
                        <p class="font-medium text-white">{{ event.title }}</p>
                        <p class="text-sm text-slate-300 mt-1">{{ event.description }}</p>
                        <a
                          v-if="event.alertId"
                          @click="viewAlert(event.alertId)"
                          class="text-primary text-sm font-semibold mt-2 inline-block cursor-pointer hover:underline"
                        >
                          View Alert #{{ event.alertId }}
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 右侧攻击链 -->
                <div class="lg:col-span-3 bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex flex-col h-[600px] lg:h-auto">
                  <div class="flex justify-between items-center mb-4">
                    <h3 class="text-white font-bold text-lg">
                      {{ $t('incidents.detail.attackChain.title') }}
                    </h3>
                    <div class="flex items-center gap-2">
                      <button
                        class="flex items-center justify-center size-8 rounded-md bg-slate-700 hover:bg-slate-600 transition-colors"
                        :title="$t('incidents.detail.attackChain.zoomIn')"
                      >
                        <span class="material-symbols-outlined text-base">zoom_in</span>
                      </button>
                      <button
                        class="flex items-center justify-center size-8 rounded-md bg-slate-700 hover:bg-slate-600 transition-colors"
                        :title="$t('incidents.detail.attackChain.zoomOut')"
                      >
                        <span class="material-symbols-outlined text-base">zoom_out</span>
                      </button>
                      <button
                        class="flex items-center justify-center size-8 rounded-md bg-slate-700 hover:bg-slate-600 transition-colors"
                        :title="$t('incidents.detail.attackChain.fullscreen')"
                      >
                        <span class="material-symbols-outlined text-base">fullscreen</span>
                      </button>
                    </div>
                  </div>
                  <div
                    class="mt-4 flex-grow rounded-md flex items-center justify-center"
                    style="--dot-bg: #101822; --dot-color: #2E4057; background-image: radial-gradient(var(--dot-color) 1px, var(--dot-bg) 1px); background-size: 20px 20px;"
                  >
                    <div
                      v-if="incident.attackChainImage"
                      class="w-full h-full bg-contain bg-no-repeat bg-center"
                      :style="{ backgroundImage: `url('${incident.attackChainImage}')` }"
                    ></div>
                    <div v-else class="text-slate-400 text-sm">
                      {{ $t('incidents.detail.attackChain.title') }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- 其他标签页内容 -->
              <div v-if="activeTab === 'overview'" class="text-slate-400">
                Overview content coming soon...
              </div>
              <div v-if="activeTab === 'attackChain'" class="text-slate-400">
                Attack Chain content coming soon...
              </div>
              <div v-if="activeTab === 'comments'" class="text-slate-400">
                Comments content coming soon...
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getIncidentDetail } from '@/api/incidents'

const props = defineProps({
  incidentId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['close'])

const { t } = useI18n()

const incident = ref(null)
const activeTab = ref('timeline')

const tabs = [
  { key: 'overview', label: 'incidents.detail.tabs.overview' },
  { key: 'timeline', label: 'incidents.detail.tabs.timeline' },
  { key: 'attackChain', label: 'incidents.detail.tabs.attackChain' },
  { key: 'comments', label: 'incidents.detail.tabs.comments' }
]

const loadIncidentDetail = async () => {
  try {
    const response = await getIncidentDetail(props.incidentId)
    incident.value = response.data
  } catch (error) {
    console.error('Failed to load incident detail:', error)
    emit('close')
  }
}

const handleClose = () => {
  emit('close')
}

const viewAlert = (alertId) => {
  // TODO: 实现查看告警的逻辑
  console.log('View alert:', alertId)
}

const getStatusDotClass = (status) => {
  const classes = {
    pending: 'bg-amber-400',
    inProgress: 'bg-blue-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.pending
}

const getSeverityDotClass = (severity) => {
  const classes = {
    high: 'bg-red-500',
    medium: 'bg-orange-500',
    low: 'bg-blue-500'
  }
  return classes[severity] || classes.low
}

const getSeverityTextClass = (severity) => {
  const classes = {
    high: 'text-red-400',
    medium: 'text-orange-400',
    low: 'text-blue-400'
  }
  return classes[severity] || classes.low
}

const getTimelineIconBgClass = (severity) => {
  const classes = {
    high: 'bg-red-500/20 ring-1 ring-inset ring-red-500/30',
    medium: 'bg-amber-500/20 ring-1 ring-inset ring-amber-500/30',
    low: 'bg-slate-700'
  }
  return classes[severity] || classes.low
}

const getTimelineIconColorClass = (severity) => {
  const classes = {
    high: 'text-red-400',
    medium: 'text-amber-400',
    low: 'text-slate-300'
  }
  return classes[severity] || classes.low
}

watch(() => props.incidentId, () => {
  if (props.incidentId) {
    loadIncidentDetail()
  }
}, { immediate: true })

onMounted(() => {
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

