/**
 * Date time formatting utility functions
 * Used to convert various date time formats to local timezone yyyy-MM-dd HH:mm:ss format
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
  // Handle empty values, undefined, null, empty strings
  if (!dateString || dateString === '' || dateString === 'null' || dateString === 'undefined') {
    return '-'
  }
  
  // If already a Date object, use directly
  let date
  if (dateString instanceof Date) {
    date = dateString
  } else if (typeof dateString === 'number') {
    // Handle timestamp (milliseconds or seconds)
    date = new Date(dateString > 1e10 ? dateString : dateString * 1000)
  } else {
    // Try to parse string
    try {
      let dateStr = String(dateString).trim()
      
      // Handle special format: 2025-11-11T20:37:57.202Z+0000
      // Remove trailing +0000 or +00:00, as Z already represents UTC
      dateStr = dateStr.replace(/Z\+0{4}$/, 'Z') // Remove Z+0000
      dateStr = dateStr.replace(/Z\+00:00$/, 'Z') // Remove Z+00:00
      
      // Try to parse
      date = new Date(dateStr)
      
      // If still invalid, try removing Z and adding timezone info
      if (isNaN(date.getTime()) && dateStr.includes('T')) {
        // Try parsing as UTC time
        dateStr = dateStr.replace(/Z$/, '') + 'Z'
        date = new Date(dateStr)
      }
      
      // If parsing fails, try other formats
      if (isNaN(date.getTime())) {
        // Try converting "YYYY-MM-DD HH:mm:ss" to ISO format
        const match = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})(?:\s+UTC)?$/)
        if (match) {
          // Parse using local timezone
          date = new Date(
            parseInt(match[1]), 
            parseInt(match[2]) - 1, 
            parseInt(match[3]), 
            parseInt(match[4]), 
            parseInt(match[5]), 
            parseInt(match[6])
          )
        } else {
          // Finally try direct parsing
          date = new Date(dateStr)
        }
      }
    } catch (error) {
      console.error('Failed to parse date:', error, 'Value:', dateString)
      return '-'
    }
  }
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    console.warn('Invalid date value:', dateString, 'Parsed as:', date)
    return '-'
  }
  
  // Format date time to yyyy-MM-dd HH:mm:ss using browser local timezone
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

