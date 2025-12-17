<template>
  <div :class="cardClass">
    <slot name="header">
      <div v-if="hasHeader" class="flex items-start justify-between gap-4">
        <div class="flex items-center gap-2 min-w-0">
          <span v-if="headerIconToShow" class="material-symbols-outlined text-primary text-base shrink-0">
            {{ headerIconToShow }}
          </span>
          <h4
            v-if="primaryHeaderText"
            class="text-base font-semibold text-gray-900 dark:text-white truncate"
            :title="primaryHeaderText"
          >
            {{ primaryHeaderText }}
          </h4>
        </div>
        <div
          v-if="displayHeaderMeta"
          class="flex items-center gap-1 text-xs text-gray-500 dark:text-text-light whitespace-nowrap"
        >
          <span v-if="headerMetaIconToShow" class="material-symbols-outlined text-base">
            {{ headerMetaIconToShow }}
          </span>
          <span>{{ displayHeaderMeta }}</span>
        </div>
      </div>
    </slot>

    <slot>
      <div
        v-if="sanitizedHtmlContent"
        :class="[
          'mt-3 text-sm text-gray-700 dark:text-[#c3d3e8] alert-info-card__html',
          { 'alert-info-card__html--dark': isDarkMode }
        ]"
        v-html="sanitizedHtmlContent"
      ></div>
      <p
        v-else-if="summary"
        class="mt-3 text-sm text-gray-700 dark:text-[#c3d3e8] whitespace-pre-wrap"
      >
        {{ summary }}
      </p>
    </slot>

    <slot name="footer" v-if="showFooter">
      <div class="mt-4 flex items-center justify-between text-xs text-gray-500 dark:text-text-light">
        <slot name="footer-right">
          <div v-if="footerRightText" :class="footerRightWrapperClass">
            <span v-if="footerRightIcon" class="material-symbols-outlined text-base">{{ footerRightIcon }}</span>
            <span>{{ footerRightText }}</span>
          </div>
        </slot>
      </div>
    </slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import DOMPurify from 'dompurify'

import { formatDateTime } from '@/utils/dateTime'
import { useDarkModeObserver } from '@/composables/useDarkModeObserver'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  headerIcon: {
    type: String,
    default: ''
  },
  headerMeta: {
    type: [String, Number, Date],
    default: ''
  },
  htmlContent: {
    type: String,
    default: ''
  },
  summary: {
    type: String,
    default: ''
  },
  owner: {
    type: String,
    default: ''
  },
  ownerIcon: {
    type: String,
    default: 'person'
  },
  footerRightText: {
    type: String,
    default: ''
  },
  footerRightIcon: {
    type: String,
    default: 'schedule'
  },
  footerRightClass: {
    type: String,
    default: 'text-text-light'
  },
  headerMetaIcon: {
    type: String,
    default: 'schedule'
  }
})

const { isDarkMode } = useDarkModeObserver()

const sanitizedHtmlContent = computed(() => {
  if (!props.htmlContent) {
    return ''
  }
  
  // 预处理：将 div 标签转换为 p 标签，以便更好地显示分段
  let processedContent = props.htmlContent
    // 将 <div> 转换为 <p>，保留内容
    .replace(/<div[^>]*>/gi, '<p>')
    .replace(/<\/div>/gi, '</p>')
  
  // 使用 DOMPurify 清理 HTML
  const sanitized = DOMPurify.sanitize(processedContent, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
  
  // 后处理：清理空的段落标签
  return sanitized
    .replace(/<p>\s*<\/p>/gi, '') // 移除空段落
    .trim()
})

const primaryHeaderText = computed(() => props.owner || props.title)

const cardClass = computed(() => [
  'rounded-lg border border-gray-200 dark:border-border-dark bg-white dark:bg-[#1f2937]/30 p-4 transition-all',
  'cursor-default'
])

const footerRightWrapperClass = computed(() => [
  'flex items-center gap-1.5 text-xs',
  props.footerRightClass
])

const hasHeader = computed(() => Boolean(primaryHeaderText.value || props.headerMeta || props.headerIcon))

const showFooter = computed(() => Boolean(props.footerRightText))

const normalizeHeaderMeta = (value) => {
  if (value === null || value === undefined || value === '') {
    return ''
  }

  if (value === '-') {
    return '-'
  }

  try {
    const formatted = formatDateTime(value)
    return formatted === '-' && typeof value === 'string' ? value : formatted
  } catch (error) {
    return typeof value === 'string' ? value : String(value)
  }
}

const displayHeaderMeta = computed(() => normalizeHeaderMeta(props.headerMeta))

const headerIconToShow = computed(() => {
  if (props.owner) {
    return props.ownerIcon || 'person'
  }
  return props.headerIcon || ''
})

const headerMetaIconToShow = computed(() => (displayHeaderMeta.value ? props.headerMetaIcon : ''))
</script>

<style scoped>
/* 段落样式 - 使分段更明显，两个段落之间显示一个空行 */
.alert-info-card__html :deep(p) {
  margin: 0;
  line-height: 1.6;
}

.alert-info-card__html :deep(p:last-child) {
  margin-bottom: 0;
}

/* 连续的段落之间增加分隔，模拟空行效果 */
.alert-info-card__html :deep(p + p) {
  margin-top: 1.5rem; /* 约等于一个空行的高度（1.6行高 * 1.5 ≈ 2.4，这里用1.5rem） */
}

/* 空段落处理 */
.alert-info-card__html :deep(p:empty) {
  margin: 0.5rem 0;
  min-height: 0.5rem;
}

.alert-info-card__html :deep(pre) {
  background: rgba(226, 232, 240, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #0f172a;
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  margin: 10px 0;
}

:global(.dark) .alert-info-card__html :deep(pre),
.alert-info-card__html--dark :deep(pre) {
  background: #111b2e;
  border: 1px solid rgba(94, 114, 164, 0.45);
  color: #f1f5f9;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.4);
}

.alert-info-card__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
  color: #0f172a;
}

:global(.dark) .alert-info-card__html :deep(code),
.alert-info-card__html--dark :deep(code) {
  color: #f1f5f9;
}

.alert-info-card__html :deep(b) {
  color: #0f172a;
}

:global(.dark) .alert-info-card__html :deep(b),
.alert-info-card__html--dark :deep(b) {
  color: #e2e8f0;
}

/* 处理多个连续的 br 标签，使其看起来像段落分隔 */
.alert-info-card__html :deep(br + br) {
  display: block;
  content: '';
  margin-top: 0.75rem;
}
</style>

