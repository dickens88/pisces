import service from './index'

// Mock数据
const mockIncidents = [
  {
    id: 73519,
    severity: 'high',
    name: '检测到恶意软件: Trojan.GenericKD.312...',
    sourceIp: '192.168.1.102',
    targetIp: '203.0.113.45',
    occurrenceTime: '2023-10-27 14:30:15',
    status: 'pending',
    fullName: '检测到恶意软件: Trojan.GenericKD.312456789',
    eventId: 73519
  },
  {
    id: 73518,
    severity: 'medium',
    name: '多次登录失败',
    sourceIp: '10.0.0.5',
    targetIp: '172.16.0.10',
    occurrenceTime: '2023-10-27 14:25:01',
    status: 'inProgress',
    fullName: '多次登录失败',
    eventId: 73518
  },
  {
    id: 73517,
    severity: 'low',
    name: '策略变更: 防火墙规则更新',
    sourceIp: 'admin@local',
    targetIp: 'firewall-01',
    occurrenceTime: '2023-10-27 14:20:55',
    status: 'closed',
    fullName: '策略变更: 防火墙规则更新',
    eventId: 73517
  },
  {
    id: 73516,
    severity: 'high',
    name: '检测到数据泄露企图',
    sourceIp: '192.168.1.150',
    targetIp: 'fileserver.internal',
    occurrenceTime: '2023-10-27 14:15:23',
    status: 'pending',
    fullName: '检测到数据泄露企图',
    eventId: 73516
  },
  {
    id: 73515,
    severity: 'medium',
    name: '检测到异常网络扫描',
    sourceIp: '103.22.14.8',
    targetIp: 'public-web-server',
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
          incident.sourceIp.toLowerCase().includes(searchLower) ||
          incident.targetIp.toLowerCase().includes(searchLower)
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

// 获取事件详情
export const getIncidentDetail = (id) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const incident = {
        id: 73519,
        eventId: 73519,
        name: 'Potential Ransomware Activity Detected on SRV-FIN-02',
        severity: 'high',
        status: 'inProgress',
        affectedAssets: 4,
        mitreTactic: 'TA0002',
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
          resolve({ data: { ...incident, ...baseIncident, eventId: baseIncident.id } })
        } else {
          reject(new Error('Incident not found'))
        }
      }
    }, 200)
  })
}

