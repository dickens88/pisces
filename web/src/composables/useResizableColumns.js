import { ref, onMounted, onUnmounted } from 'vue'

export function useResizableColumns(storageKey, defaultWidths = {}) {
  const columnWidths = ref({})
  const isResizing = ref(false)
  const resizingColumn = ref(null)
  const startX = ref(0)
  const startWidth = ref(0)
  const tableElement = ref(null)

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

  // 获取表格容器的可用宽度
  const getAvailableWidth = () => {
    const table = tableElement.value || document.querySelector(`[data-storage-key="${storageKey}"]`)
    if (!table) return window.innerWidth - 100
    
    const container = table.closest('.overflow-hidden') || 
                     table.closest('.overflow-x-auto') || 
                     table.parentElement
    return container ? container.clientWidth - 20 : window.innerWidth - 100
  }

  // 计算所有列的总宽度
  const getTotalWidth = (columns, selectable = false) => {
    const checkboxWidth = selectable ? 35 : 0
    if (!columns || columns.length === 0) return checkboxWidth
    
    const total = columns.reduce((sum, col) => {
      return sum + (columnWidths.value[col.key] || defaultWidths[col.key] || 150)
    }, 0)
    return total + checkboxWidth
  }

  // 限制列宽，确保总宽度不超过容器宽度
  const constrainWidths = (columns, selectable = false) => {
    if (!columns || columns.length === 0) return

    const availableWidth = getAvailableWidth()
    const checkboxWidth = selectable ? 35 : 0
    const availableForColumns = availableWidth - checkboxWidth
    
    const currentTotal = columns.reduce((sum, col) => {
      return sum + (columnWidths.value[col.key] || defaultWidths[col.key] || 150)
    }, 0)

    if (currentTotal > availableForColumns) {
      const scaleRatio = availableForColumns / currentTotal
      columns.forEach(col => {
        const currentWidth = columnWidths.value[col.key] || defaultWidths[col.key] || 150
        columnWidths.value[col.key] = Math.max(80, Math.floor(currentWidth * scaleRatio))
      })
    }
  }

  // 获取列宽
  const getColumnWidth = (columnKey) => {
    return columnWidths.value[columnKey] || defaultWidths[columnKey] || 150
  }

  // 开始调整列宽
  const startResize = (columnKey, event, columns = [], selectable = false) => {
    event.preventDefault()
    isResizing.value = true
    resizingColumn.value = columnKey
    startX.value = event.clientX
    startWidth.value = columnWidths.value[columnKey] || defaultWidths[columnKey] || 150

    // 存储列信息以便在调整时使用
    startResize.columns = columns
    startResize.selectable = selectable

    document.addEventListener('mousemove', handleResize)
    document.addEventListener('mouseup', stopResize)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  // 调整列宽
  const handleResize = (event) => {
    if (!isResizing.value || !resizingColumn.value) return

    const diff = event.clientX - startX.value
    const newWidth = Math.max(80, startWidth.value + diff)
    const columns = startResize.columns || []
    const selectable = startResize.selectable || false
    const checkboxWidth = selectable ? 35 : 0
    
    // 计算其他列的宽度
    const otherColumnsWidth = columns
      .filter(col => col.key !== resizingColumn.value)
      .reduce((sum, col) => sum + (columnWidths.value[col.key] || defaultWidths[col.key] || 150), 0)
    
    const availableWidth = getAvailableWidth()
    const maxWidth = availableWidth - checkboxWidth - otherColumnsWidth
    
    columnWidths.value[resizingColumn.value] = Math.max(80, Math.min(newWidth, maxWidth))
  }

  // 停止调整列宽
  const stopResize = () => {
    if (isResizing.value) {
      isResizing.value = false
      saveColumnWidths()
      resizingColumn.value = null
      startResize.columns = null
      startResize.selectable = false
      document.removeEventListener('mousemove', handleResize)
      document.removeEventListener('mouseup', stopResize)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }

  // 设置表格元素引用
  const setTableElement = (element) => {
    tableElement.value = element
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
    startResize,
    constrainWidths,
    setTableElement
  }
}

