import service from './axios.js'

/**
 * @brief 获取工具清单
 * @returns {Promise} 返回工具清单数据
 */
export const getToolkits = () => {
  return service.get('/toolkits')
}

/**
 * @brief 获取指定告警的工具执行记录
 * @param {string|number} alertId - 告警ID
 * @returns {Promise} 返回工具执行记录列表
 */
export const getToolkitRecords = (alertId) => {
  return service.get(`/alerts/${alertId}/toolkits`)
}

/**
 * @brief 执行工具
 * @param {string|number} alertId - 告警ID
 * @param {Object} data - 工具执行数据
 * @param {string} data.title - 工具标题
 * @param {string} data.app_id - 应用ID
 * @param {string} data.app_type - 应用类型
 * @param {Object} data.params - 参数对象，key为参数名，value为参数值
 * @returns {Promise} 返回执行结果
 */
export const executeToolkit = (alertId, data) => {
  return service.post(`/alerts/${alertId}/toolkits`, data)
}

