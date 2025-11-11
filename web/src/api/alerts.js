import service from './axios.js'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

/**
 * @brief 转换API返回的告警数据为前端期望的格式
 * @param {Object} apiAlert - API返回的告警对象
 * @returns {Object} 转换后的告警对象
 */
const transformAlertData = (apiAlert) => {
  // 转换severity为riskLevel (Fatal/High/Medium/Low/Tips -> fatal/high/medium/low/tips)
  const severityMap = {
    'Fatal': 'fatal',
    'High': 'high',
    'Medium': 'medium',
    'Low': 'low',
    'Tips': 'tips'
  }
  
  // 转换handle_status为status (Open/Block/Closed -> open/block/closed)
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
    // 保留原始字段以便详情页面使用
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
  
  // 添加状态条件
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
  
  // 添加搜索关键字条件（搜索标题）
  // 注意：根据API实现，多个关键字会使用AND逻辑
  if (searchKeywords) {
    const keywords = Array.isArray(searchKeywords) 
      ? searchKeywords 
      : searchKeywords.split(',').map(k => k.trim()).filter(k => k)
    
    if (keywords.length > 0) {
      // 如果多个关键字，每个关键字作为一个条件（后端会使用AND逻辑）
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
  // 构建API请求参数
  const page = params.page || 1
  const pageSize = params.pageSize || 10
  const limit = pageSize
  const offset = (page - 1) * pageSize
  
  // 转换时间范围
  const time_range = convertTimeRange(params.startTime, params.endTime)
  
  // 构建查询条件
  const conditions = buildConditions(params.searchKeywords, params.status)
  
  // 构建请求体
  const requestBody = {
    limit,
    offset,
    time_range,
    conditions
  }
  
  // 使用axios直接调用/alerts，由vite代理转发到后端
  // 在开发环境，vite代理会将/alerts转发到http://localhost:8080/alerts
  // 在生产环境，需要配置nginx或使用完整URL
  try {
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/alerts` : '/alerts'
    
    // 获取认证token
    const authStore = useAuthStore()
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    const response = await axios.post(url, requestBody, { headers })
    
    // 转换响应数据
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
 * @brief 获取告警的威胁情报信息
 * @param {number|string} alertId - 告警ID
 * @returns {Promise} 返回威胁情报数据
 */
export const getThreatIntelligence = (alertId) => {
  return service.get(`/alerts/${alertId}/threat-intelligence`)
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

