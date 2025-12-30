<template>
  <div class="w-full">
    <!-- Page header -->
    <header class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
        {{ $t('asm.title') }}
      </h1>
      <div class="flex gap-2 items-center">
        <button
          @click="handleRefresh"
          :disabled="isRefreshing"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': isRefreshing }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="asm"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </header>

    <!-- ASM list table -->
    <section class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingItems"
        class="absolute inset-0 bg-white/80 dark:bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
      >
        <div class="flex flex-col items-center gap-4">
          <div class="relative w-16 h-16">
            <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
          </div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-3 p-4 border-b border-[#324867]">
        <div class="relative w-[30%] min-w-[300px] max-w-lg" ref="searchContainerRef">
          <div 
            class="flex items-start gap-2 min-h-[42px] rounded-lg border-0 bg-gray-100 dark:bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary"
            @click="handleSearchContainerClick"
          >
            <div class="pointer-events-none flex items-center shrink-0 pt-[2px]">
              <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">search</span>
            </div>
            <div class="flex flex-1 flex-wrap items-center gap-2 max-h-32 overflow-y-auto pr-1">
              <!-- Search keyword tags -->
              <div
                v-for="(keywordObj, index) in searchKeywords"
                :key="index"
                class="flex items-center gap-1 px-2 py-1 bg-primary/20 text-primary rounded text-sm max-w-full min-w-0"
              >
                <span class="min-w-0 break-all">{{ getFieldLabel(keywordObj.field) }}: {{ keywordObj.value }}</span>
                <button
                  @click.stop="removeKeyword(index)"
                  class="flex items-center justify-center hover:text-primary/70 transition-colors ml-0.5"
                  type="button"
                  :aria-label="$t('common.delete')"
                >
                  <span class="material-symbols-outlined" style="font-size: 16px;">close</span>
                </button>
              </div>
              <!-- Input field -->
              <input
                v-model="displaySearchInput"
                @keydown.enter.prevent="addKeyword"
                @keydown.backspace="handleKeywordDeleteKey"
                @focus="showFieldMenu = !currentField.value"
                @blur="handleSearchBlur"
                class="flex-1 min-w-[120px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
                :placeholder="getSearchPlaceholder()"
                type="text"
                ref="searchInputRef"
              />
            </div>
          </div>
          <!-- Field selection menu -->
          <div
            v-if="showFieldMenu && !currentField"
            class="absolute left-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
            @mousedown.prevent
          >
            <button
              v-for="field in searchFields"
              :key="field.value"
              @click="selectField(field.value)"
              class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
            >
              <span class="material-symbols-outlined text-base">{{ field.icon }}</span>
              <span>{{ field.label }}</span>
            </button>
          </div>
        </div>
        <div class="relative">
          <select
            v-model="statusFilter"
            @change="handleFilter"
            class="pl-4 pr-9 appearance-none block w-full rounded-lg border-0 bg-gray-100 dark:bg-[#233348] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm min-w-[120px]"
          >
            <option value="all">{{ $t('asm.list.allStatus') }}</option>
            <option value="open">{{ $t('asm.list.open') }}</option>
            <option value="block">{{ $t('asm.list.block') }}</option>
            <option value="closed">{{ $t('asm.list.closed') }}</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
            <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
          </div>
        </div>
        <!-- Spacer to push right buttons to the right -->
        <div class="flex-1 min-w-0"></div>
        <div class="flex items-center gap-3 flex-shrink-0">
          <button
            :disabled="selectedItems.length === 0"
            @click="openBatchCloseDialog"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
            <span>{{ $t('asm.list.batchClose') }}</span>
          </button>
          <!-- More actions button -->
          <div class="relative">
            <button
              @click="showMoreMenu = !showMoreMenu"
              class="more-menu-button flex items-center justify-center rounded-lg h-10 w-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
              :title="$t('common.more')"
            >
              <span class="material-symbols-outlined text-base">more_vert</span>
            </button>
            <!-- Dropdown menu -->
            <div
              v-if="showMoreMenu"
              class="more-menu-dropdown absolute right-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
            >
              <button
                @click="handleToggleWordWrap"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">
                  {{ isWordWrap ? 'wrap_text' : 'text_fields' }}
                </span>
                <span>{{ isWordWrap ? $t('common.wordWrap') : $t('common.singleLine') }}</span>
              </button>
              <button
                @click="handleConvertToVulnerability"
                :disabled="selectedItems.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">bug_report</span>
                <span>{{ $t('alerts.detail.convertToVulnerability') }}</span>
              </button>
              <button
                @click="handleCreateAlertFromMenu"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">add</span>
                <span>{{ $t('alerts.list.createAlert') }}</span>
              </button>
              <button
                @click="openBatchDeleteDialog"
                :disabled="selectedItems.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">delete</span>
                <span>{{ $t('asm.list.batchDelete') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <DataTable
        ref="dataTableRef"
        :columns="columns"
        :items="items"
        :selectable="true"
        :resizable="true"
        storage-key="asm-table-columns"
        :default-widths="defaultWidths"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @update:current-page="handlePageChange"
        @update:page-size="pageSize = $event"
        @select="handleSelect"
        @select-all="handleSelectAll"
        @page-size-change="handlePageSizeChange"
      >
        <template #cell-createTime="{ value, item }">
          {{ formatDateTime(value || item?.createTime || item?.create_time) }}
        </template>
        <template #cell-alertTitle="{ item }">
          <div class="flex items-center gap-2">
            <button
              @click.stop="openItemDetailInNewWindow(item.id)"
              class="flex-shrink-0 text-gray-500 dark:text-gray-400 hover:text-primary transition-colors p-1"
              :title="$t('asm.list.openInNewWindow') || '在新窗口打开'"
            >
              <span class="material-symbols-outlined text-base">open_in_new</span>
            </button>
            <a
              @click="openItemDetail(item.id)"
              :class="[
                'hover:underline cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap flex-1 font-medium',
                (item.handle_status?.toLowerCase() === 'closed' || item.status === 'closed') 
                  ? 'text-gray-500 dark:text-gray-400' 
                  : 'text-primary'
              ]"
              :title="item.title"
            >
              {{ item.title }}
            </a>
          </div>
        </template>
        <template #cell-riskLevel="{ item }">
          <span
            :class="[
              'text-xs font-medium me-2 px-2.5 py-0.5 rounded-full inline-block',
              getRiskLevelClass(item.riskLevel)
            ]"
            :title="getRiskLevelDisplay(item.riskLevel)"
          >
            {{ getRiskLevelDisplay(item.riskLevel) }}
          </span>
        </template>
        <template #cell-status="{ item }">
          <span
            :class="[
              'inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium',
              getStatusClass(item.status)
            ]"
            :title="$t(`asm.list.${item.status}`)"
          >
            <span :class="['size-1.5 rounded-full', getStatusDotClass(item.status)]"></span>
            {{ $t(`asm.list.${item.status}`) }}
          </span>
        </template>
        <template #cell-actor="{ value, item }">
          <div class="flex justify-center w-full">
            <UserAvatar :name="value || item.is_auto_closed || '-'" />
          </div>
        </template>
      </DataTable>
    </section>

    <!-- ASM detail drawer -->
    <ASMDetail
      v-if="currentItemId"
      :alert-id="currentItemId"
      @close="closeItemDetail"
      @closed="handleItemClosed"
    />

    <!-- Create Vulnerability Dialog -->
    <CreateVulnerabilityDialog
      :visible="showCreateVulnerabilityDialog"
      :initial-data="createVulnerabilityInitialData"
      :alert-ids="selectedItems"
      workspace="asm"
      @close="closeCreateVulnerabilityDialog"
      @created="handleVulnerabilityCreated"
    />

    <!-- Create Alert Dialog -->
    <CreateAlertDialog
      :visible="showCreateAlertDialog"
      workspace="asm"
      @close="closeCreateAlertDialog"
      @created="handleAlertCreated"
    />

    <!-- AI Sidebar -->
    <AISidebar
      :visible="showAISidebar"
      @close="showAISidebar = false"
    />

    <!-- Batch delete dialog -->
    <div
      v-if="showBatchDeleteDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeBatchDeleteDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('asm.list.batchDeleteDialog.title') }}
          </h2>
          <button
            @click="closeBatchDeleteDialog"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('asm.list.batchDeleteDialog.confirmMessage', { count: selectedItems.length }) }}
          </p>
        </div>

        <!-- Confirmation input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            {{ $t('asm.list.batchDeleteDialog.confirmInputLabel') }}
          </label>
          <input
            v-model="deleteConfirmInput"
            @keydown.enter.prevent="handleBatchDelete"
            type="text"
            class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
            :placeholder="$t('asm.list.batchDeleteDialog.confirmInputPlaceholder')"
            autocomplete="off"
          />
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchDeleteDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchDelete"
            :disabled="!isDeleteConfirmValid || isBatchDeleting"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isBatchDeleting" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch close dialog -->
    <div
      v-if="showBatchCloseDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeBatchCloseDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('asm.list.batchCloseDialog.title') }}
          </h2>
          <button
            @click="closeBatchCloseDialog"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('asm.list.batchCloseDialog.confirmMessage', { count: selectedItems.length }) }}
          </p>
        </div>

        <!-- Conclusion category dropdown -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            {{ $t('asm.list.batchCloseDialog.conclusionCategory') }}
            <span class="text-red-500 ml-1">*</span>
          </label>
          <select
            v-model="closeConclusion.category"
            class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">{{ $t('asm.list.batchCloseDialog.selectCategory') }}</option>
            <option value="falsePositive">{{ $t('asm.list.batchCloseDialog.categories.falsePositive') }}</option>
            <option value="resolved">{{ $t('asm.list.batchCloseDialog.categories.resolved') }}</option>
            <option value="repeated">{{ $t('asm.list.batchCloseDialog.categories.repeated') }}</option>
            <option value="other">{{ $t('asm.list.batchCloseDialog.categories.other') }}</option>
          </select>
        </div>

        <!-- Investigation conclusion input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            {{ $t('asm.list.batchCloseDialog.conclusion') }}
          </label>
          <div class="relative">
            <textarea
              v-model="closeConclusion.notes"
              rows="4"
              class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              :placeholder="$t('asm.list.batchCloseDialog.conclusionPlaceholder')"
              @focus="handleCloseNotesFocus"
              @click="handleCloseNotesClick"
              @blur="handleCloseNotesBlur"
            ></textarea>
            <div
              v-if="showRecentCloseComments && recentCloseComments.length"
              class="absolute left-0 right-0 top-full mt-2 bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-[#324867] rounded-md shadow-lg z-10 max-h-48 overflow-y-auto"
            >
              <p
                v-for="(comment, index) in recentCloseComments"
                :key="index"
                class="px-4 py-2 text-sm text-gray-900 dark:text-white border-b border-gray-200 dark:border-[#324867]/40 last:border-b-0 cursor-pointer hover:bg-gray-100 dark:hover:bg-[#22324a]"
                @mousedown.prevent="handleRecentCommentSelect(comment)"
              >
                {{ comment }}
              </p>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchCloseDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchClose"
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim() || isBatchClosing"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isBatchClosing" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { getASMItems, batchCloseASMItems, deleteASMItems } from '@/api/asm'
import ASMDetail from '@/components/asm/ASMDetail.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import AISidebar from '@/components/common/AISidebar.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import CreateAlertDialog from '@/components/alerts/CreateAlertDialog.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { useRecentCloseCommentSuggestions } from '@/composables/useRecentCloseCommentSuggestions'

const { t } = useI18n()
const toast = useToast()

const columns = computed(() => [
  { key: 'createTime', label: t('asm.list.createTime') },
  { key: 'alertTitle', label: t('asm.list.alertTitle') },
  { key: 'riskLevel', label: t('asm.list.riskLevel') },
  { key: 'status', label: t('asm.list.status') },
  { key: 'actor', label: t('asm.list.actor') }
])

const defaultWidths = {
  createTime: 200,
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  actor: 50
}

const items = ref([])
const loadingItems = ref(false)
const isRefreshing = ref(false)
const dataTableRef = ref(null)

const getStoredSearchKeywords = () => {
  try {
    const stored = localStorage.getItem('asm-searchKeywords')
    if (stored) {
      const parsed = JSON.parse(stored)
      // 兼容旧格式：字符串数组
      if (Array.isArray(parsed)) {
        if (parsed.length > 0 && typeof parsed[0] === 'string') {
          // 旧格式：转换为新格式
          return parsed.map(kw => ({ field: 'title', value: kw }))
        } else if (parsed.length === 0 || (parsed[0] && typeof parsed[0] === 'object' && parsed[0].field && parsed[0].value)) {
          // 新格式：对象数组
          return parsed
        }
      }
    }
  } catch (error) {
    console.warn('Failed to read search keywords from localStorage:', error)
  }
  return []
}

const searchKeywords = ref(getStoredSearchKeywords())
const currentSearchInput = ref('')
const currentField = ref('')
const showFieldMenu = ref(false)
const searchInputRef = ref(null)
const searchContainerRef = ref(null)

const searchFields = computed(() => [
  { value: 'title', label: t('asm.list.alertTitle'), icon: 'title' },
  { value: 'id', label: t('asm.list.alertId'), icon: 'tag' },
  { value: 'creator', label: t('asm.list.owner'), icon: 'person' },
  { value: 'actor', label: t('asm.list.actor'), icon: 'person_search' }
])

const getFieldLabel = (field) => {
  const fieldObj = searchFields.value.find(f => f.value === field)
  return fieldObj ? fieldObj.label : field
}

// Computed property to display field prefix in input
const displaySearchInput = computed({
  get() {
    if (currentField.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      return prefix + currentSearchInput.value
    }
    return currentSearchInput.value
  },
  set(value) {
    if (currentField.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      if (value.startsWith(prefix)) {
        currentSearchInput.value = value.slice(prefix.length)
      } else {
        // If user deleted the prefix, clear the field
        currentField.value = ''
        currentSearchInput.value = value
      }
    } else {
      currentSearchInput.value = value
    }
  }
})

const getSearchPlaceholder = () => {
  // Only show placeholder when no field is selected
  if (!currentField.value) {
    return searchKeywords.value.length === 0 ? (t('asm.list.searchPlaceholder') || '点击选择搜索字段...') : ''
  }
  return ''
}

const getStoredStatusFilter = () => {
  try {
    const stored = localStorage.getItem('asm-status-filter')
    if (stored && ['all', 'open', 'block', 'closed'].includes(stored)) {
      return stored
    }
  } catch (error) {
    console.warn('Failed to read status filter from localStorage:', error)
  }
  return 'all'
}
const statusFilter = ref(getStoredStatusFilter())

const selectedItems = ref([])
const currentPage = ref(1)

const getStoredPageSize = () => {
  try {
    const stored = localStorage.getItem('asm-pageSize')
    if (stored) {
      const size = Number(stored)
      if (size && [10, 20, 50, 100].includes(size)) {
        return size
      }
    }
  } catch (error) {
    console.warn('Failed to read page size from localStorage:', error)
  }
  return 10
}

const pageSize = ref(getStoredPageSize())
const total = ref(0)

const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('asm', 'last24Hours')
const showBatchCloseDialog = ref(false)
const isBatchClosing = ref(false)
const closeConclusion = ref({
  category: 'falsePositive',
  notes: ''
})
const {
  recentComments: recentCloseComments,
  showDropdown: showRecentCloseComments,
  refresh: refreshRecentCloseComments,
  persist: persistRecentCloseComment,
  handleFocus: handleCloseNotesFocus,
  handleClick: handleCloseNotesClick,
  handleBlur: handleCloseNotesBlur,
  handleSelect: applyRecentCloseComment,
  hideDropdown: hideRecentCloseCommentsDropdown
} = useRecentCloseCommentSuggestions({
  onApply: (comment) => {
    closeConclusion.value.notes = comment
  }
})
const handleRecentCommentSelect = (comment) => {
  applyRecentCloseComment(comment)
}
const showMoreMenu = ref(false)
const showBatchDeleteDialog = ref(false)
const deleteConfirmInput = ref('')
const isBatchDeleting = ref(false)
const showCreateVulnerabilityDialog = ref(false)
const createVulnerabilityInitialData = ref(null)
const showCreateAlertDialog = ref(false)
const showAISidebar = ref(false)

const computeSelectedRange = () => {
  if (selectedTimeRange.value === 'customRange' && customTimeRange.value && customTimeRange.value.length === 2) {
    return {
      start: new Date(customTimeRange.value[0]),
      end: new Date(customTimeRange.value[1])
    }
  }

  const end = new Date()
  const start = new Date(end)

  switch (selectedTimeRange.value) {
    case 'last3Days':
      start.setDate(start.getDate() - 3)
      break
    case 'last7Days':
      start.setDate(start.getDate() - 7)
      break
    case 'last30Days':
      start.setDate(start.getDate() - 30)
      break
    case 'last3Months':
      start.setMonth(start.getMonth() - 3)
      break
    default:
      start.setHours(start.getHours() - 24)
      break
  }

  return { start, end }
}

const loadItems = async () => {
  loadingItems.value = true
  try {
    const params = {
      searchKeywords: searchKeywords.value,
      status: statusFilter.value,
      page: currentPage.value,
      pageSize: pageSize.value
    }
    
    const range = computeSelectedRange()
    if (range) {
      params.startTime = range.start
      params.endTime = range.end
    }
    
    const response = await getASMItems(params)
    const rawItems = response.data || []

    items.value = rawItems.map(item => {
      return {
        ...item
      }
    })
    total.value = response.total
    
  } catch (error) {
    console.error('Failed to load ASM items:', error)
  } finally {
    loadingItems.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  return loadItems()
}

const reloadItemsFromFirstPage = () => {
  if (currentPage.value === 1) {
    return loadItems()
  }
  return handlePageChange(1)
}

const handleRefresh = async () => {
  if (isRefreshing.value) return
  
  isRefreshing.value = true
  try {
    await loadItems()
  } catch (error) {
    console.error('Failed to refresh:', error)
  } finally {
    isRefreshing.value = false
  }
}

const saveSearchKeywords = () => {
  try {
    localStorage.setItem('asm-searchKeywords', JSON.stringify(searchKeywords.value))
  } catch (error) {
    console.warn('Failed to save search keywords to localStorage:', error)
  }
}

const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword) {
    // If no field selected, default to 'title'
    const field = currentField.value || 'title'
    
    // Check if this exact field:value combination already exists
    const exists = searchKeywords.value.some(
      k => k.field === field && k.value === keyword
    )
    
    if (!exists) {
      searchKeywords.value.push({ field, value: keyword })
      currentSearchInput.value = ''
      currentField.value = ''
      showFieldMenu.value = false
      saveSearchKeywords()
      reloadItemsFromFirstPage()
    }
  }
}

const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  saveSearchKeywords()
  reloadItemsFromFirstPage()
}

const handleKeywordDeleteKey = (event) => {
  if (event.key === 'Backspace') {
    if (!currentSearchInput.value && searchKeywords.value.length > 0) {
      event.preventDefault()
      removeKeyword(searchKeywords.value.length - 1)
    } else if (!currentSearchInput.value && currentField.value) {
      event.preventDefault()
      currentField.value = ''
    } else if (currentField.value && currentSearchInput.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      const cursorPos = event.target.selectionStart || 0
      if (cursorPos <= prefix.length) {
        event.preventDefault()
        currentField.value = ''
        currentSearchInput.value = ''
      }
    }
  }
}

const handleSearchBlur = () => {
  setTimeout(() => {
    if (!currentField.value && !currentSearchInput.value) {
      showFieldMenu.value = false
    }
  }, 200)
}

const selectField = (field) => {
  currentField.value = field
  currentSearchInput.value = ''
  showFieldMenu.value = false
  // Focus the input after selecting field
  nextTick(() => {
    if (searchInputRef.value) {
      searchInputRef.value.focus()
      // Set cursor position after the prefix
      const fieldObj = searchFields.value.find(f => f.value === field)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${field}: `
      const input = searchInputRef.value
      if (input.setSelectionRange) {
        input.setSelectionRange(prefix.length, prefix.length)
      }
    }
  })
}

const handleSearchContainerClick = () => {
  if (currentField.value) {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
    return
  }
  showFieldMenu.value = true
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

const handleFilter = () => {
  try {
    localStorage.setItem('asm-status-filter', statusFilter.value)
  } catch (error) {
    console.warn('Failed to save status filter to localStorage:', error)
  }
  reloadItemsFromFirstPage()
}

const handlePageSizeChange = () => {
  pageSize.value = Number(pageSize.value)
  try {
    localStorage.setItem('asm-pageSize', String(pageSize.value))
  } catch (error) {
    console.warn('Failed to save page size to localStorage:', error)
  }
  handlePageChange(1)
}

const handleSelect = (items) => {
  selectedItems.value = items.map(item => item.id)
}

const handleSelectAll = (items) => {
  selectedItems.value = items.map(item => item.id)
}

const getRiskLevelClass = (level) => {
  // Map risk level to 1-5 scale
  const levelMap = {
    '1': 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-200',
    '2': 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    '3': 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
    '4': 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    '5': 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300',
    // Legacy mappings for backward compatibility
    fatal: 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-200',
    high: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    medium: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
    low: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    tips: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
  }
  return levelMap[level] || levelMap[String(level)] || levelMap['3']
}

const getRiskLevelDisplay = (level) => {
  // Map risk level to 1-5 display
  const levelMap = {
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    // Legacy mappings for backward compatibility
    fatal: '1',
    high: '2',
    medium: '3',
    low: '4',
    tips: '5'
  }
  return levelMap[level] || levelMap[String(level)] || '3'
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-primary/20 text-primary',
    block: 'bg-yellow-500/20 text-yellow-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || classes.open
}

const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-primary',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.open
}

const router = useRouter()
const route = useRoute()
const currentItemId = computed(() => route.params.id ?? null)

const openItemDetail = (itemId) => {
  router.push({ path: `/asm/${itemId}`, replace: true })
}

const openItemDetailInNewWindow = (itemId) => {
  const route = router.resolve({ path: `/asm/${itemId}` })
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const closeItemDetail = () => {
  router.push({ path: '/asm', replace: true })
}

const handleItemClosed = () => {
  loadItems()
  selectedItems.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const isWordWrap = computed(() => {
  return dataTableRef.value?.wordWrap?.value ?? true
})

const handleToggleWordWrap = () => {
  if (dataTableRef.value) {
    dataTableRef.value.toggleWordWrap()
    showMoreMenu.value = false
  }
}

const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.more-menu-dropdown')
  const button = event.target.closest('.more-menu-button')
  if (!dropdown && !button) {
    showMoreMenu.value = false
  }

  const searchContainerEl = searchContainerRef.value
  if (showFieldMenu.value && searchContainerEl && !searchContainerEl.contains(event.target)) {
    showFieldMenu.value = false
  }
}

const openBatchCloseDialog = () => {
  if (selectedItems.value.length === 0) {
    console.warn('No items selected')
    return
  }
  refreshRecentCloseComments()
  hideRecentCloseCommentsDropdown()
  showBatchCloseDialog.value = true
}

const closeBatchCloseDialog = () => {
  showBatchCloseDialog.value = false
  closeConclusion.value = {
    category: 'falsePositive',
    notes: ''
  }
  hideRecentCloseCommentsDropdown()
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim() || isBatchClosing.value) {
    return
  }

  if (selectedItems.value.length === 0) {
    toast.warn('请至少选择一条记录', '提示')
    return
  }

  try {
    isBatchClosing.value = true
    
    await batchCloseASMItems(
      selectedItems.value,
      closeConclusion.value.category,
      closeConclusion.value.notes.trim()
    )
    persistRecentCloseComment(closeConclusion.value.notes.trim())
    
    toast.success(
      t('asm.list.batchCloseSuccess', { count: selectedItems.value.length }) || 
      `成功关闭 ${selectedItems.value.length} 条记录`, 
      t('common.operationSuccess')
    )
    
    closeBatchCloseDialog()
    selectedItems.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    loadItems()
  } catch (error) {
    console.error('Failed to batch close items:', error)
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('asm.list.batchCloseError') || '批量关闭失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isBatchClosing.value = false
  }
}

// Delete confirmation validation
const isDeleteConfirmValid = computed(() => {
  return deleteConfirmInput.value.toLowerCase() === 'delete'
})

const openBatchDeleteDialog = () => {
  if (selectedItems.value.length === 0) {
    console.warn('No items selected')
    return
  }
  showBatchDeleteDialog.value = true
  deleteConfirmInput.value = ''
}

const closeBatchDeleteDialog = () => {
  showBatchDeleteDialog.value = false
  deleteConfirmInput.value = ''
}

const handleBatchDelete = async () => {
  if (!isDeleteConfirmValid.value || isBatchDeleting.value) {
    return
  }

  if (selectedItems.value.length === 0) {
    toast.warn('请至少选择一条记录', '提示')
    return
  }

  try {
    isBatchDeleting.value = true
    
    await deleteASMItems(selectedItems.value)
    
    toast.success(
      t('asm.list.batchDeleteDialog.deleteSuccess', { count: selectedItems.value.length }) || 
      `成功删除 ${selectedItems.value.length} 条记录`, 
      t('common.operationSuccess')
    )
    
    closeBatchDeleteDialog()
    selectedItems.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    loadItems()
  } catch (error) {
    console.error('Failed to delete items:', error)
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('asm.list.batchDeleteDialog.deleteError') || '删除失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isBatchDeleting.value = false
  }
}

const handleTimeRangeChange = async (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    await loadItems()
  }
}

const handleCustomRangeChange = async (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    await loadItems()
  }
}

const handleConvertToVulnerability = () => {
  if (selectedItems.value.length === 0) {
    console.warn('No items selected')
    return
  }
  openCreateVulnerabilityDialog()
  showMoreMenu.value = false
}

const handleCreateAlertFromMenu = () => {
  openCreateAlertDialog()
  showMoreMenu.value = false
}

const openCreateAlertDialog = () => {
  showCreateAlertDialog.value = true
}

const closeCreateAlertDialog = () => {
  showCreateAlertDialog.value = false
}

const handleAlertCreated = async () => {
  await loadItems()
}

const openCreateVulnerabilityDialog = () => {
  const selectedItemObjects = items.value.filter(item => selectedItems.value.includes(item.id))
  
  if (selectedItemObjects.length === 0) {
    console.warn('No items selected')
    return
  }
  
  const firstItem = selectedItemObjects[0]
  
  let itemDescription = ''
  if (firstItem.aiAnalysis?.description) {
    itemDescription = typeof firstItem.aiAnalysis.description === 'string' 
      ? firstItem.aiAnalysis.description 
      : JSON.stringify(firstItem.aiAnalysis.description)
  } else if (firstItem.description) {
    itemDescription = typeof firstItem.description === 'string' 
      ? firstItem.description 
      : JSON.stringify(firstItem.description)
  }
  
  createVulnerabilityInitialData.value = {
    title: firstItem.title || '',
    riskLevel: firstItem.riskLevel || 'medium',
    status: firstItem.status || 'open',
    owner: firstItem.owner || '',
    actor: firstItem.actor || '',
    description: itemDescription
  }
  
  showCreateVulnerabilityDialog.value = true
}

const closeCreateVulnerabilityDialog = () => {
  showCreateVulnerabilityDialog.value = false
  createVulnerabilityInitialData.value = null
}

const handleVulnerabilityCreated = () => {
  closeCreateVulnerabilityDialog()
  loadItems()
  selectedItems.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const handleOpenAISidebar = () => {
  showAISidebar.value = true
}

onMounted(async () => {
  await loadItems()
  document.addEventListener('click', handleClickOutside)
  refreshRecentCloseComments()
  // 监听Header发出的打开AI侧边栏事件
  window.addEventListener('open-ai-sidebar', handleOpenAISidebar)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  hideRecentCloseCommentsDropdown()
  // 移除事件监听
  window.removeEventListener('open-ai-sidebar', handleOpenAISidebar)
})
</script>

