import { ref, onMounted, onUnmounted } from 'vue'

export function useResizableColumns(storageKey, defaultWidths = {}) {
  const columnWidths = ref({})
  const isResizing = ref(false)
  const resizingColumn = ref(null)
  const startX = ref(0)
  const startWidth = ref(0)

  // 从localStorage加载列宽
  const loadColumnWidths = () => {
    try {
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        columnWidths.value = { ...defaultWidths, ...JSON.parse(saved) }
      } else {
        columnWidths.value = { ...defaultWidths }
      }
    } catch (error) {
      console.error('Failed to load column widths:', error)
      columnWidths.value = { ...defaultWidths }
    }
  }

  // 保存列宽到localStorage
  const saveColumnWidths = () => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(columnWidths.value))
    } catch (error) {
      console.error('Failed to save column widths:', error)
    }
  }

  // 获取列宽
  const getColumnWidth = (columnKey) => {
    return columnWidths.value[columnKey] || defaultWidths[columnKey] || 'auto'
  }

  // 开始调整列宽
  const startResize = (columnKey, event) => {
    event.preventDefault()
    isResizing.value = true
    resizingColumn.value = columnKey
    startX.value = event.clientX
    startWidth.value = columnWidths.value[columnKey] || defaultWidths[columnKey] || 150

    document.addEventListener('mousemove', handleResize)
    document.addEventListener('mouseup', stopResize)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  // 调整列宽
  const handleResize = (event) => {
    if (!isResizing.value || !resizingColumn.value) return

    const diff = event.clientX - startX.value
    const newWidth = Math.max(80, startWidth.value + diff) // 最小宽度80px

    columnWidths.value[resizingColumn.value] = newWidth
  }

  // 停止调整列宽
  const stopResize = () => {
    if (isResizing.value) {
      isResizing.value = false
      saveColumnWidths()
      resizingColumn.value = null
      document.removeEventListener('mousemove', handleResize)
      document.removeEventListener('mouseup', stopResize)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }

  onMounted(() => {
    loadColumnWidths()
  })

  onUnmounted(() => {
    stopResize()
  })

  return {
    columnWidths,
    isResizing,
    getColumnWidth,
    startResize
  }
}

