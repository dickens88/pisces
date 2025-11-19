/**
 * Date time formatting utility functions
 * Used to convert various date time formats to local timezone yyyy-MM-dd HH:mm:ss format
 */

const ISO_OFFSET_REGEX = /([+-]\d{2})(\d{2})$/
const ISO_WITHOUT_TZ_REGEX = /T\d{2}:\d{2}:\d{2}/
const SPACE_SEPARATED_REGEX = /^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(?:\s+UTC)?$/

const normalizeDateString = (raw) => {
  if (!raw) return null
  let dateStr = String(raw).trim()
  if (!dateStr || dateStr === 'null' || dateStr === 'undefined') {
    return null
  }

  // Remove redundant timezone parts like Z+0000
  dateStr = dateStr.replace(/Z\+0{4}$/i, 'Z')
  dateStr = dateStr.replace(/Z\+00:00$/i, 'Z')

  // Convert +0800 to +08:00 for Date parsing compatibility
  if (ISO_OFFSET_REGEX.test(dateStr)) {
    dateStr = dateStr.replace(ISO_OFFSET_REGEX, (_, h, m) => `${h}:${m}`)
  }

  // Convert space separated format to ISO
  const spaceMatch = dateStr.match(SPACE_SEPARATED_REGEX)
  if (spaceMatch) {
    const [, year, month, day, hour, minute, second, micro] = spaceMatch
    const fractional = micro ? `.${micro.padEnd(3, '0').slice(0, 3)}` : ''
    dateStr = `${year}-${month}-${day}T${hour}:${minute}:${second}${fractional}Z`
    return dateStr
  }

  // Add 'Z' if there is time but no timezone suffix
  if (ISO_WITHOUT_TZ_REGEX.test(dateStr) && !/[Zz]|[+-]\d{2}:\d{2}$/.test(dateStr)) {
    dateStr += 'Z'
  }

  return dateStr
}

/**
 * @brief 将各种输入值解析为 Date 对象
 * @param {string|Date|number} value - 输入的时间值
 * @returns {Date|null} 解析后的 Date 对象或 null
 */
export const parseToDate = (value) => {
  if (value instanceof Date) {
    return new Date(value.getTime())
  }

  if (typeof value === 'number') {
    const milliseconds = value > 1e10 ? value : value * 1000
    const date = new Date(milliseconds)
    return isNaN(date.getTime()) ? null : date
  }

  const normalized = normalizeDateString(value)
  if (!normalized) {
    return null
  }

  const date = new Date(normalized)
  if (!isNaN(date.getTime())) {
    return date
  }

  // Fallback: try native parsing without normalization
  try {
    const fallbackDate = new Date(value)
    return isNaN(fallbackDate.getTime()) ? null : fallbackDate
  } catch (error) {
    console.error('Failed to parse date:', error, 'Value:', value)
    return null
  }
}

/**
 * @brief 格式化持续时间（毫秒）为易读字符串
 * @param {number} milliseconds - 持续时间（毫秒）
 * @returns {string} 例如 '2d 4h 15m'
 */
export const formatDuration = (milliseconds) => {
  if (typeof milliseconds !== 'number' || Number.isNaN(milliseconds) || milliseconds <= 0) {
    return '0s'
  }

  const totalSeconds = Math.floor(milliseconds / 1000)
  const days = Math.floor(totalSeconds / 86400)
  const hours = Math.floor((totalSeconds % 86400) / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  const parts = []
  if (days) parts.push(`${days}d`)
  if (hours) parts.push(`${hours}h`)
  if (minutes) parts.push(`${minutes}m`)
  if (!parts.length || (days === 0 && hours === 0 && minutes === 0)) {
    parts.push(`${seconds}s`)
  }

  return parts.join(' ')
}

/**
 * @brief 计算 TTR（响应时间）。Open 告警：当前时间 - 创建时间；Closed 告警：关闭时间 - 创建时间
 * @param {string|Date|number} createTime - 创建时间
 * @param {string|Date|number} closeTime - 关闭时间
 * @param {string} status - 告警状态
 * @returns {string} 格式化后的响应时间
 */
export const calculateTTR = (createTime, closeTime, status) => {
  const start = parseToDate(createTime)
  if (!start) {
    return '-'
  }

  const normalizedStatus = (status || '').toLowerCase()
  let end = null

  if (normalizedStatus === 'closed') {
    end = parseToDate(closeTime)
  }

  if (!end) {
    end = new Date()
  }

  const diff = end.getTime() - start.getTime()
  if (diff <= 0) {
    return '0s'
  }

  return formatDuration(diff)
}

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
  const date = parseToDate(dateString)
  if (!date) {
    return '-'
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * @brief 将日期格式化为后端期望的格式：YYYY-MM-DDTHH:mm:ssZ+HHmm
 * @param {string|Date|number} value - 日期字符串、Date对象或时间戳
 * @returns {string|null} 格式化后的日期时间字符串，无法解析时返回 null
 */
export const formatDateTimeWithOffset = (value) => {
  const date = parseToDate(value)
  if (!date) {
    return null
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  const milliseconds = String(date.getMilliseconds()).padStart(3, '0')

  const offsetMinutes = -date.getTimezoneOffset()
  const sign = offsetMinutes >= 0 ? '+' : '-'
  const absOffset = Math.abs(offsetMinutes)
  const offsetHours = String(Math.floor(absOffset / 60)).padStart(2, '0')
  const offsetMins = String(absOffset % 60).padStart(2, '0')

  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}Z${sign}${offsetHours}${offsetMins}`
}

/**
 * @brief 格式化日期为 yyyy-MM-dd 格式（浏览器时区）
 * @param {string|Date|number} dateString - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的日期字符串，无效日期返回 '-'
 */
export const formatDate = (dateString) => {
  const date = parseToDate(dateString)
  if (!date) {
    return '-'
  }
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * @brief 格式化时间为 HH:mm:ss 格式（浏览器时区）
 * @param {string|Date|number} dateString - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的时间字符串，无效日期返回 '-'
 */
export const formatTime = (dateString) => {
  const date = parseToDate(dateString)
  if (!date) {
    return '-'
  }
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

