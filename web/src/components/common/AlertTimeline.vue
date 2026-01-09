<template>
  <div class="space-y-4" v-if="timeline && timeline.length">
    <h3 class="text-base font-semibold text-gray-900 dark:text-white">
      {{ $t('alerts.detail.eventTimeline') }}
      <span class="ml-2 inline-flex items-center justify-center rounded-full bg-gray-100 dark:bg-border-dark px-2 py-0.5 text-[11px] font-medium text-gray-600 dark:text-text-light">
        {{ timeline.length }}
      </span>
    </h3>
    <div class="relative pl-6">
      <div class="absolute left-0 top-0 h-full w-0.5 bg-gray-200 dark:bg-border-dark timeline-line"></div>
      <div class="relative space-y-4">
        <div
          v-for="(event, index) in timeline"
          :key="index"
          class="relative group"
        >
          <div
            :class="[
              'absolute left-0 top-1.5 h-5 w-5 rounded-full flex items-center justify-center z-10 shadow-sm timeline-circle',
              openedIndex === index 
                ? 'bg-primary ring-2 ring-primary/20' 
                : 'bg-white dark:bg-panel-dark border-2 border-gray-300 dark:border-border-dark'
            ]"
          >
            <svg
              width="8"
              height="8"
              viewBox="0 0 8 8"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              class="timeline-arrow"
              :class="openedIndex === index ? 'timeline-arrow-active' : 'timeline-arrow-inactive'"
            >
              <path
                d="M4 1L4 7M4 7L2 5M4 7L6 5"
                stroke="currentColor"
                stroke-width="1.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>

          <details
            class="bg-gray-100/70 dark:bg-[#2a3546]/30 border border-gray-200/60 dark:border-border-dark rounded-md overflow-hidden hover:bg-gray-100 dark:hover:bg-[#2a3546]/50 transition-colors group/details"
            @toggle="handleToggle(index, $event.target.open)"
          >
            <summary class="flex items-start gap-2 p-2.5 cursor-pointer select-none outline-none">
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-0.5">
                  <span class="text-[11px] font-mono text-gray-500 dark:text-text-light font-medium">
                    {{ event.time }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {{ getEventLabel(event.event) }}
                  </h4>
                  <div
                    v-if="event.author"
                    class="shrink-0"
                    :title="event.author"
                  >
                    <div class="scale-75 origin-left">
                      <UserAvatar :name="event.author" />
                    </div>
                  </div>
                </div>
              </div>
              <span class="material-symbols-outlined text-gray-500 dark:text-text-light text-base mt-0.5 marker shrink-0">
                expand_more
              </span>
            </summary>

            <div
              v-if="event.content"
              class="px-3 pb-3 pt-0 border-t border-dashed border-gray-200/70 dark:border-border-dark/50 mt-1"
            >
              <div class="pt-3 space-y-3">
                <div class="space-y-1">
                  <span class="text-[11px] text-gray-500 dark:text-text-light uppercase tracking-wider font-semibold block">
                    {{ $t('alerts.detail.description') || 'Description' }}
                  </span>
                  <div
                    class="text-[11px] leading-snug text-gray-700 dark:text-gray-300 bg-white/60 dark:bg-background-dark/30 p-2 rounded border border-gray-200/70 dark:border-border-dark/40 whitespace-pre-wrap break-words"
                  >
                    <template v-if="isExpanded(index)">
                      {{ stripHtmlAndEntities(event.content) }}
                    </template>
                    <template v-else>
                      {{ getTruncatedContent(event.content) }}
                    </template>
                    <button
                      v-if="shouldShowExpand(event.content)"
                      @click.stop="toggleExpanded(index)"
                      class="mt-2 text-primary hover:text-primary/80 text-[11px] font-medium underline cursor-pointer transition-colors"
                    >
                      {{ isExpanded(index) ? ($t('alerts.detail.collapseContent') || '收起') : ($t('alerts.detail.expandContent') || '阅读全部') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import UserAvatar from './UserAvatar.vue'

const props = defineProps({
  timeline: {
    type: Array,
    default: () => []
  }
})

const { t } = useI18n()
const openedIndex = ref(-1)
const expandedIndices = ref(new Set())

const CONTENT_TRUNCATE_LENGTH = parseInt(import.meta.env.VITE_ALERT_TIMELINE_CONTENT_TRUNCATE_LENGTH || '500', 10)

const stripHtmlAndEntities = (html) => {
  if (typeof html !== 'string') return String(html || '')
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .trim()
}

const shouldShowExpand = (content) => {
  if (!content) return false
  return stripHtmlAndEntities(content).length > CONTENT_TRUNCATE_LENGTH
}

const getTruncatedContent = (content) => {
  if (!content) return ''
  const plain = stripHtmlAndEntities(content)
  return plain.length <= CONTENT_TRUNCATE_LENGTH 
    ? plain 
    : plain.substring(0, CONTENT_TRUNCATE_LENGTH) + '...'
}

const isExpanded = (index) => expandedIndices.value.has(index)

const toggleExpanded = (index) => {
  if (expandedIndices.value.has(index)) {
    expandedIndices.value.delete(index)
  } else {
    expandedIndices.value.add(index)
  }
}

const getEventLabel = (eventName) => {
  if (!eventName) return t('alerts.detail.unknownEvent') || 'Event'
  
  const mapping = {
    'Alert Triggered': 'alerts.detail.timelineEvents.alertTriggered',
    'Close Alert': 'alerts.detail.timelineEvents.closeAlert',
    'Add Intelligence': 'alerts.detail.timelineEvents.addIntelligence',
    'AI Analysis': 'alerts.detail.timelineEvents.aiAnalysis',
    'Find Similar Alerts': 'alerts.detail.timelineEvents.findSimilarAlerts',
    'Add Comment': 'alerts.detail.timelineEvents.addComment',
    'To Incident': 'alerts.detail.timelineEvents.toIncident'
  }
  
  const key = mapping[eventName]
  return key ? (t(key) || eventName) : eventName
}

const handleToggle = (index, isOpen) => {
  openedIndex.value = isOpen ? index : (openedIndex.value === index ? -1 : openedIndex.value)
}

watch(() => props.timeline, () => {
  expandedIndices.value.clear()
  openedIndex.value = -1
})
</script>

<style scoped>
details > summary {
  list-style: none;
}

details > summary::-webkit-details-marker {
  display: none;
}

details > summary .marker {
  transition: transform 0.2s ease-in-out;
}

details[open] > summary .marker {
  transform: rotate(90deg);
}

.timeline-line {
  /* 时间线宽度是 2px (w-0.5)，中心在 1px */
  left: 0;
  width: 2px;
}

.timeline-circle {
  /* 圆圈宽度是 20px (h-5 w-5)，中心应该在 1px 与时间线对齐 */
  left: 1px;
  transform: translateX(-50%);
}

.timeline-arrow {
  color: #9ca3af;
}

.dark .timeline-arrow {
  color: #cbd5e1;
}

.timeline-arrow-active {
  color: #ffffff;
}
</style>

