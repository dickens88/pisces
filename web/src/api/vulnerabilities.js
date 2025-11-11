import service from './axios.js'

// 获取漏洞列表
export const getVulnerabilities = (params = {}) => {
  return service.post('/vulnerabilities', params)
}

// 获取漏洞趋势统计
export const getVulnerabilityTrend = (params = {}) => {
  return service.get('/vulnerabilities/trend', { params })
}

// 获取漏洞责任部门分布
export const getVulnerabilityDepartmentDistribution = (params = {}) => {
  return service.get('/vulnerabilities/department-distribution', { params })
}

// 获取漏洞详情
export const getVulnerabilityDetail = (id) => {
  return service.get(`/vulnerabilities/${id}`)
}

// 批量操作漏洞
export const batchOperateVulnerabilities = (params) => {
  return service.post('/vulnerabilities/batch-operate', params)
}

// 导出报告
export const exportVulnerabilityReport = (params) => {
  return service.post('/vulnerabilities/export', params, {
    responseType: 'blob'
  }).then(response => {
    // 创建下载链接
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

