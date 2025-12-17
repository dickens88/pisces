import service from './axios.js'
import { formatDateTimeWithOffset } from '@/utils/dateTime'

const setDateParam = (params, key, value) => {
  const formatted = formatDateTimeWithOffset(value)
  if (formatted) {
    params[key] = formatted
  }
}

// Get incident list
export const getIncidents = (params = {}) => {
  return service.post('/incidents', params)
}

// Batch close incidents
export const batchCloseIncidents = (params) => {
  return service.post('/incidents/batch-close', params)
}

// Update incident
export const updateIncident = (id, data) => {
  return service.put(`/incidents/${id}/update`, data)
}

// Get incident detail
export const getIncidentDetail = (id) => {
  return service.get(`/incidents/${id}`)
}

// Associate alerts to incident (optionally in a workspace, e.g., ASM vulnerabilities)
export const associateAlertsToIncident = (incidentId, alertIds, workspace = null) => {
  const data = {
    ids: alertIds
  }
  if (workspace) {
    data.workspace = workspace
  }
  return service.post(`/incidents/${incidentId}/relations`, data)
}

// Disassociate alerts from incident
export const disassociateAlertsFromIncident = (incidentId, alertIds) => {
  return service.delete(`/incidents/${incidentId}/relations`, {
    data: {
      ids: alertIds
    }
  })
}

export const regenerateIncidentGraph = (incidentId) => {
  return service.post(`/incidents/${incidentId}/graph`)
}

/**
 * @brief 批量删除事件
 * @param {Array<string>} incidentIds - 事件ID数组
 * @param {string} workspace - 工作空间（可选）
 * @returns {Promise} 返回删除结果
 */
export const deleteIncidents = (incidentIds, workspace = null) => {
  const data = {
    batch_ids: incidentIds
  }
  if (workspace) {
    data.workspace = workspace
  }
  return service.delete('/incidents', {
    data
  })
}

// Post comment (imported from comments.js for backward compatibility)
export { postComment } from './comments.js'

/**
 * @brief 获取事件趋势数据（按日期分组统计）
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 事件趋势数据数组，格式为 [{date: string, count: number}, ...]
 */
export const getIncidentTrend = (startDate, endDate) => {
  const params = {
    chart: 'incident-trend'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取漏洞趋势数据（按日期分组统计）
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 漏洞趋势数据数组，格式为 [{date: string, count: number}, ...]
 */
export const getVulnerabilityTrend = (startDate, endDate) => {
  const params = {
    chart: 'vulnerability-trend'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取漏洞趋势数据（按日期和severity分组统计）
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 漏洞趋势数据数组，格式为 [{date: string, severity: string, count: number}, ...]
 */
export const getVulnerabilityTrendBySeverity = (startDate, endDate) => {
  const params = {
    chart: 'vulnerability-trend-by-severity'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取事件趋势数据（按日期和severity分组统计）
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 事件趋势数据数组，格式为 [{date: string, severity: string, count: number}, ...]
 */
export const getIncidentTrendBySeverity = (startDate, endDate) => {
  const params = {
    chart: 'incident-trend-by-severity'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取事件部门分布数据（按严重程度分组）
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 事件部门分布数据，格式为 {department: {severity: count, ...}, ...}
 */
export const getIncidentDepartmentDistribution = (startDate, endDate) => {
  const params = {
    chart: 'incident-department-distribution'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取事件根因分布数据
 * @param {string|Date} startDate - 开始时间（ISO字符串或Date对象）
 * @param {string|Date} endDate - 结束时间（ISO字符串或Date对象）
 * @returns {Promise} 事件根因分布数据，格式为 {root_cause: count, ...}
 */
export const getIncidentRootCauseDistribution = (startDate, endDate) => {
  const params = {
    chart: 'incident-root-cause-distribution'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

