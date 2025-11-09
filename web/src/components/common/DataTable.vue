<template>
  <div class="bg-[#111822] border border-[#324867] rounded-lg overflow-hidden">
    <!-- 表格 -->
    <div class="overflow-x-auto">
      <table class="w-full text-sm text-left text-gray-300" style="table-layout: fixed;">
        <thead class="text-xs text-white uppercase bg-[#1e293b]">
          <tr>
            <!-- 复选框列 -->
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
                  class="w-4 h-4 text-primary bg-gray-700 border-gray-600 rounded focus:ring-primary focus:ring-2"
                  type="checkbox"
                />
              </div>
            </th>
            <!-- 数据列 -->
            <th
              v-for="(column, index) in columns"
              :key="column.key"
              :scope="'col'"
              :style="{ width: getColumnWidth(column.key) + 'px', minWidth: '80px' }"
              class="px-6 py-3 relative border-r border-[#324867]/50 overflow-hidden text-ellipsis whitespace-nowrap"
            >
              <div class="flex items-center overflow-hidden text-ellipsis whitespace-nowrap">
                <slot :name="`header-${column.key}`" :column="column">
                  {{ column.label }}
                </slot>
              </div>
              <!-- 调整列宽的手柄 -->
              <div
                v-if="resizable && index < columns.length - 1"
                @mousedown="startResize(column.key, $event)"
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
              <!-- 复选框列 -->
              <td
                v-if="selectable"
                class="p-2"
                style="width: 35px; min-width: 35px; max-width: 35px;"
                @click.stop
              >
                <div class="flex items-center justify-center">
                  <input
                    :checked="isSelected(item)"
                    @change="handleItemSelect(item, $event.target.checked)"
                    class="w-4 h-4 text-primary bg-gray-700 border-gray-600 rounded focus:ring-primary focus:ring-2"
                    type="checkbox"
                  />
                </div>
              </td>
              <!-- 数据列 -->
              <td
                v-for="column in columns"
                :key="column.key"
                class="px-6 py-4 border-r border-[#324867]/30 overflow-hidden text-ellipsis whitespace-nowrap"
                :title="getCellValue(item, column.key)"
              >
                <slot :name="`cell-${column.key}`" :item="item" :value="getCellValue(item, column.key)" :column="column">
                  {{ getCellValue(item, column.key) }}
                </slot>
              </td>
            </tr>
          </slot>
          <!-- 空状态 -->
          <tr v-if="items.length === 0">
            <td :colspan="selectable ? columns.length + 1 : columns.length" class="px-4 py-8 text-center text-gray-400">
              <slot name="empty">
                {{ emptyText }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <nav
      v-if="pagination"
      aria-label="Table navigation"
      class="flex items-center justify-between p-4"
    >
      <div class="flex items-center gap-4">
        <span class="text-sm font-normal text-gray-400">
          {{ $t('common.pagination.showing', {
            start: (currentPage - 1) * pageSize + 1,
            end: Math.min(currentPage * pageSize, total),
            total: total
          }) }}
        </span>
        <div v-if="showPageSizeSelector" class="flex items-center gap-2">
          <span class="text-sm text-gray-400">{{ $t('common.pagination.itemsPerPage') }}</span>
          <div class="relative">
            <select
              :value="pageSize"
              @change="handlePageSizeChange"
              class="pl-3 pr-8 appearance-none block rounded-lg border-0 bg-[#233348] h-8 text-white text-sm focus:ring-2 focus:ring-inset focus:ring-primary"
            >
              <option v-for="size in pageSizeOptions" :key="size" :value="size">
                {{ size }}
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
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
            class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-400 bg-[#233348] border border-gray-700 rounded-s-lg hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.pagination.previous') }}
          </button>
        </li>
        <li v-for="page in totalPages" :key="page">
          <button
            @click="handlePageChange(page)"
            :class="[
              'flex items-center justify-center px-3 h-8 leading-tight border border-gray-700',
              currentPage === page
                ? 'text-white bg-primary hover:bg-primary/90'
                : 'text-gray-400 bg-[#233348] hover:bg-gray-700 hover:text-white'
            ]"
          >
            {{ page }}
          </button>
        </li>
        <li>
          <button
            @click="handleNextPage"
            :disabled="currentPage === totalPages"
            class="flex items-center justify-center px-3 h-8 leading-tight text-gray-400 bg-[#233348] border border-gray-700 rounded-e-lg hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.pagination.next') }}
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useResizableColumns } from '@/composables/useResizableColumns'

const props = defineProps({
  // 列配置
  columns: {
    type: Array,
    required: true,
    validator: (value) => {
      return value.every(col => col.key && col.label)
    }
  },
  // 数据
  items: {
    type: Array,
    default: () => []
  },
  // 是否可选择
  selectable: {
    type: Boolean,
    default: false
  },
  // 行键获取函数
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  // 是否可调整列宽
  resizable: {
    type: Boolean,
    default: true
  },
  // 列宽存储键
  storageKey: {
    type: String,
    required: true
  },
  // 默认列宽
  defaultWidths: {
    type: Object,
    default: () => ({})
  },
  // 分页配置
  pagination: {
    type: Boolean,
    default: true
  },
  // 当前页
  currentPage: {
    type: Number,
    default: 1
  },
  // 每页显示条数
  pageSize: {
    type: Number,
    default: 10
  },
  // 总条数
  total: {
    type: Number,
    default: 0
  },
  // 是否显示每页显示条数选择器
  showPageSizeSelector: {
    type: Boolean,
    default: true
  },
  // 每页显示条数选项
  pageSizeOptions: {
    type: Array,
    default: () => [10, 20, 50, 100, 200]
  },
  // 空状态文本
  emptyText: {
    type: String,
    default: '暂无数据'
  },
  // 行样式类
  rowClass: {
    type: String,
    default: 'border-b border-[#324867] hover:bg-white/5'
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

// 使用可调整列宽的composable
const { getColumnWidth, startResize } = useResizableColumns(
  props.storageKey,
  props.defaultWidths
)

// 选中的项
const selectedItems = ref([])

// 全选状态
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

// 总页数
const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

// 获取行键
const getRowKey = (item, index) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item, index)
  }
  return item[props.rowKey] || index
}

// 获取单元格值
const getCellValue = (item, key) => {
  const keys = key.split('.')
  let value = item
  for (const k of keys) {
    value = value?.[k]
  }
  return value ?? ''
}

// 判断项是否被选中
const isSelected = (item) => {
  const key = getRowKey(item)
  return selectedItems.value.some(selected => getRowKey(selected) === key)
}

// 处理全选
const handleSelectAll = (event) => {
  selectAll.value = event.target.checked
}

// 处理单项选择
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

// 处理行点击
const handleRowClick = (item, index) => {
  emit('row-click', item, index)
}

// 处理页码变化
const handlePageChange = (page) => {
  emit('update:currentPage', page)
  emit('page-change', page)
}

// 处理上一页
const handlePreviousPage = () => {
  if (props.currentPage > 1) {
    handlePageChange(props.currentPage - 1)
  }
}

// 处理下一页
const handleNextPage = () => {
  if (props.currentPage < totalPages.value) {
    handlePageChange(props.currentPage + 1)
  }
}

// 处理每页显示条数变化
const handlePageSizeChange = (event) => {
  const newPageSize = Number(event.target.value)
  emit('update:pageSize', newPageSize)
  emit('page-size-change', newPageSize)
  // 重置到第一页
  handlePageChange(1)
}

// 监听 items 变化，更新选中状态
watch(() => props.items, (newItems) => {
  // 移除不在当前列表中的选中项
  selectedItems.value = selectedItems.value.filter(selected => {
    return newItems.some(item => getRowKey(item) === getRowKey(selected))
  })
}, { deep: true })

// 暴露方法给父组件
defineExpose({
  getSelectedItems: () => selectedItems.value,
  clearSelection: () => {
    selectedItems.value = []
    emit('select', [])
  },
  selectAll: () => {
    selectedItems.value = [...props.items]
    emit('select-all', selectedItems.value)
  }
})
</script>

