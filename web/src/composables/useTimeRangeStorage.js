import { ref } from 'vue'

/**
 * 时间范围存储的 composable
 * @param {string} storageKey - localStorage 的存储键前缀
 * @param {string} defaultTimeRange - 默认时间范围，可选值: 'last24Hours', 'last3Days', 'last7Days', 'last30Days', 'last3Months', 'customRange'
 * @returns {Object} 包含 selectedTimeRange 和 customTimeRange 的响应式对象
 */
export function useTimeRangeStorage(storageKey, defaultTimeRange = 'last24Hours') {
  /**
   * 从 localStorage 读取保存的时间范围
   */
  const getStoredTimeRange = () => {
    if (!storageKey) return defaultTimeRange
    try {
      const stored = localStorage.getItem(`${storageKey}-timeRange`)
      if (stored && ['last24Hours', 'last3Days', 'last7Days', 'last30Days', 'last3Months', 'customRange'].includes(stored)) {
        return stored
      }
    } catch (error) {
      console.warn('Failed to read time range from localStorage:', error)
    }
    return defaultTimeRange
  }

  /**
   * 从 localStorage 读取保存的自定义时间范围
   */
  const getStoredCustomRange = () => {
    if (!storageKey) return null
    try {
      const stored = localStorage.getItem(`${storageKey}-customTimeRange`)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (Array.isArray(parsed) && parsed.length === 2) {
          return [new Date(parsed[0]), new Date(parsed[1])]
        }
      }
    } catch (error) {
      console.warn('Failed to read custom time range from localStorage:', error)
    }
    return null
  }

  const selectedTimeRange = ref(getStoredTimeRange())
  const customTimeRange = ref(getStoredCustomRange())

  return {
    selectedTimeRange,
    customTimeRange
  }
}

