import service from './axios.js'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

/**
 * @brief 转换API返回的告警数据为前端期望的格式
 * @param {Object} apiAlert - API返回的告警对象
 * @returns {Object} 转换后的告警对象
 */
const transformAlertData = (apiAlert) => {
  // Convert severity to riskLevel (Fatal/High/Medium/Low/Tips -> fatal/high/medium/low/tips)
  const severityMap = {
    'Fatal': 'fatal',
    'High': 'high',
    'Medium': 'medium',
    'Low': 'low',
    'Tips': 'tips'
  }
  
  // Convert handle_status to status (Open/Block/Closed -> open/block/closed)
  const statusMap = {
    'Open': 'open',
    'Block': 'block',
    'Closed': 'closed'
  }
  
  return {
    id: apiAlert.id,
    createTime: apiAlert.create_time || apiAlert.createTime,
    title: apiAlert.title,
    riskLevel: severityMap[apiAlert.severity] || apiAlert.severity?.toLowerCase() || 'medium',
    status: statusMap[apiAlert.handle_status] || apiAlert.handle_status?.toLowerCase() || 'open',
    owner: apiAlert.owner,
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
    ttr: apiAlert.ttr,
    extend_properties: apiAlert.extend_properties,
    description: apiAlert.description
  }
}

/**
 * @brief 转换时间范围为time_range参数
 * @param {string} startTime - 开始时间 ISO字符串
 * @param {string} endTime - 结束时间 ISO字符串
 * @returns {number} time_range值 (1=24小时, 2=3天, 3=7天, 4=30天, 5=3个月)
 */
const convertTimeRange = (startTime, endTime) => {
  if (!startTime || !endTime) return 1
  
  const start = new Date(startTime)
  const end = new Date(endTime)
  const diffHours = (end - start) / (1000 * 60 * 60)
  
  if (diffHours <= 24) return 1
  if (diffHours <= 72) return 2  // 3 days
  if (diffHours <= 168) return 3  // 7 days
  if (diffHours <= 720) return 4  // 30 days
  return 5  // 3 months
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
    const statusMap = {
      'open': 'Open',
      'block': 'Block',
      'closed': 'Closed'
    }
    conditions.push({
      'handle_status': statusMap[status] || status
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
  
  // Convert time range
  const time_range = convertTimeRange(params.startTime, params.endTime)
  
  // Build query conditions
  const conditions = buildConditions(params.searchKeywords, params.status)
  
  // Build request body
  const requestBody = {
    limit,
    offset,
    time_range,
    conditions
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

// 获取统计数据
export const getAlertStatistics = () => {
  return service.get('/alerts/statistics')
}

/**
 * @brief 获取按数据源产品名称统计的告警数量
 * @param {string} startDate - ISO格式的开始时间（不带Z标志）
 * @returns {Promise} 告警数量映射
 */
export const getAlertCountsBySource = (startDate) => {
  const params = {}
  if (startDate) {
    params.start_date = startDate
  }
  return service.get('/alerts/data-source-count', { params })
}

// 批量关闭告警
export const batchCloseAlerts = (params) => {
  return service.post('/alerts/batch-close', params)
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
 * @param {string} data.riskLevel - 风险等级 (high/medium/low)
 * @param {string} data.status - 状态 (open/pending/closed)
 * @param {string} data.owner - 责任人
 * @param {string} data.description - 描述
 * @param {string} data.ruleName - 规则名称（可选）
 * @param {string|Date} data.timestamp - 时间戳（可选，默认当前时间）
 * @returns {Promise} 返回创建的告警数据
 */
export const createAlert = (data) => {
  return service.post('/alerts/create', data)
}

/**
 * @brief 更新告警
 * @param {number|string} alertId - 告警ID
 * @param {Object} data - 告警数据
 * @param {string} data.title - 告警标题
 * @param {string} data.riskLevel - 风险等级 (high/medium/low)
 * @param {string} data.status - 状态 (open/pending/closed)
 * @param {string} data.owner - 责任人
 * @param {string} data.description - 描述
 * @param {string} data.ruleName - 规则名称（可选）
 * @param {string|Date} data.timestamp - 时间戳（可选）
 * @returns {Promise} 返回更新的告警数据
 */
export const updateAlert = (alertId, data) => {
  return service.put(`/alerts/${alertId}/update`, data)
}

