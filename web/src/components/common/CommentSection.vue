<template>
  <div class="comment-section flex flex-col">
    <!-- 标题（可选） -->
    <h3 v-if="title" class="text-lg font-semibold mb-4 text-gray-900 dark:text-white shrink-0">{{ title }}</h3>
    
    <!-- 评论列表 -->
    <div class="space-y-6 mb-6">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="flex items-start gap-4"
      >
        <!-- 头像 -->
        <UserAvatar 
          v-if="useAvatarComponent"
          :name="comment.author" 
          class="w-10 h-10 shrink-0" 
        />
        <div
          v-else
          :class="[
            'flex-shrink-0 size-10 rounded-full flex items-center justify-center font-bold text-white text-base',
            comment.avatarColor || 'bg-teal-500'
          ]"
        >
          <span>{{ comment.authorInitials || getInitials(comment.author) }}</span>
        </div>
        
        <!-- 评论内容 -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
            <p class="font-semibold text-gray-900 dark:text-white">{{ comment.author }}</p>
            <p class="text-xs shrink-0 text-gray-500 dark:text-slate-400">{{ comment.time }}</p>
          </div>
          <div class="mt-2 text-sm leading-relaxed text-gray-700 dark:text-slate-300 bg-gray-100 dark:bg-slate-800 p-3 rounded-lg border border-gray-200 dark:border-slate-700">
            <!-- 内容 + 右侧类型标签 -->
            <div
              v-if="comment.type"
              class="flex items-start justify-between gap-3"
            >
              <div 
                v-html="sanitizeHtml(comment.content)"
                class="comment-content flex-1"
              ></div>
              <span
                :class="[
                  'inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium shrink-0 ml-1',
                  getCommentTypeClass(comment.type)
                ]"
              >
                {{ getCommentTypeLabel(comment.type) }}
              </span>
            </div>

            <!-- 无类型时正常显示 -->
            <div 
              v-else
              v-html="sanitizeHtml(comment.content)"
              class="comment-content"
            ></div>
            
            <!-- Display file attachments from backend -->
            <div v-if="comment.file" class="mt-3">
              <!-- Display image -->
              <div v-if="comment.file.is_image" class="mt-2">
                <img
                  :src="comment.file.data"
                  :alt="comment.file.file_name || 'Uploaded image'"
                  class="max-w-full max-h-96 rounded-lg border border-gray-200 dark:border-slate-600 cursor-pointer hover:opacity-90 transition-opacity"
                  @click="openImageModal(comment.file.data)"
                />
                <p v-if="comment.file.file_name" class="mt-1 text-xs text-gray-500 dark:text-slate-400">
                  {{ comment.file.file_name }}
                </p>
              </div>
              <!-- Display download link for non-image files -->
              <div v-else class="mt-2">
                <a
                  :href="comment.file.download_url"
                  target="_blank"
                  class="inline-flex items-center gap-2 rounded-md bg-gray-100 dark:bg-slate-700 border border-gray-200 dark:border-slate-600 px-2.5 py-1.5 text-xs text-gray-700 dark:text-slate-300 hover:text-gray-900 dark:hover:text-white hover:border-primary/50 transition-colors"
                  @click.prevent="handleDownloadFile(comment.file.download_url, comment.file.type, comment.file.file_name)"
                >
                  <span class="material-symbols-outlined text-primary text-sm">
                    {{ getFileIcon(comment.file.type) }}
                  </span>
                  <span>{{ comment.file.file_name || '下载文件' }}</span>
                  <span v-if="!comment.file.file_name" class="text-gray-500 dark:text-slate-400/60">
                    ({{ comment.file.type }})
                  </span>
                </a>
              </div>
            </div>
            
            <!-- Display legacy attachments (if any) -->
            <div v-if="comment.files && comment.files.length > 0" class="mt-3 flex flex-wrap gap-2">
              <a
                v-for="(file, fileIndex) in comment.files"
                :key="fileIndex"
                href="#"
                class="inline-flex items-center gap-2 rounded-md bg-gray-100 dark:bg-slate-700 border border-gray-200 dark:border-slate-600 px-2.5 py-1.5 text-xs text-gray-700 dark:text-slate-300 hover:text-gray-900 dark:hover:text-white hover:border-primary/50 transition-colors"
              >
                <span class="material-symbols-outlined text-primary text-sm">
                  {{ getFileIcon(file.type) }}
                </span>
                <span class="max-w-[150px] truncate">{{ file.name }}</span>
                <span class="text-gray-500 dark:text-slate-400/60">
                  {{ formatFileSize(file.size) }}
                </span>
              </a>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!comments || comments.length === 0" class="text-center py-8 text-gray-500 dark:text-slate-400">
        {{ $t('common.noComments') || 'No comments yet' }}
      </div>
    </div>
    
    <!-- 评论输入框 -->
    <div class="border-t border-gray-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800/80 rounded-b-lg p-4 shrink-0">
      <CommentInput
        v-model="newCommentText"
        :disabled="disabled"
        :loading="loading"
        :enable-comment-type="enableCommentType"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'
import UserAvatar from './UserAvatar.vue'
import CommentInput from './CommentInput.vue'

const props = defineProps({
  // 评论列表
  comments: {
    type: Array,
    default: () => []
  },
  // 标题（可选）
  title: {
    type: String,
    default: ''
  },
  // 是否禁用输入
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否使用 UserAvatar 组件（告警详情使用，事件和漏洞使用自定义头像）
  useAvatarComponent: {
    type: Boolean,
    default: false
  },
  // 是否正在提交评论（显示发送按钮loading状态）
  loading: {
    type: Boolean,
    default: false
  },
  // 是否启用评论类型下拉
  enableCommentType: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const { t } = useI18n()
const toast = useToast()
const newCommentText = ref('')
// 归一化评论类型 key（用于 label 和样式）
const normalizeCommentType = (rawType) => {
  if (!rawType) return 'comment'
  const value = String(rawType).toLowerCase()

  // 兼容后端不同命名
  let key = 'comment'
  if (value === 'comment') {
    key = 'comment'
  } else if (value === 'attacktrace' || value === 'attack_tracing' || value === 'attack-trace') {
    key = 'attackTrace'
  } else if (value === 'attackblock' || value === 'attack_block' || value === 'attack-block') {
    key = 'attackBlock'
  } else if (value === 'riskmitigation' || value === 'risk_mitigation' || value === 'risk-mitigation') {
    key = 'riskMitigation'
  } else if (value === 'vulnerabilitylocate' || value === 'vulnerability_location' || value === 'vulnerability-identification' || value === 'vulnerabilityidentification') {
    key = 'vulnerabilityLocate'
  }

  return key
}

// 获取评论类型展示文案
const getCommentTypeLabel = (rawType) => {
  const key = normalizeCommentType(rawType)
  return t(`common.commentTypes.${key}`) || key
}

// 不同类型对应不同颜色样式
const getCommentTypeClass = (rawType) => {
  const key = normalizeCommentType(rawType)

  const map = {
    comment: 'bg-gray-100 text-gray-700 dark:bg-slate-700/60 dark:text-slate-100',
    attackTrace: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300',
    attackBlock: 'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300',
    riskMitigation: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300',
    vulnerabilityLocate: 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-300'
  }

  return map[key] || map.comment
}

// 获取作者首字母
const getInitials = (name) => {
  if (!name) return 'U'
  const words = name.trim().split(/\s+/)
  if (words.length > 1) {
    return words.slice(0, 3).map(word => word.charAt(0).toUpperCase()).join('')
  }
  return name.charAt(0).toUpperCase()
}

// 清理 HTML
const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  
  let processedHtml = html
    .replace(/<div\s*\/?>/gi, '<br>')  // 将 <div> 和 <div/> 转换为 <br>
    .replace(/<\/div>/gi, '')          // 移除 </div> 标签
  
  return DOMPurify.sanitize(processedHtml, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}

// 文件图标
const getFileIcon = (mimeType) => {
  if (!mimeType) return 'description'
  if (mimeType.startsWith('image/')) return 'image'
  if (mimeType.startsWith('video/')) return 'video_file'
  if (mimeType.startsWith('audio/')) return 'audio_file'
  if (mimeType.includes('pdf')) return 'picture_as_pdf'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'description'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'table_chart'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'folder_zip'
  return 'attach_file'
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 打开图片模态框
const openImageModal = (imageSrc) => {
  const modal = document.createElement('div')
  modal.className = 'fixed inset-0 z-[100] flex items-center justify-center bg-black/90'
  modal.onclick = () => document.body.removeChild(modal)
  
  const img = document.createElement('img')
  img.src = imageSrc
  img.className = 'max-w-[90vw] max-h-[90vh] object-contain'
  img.onclick = (e) => e.stopPropagation()
  
  modal.appendChild(img)
  document.body.appendChild(modal)
}

// 下载文件
const handleDownloadFile = async (url, fileType, fileName) => {
  try {
    let fullUrl = url
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
      if (apiBaseURL) {
        if (apiBaseURL.endsWith('/api') && url.startsWith('/api')) {
          fullUrl = `${apiBaseURL}${url.substring(4)}`
        } else {
          fullUrl = `${apiBaseURL}${url}`
        }
      } else {
        fullUrl = url
      }
    }
    
    const response = await fetch(fullUrl)
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    if (fileName) {
      link.download = fileName
    } else {
      link.download = `file_${Date.now()}.${fileType.split('/').pop() || 'bin'}`
    }
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    console.error('Failed to download file:', error)
    toast.error('文件下载失败', 'ERROR')
  }
}

// 处理提交
const handleSubmit = (data) => {
  emit('submit', data)
  newCommentText.value = ''
}

// 暴露清空方法
defineExpose({
  clear: () => {
    newCommentText.value = ''
  }
})
</script>

<style scoped>
/* Ensure long comment text wraps inside the bubble instead of overflowing */
.comment-content {
  white-space: pre-wrap;          /* keep line breaks, wrap long lines */
  word-wrap: break-word;          /* legacy name */
  overflow-wrap: anywhere;        /* modern name, handles very long tokens/URLs */
}

/* Ensure <pre> / <code> blocks inside comments also wrap instead of overflowing */
.comment-content :deep(pre),
.comment-content :deep(code) {
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
</style>

