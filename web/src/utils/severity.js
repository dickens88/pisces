/**
 * Severity level utility functions
 * Used to convert severity text to numeric display values
 */

/**
 * @brief 将漏洞等级文字转换为数字（用于页面展示）
 * @param {string} severity - 漏洞等级文字（Fatal/Critical/High/Medium/Low/Tips）
 * @returns {number} 对应的数字等级，无效值返回 null
 * 
 * 映射关系：
 * - Fatal/Critical: 1
 * - High: 2
 * - Medium: 3
 * - Low: 4
 * - Tips: 5
 * 
 * @example
 * severityToNumber('Fatal') // 1
 * severityToNumber('High') // 2
 * severityToNumber('Medium') // 3
 * severityToNumber('Low') // 4
 * severityToNumber('Tips') // 5
 */
export const severityToNumber = (severity) => {
  if (!severity) {
    return null
  }
  
  const severityLower = String(severity).toLowerCase().trim()
  
  const severityMap = {
    'fatal': 1,
    'critical': 1, // Critical 也映射到 1（兼容性）
    'high': 2,
    'medium': 3,
    'low': 4,
    'tips': 5
  }
  
  return severityMap[severityLower] || null
}

/**
 * @brief 将数字等级转换为文字（用于API提交）
 * @param {number} level - 数字等级（1-5）
 * @returns {string} 对应的文字等级
 * 
 * @example
 * numberToSeverity(1) // 'Fatal'
 * numberToSeverity(2) // 'High'
 */
export const numberToSeverity = (level) => {
  if (typeof level !== 'number' || level < 1 || level > 5) {
    return null
  }
  
  const levelMap = {
    1: 'Fatal',
    2: 'High',
    3: 'Medium',
    4: 'Low',
    5: 'Tips'
  }
  
  return levelMap[level] || null
}

