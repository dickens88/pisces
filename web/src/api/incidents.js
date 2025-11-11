import service from './axios.js'

// 获取事件列表
export const getIncidents = (params = {}) => {
  return service.post('/incidents', params)
}

// 批量关闭事件
export const batchCloseIncidents = (params) => {
  return service.post('/incidents/batch-close', params)
}

// 创建事件
export const createIncident = (data) => {
  return service.post('/incidents/create', data)
}

// 更新事件
export const updateIncident = (id, data) => {
  return service.put(`/incidents/${id}/update`, data)
}

// 获取事件详情
export const getIncidentDetail = (id) => {
  return service.get(`/incidents/${id}`)
}

