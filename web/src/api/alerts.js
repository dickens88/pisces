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
    description: apiAlert.description,
    verification_state: apiAlert.verification_state
  }
}

/**
 * 统一格式化搜索关键字
 * 期望格式：[{ field: 'title'|'creator'|'actor', value: 'keyword' }]
 */
const normalizeSearchKeywords = (searchKeywords) => {
  if (!searchKeywords) return []
  if (!Array.isArray(searchKeywords)) return []
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
 * @param {Array<Object>} searchKeywords - 搜索关键字（统一使用对象数组：{field: 'title'|'creator'|'actor', value: 'keyword'}）
 * @param {string} status - 状态过滤
 * @param {string} severity - 风险等级过滤
 * @param {string} verificationState - AI研判状态过滤 (True_Positive, False_Positive, Unknown)
 * @param {string} autoClose - 关闭方式过滤 (AutoClosed/Manual)
 * @returns {Array} 条件数组，格式为 [{field_name: value}, ...]
 */
const buildConditions = (searchKeywords, status, severity, verificationState, autoClose) => {
  const conditions = []
  
  // 状态
  if (status && status !== 'all') {
    conditions.push({
      'handle_status': CLIENT_STATUS_TO_API_MAP[status] || status
    })
  }
  
  // 关键字（统一为对象数组）
  normalizeSearchKeywords(searchKeywords).forEach(keywordObj => {
    conditions.push({
      [keywordObj.field]: keywordObj.value
    })
  })
  
  // 风险等级
  if (severity && severity !== 'all') {
    conditions.push({
      'severity': CLIENT_SEVERITY_TO_API_MAP[severity] || severity
    })
  }

  if (autoClose && autoClose !== 'all') {
    conditions.push({
      'is_auto_closed': autoClose
    })
  }
  
  // AI 研判
  if (verificationState && verificationState !== 'all') {
    conditions.push({
      'verification_state': verificationState
    })
  }
  
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
 * @brief 获取告警列表
 * @param {Object} params - 查询参数
 * @param {Array<Object>} params.searchKeywords - 搜索关键字（统一格式：{field: 'title'|'creator'|'actor', value: 'keyword'}）
 * @param {string} params.status - 状态过滤
 * @param {string} params.severity - 风险等级过滤 (fatal/high/medium/low/tips)
 * @param {string} params.autoClose - 关闭方式过滤 (AutoClosed/Manual)
 * @param {string} params.verificationState - AI研判状态过滤 (True_Positive, False_Positive, Unknown)
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @param {string} params.startTime - 开始时间（ISO字符串）
 * @param {string} params.endTime - 结束时间（ISO字符串）
 * @returns {Promise} 返回告警列表数据
 */
export const getAlerts = async (params = {}) => {
  // Build API request parameters
  const page = params.page || 1
  const pageSize = params.pageSize || 10
  const limit = pageSize
  const offset = (page - 1) * pageSize
  const risk_mode = params.risk_mode || 'allAlerts'
  
  // Build query conditions
  const conditions = buildConditions(params.searchKeywords, params.status, params.severity, params.verificationState, params.autoClose)
  
  // Build request body
  const requestBody = {
    action: 'list',
    limit,
    offset,
    conditions,
    risk_mode
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
    console.error('Failed to fetch alerts:', error)
    throw error
  }
}

/**
 * @brief 获取告警详情
 * @param {string|number} id - 告警ID
 * @returns {Promise} 返回告警详情数据
 */
export const getAlertDetail = (id) => {
  return service.get(`/alerts/${id}`)
}

/**
 * @brief 获取自动化关闭率统计
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 返回自动化关闭率统计数据
 */
export const getAlertStatistics = (startDate, endDate) => {
  const params = {
    chart: 'automation-closure-rate'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

const setDateParam = (params, key, value) => {
  const formatted = formatDateTimeWithOffset(value)
  if (formatted) {
    params[key] = formatted
  }
}

/**
 * @brief 获取按数据源产品名称统计的告警数量
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象，可选）
 * @param {string} status - 状态过滤（可选）
 * @returns {Promise} 告警数量映射
 */
export const getAlertCountsBySource = (startDate, endDate = null, status = null) => {
  const params = {}
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  if (status && status !== 'all') {
    params.status = status
  }
  return service.get('/stats/alerts?chart=data-source-count', { params })
}

/**
 * @brief 获取告警趋势数据（按日期分组统计）
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 告警趋势数据数组，格式为 [{date: string, count: number}, ...]
 */
export const getAlertTrend = (startDate, endDate) => {
  const params = {
    chart: 'alert-trend'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取按状态和风险等级分组的告警数量（用于横向柱状图）
 * 返回格式示例：
 * {
 *   Open:   { Fatal: 10, High: 20, Medium: 5, Low: 1, Tips: 0 },
 *   Block:  { Fatal: 2,  High: 3,  Medium: 1, Low: 0, Tips: 0 },
 *   Closed: { Fatal: 5,  High: 8,  Medium: 12, Low: 4, Tips: 1 }
 * }
 *
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @param {string} status - 状态过滤（可选）
 * @returns {Promise} 告警状态与风险等级分布数据
 */
export const getAlertStatusBySeverity = (startDate, endDate, status = null) => {
  const params = {
    chart: 'alert-status-by-severity'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  if (status && status !== 'all') {
    params.status = status
  }
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取按模型统计的AI准确率
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @param {number} limit - 返回的模型数量上限（默认10）
 * @returns {Promise} AI准确率数据数组
 */
export const getAiAccuracyByModel = (startDate, endDate, limit = 10) => {
  if (!startDate || !endDate) {
    throw new Error('startDate and endDate are required for AI accuracy statistics')
  }

  const params = {
    chart: 'ai-model-accuracy',
    limit
  }

  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)

  if (!params.start_date || !params.end_date) {
    throw new Error('Invalid startDate or endDate format')
  }

  return service.get('/stats/alerts', { params })
}

// 关闭单个告警
export const closeAlert = (alertId, params) => {
  // 将 category 映射到 close_reason
  const closeReason = CLOSE_REASON_CATEGORY_MAP[params.category] || params.category || 'Other'
  
  return service.put(`/alerts/${alertId}`, {
    action: 'close',
    data: {
      close_reason: closeReason,
      close_comment: params.notes || ''
    }
  })
}

// 批量关闭告警
export const batchCloseAlerts = (params) => {
  return service.post('/alerts/batch-close', params)
}

/**
 * @brief 批量关闭告警（使用 PUT /api/alerts 接口）
 * @param {Array<number|string>} alertIds - 告警ID数组
 * @param {string} closeReason - 关闭原因
 * @param {string} closeComment - 关闭备注
 * @returns {Promise} 返回批量关闭结果
 */
export const batchCloseAlertsByPut = (alertIds, closeReason, closeComment) => {
  // 将 category 映射到 close_reason
  const mappedCloseReason = CLOSE_REASON_CATEGORY_MAP[closeReason] || closeReason || 'Other'
  
  const payload = {
    batch_ids: alertIds,
    data_object: {
      handle_status: 'Closed',
      close_reason: mappedCloseReason,
      close_comment: closeComment || ''
    }
  }
  
  return service.put('/alerts', payload)
}

// 开启告警
export const openAlert = (alertId) => {
  return service.put(`/alerts/${alertId}`, {
    action: 'update',
    data: {
      handle_status: 'Open'
    }
  })
}

// 关联告警到事件
export const associateAlertsToIncident = (params) => {
  return service.post('/alerts/associate', params)
}

/**
 * @brief 获取告警的关联告警列表
 * @param {number|string} alertId - 告警ID
 * @returns {Promise} 返回关联告警数据
 */
export const getAssociatedAlerts = (alertId) => {
  return service.get(`/alerts/${alertId}/associated`)
}

/**
 * @brief 创建告警
 * @param {Object} data - 告警数据
 * @param {string} data.title - 告警标题
 * @param {string} data.riskLevel - 风险等级 (fatal/high/medium/low/tips)
 * @param {string} data.status - 状态 (open/block/closed)
 * @param {string} data.owner - 责任人
 * @param {string} data.description - 描述
 * @param {string} data.ruleName - 规则名称（可选）
 * @param {string|Date} data.timestamp - 时间戳（可选，默认当前时间）
 * @param {string} data.creator - 创建者（可选）
 * @returns {Promise} 返回创建的告警数据
 */
export const createAlert = (data) => {
  // 构建请求体，符合后端期望的格式
  const requestBody = {
    action: 'create',
    data: {
      title: data.title,
      create_time: formatTimestamp(data.timestamp),
      severity: CLIENT_SEVERITY_TO_API_MAP[data.riskLevel] || data.riskLevel || 'Medium',
      handle_status: CLIENT_STATUS_TO_API_MAP[data.status] || data.status || 'Open',
      owner: data.owner,
      creator: data.creator || data.owner || 'System',
      rule_name: data.ruleName || '',
      description: data.description
    }
  }
  
  if (data.workspace) {
    requestBody.workspace = data.workspace
  }
  
  return service.post('/alerts', requestBody)
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
export const updateAlert = (alertId, data) => {
  // 构建请求体，符合后端期望的格式，与创建告警类似但 action 为 'update'
  const requestBody = {
    action: 'update',
    data: {}
  }
  
  if (data.title !== undefined) {
    requestBody.data.title = data.title
  }
  if (data.createTime !== undefined || data.timestamp !== undefined) {
    requestBody.data.create_time = formatTimestamp(data.createTime || data.timestamp)
  }
  if (data.riskLevel !== undefined) {
    requestBody.data.severity = CLIENT_SEVERITY_TO_API_MAP[data.riskLevel] || data.riskLevel || 'Medium'
  }
  if (data.status !== undefined) {
    requestBody.data.handle_status = CLIENT_STATUS_TO_API_MAP[data.status] || data.status || 'Open'
  }
  if (data.owner !== undefined) {
    requestBody.data.owner = data.owner
  }
  if (data.ruleName !== undefined) {
    requestBody.data.rule_name = data.ruleName || ''
  }
  if (data.description !== undefined) {
    requestBody.data.description = data.description
  }
  if (data.actor !== undefined) {
    requestBody.data.actor = data.actor
  }
  
  return service.put(`/alerts/${alertId}`, requestBody)
}

/**
 * @brief 批量删除告警
 * @param {Array<string>} alertIds - 告警ID数组
 * @returns {Promise} 返回删除结果
 */
export const deleteAlerts = (alertIds) => {
  return service.delete('/alerts', {
    data: {
      batch_ids: alertIds
    }
  })
}

