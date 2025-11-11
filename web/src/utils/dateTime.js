/**
 * 日期时间格式化工具函数
 * 用于将各种日期时间格式转换为本地时区的 yyyy-MM-dd HH:mm:ss 格式
 */

/**
 * @brief 格式化日期时间为 yyyy-MM-dd HH:mm:ss 格式（浏览器时区）
 * @param {string|Date|number} dateString - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的日期时间字符串，无效日期返回 '-'
 * 
 * @example
 * formatDateTime('2025-11-11T20:37:57.202Z+0000') // '2025-11-12 04:37:57' (UTC+8)
 * formatDateTime(new Date()) // '2025-11-11 20:37:57'
 * formatDateTime(1699723077202) // '2025-11-11 20:37:57'
 * formatDateTime(null) // '-'
 */
export const formatDateTime = (dateString) => {
  // 处理空值、undefined、null、空字符串
  if (!dateString || dateString === '' || dateString === 'null' || dateString === 'undefined') {
    return '-'
  }
  
  // 如果已经是Date对象，直接使用
  let date
  if (dateString instanceof Date) {
    date = dateString
  } else if (typeof dateString === 'number') {
    // 处理时间戳（毫秒或秒）
    date = new Date(dateString > 1e10 ? dateString : dateString * 1000)
  } else {
    // 尝试解析字符串
    try {
      let dateStr = String(dateString).trim()
      
      // 处理特殊格式：2025-11-11T20:37:57.202Z+0000
      // 移除末尾的 +0000 或 +00:00，因为 Z 已经表示 UTC
      dateStr = dateStr.replace(/Z\+0{4}$/, 'Z') // 移除 Z+0000
      dateStr = dateStr.replace(/Z\+00:00$/, 'Z') // 移除 Z+00:00
      
      // 尝试解析
      date = new Date(dateStr)
      
      // 如果仍然无效，尝试移除 Z 并添加时区信息
      if (isNaN(date.getTime()) && dateStr.includes('T')) {
        // 尝试作为 UTC 时间解析
        dateStr = dateStr.replace(/Z$/, '') + 'Z'
        date = new Date(dateStr)
      }
      
      // 如果解析失败，尝试其他格式
      if (isNaN(date.getTime())) {
        // 尝试将 "YYYY-MM-DD HH:mm:ss" 转换为 ISO 格式
        const match = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})(?:\s+UTC)?$/)
        if (match) {
          // 使用本地时区解析
          date = new Date(
            parseInt(match[1]), 
            parseInt(match[2]) - 1, 
            parseInt(match[3]), 
            parseInt(match[4]), 
            parseInt(match[5]), 
            parseInt(match[6])
          )
        } else {
          // 最后尝试直接解析
          date = new Date(dateStr)
        }
      }
    } catch (error) {
      console.error('Failed to parse date:', error, 'Value:', dateString)
      return '-'
    }
  }
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    console.warn('Invalid date value:', dateString, 'Parsed as:', date)
    return '-'
  }
  
  // 使用浏览器本地时区格式化日期时间为 yyyy-MM-dd HH:mm:ss
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * @brief 格式化日期为 yyyy-MM-dd 格式（浏览器时区）
 * @param {string|Date|number} dateString - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的日期字符串，无效日期返回 '-'
 */
export const formatDate = (dateString) => {
  const dateTimeStr = formatDateTime(dateString)
  if (dateTimeStr === '-') {
    return '-'
  }
  return dateTimeStr.split(' ')[0]
}

/**
 * @brief 格式化时间为 HH:mm:ss 格式（浏览器时区）
 * @param {string|Date|number} dateString - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的时间字符串，无效日期返回 '-'
 */
export const formatTime = (dateString) => {
  const dateTimeStr = formatDateTime(dateString)
  if (dateTimeStr === '-') {
    return '-'
  }
  return dateTimeStr.split(' ')[1]
}

