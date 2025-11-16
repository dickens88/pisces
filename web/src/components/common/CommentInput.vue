<template>
  <div class="comment-input-container">
    <div class="flex items-start gap-4">
      <UserAvatar name="Current User" class="w-10 h-10 shrink-0" />
      <div class="flex-1">
        <!-- Input container -->
        <div 
          class="relative rounded-xl border-2 border-[#3c4a60] bg-[#1e293b] transition-all duration-200 focus-within:border-primary focus-within:shadow-lg focus-within:shadow-primary/20"
          :class="{ 
            'border-primary shadow-lg shadow-primary/20 drag-active': isDragging,
            'border-primary/50': isDragging
          }"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
        >
          <textarea
            v-model="commentText"
            class="w-full rounded-xl bg-transparent p-4 pr-32 text-white placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[100px]"
            :placeholder="placeholder"
            rows="3"
            @input="handleTextareaInput"
          ></textarea>
          
          <!-- Toolbar -->
          <div class="absolute bottom-3 left-4 flex items-center gap-2">
            <!-- File upload button -->
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileSelect"
            />
            <button
              type="button"
              @click="triggerFileInput"
              class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200 group"
              :title="$t('incidents.detail.comments.attachFile') || 'Upload file'"
            >
              <span class="material-symbols-outlined text-lg">attach_file</span>
            </button>
          </div>
          
          <!-- Submit button -->
          <button
            @click="handleSubmit"
            :disabled="!canSubmit"
            class="absolute bottom-3 right-3 flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-blue-600 px-4 py-2 text-xs font-semibold text-white transition-all duration-200 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl disabled:shadow-none"
          >
            <span class="material-symbols-outlined text-base">send</span>
            <span>{{ $t('common.send') }}</span>
          </button>
        </div>
        
        <!-- Uploaded files list -->
        <div v-if="uploadedFiles.length > 0" class="mt-3 flex flex-wrap gap-2">
          <div
            v-for="(file, index) in uploadedFiles"
            :key="index"
            class="group relative flex items-center gap-2 rounded-lg bg-[#2a3546] border border-[#3c4a60] px-3 py-2 hover:bg-[#3c4a60] transition-colors"
          >
            <span class="material-symbols-outlined text-primary text-sm">
              {{ getFileIcon(file.type) }}
            </span>
            <span class="text-sm text-white max-w-[200px] truncate">{{ file.name }}</span>
            <span class="text-xs text-text-light">{{ formatFileSize(file.size) }}</span>
            <button
              @click="removeFile(0)"
              class="ml-1 flex items-center justify-center w-5 h-5 rounded-full bg-red-500/20 hover:bg-red-500/30 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
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
  placeholder: {
    type: String,
    default: 'Add a comment...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: String,
    default: ''
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
const isDragging = ref(false)
const fileInput = ref(null)

const canSubmit = computed(() => {
  return !props.disabled && (commentText.value.trim().length > 0 || uploadedFiles.value.length > 0)
})

const handleTextareaInput = () => {
  // 可以在这里添加自动调整高度的逻辑
}

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  // 只取第一个文件
  if (files.length > 0) {
    addFiles([files[0]])
  }
  // 清空input，以便可以再次选择相同文件
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  // 只取第一个文件
  if (files.length > 0) {
    addFiles([files[0]])
  }
}

const MAX_FILE_SIZE = 500 * 1024 // 500KB

const addFiles = (files) => {
  if (files.length === 0) return
  
  const file = files[0] // 只处理第一个文件
  
  // 检查文件大小（限制为500KB）
  if (file.size > MAX_FILE_SIZE) {
    const errorMsg = t('common.fileSizeExceeded', { 
      fileName: file.name, 
      maxSize: '500KB' 
    }) || `文件 ${file.name} 超过大小限制（最大 500KB）`
    toast.error(errorMsg, '文件过大')
    console.warn(`File ${file.name} is too large (max 500KB), size: ${formatFileSize(file.size)}`)
    return
  }
  
  // 一条评论只能附加一个附件，直接替换现有文件
  uploadedFiles.value = [file]
}

const removeFile = (index) => {
  uploadedFiles.value = []
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
    files: [...uploadedFiles.value]
  })
  
  // 清空输入和文件
  commentText.value = ''
  uploadedFiles.value = []
}

// 暴露方法供父组件调用
defineExpose({
  clear: () => {
    commentText.value = ''
    uploadedFiles.value = []
  },
  getFiles: () => [...uploadedFiles.value]
})
</script>

<style scoped>
.comment-input-container {
  /* 组件样式 */
}
</style>

