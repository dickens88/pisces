import service from './axios.js'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { calculateTTR, formatDateTimeWithOffset } from '@/utils/dateTime'

const API_SEVERITY_TO_CLIENT_MAP = {
  'Fatal': 'fatal',
  'High': 'high',
  'Medium': 'medium',
  'Low': 'low',
  'Tips': 'tips'
}

const CLIENT_SEVERITY_TO_API_MAP = {
  'fatal': 'Fatal',
  'high': 'High',
  'medium': 'Medium',
  'low': 'Low',
  'tips': 'Tips'
}

const API_STATUS_TO_CLIENT_MAP = {
  'Open': 'open',
  'Block': 'block',
  'Closed': 'closed'
}

const CLIENT_STATUS_TO_API_MAP = {
  'open': 'Open',
  'block': 'Block',
  'closed': 'Closed'
}

const CLOSE_REASON_CATEGORY_MAP = {
  'falsePositive': 'False detection',
  'resolved': 'Resolved',
  'repeated': 'Repeated',
  'other': 'Other'
}

/**
 * @brief 转换API返回的告警数据为前端期望的格式
 * @param {Object} apiAlert - API返回的告警对象
 * @returns {Object} 转换后的告警对象
 */
const transformAlertData = (apiAlert) => {
  const computedTtr = calculateTTR(
    apiAlert.create_time || apiAlert.createTime,
    apiAlert.close_time,
    apiAlert.handle_status
  )

  return {
    id: apiAlert.id,
    createTime: apiAlert.create_time || apiAlert.createTime,
    title: apiAlert.title,
    riskLevel: API_SEVERITY_TO_CLIENT_MAP[apiAlert.severity] || apiAlert.severity?.toLowerCase() || 'medium',
    status: API_STATUS_TO_CLIENT_MAP[apiAlert.handle_status] || apiAlert.handle_status?.toLowerCase() || 'open',
    owner: apiAlert.creator,
    actor: apiAlert.actor,
    // Keep original fields for detail page use
    severity: apiAlert.severity,
    handle_status: apiAlert.handle_status,
    update_time: apiAlert.update_time,
    close_time: apiAlert.close_time,
    arrive_time: apiAlert.arrive_time,
    labels: apiAlert.labels,
    close_reason: apiAlert.close_reason,
    is_auto_closed: apiAlert.is_auto_closed,
    close_comment: apiAlert.close_comment,
    creator: apiAlert.creator,
    responseTime: computedTtr,
    extend_properties: apiAlert.extend_properties,
    description: apiAlert.description
  }
}

/**
 * 统一格式化搜索关键字
 * 期望格式：[{ field: 'id'|'title'|'creator'|'actor', value: 'keyword' }]
 */
const normalizeSearchKeywords = (searchKeywords) => {
  if (!searchKeywords) return []
  if (!Array.isArray(searchKeywords)) return []
  
  // 兼容旧格式：字符串数组
  if (searchKeywords.length > 0 && typeof searchKeywords[0] === 'string') {
    return searchKeywords
      .filter(kw => kw && typeof kw === 'string')
      .map(kw => ({
        field: 'title',
        value: kw.trim()
      }))
      .filter(kw => kw.value !== '')
  }
  
  // 新格式：对象数组
  return searchKeywords
    .filter(kw => kw && typeof kw === 'object' && kw.field && kw.value)
    .map(kw => ({
      field: kw.field,
      value: typeof kw.value === 'string' ? kw.value.trim() : kw.value
    }))
    .filter(kw => kw.value !== '')
}

/**
 * @brief 构建查询条件
 * @param {Array<Object>|Array<string>} searchKeywords - 搜索关键字（支持对象数组：{field: 'id'|'title'|'creator'|'actor', value: 'keyword'} 或字符串数组（兼容旧格式））
 * @param {string} status - 状态过滤
 * @returns {Array} 条件数组，格式为 [{field_name: value}, ...]
 */
const buildConditions = (searchKeywords, status) => {
  const conditions = []
  
  // Add status condition
  if (status && status !== 'all') {
    conditions.push({
      'handle_status': CLIENT_STATUS_TO_API_MAP[status] || status
    })
  }
  
  // Add search keyword conditions
  // Note: According to API implementation, multiple keywords will use AND logic
  normalizeSearchKeywords(searchKeywords).forEach(keywordObj => {
    // Map field names to API field names
    const fieldMap = {
      'title': 'title',
      'id': 'alert_id',
      'creator': 'creator',
      'actor': 'actor'
    }
    const apiField = fieldMap[keywordObj.field] || keywordObj.field
    conditions.push({
      [apiField]: keywordObj.value
    })
  })
  
  return conditions
}

/**
 * @brief 将时间戳转换为后端期望的格式
 * @param {Date|string|undefined} timestamp - 时间戳（Date对象、ISO字符串或undefined）
 * @returns {string} 格式化后的时间字符串，使用统一的 formatDateTimeWithOffset 函数
 */
const formatTimestamp = (timestamp) => {
  return formatDateTimeWithOffset(timestamp) || formatDateTimeWithOffset(new Date())
}

/**
 * @brief 获取攻击面管理列表
 * @param {Object} params - 查询参数
 * @param {Array<Object>|Array<string>} params.searchKeywords - 搜索关键字（支持对象数组：{field: 'id'|'title'|'creator'|'actor', value: 'keyword'} 或字符串数组（兼容旧格式））
 * @param {string} params.status - 状态过滤
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @param {string} params.startTime - 开始时间（ISO字符串）
 * @param {string} params.endTime - 结束时间（ISO字符串）
 * @returns {Promise} 返回告警列表数据
 */
export const getASMItems = async (params = {}) => {
  // Build API request parameters
  const page = params.page || 1
  const pageSize = params.pageSize || 10
  const limit = pageSize
  const offset = (page - 1) * pageSize
  
  // Build query conditions
  const conditions = buildConditions(params.searchKeywords, params.status)
  
  // Build request body
  const requestBody = {
    action: 'list',
    limit,
    offset,
    conditions,
    workspace: 'asm'
  }

  const start_time = formatDateTimeWithOffset(params.startTime)
  const end_time = formatDateTimeWithOffset(params.endTime)
  if (start_time && end_time) {
    requestBody.start_time = start_time
    requestBody.end_time = end_time
  }
  
  // Use service (axios instance with interceptors) to call /alerts
  // This ensures 403 errors are properly handled by the interceptor
  try {
    const response = await service.post('/alerts', requestBody)
    
    // Transform response data
    const transformedData = {
      data: (response.data || []).map(transformAlertData),
      total: response.total || 0
    }
    
    return transformedData
  } catch (error) {
    console.error('Failed to fetch ASM items:', error)
    throw error
  }
}

/**
 * @brief 获取攻击面管理详情
 * @param {string|number} id - 告警ID
 * @returns {Promise} 返回告警详情数据
 */
export const getASMDetail = (id) => {
  return service.get(`/alerts/${id}`, {
    params: {
      workspace: 'asm'
    }
  })
}

/**
 * @brief 获取ASM漏洞扩展数据（评论和时间线等）
 * @param {string|number} id - 告警ID
 * @returns {Promise} 返回ASM漏洞扩展数据（评论、时间线等）
 */
export const getASMCommentsExtension = (id) => {
  return service.get(`/alerts/${id}`, {
    params: {
      action: 'comments_extension',
      workspace: 'asm'
    }
  })
}

// 关闭单个告警
export const closeASMItem = (alertId, params) => {
  // 将 category 映射到 close_reason
  const closeReason = CLOSE_REASON_CATEGORY_MAP[params.category] || params.category || 'Other'
  
  return service.put(`/alerts/${alertId}`, {
    action: 'close',
    workspace: 'asm',
    data: {
      close_reason: closeReason,
      close_comment: params.notes || ''
    }
  })
}

/**
 * @brief 批量关闭告警（使用 PUT /api/alerts 接口）
 * @param {Array<number|string>} alertIds - 告警ID数组
 * @param {string} closeReason - 关闭原因
 * @param {string} closeComment - 关闭备注
 * @returns {Promise} 返回批量关闭结果
 */
export const batchCloseASMItems = (alertIds, closeReason, closeComment) => {
  // 将 category 映射到 close_reason
  const mappedCloseReason = CLOSE_REASON_CATEGORY_MAP[closeReason] || closeReason || 'Other'
  
  const payload = {
    batch_ids: alertIds,
    workspace: 'asm',
    data_object: {
      handle_status: 'Closed',
      close_reason: mappedCloseReason,
      close_comment: closeComment || '',
    }
  }
  
  return service.put('/alerts', payload)
}

// 开启告警
export const openASMItem = (alertId) => {
  return service.put(`/alerts/${alertId}`, {
    action: 'update',
    workspace: 'asm',
    data: {
      handle_status: 'Open'
    }
  })
}

/**
 * @brief 更新告警
 * @param {number|string} alertId - 告警ID
 * @param {Object} data - 告警数据
 * @param {string} data.title - 告警标题
 * @param {string} data.riskLevel - 风险等级 (fatal/high/medium/low/tips)
 * @param {string} data.status - 状态 (open/block/closed)
 * @param {string} data.owner - 责任人
 * @param {string} data.description - 描述
 * @param {string} data.ruleName - 规则名称（可选）
 * @param {string|Date} data.createTime - 创建时间（可选）
 * @returns {Promise} 返回更新的告警数据
 */
export const updateASMItem = (alertId, data) => {
  // 构建请求体，符合后端期望的格式，与创建告警类似但 action 为 'update'
  const requestBody = {
    action: 'update',
    workspace: 'asm',
    data: {
      title: data.title,
      create_time: formatTimestamp(data.createTime || data.timestamp),
      severity: CLIENT_SEVERITY_TO_API_MAP[data.riskLevel] || data.riskLevel || 'Medium',
      handle_status: CLIENT_STATUS_TO_API_MAP[data.status] || data.status || 'Open',
      owner: data.owner,
      rule_name: data.ruleName || '',
      description: data.description      
    }
  }
  
  return service.put(`/alerts/${alertId}`, requestBody)
}

/**
 * @brief 批量删除告警
 * @param {Array<string>} alertIds - 告警ID数组
 * @returns {Promise} 返回删除结果
 */
export const deleteASMItems = (alertIds) => {
  return service.delete('/alerts', {
    workspace: 'asm',
    data: {
      batch_ids: alertIds,
    }
  })
}

