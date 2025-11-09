<template>
  <div class="w-full overflow-x-auto">
    <table class="w-full text-sm text-left" :class="tableClass">
      <thead :class="theadClass">
        <tr>
          <th
            v-for="(column, index) in columns"
            :key="column.key"
            :scope="'col'"
            :style="{ width: getColumnWidth(column.key) + 'px', minWidth: '80px' }"
            class="relative"
          >
            <div class="flex items-center">
              <slot :name="`header-${column.key}`" :column="column">
                {{ column.label }}
              </slot>
            </div>
            <!-- 调整列宽的手柄 -->
            <div
              v-if="index < columns.length - 1"
              @mousedown="startResize(column.key, $event)"
              class="absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-primary/50 transition-colors"
              style="touch-action: none;"
            ></div>
          </th>
        </tr>
      </thead>
      <tbody>
        <slot name="body"></slot>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { useResizableColumns } from '@/composables/useResizableColumns'

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  storageKey: {
    type: String,
    required: true
  },
  defaultWidths: {
    type: Object,
    default: () => ({})
  },
  tableClass: {
    type: String,
    default: ''
  },
  theadClass: {
    type: String,
    default: ''
  }
})

const { getColumnWidth, startResize } = useResizableColumns(
  props.storageKey,
  props.defaultWidths
)
</script>

