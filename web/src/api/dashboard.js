import service from './axios.js'

/**
 * @brief 获取Dashboard统计数据
 * @details 返回告警数量、事件数、漏洞数、平均检测时间等统计信息
 * @return {Promise} 返回统计数据
 */
export const getDashboardStatistics = () => {
  return service.get('/dashboard/statistics')
}

/**
 * @brief 获取最近未关闭的告警
 * @details 返回最近未关闭的告警列表
 * @param {Object} params 查询参数
 * @param {Number} params.limit 返回数量限制，默认3
 * @return {Promise} 返回告警列表
 */
export const getRecentOpenAlerts = (params = {}) => {
  return service.get('/dashboard/recent-alerts', { params })
}

/**
 * @brief 获取最近未关闭的漏洞
 * @details 返回最近未关闭的漏洞列表
 * @param {Object} params 查询参数
 * @param {Number} params.limit 返回数量限制，默认3
 * @return {Promise} 返回漏洞列表
 */
export const getRecentOpenVulnerabilities = (params = {}) => {
  return service.get('/dashboard/recent-vulnerabilities', { params })
}

