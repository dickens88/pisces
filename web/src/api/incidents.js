import service from './axios.js'

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

// Associate alerts to incident
export const associateAlertsToIncident = (incidentId, alertIds) => {
  return service.post(`/incidents/${incidentId}/relations`, {
    ids: alertIds
  })
}

export const regenerateIncidentGraph = (incidentId) => {
  return service.post(`/incidents/${incidentId}/graph`)
}

// Post comment (imported from comments.js for backward compatibility)
export { postComment } from './comments.js'

/**
 * @brief 获取事件趋势数据（按日期分组统计）
 * @param {string} startDate - ISO格式的开始时间（不带Z标志）
 * @param {string} endDate - ISO格式的结束时间（不带Z标志）
 * @returns {Promise} 事件趋势数据数组，格式为 [{date: string, count: number}, ...]
 */
export const getIncidentTrend = (startDate, endDate) => {
  const params = {
    chart: 'incident-trend'
  }
  if (startDate) {
    params.start_date = startDate
  }
  if (endDate) {
    params.end_date = endDate
  }
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取漏洞趋势数据（按日期分组统计）
 * @param {string} startDate - ISO格式的开始时间（不带Z标志）
 * @param {string} endDate - ISO格式的结束时间（不带Z标志）
 * @returns {Promise} 漏洞趋势数据数组，格式为 [{date: string, count: number}, ...]
 */
export const getVulnerabilityTrend = (startDate, endDate) => {
  const params = {
    chart: 'vulnerability-trend'
  }
  if (startDate) {
    params.start_date = startDate
  }
  if (endDate) {
    params.end_date = endDate
  }
  return service.get('/stats/alerts', { params })
}

/**
 * @brief 获取漏洞趋势数据（按日期和severity分组统计）
 * @param {string} startDate - ISO格式的开始时间（不带Z标志）
 * @param {string} endDate - ISO格式的结束时间（不带Z标志）
 * @returns {Promise} 漏洞趋势数据数组，格式为 [{date: string, severity: string, count: number}, ...]
 */
export const getVulnerabilityTrendBySeverity = (startDate, endDate) => {
  const params = {
    chart: 'vulnerability-trend-by-severity'
  }
  if (startDate) {
    params.start_date = startDate
  }
  if (endDate) {
    params.end_date = endDate
  }
  return service.get('/stats/alerts', { params })
}

