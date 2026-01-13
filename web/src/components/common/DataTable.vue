<template>
  <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg overflow-hidden">
    <!-- Table -->
    <div class="overflow-hidden" :data-storage-key="storageKey">
      <table ref="tableRef" class="w-full text-sm text-left text-gray-700 dark:text-gray-300" style="table-layout: fixed; width: 100%;">
        <thead class="text-xs text-gray-900 dark:text-white uppercase bg-gray-50 dark:bg-[#1e293b]">
          <tr>
            <!-- Checkbox column -->
            <th
              v-if="selectable"
              class="p-2"
              scope="col"
              style="width: 35px; min-width: 35px; max-width: 35px;"
            >
              <div class="flex items-center justify-center">
                <input
                  :checked="selectAll"
                  @change="handleSelectAll"
                  class="w-4 h-4 text-primary bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-primary focus:ring-2"
                  type="checkbox"
                />
              </div>
            </th>
            <!-- Data columns -->
            <th
              v-for="(column, index) in columns"
              :key="column.key"
              :scope="'col'"
              :style="{ width: getColumnWidth(column.key) + 'px', minWidth: '80px' }"
              class="px-4 py-2 relative border-r border-gray-200 dark:border-[#324867]/50 overflow-hidden text-ellipsis whitespace-nowrap"
            >
              <div class="flex items-center overflow-hidden text-ellipsis whitespace-nowrap">
                <slot :name="`header-${column.key}`" :column="column">
                  {{ column.label }}
                </slot>
              </div>
              <!-- Column resize handle -->
              <div
                v-if="resizable && index < columns.length - 1"
                @mousedown="(e) => startResize(column.key, e, columns, selectable)"
                class="absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-primary/50 transition-colors z-10"
                style="touch-action: none;"
              ></div>
            </th>
          </tr>
        </thead>
        <tbody>
          <slot name="body" :items="items">
            <tr
              v-for="(item, rowIndex) in items"
              :key="getRowKey(item, rowIndex)"
              :class="rowClass"
              @click="handleRowClick(item, rowIndex)"
            >
              <!-- Checkbox column -->
              <td
                v-if="selectable"
                class="p-1"
                style="width: 35px; min-width: 35px; max-width: 35px;"
                @click.stop
              >
                <div class="flex items-center justify-center">
                  <input
                    :checked="isSelected(item)"
                    @change="handleItemSelect(item, $event.target.checked)"
                    class="w-4 h-4 text-primary bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-primary focus:ring-2"
                    type="checkbox"
                  />
                </div>
              </td>
              <!-- Data columns -->
              <td
                v-for="column in columns"
                :key="column.key"
                :class="[
                  'px-4 py-2 border-r border-gray-200 dark:border-[#324867]/30',
                  wordWrap ? 'cell-content-wrap' : 'cell-content-nowrap'
                ]"
              >
                <slot :name="`cell-${column.key}`" :item="item" :value="getCellValue(item, column.key)" :column="column">
                  {{ getCellValue(item, column.key) }}
                </slot>
              </td>
            </tr>
          </slot>
          <!-- Empty state -->
          <tr v-if="items.length === 0">
            <td :colspan="selectable ? columns.length + 1 : columns.length" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
              <slot name="empty">
                {{ emptyMessage }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <nav
      v-if="pagination"
      aria-label="Table navigation"
      class="flex items-center justify-between p-4"
    >
      <div class="flex items-center gap-4">
        <span class="text-sm font-normal text-gray-600 dark:text-gray-400">
          {{ $t('common.pagination.showing', {
            start: (currentPage - 1) * pageSize + 1,
            end: Math.min(currentPage * pageSize, total),
            total: total
          }) }}
        </span>
        <div v-if="showPageSizeSelector" class="flex items-center gap-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">{{ $t('common.pagination.itemsPerPage') }}</span>
          <div class="relative">
            <select
              :value="pageSize"
              @change="handlePageSizeChange"
              class="pl-3 pr-8 appearance-none block rounded-lg border border-gray-300 dark:border-[#324867] bg-gray-100 dark:bg-[#233348] h-8 text-gray-900 dark:text-white text-sm"
            >
              <option v-for="size in pageSizeOptions" :key="size" :value="size">
                {{ size }}
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 16px;">arrow_drop_down</span>
            </div>
          </div>
        </div>
      </div>
      <ul class="inline-flex -space-x-px text-sm h-8">
        <li>
          <button
            @click="handlePreviousPage"
            :disabled="currentPage === 1"
            class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] border border-gray-300 dark:border-gray-700 rounded-s-lg hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.pagination.previous') }}
          </button>
        </li>
        <template v-for="(item, index) in displayPages" :key="index">
          <li v-if="item.type === 'page'">
            <button
              @click="handlePageChange(item.value)"
              :class="[
                'flex items-center justify-center px-3 h-8 leading-tight border border-gray-300 dark:border-gray-700',
                currentPage === item.value
                  ? 'text-white bg-primary hover:bg-primary/90'
                  : 'text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
              ]"
            >
              {{ item.value }}
            </button>
          </li>
          <li v-else-if="item.type === 'ellipsis'" class="flex items-center justify-center px-2 h-8 text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] border border-gray-300 dark:border-gray-700">
            <span class="material-symbols-outlined" style="font-size: 18px;">more_horiz</span>
          </li>
        </template>
        <li>
          <button
            @click="handleNextPage"
            :disabled="currentPage === totalPages"
            class="flex items-center justify-center px-3 h-8 leading-tight text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-[#233348] border border-gray-300 dark:border-gray-700 rounded-e-lg hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.pagination.next') }}
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useResizableColumns } from '@/composables/useResizableColumns'

const props = defineProps({
  // Column configuration
  columns: {
    type: Array,
    required: true,
    validator: (value) => {
      return value.every(col => col.key && col.label)
    }
  },
  // Data
  items: {
    type: Array,
    default: () => []
  },
  // Whether selectable
  selectable: {
    type: Boolean,
    default: false
  },
  // Row key getter function
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  // Whether resizable
  resizable: {
    type: Boolean,
    default: true
  },
  // Column width storage key
  storageKey: {
    type: String,
    required: true
  },
  // Default column widths
  defaultWidths: {
    type: Object,
    default: () => ({})
  },
  // Pagination configuration
  pagination: {
    type: Boolean,
    default: true
  },
  // Current page
  currentPage: {
    type: Number,
    default: 1
  },
  // Items per page
  pageSize: {
    type: Number,
    default: 10
  },
  // Total count
  total: {
    type: Number,
    default: 0
  },
  // Whether to show page size selector
  showPageSizeSelector: {
    type: Boolean,
    default: true
  },
  // Page size options
  pageSizeOptions: {
    type: Array,
    default: () => [10, 20, 50, 100, 200]
  },
  // Empty state text
  emptyText: {
    type: String,
    default: ''
  },
  // Row style class
  rowClass: {
    type: String,
    default: 'border-b border-gray-200 dark:border-[#324867] hover:bg-gray-50 dark:hover:bg-white/5'
  }
})

const emit = defineEmits([
  'update:currentPage',
  'update:pageSize',
  'select',
  'select-all',
  'row-click',
  'page-change',
  'page-size-change'
])

const { t } = useI18n()
const emptyMessage = computed(() => props.emptyText || t('common.noData'))

// Use resizable columns composable
const { getColumnWidth, startResize, constrainWidths, setTableElement } = useResizableColumns(
  props.storageKey,
  props.defaultWidths
)

// Table element ref
const tableRef = ref(null)

// Constrain column widths
const applyConstraints = () => {
  if (tableRef.value) {
    setTableElement(tableRef.value)
    constrainWidths(props.columns, props.selectable)
  }
}

// Constrain on mount and when columns change
watch(() => props.columns, () => nextTick(applyConstraints), { immediate: true })

// Handle window resize
const handleResize = () => nextTick(applyConstraints)

onMounted(() => {
  nextTick(applyConstraints)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Word wrap state (default auto wrap)
const getInitialWordWrap = () => {
  const saved = localStorage.getItem(`datatable-wordwrap-${props.storageKey}`)
  return saved !== null ? saved === 'true' : true
}
const wordWrap = ref(getInitialWordWrap())

// Toggle word wrap state
const toggleWordWrap = () => {
  wordWrap.value = !wordWrap.value
  localStorage.setItem(`datatable-wordwrap-${props.storageKey}`, wordWrap.value.toString())
}

// Selected items
const selectedItems = ref([])

// Select all state
const selectAll = computed({
  get: () => {
    return props.items.length > 0 && selectedItems.value.length === props.items.length
  },
  set: (value) => {
    if (value) {
      selectedItems.value = [...props.items]
    } else {
      selectedItems.value = []
    }
    emit('select-all', selectedItems.value)
  }
})

// Total pages
const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

// Calculate page numbers array to display
const displayPages = computed(() => {
  const total = totalPages.value
  const current = props.currentPage
  const pages = []
  
  // If total pages <= 5, show all page numbers
  if (total <= 5) {
    for (let i = 1; i <= total; i++) {
      pages.push({ type: 'page', value: i })
    }
    return pages
  }
  
  // Always show first page
  pages.push({ type: 'page', value: 1 })
  
  // Calculate page numbers near current page
  let start = Math.max(2, current - 1)
  let end = Math.min(total - 1, current + 1)
  
  // If current page is near the beginning, show first few pages
  if (current <= 3) {
    start = 2
    end = Math.min(4, total - 1)
  }
  // If current page is near the end, show last few pages
  else if (current >= total - 2) {
    start = Math.max(2, total - 3)
    end = total - 1
  }
  
  // If start > 2, add ellipsis
  if (start > 2) {
    pages.push({ type: 'ellipsis' })
  }
  
  // Add page numbers near current page
  for (let i = start; i <= end; i++) {
    pages.push({ type: 'page', value: i })
  }
  
  // If end < total - 1, add ellipsis
  if (end < total - 1) {
    pages.push({ type: 'ellipsis' })
  }
  
  // Always show last page (if not first page)
  if (total > 1) {
    pages.push({ type: 'page', value: total })
  }
  
  return pages
})

// Get row key
const getRowKey = (item, index) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item, index)
  }
  return item[props.rowKey] || index
}

// Get cell value
const getCellValue = (item, key) => {
  const keys = key.split('.')
  let value = item
  for (const k of keys) {
    value = value?.[k]
  }
  return value ?? ''
}

// Check if item is selected
const isSelected = (item) => {
  const key = getRowKey(item)
  return selectedItems.value.some(selected => getRowKey(selected) === key)
}

// Handle select all
const handleSelectAll = (event) => {
  selectAll.value = event.target.checked
}

// Handle single item selection
const handleItemSelect = (item, checked) => {
  const key = getRowKey(item)
  if (checked) {
    if (!isSelected(item)) {
      selectedItems.value.push(item)
    }
  } else {
    selectedItems.value = selectedItems.value.filter(
      selected => getRowKey(selected) !== key
    )
  }
  emit('select', selectedItems.value)
}

// Handle row click
const handleRowClick = (item, index) => {
  emit('row-click', item, index)
}

// Handle page change
const handlePageChange = (page) => {
  emit('update:currentPage', page)
  emit('page-change', page)
}

// Handle previous page
const handlePreviousPage = () => {
  if (props.currentPage > 1) {
    handlePageChange(props.currentPage - 1)
  }
}

// Handle next page
const handleNextPage = () => {
  if (props.currentPage < totalPages.value) {
    handlePageChange(props.currentPage + 1)
  }
}

// Handle page size change
const handlePageSizeChange = (event) => {
  const newPageSize = Number(event.target.value)
  emit('update:pageSize', newPageSize)
  emit('page-size-change', newPageSize)
  // Reset to first page
  handlePageChange(1)
}

// Watch items changes, update selection state
watch(() => props.items, (newItems) => {
  // Remove selected items not in current list
  selectedItems.value = selectedItems.value.filter(selected => {
    return newItems.some(item => getRowKey(item) === getRowKey(selected))
  })
}, { deep: true })

// Expose methods to parent component
defineExpose({
  getSelectedItems: () => selectedItems.value,
  clearSelection: () => {
    selectedItems.value = []
    emit('select', [])
  },
  selectAll: () => {
    selectedItems.value = [...props.items]
    emit('select-all', selectedItems.value)
  },
  setSelectedItems: (items, silent = false) => {
    selectedItems.value = items || []
    if (!silent) {
      emit('select', selectedItems.value)
    }
  },
  toggleWordWrap,
  wordWrap,
  constrainColumns: () => nextTick(applyConstraints)
})
</script>

<style scoped>
/* Auto wrap mode */
.cell-content-wrap {
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  white-space: normal !important;
  word-break: break-word !important;
}

.cell-content-wrap * {
  white-space: normal !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
  max-width: 100% !important;
}

/* Single line display mode */
.cell-content-nowrap {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.cell-content-nowrap * {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  max-width: 100% !important;
}
</style>
