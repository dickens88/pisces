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
    owner: apiAlert.owner,
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
 * @brief 构建查询条件
 * @param {Array<string>|string} searchKeywords - 搜索关键字
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
  
  // Add search keyword conditions (search title)
  // Note: According to API implementation, multiple keywords will use AND logic
  if (searchKeywords) {
    const keywords = Array.isArray(searchKeywords) 
      ? searchKeywords 
      : searchKeywords.split(',').map(k => k.trim()).filter(k => k)
    
    if (keywords.length > 0) {
      // If multiple keywords, each keyword is a condition (backend will use AND logic)
      keywords.forEach(keyword => {
        conditions.push({
          'title': keyword
        })
      })
    }
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
 * @param {Array<string>|string} params.searchKeywords - 搜索关键字数组或逗号分隔字符串（支持多关键字AND搜索）
 * @param {string} params.status - 状态过滤
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
  
  // Build query conditions
  const conditions = buildConditions(params.searchKeywords, params.status)
  
  // Build request body
  const requestBody = {
    action: 'list',
    limit,
    offset,
    conditions
  }

  const start_time = formatDateTimeWithOffset(params.startTime)
  const end_time = formatDateTimeWithOffset(params.endTime)
  if (start_time && end_time) {
    requestBody.start_time = start_time
    requestBody.end_time = end_time
  }
  
  // Use axios to directly call /alerts, forwarded to backend by vite proxy
  // In development, vite proxy will forward /alerts to http://localhost:8080/alerts
  // In production, need to configure nginx or use full URL
  try {
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/alerts` : '/alerts'
    
    // Get authentication token
    const authStore = useAuthStore()
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    const response = await axios.post(url, requestBody, { headers })
    
    // Transform response data
    const transformedData = {
      data: (response.data.data || []).map(transformAlertData),
      total: response.data.total || 0
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
  return service.post(`/alerts/${alertId}/open`)
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
 * @param {string|Date} data.timestamp - 时间戳（可选）
 * @returns {Promise} 返回更新的告警数据
 */
export const updateAlert = (alertId, data) => {
  // 构建请求体，符合后端期望的格式，与创建告警类似但 action 为 'update'
  const requestBody = {
    action: 'update',
    data: {
      title: data.title,
      create_time: formatTimestamp(data.timestamp),
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
export const deleteAlerts = (alertIds) => {
  return service.delete('/alerts', {
    data: {
      batch_ids: alertIds
    }
  })
}

