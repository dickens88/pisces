import service from './axios.js'

// Mock数据
const mockVulnerabilities = [
  {
    id: 1,
    name: 'CVE-2023-4863: Heap buffer overflow in WebP',
    cve: 'CVE-2023-4863',
    riskLevel: 'critical',
    affectedAsset: '192.168.1.101',
    firstDiscoveryTime: '2023-09-15',
    status: 'pending',
    department: '研发部'
  },
  {
    id: 2,
    name: 'CVE-2023-38545: SOCKS5 heap buffer overflow in curl',
    cve: 'CVE-2023-38545',
    riskLevel: 'high',
    affectedAsset: '192.168.1.102',
    firstDiscoveryTime: '2023-09-12',
    status: 'fixed',
    department: '运维部'
  },
  {
    id: 3,
    name: 'Log4Shell: RCE in Apache Log4j',
    cve: 'CVE-2021-44228',
    riskLevel: 'critical',
    affectedAsset: '10.0.0.5',
    firstDiscoveryTime: '2023-09-10',
    status: 'inProgress',
    department: '产品部'
  },
  {
    id: 4,
    name: 'OpenSSH User Enumeration Vulnerability',
    cve: 'CVE-2018-15473',
    riskLevel: 'medium',
    affectedAsset: '172.16.0.20',
    firstDiscoveryTime: '2023-09-08',
    status: 'pending',
    department: '测试部'
  },
  {
    id: 5,
    name: 'SSL/TLS: Weak Cipher Suites Supported',
    cve: 'CVE-2016-2183',
    riskLevel: 'low',
    affectedAsset: 'webapp.internal.net',
    firstDiscoveryTime: '2023-09-05',
    status: 'ignored',
    department: '市场部'
  },
  {
    id: 6,
    name: 'CVE-2023-34362: MOVEit SQL Injection',
    cve: 'CVE-2023-34362',
    riskLevel: 'critical',
    affectedAsset: '192.168.1.105',
    firstDiscoveryTime: '2023-09-20',
    status: 'pending',
    department: '研发部'
  },
  {
    id: 7,
    name: 'CVE-2023-22515: Confluence RCE',
    cve: 'CVE-2023-22515',
    riskLevel: 'high',
    affectedAsset: '192.168.1.106',
    firstDiscoveryTime: '2023-09-18',
    status: 'inProgress',
    department: '运维部'
  },
  {
    id: 8,
    name: 'CVE-2023-20887: VMware vCenter Server RCE',
    cve: 'CVE-2023-20887',
    riskLevel: 'high',
    affectedAsset: '10.0.0.10',
    firstDiscoveryTime: '2023-09-15',
    status: 'fixed',
    department: '产品部'
  }
]

// 获取漏洞列表
export const getVulnerabilities = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredVulnerabilities = [...mockVulnerabilities]
      
      // 搜索过滤
      if (params.search) {
        const searchLower = params.search.toLowerCase()
        filteredVulnerabilities = filteredVulnerabilities.filter(vuln => 
          vuln.name.toLowerCase().includes(searchLower) ||
          vuln.cve.toLowerCase().includes(searchLower) ||
          vuln.affectedAsset.toLowerCase().includes(searchLower)
        )
      }
      
      // 风险等级过滤
      if (params.riskLevel && params.riskLevel !== 'all') {
        filteredVulnerabilities = filteredVulnerabilities.filter(vuln => vuln.riskLevel === params.riskLevel)
      }
      
      // 状态过滤
      if (params.status && params.status !== 'all') {
        filteredVulnerabilities = filteredVulnerabilities.filter(vuln => vuln.status === params.status)
      }
      
      // 分页
      const page = params.page || 1
      const pageSize = params.pageSize || 10
      const start = (page - 1) * pageSize
      const end = start + pageSize
      const paginatedData = filteredVulnerabilities.slice(start, end)
      
      resolve({
        data: paginatedData,
        total: filteredVulnerabilities.length,
        page: page,
        pageSize: pageSize
      })
    }, 300)
  })
}

// 获取漏洞趋势统计
export const getVulnerabilityTrend = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 模拟6个月的数据
      const trendData = [
        { month: '7月', critical: 25, high: 40, medium: 20, low: 10 },
        { month: '8月', critical: 30, high: 35, medium: 15, low: 5 },
        { month: '9月', critical: 15, high: 25, medium: 35, low: 20 },
        { month: '10月', critical: 35, high: 45, medium: 15, low: 5 },
        { month: '11月', critical: 20, high: 30, medium: 25, low: 15 },
        { month: '12月', critical: 25, high: 50, medium: 15, low: 10 }
      ]
      
      resolve({ data: trendData })
    }, 200)
  })
}

// 获取漏洞责任部门分布
export const getVulnerabilityDepartmentDistribution = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 模拟5个部门的数据
      const distributionData = [
        { department: '研发部', critical: 20, high: 40, medium: 25, low: 15 },
        { department: '运维部', critical: 35, high: 30, medium: 20, low: 15 },
        { department: '市场部', critical: 25, high: 20, medium: 30, low: 25 },
        { department: '产品部', critical: 50, high: 25, medium: 15, low: 10 },
        { department: '测试部', critical: 15, high: 35, medium: 30, low: 20 }
      ]
      
      resolve({ data: distributionData })
    }, 200)
  })
}

// 获取漏洞详情
export const getVulnerabilityDetail = (id) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const vulnerability = mockVulnerabilities.find(v => v.id === parseInt(id))
      if (vulnerability) {
        resolve({ 
          data: {
            ...vulnerability,
            description: '这是一个详细的漏洞描述信息，包含了漏洞的详细信息、影响范围、修复建议等。',
            cvss: '9.8',
            affectedSystems: ['Windows Server 2019', 'Windows Server 2022'],
            remediation: '建议立即更新到最新版本或应用安全补丁。',
            references: [
              'https://cve.mitre.org/cgi-bin/cvename.cgi?name=' + vulnerability.cve
            ]
          }
        })
      } else {
        reject(new Error('Vulnerability not found'))
      }
    }, 200)
  })
}

// 批量操作漏洞
export const batchOperateVulnerabilities = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log('Batch operating vulnerabilities:', params)
      resolve({
        success: true,
        message: `成功处理 ${params.vulnerabilityIds.length} 个漏洞`,
        data: {
          processedCount: params.vulnerabilityIds.length,
          operation: params.operation
        }
      })
    }, 500)
  })
}

// 导出报告
export const exportVulnerabilityReport = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log('Exporting vulnerability report:', params)
      // 模拟导出
      const blob = new Blob(['漏洞报告内容'], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `vulnerability-report-${new Date().getTime()}.txt`
      a.click()
      URL.revokeObjectURL(url)
      
      resolve({
        success: true,
        message: '报告导出成功'
      })
    }, 500)
  })
}

