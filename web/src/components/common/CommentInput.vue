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
          class="relative rounded-xl border-2 border-gray-200 dark:border-[#3c4a60] bg-white dark:bg-[#1e293b] transition-all duration-200 focus-within:border-primary focus-within:shadow-lg focus-within:shadow-primary/20"
          :class="{ 
            'border-primary shadow-lg shadow-primary/20 drag-active': isDragging,
            'border-primary/50': isDragging
          }"
          @drop.prevent="handleDrop"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
        >
          <div
            v-if="prefixIcon && !imagePreviewUrl"
            class="absolute left-3 top-2.5 text-gray-400 dark:text-text-light/70 pointer-events-none"
          >
            <span class="material-symbols-outlined text-base leading-none">
              {{ prefixIcon }}
            </span>
          </div>
          <textarea
            v-model="commentText"
            :class="[
              // 为了避免底部工具栏和右侧发送按钮遮挡文字，这里增加了底部和右侧的额外内边距
              'w-full rounded-xl bg-transparent px-2.5 pt-2.5 pb-10 pr-12 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[40px] max-h-[200px]',
              imagePreviewUrl ? 'pl-20' : '',
              prefixIcon && !imagePreviewUrl ? 'pl-10' : ''
            ]"
            :placeholder="placeholder"
            rows="1"
            @input="handleTextareaInput"
            @keydown="handleKeyDown"
            @paste="handlePaste"
          ></textarea>
          
          <!-- 图片缩略图预览（显示在输入框内左上角） -->
          <div v-if="imagePreviewUrl" class="group absolute top-2 left-2 w-12 h-12 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-[#3c4a60] bg-gray-100 dark:bg-[#2a3546] shadow-md">
            <img
              :src="imagePreviewUrl"
              alt="Preview"
              class="w-full h-full object-cover"
            />
          <!-- 启用评论类型时的布局（事件管理使用） -->
          <template v-if="props.enableCommentType">
            <div class="flex items-start gap-3 py-1 pl-2 pr-12">
              <!-- 左侧工具区：附件 + 评论类型 -->
              <div
                v-if="props.enableFileUpload"
                class="flex items-center gap-2 pt-0.5 shrink-0"
              >
                <input
                  ref="fileInput"
                  type="file"
                  class="hidden"
                  @change="handleFileSelect"
                />
                <button
                  type="button"
                  @click="triggerFileInput"
                  class="flex items-center justify-center w-8 h-8 rounded-lg bg-gray-100 dark:bg-[#2a3546] hover:bg-gray-200 dark:hover:bg-[#3c4a60] text-gray-600 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-all duration-200 group border border-transparent hover:border-primary/30"
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

              <!-- 文本输入（带类型） -->
              <div class="relative flex-1">
                <div
                  v-if="prefixIcon && !imagePreviewUrl"
                  class="absolute left-3 top-2.5 text-gray-400 dark:text-text-light/70 pointer-events-none"
                >
                  <span class="material-symbols-outlined text-base leading-none">
                    {{ prefixIcon }}
                  </span>
                </div>

                <div
                  v-if="imagePreviewUrl"
                  class="group absolute -top-1 left-0 w-16 h-16 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-[#3c4a60] bg-gray-100 dark:bg-[#2a3546] shadow-md"
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
                    'w-full rounded-xl bg-transparent px-3 py-1.5 pr-2 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[36px] max-h-[200px] border border-transparent',
                    imagePreviewUrl ? 'pl-20' : '',
                    prefixIcon && !imagePreviewUrl ? 'pl-10' : ''
                  ]"
                  :placeholder="placeholder || $t('incidents.detail.comments.addComment')"
                  rows="1"
                  @input="handleTextareaInput"
                  @keydown="handleKeyDown"
                  @paste="handlePaste"
                ></textarea>
              </div>
            </div>

            <!-- 发送按钮（带类型布局） -->
            <button
              @click="handleSubmit"
              :disabled="!canSubmit || props.loading"
              class="absolute bottom-2 right-2 flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-r from-primary to-blue-600 text-white transition-all duration-200 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none"
              :title="$t('common.send') || '发送'"
            >
              <span
                class="material-symbols-outlined text-base"
                :class="{ 'animate-spin': props.loading }"
              >
                {{ props.loading ? 'refresh' : 'send' }}
              </span>
            </button>
          </template>

          <!-- 默认紧凑布局（告警/ASM/漏洞等），附件按钮与光标同一行 -->
          <template v-else>
            <div class="flex items-start gap-3 py-1 pl-2 pr-12">
              <!-- 左侧附件按钮 -->
              <div
                v-if="props.enableFileUpload"
                class="flex items-center pt-0.5 shrink-0"
              >
                <input
                  ref="fileInput"
                  type="file"
                  class="hidden"
                  @change="handleFileSelect"
                />
                <button
                  type="button"
                  @click="triggerFileInput"
                  class="flex items-center justify-center w-8 h-8 rounded-lg bg-gray-100 dark:bg-[#2a3546] hover:bg-gray-200 dark:hover:bg-[#3c4a60] text-gray-600 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-all duration-200 group border border-transparent hover:border-primary/30"
                  :title="$t('incidents.detail.comments.attachFile') || 'Upload file'"
                >
                  <span class="material-symbols-outlined text-lg">attach_file</span>
                </button>
              </div>

              <!-- 文本输入（无类型时） -->
              <div class="relative flex-1">
                <div
                  v-if="prefixIcon && !imagePreviewUrl"
                  class="absolute left-3 top-2.5 text-gray-400 dark:text-text-light/70 pointer-events-none"
                >
                  <span class="material-symbols-outlined text-base leading-none">
                    {{ prefixIcon }}
                  </span>
                </div>

                <!-- 图片缩略图预览 -->
                <div
                  v-if="imagePreviewUrl"
                  class="group absolute -top-1 left-0 w-16 h-16 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-[#3c4a60] bg-gray-100 dark:bg-[#2a3546] shadow-md"
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
                    'w-full rounded-xl bg-transparent px-3 py-1.5 pr-2 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[36px] max-h-[200px] border border-transparent',
                    imagePreviewUrl ? 'pl-20' : '',
                    prefixIcon && !imagePreviewUrl ? 'pl-10' : ''
                  ]"
                  :placeholder="placeholder"
                  rows="1"
                  @input="handleTextareaInput"
                  @keydown="handleKeyDown"
                  @paste="handlePaste"
                ></textarea>
              </div>
            </div>

            <!-- Submit button -->
            <button
              @click="handleSubmit"
              :disabled="!canSubmit || props.loading"
              class="absolute bottom-2 right-2 flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-r from-primary to-blue-600 text-white transition-all duration-200 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none"
              :title="$t('common.send') || '发送'"
            >
              <span
                class="material-symbols-outlined text-base"
                :class="{ 'animate-spin': props.loading }"
              >
                {{ props.loading ? 'refresh' : 'send' }}
              </span>
            </button>
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
</style>

