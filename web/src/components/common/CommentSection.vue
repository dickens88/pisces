<template>
  <div class="comment-section flex flex-col">
    <!-- 标题（可选） -->
    <h3 v-if="title" class="text-lg font-semibold mb-4 text-gray-900 dark:text-white shrink-0">{{ title }}</h3>
    
    <!-- 评论列表 -->
    <div class="space-y-6 mb-6">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="flex items-start gap-4 group"
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
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <p class="font-semibold text-gray-900 dark:text-white">{{ comment.author }}</p>
                <div class="flex items-center gap-2 flex-shrink-0">
                  <template v-if="comment.type">
                    <span class="text-xs text-gray-500 dark:text-slate-400">{{ $t('common.action') }}:</span>
                    <span
                      :class="[
                        'inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium',
                        getActionTypeClass(comment.type)
                      ]"
                    >
                      {{ getActionTypeLabel(comment.type) }}
                    </span>
                    <span class="h-3 w-px bg-gray-300 dark:bg-gray-600"></span>
                  </template>
                  <p class="text-xs text-gray-500 dark:text-slate-400">{{ comment.time }}</p>
                </div>
              </div>
            </div>
            <!-- 删除按钮（仅作者可见） -->
            <div v-if="isCommentAuthor(comment)" class="hidden group-hover:flex items-center ml-2">
              <button
                @click="handleDeleteComment(comment)"
                class="p-0 rounded hover:bg-red-100 dark:hover:bg-red-900/20 text-gray-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                :title="$t('incidents.detail.comments.deleteComment')"
              >
                <span class="material-symbols-outlined text-sm leading-none">delete</span>
              </button>
            </div>
          </div>
           <div class="mt-2 text-sm leading-relaxed text-gray-700 dark:text-slate-300 bg-gray-100 dark:bg-slate-800 p-3 rounded-lg border border-gray-200 dark:border-slate-700">
             <div
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
        :current-user-name="currentUserName"
        :enable-comment-type="enableCommentType"
        @submit="handleSubmit"
      />
    </div>

    <!-- 编辑评论对话框 -->
    <div
      v-if="editingComment"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="cancelEdit"
    >
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-xl max-w-2xl w-full mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {{ $t('incidents.detail.comments.editComment') }}
        </h3>
        <div class="space-y-4">
          <!-- 评论类型选择 -->
          <div v-if="enableCommentType">
            <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              {{ $t('common.commentTypes.label') }}
            </label>
            <select
              v-model="editCommentType"
              class="w-full rounded-lg border border-gray-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm text-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/60"
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
          <!-- 评论内容输入 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
              {{ $t('incidents.detail.comments.addComment') }}
            </label>
            <textarea
              v-model="editCommentText"
              rows="6"
              class="w-full rounded-lg border border-gray-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/60 resize-none"
              :placeholder="$t('incidents.detail.comments.addComment')"
            ></textarea>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="cancelEdit"
            class="px-4 py-2 rounded-lg border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="saveEdit"
            :disabled="!editCommentText.trim() || savingEdit"
            class="px-4 py-2 rounded-lg bg-primary text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ savingEdit ? $t('common.loading') : $t('common.save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除评论确认对话框 -->
    <div
      v-if="showDeleteCommentDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeDeleteCommentDialog"
    >
      <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">
            {{ $t('incidents.detail.comments.deleteDialog.title') }}
          </h2>
          <button
            @click="closeDeleteCommentDialog"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('incidents.detail.comments.confirmDeleteMessage') || '确认要删除这条评论吗？此操作不可撤销。' }}
          </p>
        </div>

        <!-- Confirmation input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('incidents.detail.comments.deleteDialog.confirmInputLabel') }}
          </label>
          <input
            v-model="deleteConfirmInput"
            @keydown.enter.prevent="confirmDeleteComment"
            type="text"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
            :placeholder="$t('incidents.detail.comments.deleteDialog.confirmInputPlaceholder')"
            autocomplete="off"
          />
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeDeleteCommentDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmDeleteComment"
            :disabled="!isDeleteConfirmValid || isDeletingComment"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isDeletingComment" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'
import UserAvatar from './UserAvatar.vue'
import CommentInput from './CommentInput.vue'
import { useAuthStore } from '@/stores/auth'

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

const emit = defineEmits(['submit', 'update', 'delete'])

const { t } = useI18n()
const authStore = useAuthStore()
const toast = useToast()
const newCommentText = ref('')

// 编辑相关状态
const editingComment = ref(null)
const editCommentText = ref('')
const editCommentType = ref('comment')
const savingEdit = ref(false)

// 删除相关状态
const showDeleteCommentDialog = ref(false)
const deleteConfirmInput = ref('')
const deletingComment = ref(null)
const isDeletingComment = ref(false)

// 统一的动作/评论类型文案：系统动作和评论类型视为一套
const getActionTypeLabel = (rawType) => {
  if (!rawType) return ''

  const raw = String(rawType)
  const lower = raw.toLowerCase()

  // 1. 优先匹配系统动作（actionTypes），key 统一用小写
  const actionLabel = t(`common.actionTypes.${lower}`)
  if (actionLabel && actionLabel !== `common.actionTypes.${lower}`) {
    return actionLabel
  }

  // 2. 再按评论类型（commentTypes）key 匹配（保持原始大小写，兼容现有配置）
  const commentLabel = t(`common.commentTypes.${raw}`)
  if (commentLabel && commentLabel !== `common.commentTypes.${raw}`) {
    return commentLabel
  }

  // 3. 都没有就直接回退原始值
  return raw
}

// 统一的动作/评论类型样式
const getActionTypeClass = (rawType) => {
  const raw = String(rawType || '')
  const lower = raw.toLowerCase()

  const typeColorMap = {

    // 攻击相关
    attacktracing: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300',
    attackTracing: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300',
    attackblocking: 'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300',
    attackBlocking: 'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300',

    // 风险/漏洞处理
    riskmitigation: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300',
    riskMitigation: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300',
    vulnerabilityidentification: 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-300',
    vulnerabilityIdentification: 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-300'
  }

  if (typeColorMap[lower]) {
    return typeColorMap[lower]
  }
  if (typeColorMap[raw]) {
    return typeColorMap[raw]
  }

  // 特殊：关闭/关联/转移类动作统一红色
  if (lower === 'close' || lower === 'relatetodataobject' || lower === 'transfertoincident') {
    return 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'
  }

  // 其他未知动作统一蓝色
  return 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300'
}

// 当前登录用户名称（用于输入框左侧头像）
const currentUserName = computed(() => {
  const user = authStore.user
  if (!user) return ''
  return user.username
})

// 检查当前用户是否是评论作者
const isCommentAuthor = (comment) => {
  if (!comment || !comment.author) return false
  const currentUser = currentUserName.value
  if (!currentUser) return false
  // 比较用户名（不区分大小写）
  return currentUser.toLowerCase() === comment.author.toLowerCase()
}

onMounted(() => {
  // 确保已获取到当前用户信息（内部有缓存，不会重复请求）
  authStore.fetchCurrentUser().catch(() => {})
})

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

// 处理编辑评论
const handleEditComment = (comment) => {
  editingComment.value = comment
  editCommentText.value = comment.content || ''
  editCommentType.value = comment.note_type || comment.type || 'comment'
}

// 取消编辑
const cancelEdit = () => {
  editingComment.value = null
  editCommentText.value = ''
  editCommentType.value = 'comment'
}

// 保存编辑
const saveEdit = async () => {
  if (!editingComment.value || !editCommentText.value.trim()) {
    return
  }

  savingEdit.value = true
  try {
    // 需要从父组件获取 eventId，这里先通过 emit 传递
    emit('update', {
      commentId: editingComment.value.id || editingComment.value.comment_id,
      comment: editCommentText.value.trim(),
      noteType: editCommentType.value
    })
    cancelEdit()
  } catch (error) {
    console.error('Failed to update comment:', error)
    toast.error(t('incidents.detail.comments.updateError'), 'ERROR')
  } finally {
    savingEdit.value = false
  }
}

// 删除确认验证
const isDeleteConfirmValid = computed(() => {
  return deleteConfirmInput.value.toLowerCase() === 'delete'
})

// 打开删除确认对话框
const openDeleteCommentDialog = (comment) => {
  deletingComment.value = comment
  showDeleteCommentDialog.value = true
  deleteConfirmInput.value = ''
}

// 关闭删除确认对话框
const closeDeleteCommentDialog = () => {
  showDeleteCommentDialog.value = false
  deleteConfirmInput.value = ''
  deletingComment.value = null
}

// 确认删除评论
const confirmDeleteComment = async () => {
  if (!isDeleteConfirmValid.value || isDeletingComment.value || !deletingComment.value) {
    return
  }

  const comment = deletingComment.value
  isDeletingComment.value = true

  try {
    // 直接调用 delete 事件，由父组件处理 API 调用
    emit('delete', {
      commentId: comment.id || comment.comment_id,
      comment: comment
    })
    closeDeleteCommentDialog()
  } catch (error) {
    console.error('Failed to delete comment:', error)
    toast.error(t('incidents.detail.comments.deleteError') || '评论删除失败，请稍后重试', 'ERROR')
  } finally {
    isDeletingComment.value = false
  }
}

// 处理删除评论（打开确认对话框）
const handleDeleteComment = (comment) => {
  openDeleteCommentDialog(comment)
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

