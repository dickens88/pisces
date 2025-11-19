import service from './axios.js'
import { formatDateTimeWithOffset } from '@/utils/dateTime'

const setDateParam = (params, key, value) => {
  const formatted = formatDateTimeWithOffset(value)
  if (formatted) {
    params[key] = formatted
  }
}

// Get vulnerability list
export const getVulnerabilities = (params = {}) => {
  return service.post('/vulnerabilities', params)
}

// Get vulnerability trend statistics
export const getVulnerabilityTrend = (params = {}) => {
  return service.get('/vulnerabilities/trend', { params })
}

// Get vulnerability department distribution
export const getVulnerabilityDepartmentDistribution = (startDate, endDate) => {
  const params = {
    chart: 'vulnerability-department-distribution'
  }
  setDateParam(params, 'start_date', startDate)
  setDateParam(params, 'end_date', endDate)
  return service.get('/stats/alerts', { params })
}

// Get vulnerability detail
export const getVulnerabilityDetail = (id) => {
  return service.get(`/vulnerabilities/${id}`)
}

// Batch operate vulnerabilities
export const batchOperateVulnerabilities = (params) => {
  return service.post('/vulnerabilities/batch-operate', params)
}

// Export report
export const exportVulnerabilityReport = (params) => {
  return service.post('/vulnerabilities/export', params, {
    responseType: 'blob'
  }).then(response => {
    // Create download link
    const blob = new Blob([response.data])
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vulnerability-report-${new Date().getTime()}.txt`
    a.click()
    URL.revokeObjectURL(url)
    
    return {
      success: true,
      message: '报告导出成功'
    }
  })
}

