import service from './axios.js'

// Get incident list
export const getIncidents = (params = {}) => {
  return service.post('/incidents', params)
}

// Batch close incidents
export const batchCloseIncidents = (params) => {
  return service.post('/incidents/batch-close', params)
}

// Create incident
export const createIncident = (data) => {
  return service.post('/incidents/create', data)
}

// Update incident
export const updateIncident = (id, data) => {
  return service.put(`/incidents/${id}/update`, data)
}

// Get incident detail
export const getIncidentDetail = (id) => {
  return service.get(`/incidents/${id}`)
}

