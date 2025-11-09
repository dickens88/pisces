import service from './index'

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

// 获取告警列表
export const getAlerts = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredAlerts = [...mockAlerts]
      
      // 简单的搜索过滤
      if (params.search) {
        const searchLower = params.search.toLowerCase()
        filteredAlerts = filteredAlerts.filter(alert => 
          alert.title.toLowerCase().includes(searchLower) ||
          alert.riskLevel.toLowerCase().includes(searchLower) ||
          alert.status.toLowerCase().includes(searchLower)
        )
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

