import service from './axios.js'

// Mock数据
const mockAlerts = [
  {
    id: 1,
    createTime: '2023-10-27 14:30:15',
    title: 'SQL Injection Attempt Detected on Server DB01',
    riskLevel: 'high',
    status: 'open',
    owner: '张三',
    severity: 'high',
    ruleName: 'SQL Injection Detection',
    timestamp: '2023-10-27 14:35:10 UTC',
    aiAnalysis: {
      confidence: 'high',
      summary: 'High Confidence SQL Injection Attempt Detected',
      description: 'The AI model detected a SQL injection attempt targeting the database server. Multiple suspicious SQL patterns were identified in the request payload.',
      recommendation: 'Immediately block the source IP and review database access logs.'
    },
    associatedEntities: [
      { type: 'host', name: 'prod-db-server-01', label: 'Host' },
      { type: 'ip', name: '192.168.1.50', label: 'Source IP' },
      { type: 'user', name: 'admin_user', label: 'Target User' }
    ],
    timeline: [
      { time: '14:35:10 UTC', event: 'Alert Triggered' },
      { time: '14:34:55 UTC', event: 'Suspicious SQL Pattern Detected' },
      { time: '14:33:12 UTC', event: 'First Suspicious Request' }
    ],
    comments: [
      {
        id: 1,
        author: 'Jane Doe',
        authorInitials: 'JD',
        time: '2 hours ago',
        content: 'Confirmed SQL injection attempt. Blocking source IP now.'
      },
      {
        id: 2,
        author: 'Alex Smith',
        authorInitials: 'AS',
        time: '4 hours ago',
        content: 'Reviewing database logs for any successful injection attempts.'
      }
    ]
  },
  {
    id: 2,
    createTime: '2023-10-27 13:55:02',
    title: 'Unusual Login Activity from an Unrecognized IP',
    riskLevel: 'medium',
    status: 'pending',
    owner: '李四',
    severity: 'medium',
    ruleName: 'Unusual Login Detection',
    timestamp: '2023-10-27 13:55:02 UTC',
    aiAnalysis: {
      confidence: 'medium',
      summary: 'Unusual Login Pattern Detected',
      description: 'Multiple login attempts from an unrecognized IP address. The IP has no prior successful login history.',
      recommendation: 'Verify user identity and consider implementing additional authentication factors.'
    },
    associatedEntities: [
      { type: 'host', name: 'prod-web-server-01', label: 'Host' },
      { type: 'ip', name: '203.0.113.45', label: 'Source IP' },
      { type: 'user', name: 'user123', label: 'Target User' }
    ],
    timeline: [
      { time: '13:55:02 UTC', event: 'Alert Triggered' },
      { time: '13:54:30 UTC', event: 'Third Failed Login Attempt' },
      { time: '13:53:15 UTC', event: 'First Login Attempt' }
    ],
    comments: []
  },
  {
    id: 3,
    createTime: '2023-10-27 12:10:48',
    title: 'Potential Malware Detected on Workstation WS102',
    riskLevel: 'high',
    status: 'closed',
    owner: '王五',
    severity: 'high',
    ruleName: 'Malware Detection',
    timestamp: '2023-10-27 12:10:48 UTC',
    aiAnalysis: {
      confidence: 'high',
      summary: 'Malware Signature Detected',
      description: 'A known malware signature was detected on the workstation. Immediate isolation recommended.',
      recommendation: 'Isolate the workstation from the network and initiate malware removal procedures.'
    },
    associatedEntities: [
      { type: 'host', name: 'workstation-ws102', label: 'Host' },
      { type: 'ip', name: '192.168.1.102', label: 'IP Address' }
    ],
    timeline: [
      { time: '12:10:48 UTC', event: 'Alert Triggered' },
      { time: '12:09:20 UTC', event: 'Malware Signature Matched' }
    ],
    comments: [
      {
        id: 1,
        author: 'Security Team',
        authorInitials: 'ST',
        time: '1 hour ago',
        content: 'Workstation isolated and cleaned. Alert resolved.'
      }
    ]
  },
  {
    id: 4,
    createTime: '2023-10-27 11:45:21',
    title: 'Multiple Failed Login Attempts for admin account',
    riskLevel: 'medium',
    status: 'open',
    owner: '赵六',
    severity: 'medium',
    ruleName: 'Brute Force Detection',
    timestamp: '2023-10-27 11:45:21 UTC',
    aiAnalysis: {
      confidence: 'high',
      summary: 'Brute Force Attack Detected',
      description: 'Multiple failed login attempts detected for the admin account. This appears to be a brute force attack.',
      recommendation: 'Block the source IP and enable account lockout policy.'
    },
    associatedEntities: [
      { type: 'host', name: 'auth-server-01', label: 'Host' },
      { type: 'ip', name: '192.168.1.100', label: 'Source IP' },
      { type: 'user', name: 'admin', label: 'Target User' }
    ],
    timeline: [
      { time: '11:45:21 UTC', event: 'Alert Triggered' },
      { time: '11:44:50 UTC', event: '10th Failed Attempt' },
      { time: '11:43:15 UTC', event: 'First Failed Attempt' }
    ],
    comments: []
  },
  {
    id: 5,
    createTime: '2023-10-27 10:20:00',
    title: 'Port Scan Detected from External IP 203.0.113.55',
    riskLevel: 'low',
    status: 'closed',
    owner: '孙七',
    severity: 'low',
    ruleName: 'Port Scan Detection',
    timestamp: '2023-10-27 10:20:00 UTC',
    aiAnalysis: {
      confidence: 'medium',
      summary: 'Port Scanning Activity Detected',
      description: 'Port scanning activity detected from an external IP address. This may be reconnaissance activity.',
      recommendation: 'Monitor the IP address and consider blocking if the activity continues.'
    },
    associatedEntities: [
      { type: 'ip', name: '203.0.113.55', label: 'Source IP' }
    ],
    timeline: [
      { time: '10:20:00 UTC', event: 'Alert Triggered' },
      { time: '10:19:30 UTC', event: 'Port Scan Started' }
    ],
    comments: [
      {
        id: 1,
        author: 'Network Team',
        authorInitials: 'NT',
        time: '3 hours ago',
        content: 'IP address added to monitoring list. No further action required at this time.'
      }
    ]
  }
]

/**
 * @brief 获取告警列表
 * @param {Object} params - 查询参数
 * @param {Array<string>} params.searchKeywords - 搜索关键字数组（支持多关键字AND搜索）
 * @param {string} params.status - 状态过滤
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 * @returns {Promise} 返回告警列表数据
 */
export const getAlerts = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredAlerts = [...mockAlerts]
      
      // 多关键字搜索过滤（AND逻辑：标题必须同时包含所有关键字）
      if (params.searchKeywords && params.searchKeywords.length > 0) {
        filteredAlerts = filteredAlerts.filter(alert => {
          const titleLower = alert.title.toLowerCase()
          // 检查标题是否同时包含所有关键字
          return params.searchKeywords.every(keyword => 
            titleLower.includes(keyword.toLowerCase())
          )
        })
      }
      
      // 状态过滤
      if (params.status && params.status !== 'all') {
        filteredAlerts = filteredAlerts.filter(alert => alert.status === params.status)
      }
      
      resolve({
        data: filteredAlerts,
        total: filteredAlerts.length,
        page: params.page || 1,
        pageSize: params.pageSize || 10
      })
    }, 300)
  })
}

// 获取告警详情
export const getAlertDetail = (id) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const alert = mockAlerts.find(a => a.id === parseInt(id))
      if (alert) {
        resolve({ data: alert })
      } else {
        reject(new Error('Alert not found'))
      }
    }, 200)
  })
}

// 获取统计数据
export const getAlertStatistics = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          totalAlerts: 1230,
          trend: 5.2,
          alertCount: 894,
          alertTrend: -1.8,
          mttd: '4.5 hours',
          mttdChange: 0.5,
          typeStats: [
            { name: 'Phishing', value: 40 },
            { name: 'Malware', value: 70 },
            { name: 'DDoS', value: 20 },
            { name: 'Ransomware', value: 60 },
            { name: 'Insider', value: 30 }
          ]
        }
      })
    }, 200)
  })
}

// 批量关闭告警
export const batchCloseAlerts = (params) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Batch closing alerts:', {
        alertIds: params.alertIds,
        category: params.category,
        notes: params.notes
      })
      
      // 更新mock数据中的告警状态
      params.alertIds.forEach(alertId => {
        const alert = mockAlerts.find(a => a.id === alertId)
        if (alert) {
          alert.status = 'closed'
        }
      })
      
      // 模拟成功响应
      resolve({
        success: true,
        message: `Successfully closed ${params.alertIds.length} alert(s)`,
        data: {
          closedCount: params.alertIds.length,
          category: params.category,
          notes: params.notes
        }
      })
    }, 500)
  })
}

// 开启告警
export const openAlert = (alertId) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Opening alert:', alertId)
      
      // 更新mock数据中的告警状态
      const alert = mockAlerts.find(a => a.id === alertId)
      if (alert) {
        alert.status = 'open'
      } else {
        reject(new Error('Alert not found'))
        return
      }
      
      // 模拟成功响应
      resolve({
        success: true,
        message: 'Successfully opened alert',
        data: {
          alertId: alertId,
          status: 'open'
        }
      })
    }, 500)
  })
}

// 关联告警到事件
export const associateAlertsToIncident = (params) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Associating alerts to incident:', {
        alertIds: params.alertIds,
        incidentId: params.incidentId
      })
      
      // 模拟成功响应
      resolve({
        success: true,
        message: `Successfully associated ${params.alertIds.length} alert(s) to incident ${params.incidentId}`,
        data: {
          associatedCount: params.alertIds.length,
          incidentId: params.incidentId
        }
      })
    }, 500)
  })
}

/**
 * @brief 威胁情报匹配数据（Mock）
 * @details 包含恶意IP、TTP、Campaign、Vulnerability等威胁情报信息
 */
const mockThreatIntelligence = {
  1: [
    {
      id: 1,
      type: 'ip',
      title: 'Malicious IP: 192.168.1.100',
      description: 'IP associated with known botnet activity and SSH brute-force campaigns. Classified as high-confidence threat.',
      source: 'SOC Team',
      timestamp: '2023-10-26 09:15:00'
    },
    {
      id: 2,
      type: 'ttp',
      title: 'TTP: T1078 - Valid Accounts',
      description: 'Adversaries may obtain and abuse credentials of existing accounts as a means of gaining initial access, persistence, privilege escalation, or defense evasion.',
      source: 'Threat Intel Feed',
      timestamp: '2023-10-25 11:30:21'
    },
    {
      id: 3,
      type: 'campaign',
      title: 'Campaign: "Winter Dragon"',
      description: 'Ongoing campaign targeting financial institutions using SSH brute-force and credential stuffing. The source IP is a known indicator for this campaign.',
      source: 'Alex Smith',
      timestamp: '2023-10-24 18:05:44'
    },
    {
      id: 4,
      type: 'vulnerability',
      title: 'Vulnerability: CVE-2023-4863',
      description: 'Heap buffer overflow in WebP in Google Chrome prior to 116.0.5845.187 and libwebp 1.3.2 allowed a remote attacker to perform an out of bounds memory write.',
      source: 'NVD Feed',
      timestamp: '2023-09-11 10:00:00'
    }
  ],
  2: [
    {
      id: 1,
      type: 'ip',
      title: 'Suspicious IP: 203.0.113.45',
      description: 'IP address with no prior successful login history. Multiple failed login attempts detected.',
      source: 'Security Team',
      timestamp: '2023-10-27 13:50:00'
    }
  ],
  4: [
    {
      id: 1,
      type: 'ip',
      title: 'Malicious IP: 192.168.1.100',
      description: 'IP associated with known brute-force attacks targeting admin accounts.',
      source: 'Threat Intel Feed',
      timestamp: '2023-10-27 11:40:00'
    },
    {
      id: 2,
      type: 'ttp',
      title: 'TTP: T1110 - Brute Force',
      description: 'Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.',
      source: 'MITRE ATT&CK',
      timestamp: '2023-10-27 11:35:00'
    }
  ]
}

/**
 * @brief 关联告警数据（Mock）
 * @details 包含与当前告警相关的其他告警信息
 */
const mockAssociatedAlerts = {
  1: [
    {
      id: 4,
      title: 'Multiple Failed Login Attempts for admin account',
      description: 'Detected 15 failed login attempts within 5 minutes from IP 192.168.1.100 targeting the admin account. This may indicate a brute force attack.',
      createTime: '2023-10-27 11:45:21',
      owner: 'John Smith',
      riskLevel: 'medium',
      status: 'open',
      severity: 'medium'
    },
    {
      id: 2,
      title: 'Unusual Login Activity from an Unrecognized IP',
      description: 'Successful login detected from IP address 203.0.113.45 which has not been seen in the past 90 days. User account: jane.doe@company.com',
      createTime: '2023-10-27 13:55:02',
      owner: 'Sarah Johnson',
      riskLevel: 'medium',
      status: 'pending',
      severity: 'medium'
    }
  ],
  2: [
    {
      id: 1,
      title: 'SQL Injection Attempt Detected on Server DB01',
      description: 'Potential SQL injection attack detected in web application logs. Malicious payload identified in POST request to /api/users endpoint.',
      createTime: '2023-10-27 14:30:15',
      owner: 'Mike Chen',
      riskLevel: 'high',
      status: 'open',
      severity: 'high'
    }
  ],
  4: [
    {
      id: 1,
      title: 'SQL Injection Attempt Detected on Server DB01',
      description: 'Potential SQL injection attack detected in web application logs. Malicious payload identified in POST request to /api/users endpoint.',
      createTime: '2023-10-27 14:30:15',
      owner: 'Mike Chen',
      riskLevel: 'high',
      status: 'open',
      severity: 'high'
    },
    {
      id: 2,
      title: 'Unusual Login Activity from an Unrecognized IP',
      description: 'Successful login detected from IP address 203.0.113.45 which has not been seen in the past 90 days. User account: jane.doe@company.com',
      createTime: '2023-10-27 13:55:02',
      owner: 'Sarah Johnson',
      riskLevel: 'medium',
      status: 'pending',
      severity: 'medium'
    }
  ]
}

/**
 * @brief 获取告警的威胁情报信息
 * @param {number|string} alertId - 告警ID
 * @returns {Promise} 返回威胁情报数据
 */
export const getThreatIntelligence = (alertId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const threatIntel = mockThreatIntelligence[parseInt(alertId)] || []
      resolve({ data: threatIntel })
    }, 200)
  })
}

/**
 * @brief 获取告警的关联告警列表
 * @param {number|string} alertId - 告警ID
 * @returns {Promise} 返回关联告警数据
 */
export const getAssociatedAlerts = (alertId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const associatedAlerts = mockAssociatedAlerts[parseInt(alertId)] || []
      resolve({ data: associatedAlerts })
    }, 200)
  })
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
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Creating alert:', data)
      
      // 生成新的告警ID
      const newId = Math.max(...mockAlerts.map(a => a.id), 0) + 1
      
      // 处理时间戳
      const timestamp = data.timestamp 
        ? (data.timestamp instanceof Date ? data.timestamp.toISOString() : data.timestamp)
        : new Date().toISOString()
      
      // 格式化创建时间
      const now = new Date()
      const createTime = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
      
      // 创建新告警对象
      const newAlert = {
        id: newId,
        createTime: createTime,
        title: data.title,
        riskLevel: data.riskLevel || 'medium',
        status: data.status || 'open',
        owner: data.owner,
        severity: data.riskLevel || 'medium',
        ruleName: data.ruleName || 'Manual Alert',
        timestamp: timestamp,
        description: data.description,
        aiAnalysis: null,
        associatedEntities: [],
        timeline: [
          { time: timestamp, event: 'Alert Created' }
        ],
        comments: []
      }
      
      // 添加到mock数据
      mockAlerts.unshift(newAlert)
      
      // 模拟成功响应
      resolve({
        success: true,
        message: 'Successfully created alert',
        data: newAlert
      })
    }, 500)
  })
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
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Updating alert:', alertId, data)
      
      // 查找告警
      const alert = mockAlerts.find(a => a.id === parseInt(alertId))
      if (!alert) {
        reject(new Error('Alert not found'))
        return
      }
      
      // 更新告警字段
      if (data.title !== undefined) alert.title = data.title
      if (data.riskLevel !== undefined) {
        alert.riskLevel = data.riskLevel
        alert.severity = data.riskLevel // 同时更新severity
      }
      if (data.status !== undefined) alert.status = data.status
      if (data.owner !== undefined) alert.owner = data.owner
      if (data.description !== undefined) alert.description = data.description
      if (data.ruleName !== undefined) alert.ruleName = data.ruleName
      if (data.timestamp !== undefined) {
        alert.timestamp = data.timestamp instanceof Date 
          ? data.timestamp.toISOString() 
          : data.timestamp
      }
      
      // 模拟成功响应
      resolve({
        success: true,
        message: 'Successfully updated alert',
        data: alert
      })
    }, 500)
  })
}

