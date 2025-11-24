/**
 * 关闭告警/事件评论历史记录管理工具
 * 用于保存和读取最近5条关闭告警/事件的文本内容
 */

const STORAGE_KEY_ALERT = 'close_alert_comment_history'
const STORAGE_KEY_INCIDENT = 'close_incident_comment_history'
const MAX_HISTORY_COUNT = 5

/**
 * @brief 获取存储键
 * @param {string} type - 类型：'alert' 或 'incident'
 * @returns {string} 存储键
 */
const getStorageKey = (type) => {
  return type === 'alert' ? STORAGE_KEY_ALERT : STORAGE_KEY_INCIDENT
}

/**
 * @brief 保存评论到历史记录
 * @param {string} comment - 评论内容
 * @param {string} type - 类型：'alert' 或 'incident'，默认为 'incident'
 */
export const saveCloseComment = (comment, type = 'incident') => {
  if (!comment || !comment.trim()) {
    return
  }

  try {
    const storageKey = getStorageKey(type)
    // 获取现有历史记录
    const existingHistory = getCloseCommentHistory(type)
    
    // 移除重复项（如果新评论已存在，先移除它）
    const filteredHistory = existingHistory.filter(item => item !== comment.trim())
    
    // 将新评论添加到最前面
    const newHistory = [comment.trim(), ...filteredHistory]
    
    // 只保留最近5条
    const finalHistory = newHistory.slice(0, MAX_HISTORY_COUNT)
    
    // 保存到 localStorage
    localStorage.setItem(storageKey, JSON.stringify(finalHistory))
  } catch (error) {
    console.error('Failed to save close comment history:', error)
  }
}

/**
 * @brief 获取评论历史记录
 * @param {string} type - 类型：'alert' 或 'incident'，默认为 'incident'
 * @returns {string[]} 历史记录数组，最多5条
 */
export const getCloseCommentHistory = (type = 'incident') => {
  try {
    const storageKey = getStorageKey(type)
    const stored = localStorage.getItem(storageKey)
    if (!stored) {
      return []
    }
    
    const history = JSON.parse(stored)
    if (!Array.isArray(history)) {
      return []
    }
    
    // 过滤掉空值，只保留字符串
    return history.filter(item => typeof item === 'string' && item.trim())
  } catch (error) {
    console.error('Failed to get close comment history:', error)
    return []
  }
}

/**
 * @brief 清空评论历史记录
 * @param {string} type - 类型：'alert' 或 'incident'，默认为 'incident'
 */
export const clearCloseCommentHistory = (type = 'incident') => {
  try {
    const storageKey = getStorageKey(type)
    localStorage.removeItem(storageKey)
  } catch (error) {
    console.error('Failed to clear close comment history:', error)
  }
}

