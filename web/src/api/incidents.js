import service from './axios.js'

// Mock数据
const mockIncidents = [
  {
    id: 73519,
    severity: 'high',
    name: '检测到恶意软件: Trojan.GenericKD.312...',
    responsibleDepartment: '安全运营部',
    rootCause: '弱口令',
    occurrenceTime: '2023-10-27 14:30:15',
    status: 'pending',
    fullName: '检测到恶意软件: Trojan.GenericKD.312456789',
    eventId: 73519
  },
  {
    id: 73518,
    severity: 'medium',
    name: '多次登录失败',
    responsibleDepartment: 'IT运维部',
    rootCause: '弱配置',
    occurrenceTime: '2023-10-27 14:25:01',
    status: 'inProgress',
    fullName: '多次登录失败',
    eventId: 73518
  },
  {
    id: 73517,
    severity: 'low',
    name: '策略变更: 防火墙规则更新',
    responsibleDepartment: '网络管理部',
    rootCause: '弱配置',
    occurrenceTime: '2023-10-27 14:20:55',
    status: 'closed',
    fullName: '策略变更: 防火墙规则更新',
    eventId: 73517
  },
  {
    id: 73516,
    severity: 'high',
    name: '检测到数据泄露企图',
    responsibleDepartment: '安全运营部',
    rootCause: '高危端口暴露',
    occurrenceTime: '2023-10-27 14:15:23',
    status: 'pending',
    fullName: '检测到数据泄露企图',
    eventId: 73516
  },
  {
    id: 73515,
    severity: 'medium',
    name: '检测到异常网络扫描',
    responsibleDepartment: 'IT运维部',
    rootCause: '未授权接口',
    occurrenceTime: '2023-10-27 14:10:02',
    status: 'pending',
    fullName: '检测到异常网络扫描',
    eventId: 73515
  }
]

// 获取事件列表
export const getIncidents = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredIncidents = [...mockIncidents]
      
      // 搜索过滤
      if (params.search) {
        const searchLower = params.search.toLowerCase()
        filteredIncidents = filteredIncidents.filter(incident => 
          incident.name.toLowerCase().includes(searchLower) ||
          (incident.responsibleDepartment && incident.responsibleDepartment.toLowerCase().includes(searchLower)) ||
          (incident.rootCause && incident.rootCause.toLowerCase().includes(searchLower))
        )
      }
      
      // 严重等级过滤
      if (params.severity && params.severity !== 'all') {
        filteredIncidents = filteredIncidents.filter(incident => incident.severity === params.severity)
      }
      
      // 状态过滤
      if (params.status && params.status !== 'all') {
        filteredIncidents = filteredIncidents.filter(incident => incident.status === params.status)
      }
      
      resolve({
        data: filteredIncidents,
        total: filteredIncidents.length,
        page: params.page || 1,
        pageSize: params.pageSize || 10
      })
    }, 300)
  })
}

// 批量关闭事件
export const batchCloseIncidents = (params) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Batch closing incidents:', {
        incidentIds: params.incidentIds,
        category: params.category,
        notes: params.notes
      })
      
      // 模拟成功响应
      resolve({
        success: true,
        message: `Successfully closed ${params.incidentIds.length} incident(s)`,
        data: {
          closedCount: params.incidentIds.length,
          category: params.category,
          notes: params.notes
        }
      })
    }, 500)
  })
}

// 创建事件
export const createIncident = (data) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Creating incident:', data)
      
      // 模拟成功响应
      const newIncident = {
        id: Date.now(),
        severity: 'medium',
        name: data.title,
        responsibleDepartment: data.responsibleDepartment || '-',
        rootCause: data.rootCause || '-',
        occurrenceTime: data.occurrenceTime,
        status: data.status || 'open',
        fullName: data.title,
        eventId: Date.now(),
        ...data
      }
      
      resolve({
        success: true,
        message: 'Successfully created incident',
        data: newIncident
      })
    }, 500)
  })
}

// 更新事件
export const updateIncident = (id, data) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Mock API调用
      console.log('Updating incident:', id, data)
      
      // 模拟成功响应，保存所有字段
      const now = new Date().toISOString()
      const updatedIncident = {
        id: parseInt(id),
        eventId: parseInt(id),
        name: data.title,
        title: data.title,
        severity: 'high', // 保持原有严重等级
        status: data.status || 'open',
        category: data.category || 'platform',
        responsibleDepartment: data.responsibleDepartment || '',
        responsiblePerson: data.responsiblePerson || '',
        rootCause: data.rootCause || '',
        occurrenceTime: data.occurrenceTime,
        description: data.description || '',
        fullName: data.title,
        createTime: data.createTime || now, // 保留创建时间
        updateTime: now, // 更新最后更新时间
        // 保留其他字段（如果有）
        affectedAssets: 4
      }
      
      resolve({
        success: true,
        message: 'Successfully updated incident',
        data: updatedIncident
      })
    }, 500)
  })
}

// 获取事件详情
export const getIncidentDetail = (id) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const incident = {
        id: 73519,
        eventId: 73519,
        name: 'Potential Ransomware Activity Detected on SRV-FIN-02',
        title: 'Potential Ransomware Activity Detected on SRV-FIN-02',
        severity: 'high',
        status: 'inProgress',
        affectedAssets: 4,
        category: 'platform',
        responsibleDepartment: '安全运营部',
        responsiblePerson: 'Anna Lawson',
        rootCause: 'weakPassword',
        occurrenceTime: '2023-10-27T14:30:15',
        createTime: '2023-10-27T14:30:15',
        updateTime: '2023-10-27T15:45:30',
        description: 'This event correlates multiple high-severity alerts indicating a sophisticated attack targeting financial server SRV-FIN-02. The attack chain began with a successful phishing attempt, followed by PowerShell execution for persistence, command and control communication, and culminating in widespread file encryption activity characteristic of ransomware. The affected asset is a critical server containing sensitive financial data, elevating the incident\'s impact. Immediate response is required to contain the threat and prevent further data loss.',
        associatedAlerts: [
          {
            id: 1,
            timestamp: '2023-10-27 14:30:15',
            description: 'SQL Injection Attempt Detected on Server DB01',
            severity: 'high',
            status: 'open'
          },
          {
            id: 2,
            timestamp: '2023-10-27 13:55:02',
            description: 'Unusual Login Activity from an Unrecognized IP',
            severity: 'medium',
            status: 'pending'
          },
          {
            id: 3,
            timestamp: '2023-10-27 12:10:48',
            description: 'Potential Malware Detected on Workstation WS102',
            severity: 'high',
            status: 'closed'
          },
          {
            id: 4,
            timestamp: '2023-10-27 11:45:21',
            description: 'Multiple Failed Login Attempts for admin account',
            severity: 'medium',
            status: 'open'
          },
          {
            id: 5,
            timestamp: '2023-10-27 10:20:00',
            description: 'Port Scan Detected from External IP 203.0.113.55',
            severity: 'low',
            status: 'closed'
          }
        ],
        comments: [
          {
            id: 1,
            author: 'Anna Lawson',
            authorInitials: 'AL',
            avatarColor: 'bg-teal-500',
            time: '2 hours ago',
            content: 'Initial analysis complete. The activity appears to originate from user \'john.doe\'s workstation. I\'ve isolated the host from the network and am proceeding with digital forensics to determine the full scope of the compromise. Assigning this to myself for now.'
          },
          {
            id: 2,
            author: 'Robert Miles',
            authorInitials: 'RM',
            avatarColor: 'bg-rose-500',
            time: '1 hour ago',
            content: 'Good work, Anna. I\'ve checked the firewall logs and found corresponding C2 traffic from the isolated host to 198.51.100.24:4444. I\'ve added a block rule for this IP address across the entire network.'
          },
          {
            id: 3,
            author: 'Sarah Chen (Manager)',
            authorInitials: 'SC',
            avatarColor: 'bg-indigo-500',
            time: '35 minutes ago',
            content: 'Thanks for the quick response, team. Let\'s make sure we document all IOCs and update the incident response plan with our findings. Keep me posted on the forensics report.'
          },
          {
            id: 4,
            author: 'Anna Lawson',
            authorInitials: 'AL',
            avatarColor: 'bg-teal-500',
            time: '5 minutes ago',
            content: 'Forensics image is being captured. ETA is approximately 45 minutes. I will start the analysis as soon as it\'s ready.'
          }
        ],
        timeline: [
          {
            time: '10:20:00 AM',
            title: 'Port Scan Detected from External IP',
            description: 'Port scanning activity detected from an external IP address.',
            alertId: 5,
            icon: 'network_check',
            severity: 'low'
          },
          {
            time: '11:45:21 AM',
            title: 'Multiple Failed Login Attempts for admin account',
            description: 'Multiple failed login attempts detected for the admin account.',
            alertId: 4,
            icon: 'lock',
            severity: 'medium'
          },
          {
            time: '12:10:48 PM',
            title: 'Potential Malware Detected on Workstation',
            description: 'A known malware signature was detected on the workstation.',
            alertId: 3,
            icon: 'security',
            severity: 'high'
          },
          {
            time: '1:55:02 PM',
            title: 'Unusual Login Activity from an Unrecognized IP',
            description: 'Multiple login attempts from an unrecognized IP address.',
            alertId: 2,
            icon: 'login',
            severity: 'medium'
          },
          {
            time: '2:30:15 PM',
            title: 'SQL Injection Attempt Detected on Server',
            description: 'SQL injection attempt targeting the database server detected.',
            alertId: 1,
            icon: 'bug_report',
            severity: 'high'
          }
        ],
        attackChainImage: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCKh_sUB5SQUBCbBOxHH4SP4hVt31y_aYmZDI29LgiJNMW14lw9g285Ca0bAi2DpUCcD8XumNMBjNYsDNUWONOiBDUWhX0YkwnkYbaakOyh_9PvKmsIS_2xyr-zF2S2MW9U9T5aVyURip4pe-LyVw9XUAB1nI3Y5gqy5PCXD-gGM7h4PpIJ5hvMBBJmGKcTIvJ3YQJ1IiPrvyjXexda43jh3Pfg0fArfIT5PCEQVYUGr1kK57zbehza2uu4O1TJadCMTDfFF4D7YPE_'
      }
      
      if (parseInt(id) === 73519) {
        resolve({ data: incident })
      } else {
        // 为其他ID生成模拟数据
        const baseIncident = mockIncidents.find(i => i.id === parseInt(id))
        if (baseIncident) {
          // 映射 rootCause 的中文到英文
          const rootCauseMap = {
            '弱口令': 'weakPassword',
            '弱配置': 'weakConfig',
            '高危端口暴露': 'exposedPort',
            '未授权接口': 'unauthorizedApi',
            '历史漏洞': 'historicalVulnerability'
          }
          
          resolve({ 
            data: { 
              ...incident, 
              ...baseIncident, 
              eventId: baseIncident.id,
              title: baseIncident.name || baseIncident.fullName,
              name: baseIncident.name || baseIncident.fullName,
              category: baseIncident.category || 'platform',
              responsibleDepartment: baseIncident.responsibleDepartment || '安全运营部',
              responsiblePerson: baseIncident.responsiblePerson || '系统管理员',
              rootCause: rootCauseMap[baseIncident.rootCause] || baseIncident.rootCause || 'weakPassword',
              occurrenceTime: baseIncident.occurrenceTime || '2023-10-27T14:30:15',
              createTime: baseIncident.createTime || baseIncident.occurrenceTime || '2023-10-27T14:30:15',
              updateTime: baseIncident.updateTime || baseIncident.occurrenceTime || '2023-10-27T14:30:15',
              description: baseIncident.description || incident.description
            } 
          })
        } else {
          reject(new Error('Incident not found'))
        }
      }
    }, 200)
  })
}

