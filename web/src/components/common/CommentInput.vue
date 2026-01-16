<template>
  <div class="comment-input-container">
    <div class="flex items-start gap-4">
      <UserAvatar
        :name="props.currentUserName || $t('common.currentUser')"
        class="w-10 h-10 shrink-0"
      />
      <div class="flex-1">
        <!-- Input container -->
        <div 
          class="relative rounded-xl border-2 border-gray-200 dark:border-[#3c4a60] bg-white dark:bg-[#1e293b] transition-all duration-200 focus-within:border-primary focus-within:shadow-lg focus-within:shadow-primary/20 flex flex-col"
          :class="{ 
            'border-primary shadow-lg shadow-primary/20 drag-active': isDragging,
            'border-primary/50': isDragging
          }"
          @drop.prevent="handleDrop"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
        >
          <!-- 启用评论类型时的布局（事件管理使用） -->
          <template v-if="props.enableCommentType">
            <!-- 文本输入区域 -->
            <div class="relative px-3 py-2">
              <div
                v-if="prefixIcon && !imagePreviewUrl"
                class="absolute left-5 top-3.5 text-gray-400 dark:text-text-light/70 pointer-events-none z-10"
              >
                <span class="material-symbols-outlined text-base leading-none">
                  {{ prefixIcon }}
                </span>
              </div>

              <!-- 图片缩略图预览 -->
              <div
                v-if="imagePreviewUrl"
                class="group absolute left-3 top-2 w-16 h-16 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-[#3c4a60] bg-gray-100 dark:bg-[#2a3546] shadow-md z-10"
              >
                <img
                  :src="imagePreviewUrl"
                  alt="Preview"
                  class="w-full h-full object-cover"
                />
                <button
                  @click.stop="removeFile()"
                  class="absolute top-1 right-1 w-5 h-5 flex items-center justify-center rounded-full bg-black/40 hover:bg-black/60 backdrop-blur-sm text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <span class="material-symbols-outlined text-xs">close</span>
                </button>
              </div>

              <textarea
                v-model="commentText"
                :class="[
                  'comment-textarea w-full rounded-lg bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[40px] max-h-[200px] border-0 overflow-y-auto',
                  imagePreviewUrl ? 'pl-20' : '',
                  prefixIcon && !imagePreviewUrl ? 'pl-10' : ''
                ]"
                :placeholder="placeholder || $t('common.addComment') || '添加评论，支持ctrl+v粘贴图片'"
                rows="1"
                @input="handleTextareaInput"
                @keydown="handleKeyDown"
                @paste="handlePaste"
              ></textarea>
            </div>

            <!-- 底部控制栏 -->
            <div class="flex items-center justify-between px-3 py-2 border-t border-gray-200 dark:border-[#3c4a60]">
              <!-- 左侧：附件按钮 + 评论类型 -->
              <div class="flex items-center gap-2">
                <input
                  v-if="props.enableFileUpload"
                  ref="fileInput"
                  type="file"
                  class="hidden"
                  @change="handleFileSelect"
                />
                <button
                  v-if="props.enableFileUpload"
                  type="button"
                  @click="triggerFileInput"
                  class="flex items-center justify-center w-8 h-8 rounded-lg text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-[#2a3546] transition-all duration-200"
                  :title="$t('incidents.detail.comments.attachFile') || 'Upload file'"
                >
                  <span class="material-symbols-outlined text-lg">attach_file</span>
                </button>

                <select
                  v-model="commentType"
                  class="h-8 min-w-[120px] rounded-lg border border-gray-200 dark:border-[#3c4a60] bg-gray-50 dark:bg-[#2a3546] text-sm text-gray-800 dark:text-white px-3 focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/60 transition"
                  :title="$t('common.commentTypes.label')"
                >
                  <option
                    v-for="option in commentTypeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <!-- 右侧：发送按钮 -->
              <button
                @click="handleSubmit"
                :disabled="!canSubmit || props.loading"
                class="flex items-center justify-center w-8 h-8 rounded-full bg-primary hover:bg-primary/90 text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary"
                :title="$t('common.send') || '发送'"
              >
                <span
                  class="material-symbols-outlined text-base"
                  :class="{ 'animate-spin': props.loading }"
                >
                  {{ props.loading ? 'refresh' : 'arrow_upward' }}
                </span>
              </button>
            </div>
          </template>

          <!-- 默认紧凑布局（告警/ASM/漏洞等），优化后的布局 -->
          <template v-else>
            <!-- 文本输入区域 -->
            <div class="relative px-3 py-2">
              <div
                v-if="prefixIcon && !imagePreviewUrl"
                class="absolute left-5 top-3.5 text-gray-400 dark:text-text-light/70 pointer-events-none z-10"
              >
                <span class="material-symbols-outlined text-base leading-none">
                  {{ prefixIcon }}
                </span>
              </div>

              <!-- 图片缩略图预览 -->
              <div
                v-if="imagePreviewUrl"
                class="group absolute left-3 top-2 w-16 h-16 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-[#3c4a60] bg-gray-100 dark:bg-[#2a3546] shadow-md z-10"
              >
                <img
                  :src="imagePreviewUrl"
                  alt="Preview"
                  class="w-full h-full object-cover"
                />
                <button
                  @click.stop="removeFile()"
                  class="absolute top-1 right-1 w-5 h-5 flex items-center justify-center rounded-full bg-black/40 hover:bg-black/60 backdrop-blur-sm text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <span class="material-symbols-outlined text-xs">close</span>
                </button>
              </div>

              <textarea
                v-model="commentText"
                :class="[
                  'comment-textarea w-full rounded-lg bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[40px] max-h-[200px] border-0 overflow-y-auto',
                  imagePreviewUrl ? 'pl-20' : '',
                  prefixIcon && !imagePreviewUrl ? 'pl-10' : ''
                ]"
                :placeholder="placeholder || $t('common.addComment') || '添加评论，支持ctrl+v粘贴图片'"
                rows="1"
                @input="handleTextareaInput"
                @keydown="handleKeyDown"
                @paste="handlePaste"
              ></textarea>
            </div>

            <!-- 底部控制栏 -->
            <div class="flex items-center justify-between px-3 py-2 border-t border-gray-200 dark:border-[#3c4a60]">
              <!-- 左侧：附件按钮 -->
              <div class="flex items-center gap-2">
                <input
                  v-if="props.enableFileUpload"
                  ref="fileInput"
                  type="file"
                  class="hidden"
                  @change="handleFileSelect"
                />
                <button
                  v-if="props.enableFileUpload"
                  type="button"
                  @click="triggerFileInput"
                  class="flex items-center justify-center w-8 h-8 rounded-lg text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-[#2a3546] transition-all duration-200"
                  :title="$t('incidents.detail.comments.attachFile') || 'Upload file'"
                >
                  <span class="material-symbols-outlined text-lg">attach_file</span>
                </button>
              </div>

              <!-- 右侧：发送按钮 -->
              <button
                @click="handleSubmit"
                :disabled="!canSubmit || props.loading"
                class="flex items-center justify-center w-8 h-8 rounded-full bg-primary hover:bg-primary/90 text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary"
                :title="$t('common.send') || '发送'"
              >
                <span
                  class="material-symbols-outlined text-base"
                  :class="{ 'animate-spin': props.loading }"
                >
                  {{ props.loading ? 'refresh' : 'arrow_upward' }}
                </span>
              </button>
            </div>
          </template>
        </div>
        
        <!-- Uploaded files list (只显示非图片文件) -->
        <div v-if="props.enableFileUpload && uploadedFiles.length > 0 && !imagePreviewUrl" class="mt-3 flex flex-wrap gap-2">
          <div
            v-for="(file, index) in uploadedFiles"
            :key="index"
            class="group relative flex items-center gap-2 rounded-lg bg-gray-100 dark:bg-[#2a3546] border border-gray-200 dark:border-[#3c4a60] px-3 py-2 hover:bg-gray-200 dark:hover:bg-[#3c4a60] transition-colors"
          >
            <span class="material-symbols-outlined text-primary text-sm">
              {{ getFileIcon(file.type) }}
            </span>
            <span class="text-sm text-gray-900 dark:text-white max-w-[200px] truncate">{{ file.name }}</span>
            <span class="text-xs text-gray-600 dark:text-text-light">{{ formatFileSize(file.size) }}</span>
            <button
              @click="removeFile()"
              class="ml-1 flex items-center justify-center w-5 h-5 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <span class="material-symbols-outlined text-xs">close</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import UserAvatar from './UserAvatar.vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: String,
    default: ''
  },
  // 当前用户显示名称，用来生成左侧头像
  currentUserName: {
    type: String,
    default: ''
  },
  enableFileUpload: {
    type: Boolean,
    default: true
  },
  // 是否显示评论类型下拉（仅事件详情 Evidence & Response 启用）
  enableCommentType: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: ''
  },
  prefixIcon: {
    type: String,
    default: ''
  },
  submitOnEnter: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const { t } = useI18n()
const toast = useToast()

const commentText = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const uploadedFiles = ref([])
const imagePreviewUrl = ref(null)
const isDragging = ref(false)
const fileInput = ref(null)
const commentType = ref('comment')

const commentTypeOptions = computed(() => [
  { value: 'comment', label: t('common.commentTypes.comment') },
  { value: 'attackTracing', label: t('common.commentTypes.attackTracing') },
  { value: 'attackBlocking', label: t('common.commentTypes.attackBlocking') },
  { value: 'riskMitigation', label: t('common.commentTypes.riskMitigation') },
  { value: 'vulnerabilityIdentification', label: t('common.commentTypes.vulnerabilityIdentification') }
])

const canSubmit = computed(() => {
  return !props.disabled && (commentText.value.trim().length > 0 || uploadedFiles.value.length > 0)
})

const handleTextareaInput = (event) => {
  const textarea = event.target
  textarea.style.height = 'auto'
  const scrollHeight = textarea.scrollHeight
  const maxHeight = 200
  textarea.style.height = Math.min(scrollHeight, maxHeight) + 'px'
}

const handleKeyDown = (event) => {
  if (!props.submitOnEnter) return
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSubmit()
  }
}

const handlePaste = async (event) => {
  if (!props.enableFileUpload) return
  
  const clipboardData = event.clipboardData || window.clipboardData
  if (!clipboardData) return
  
  const items = clipboardData.items
  if (!items) return

  const imageItems = []
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.type.indexOf('image') !== -1) {
      imageItems.push(item)
    }
  }

  if (imageItems.length > 0) {
    event.preventDefault()
    
    const lastImageItem = imageItems[imageItems.length - 1]
    const blob = lastImageItem.getAsFile()
    
    if (blob) {
      const file = new File([blob], `pasted-image-${Date.now()}.png`, {
        type: blob.type || 'image/png',
        lastModified: Date.now()
      })

      addFiles([file])
    }
  }
}

const triggerFileInput = () => {
  if (!props.enableFileUpload) return
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event) => {
  if (!props.enableFileUpload) return
  const files = Array.from(event.target.files || [])
  if (files.length > 0) {
    addFiles([files[0]])
  }
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  if (!props.enableFileUpload) return
  const files = Array.from(event.dataTransfer.files || [])
  if (files.length > 0) {
    addFiles([files[0]])
  }
}

const MAX_FILE_SIZE = 500 * 1024

const addFiles = (files) => {
  if (!props.enableFileUpload || files.length === 0) return
  
  const file = files[0]

  if (file.size > MAX_FILE_SIZE) {
    const errorMsg = t('common.fileSizeExceeded', { 
      fileName: file.name, 
      maxSize: '500KB' 
    }) || `文件 ${file.name} 超过大小限制（最大 500KB）`
    toast.error(errorMsg, '文件过大')
    console.warn(`File ${file.name} is too large (max 500KB), size: ${formatFileSize(file.size)}`)
    return
  }

  uploadedFiles.value = [file]

  if (file.type.startsWith('image/')) {
    if (imagePreviewUrl.value) {
      URL.revokeObjectURL(imagePreviewUrl.value)
    }
    imagePreviewUrl.value = URL.createObjectURL(file)
  } else {
    if (imagePreviewUrl.value) {
      URL.revokeObjectURL(imagePreviewUrl.value)
      imagePreviewUrl.value = null
    }
  }
}

const removeFile = () => {
  if (imagePreviewUrl.value) {
    URL.revokeObjectURL(imagePreviewUrl.value)
    imagePreviewUrl.value = null
  }
  uploadedFiles.value = []
}

const handleDragOver = () => {
  if (!props.enableFileUpload) return
  isDragging.value = true
}

const handleDragLeave = () => {
  if (!props.enableFileUpload) return
  isDragging.value = false
}

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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleSubmit = () => {
  if (!canSubmit.value) return
  
  emit('submit', {
    comment: commentText.value.trim(),
    files: [...uploadedFiles.value],
    type: commentType.value
  })

  commentText.value = ''
  commentType.value = 'comment'
  if (imagePreviewUrl.value) {
    URL.revokeObjectURL(imagePreviewUrl.value)
    imagePreviewUrl.value = null
  }
  uploadedFiles.value = []
}

defineExpose({
  clear: () => {
    commentText.value = ''
    commentType.value = 'comment'
    if (imagePreviewUrl.value) {
      URL.revokeObjectURL(imagePreviewUrl.value)
      imagePreviewUrl.value = null
    }
    uploadedFiles.value = []
  },
  getFiles: () => [...uploadedFiles.value]
})
</script>

<style scoped>
/* 隐藏 textarea 的滚动条，但保持滚动功能 */
.comment-textarea {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.comment-textarea::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

/* 确保 textarea 在内容变化时正确调整高度 */
.comment-textarea {
  overflow-y: auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
</style>

