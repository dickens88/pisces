import service from './axios.js'

/**
 * @brief 获取Dashboard统计数据
 * @details 返回告警数量、事件数、漏洞数、平均检测时间等统计信息
 * @return {Promise} 返回统计数据
 */
export const getDashboardStatistics = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          // 告警数量 (24小时)
          alertCount24h: 1258,
          alertCount24hChange: 12.5,
          alertCount24hTrend: 'up',
          
          // 事件数 (24小时)
          incidentCount24h: 1283594,
          incidentCount24hChange: -2.1,
          incidentCount24hTrend: 'down',
          
          // 漏洞数 (未关闭)
          vulnerabilityCount: 87,
          vulnerabilityCountChange: -5,
          vulnerabilityCountTrend: 'down',
          
          // 平均检测时间 (MTTD)
          mttd: '12m 34s',
          mttdChange: -1.2,
          mttdTrend: 'down',
          
          // 告警类型统计
          alertTypeStats: [
            { name: 'IAM', manual: 75, auto: 40 },
            { name: 'HSS', manual: 60, auto: 60 },
            { name: 'NDR', manual: 90, auto: 30 },
            { name: 'COP', manual: 50, auto: 55 },
            { name: 'SA', manual: 70, auto: 45 },
            { name: 'SIEM', manual: 85, auto: 80 }
          ],
          
          // AI研判正确率
          aiAccuracy: [
            { name: 'IAM', accuracy: 99.8 },
            { name: 'HSS', accuracy: 99.5 },
            { name: 'NDR', accuracy: 98.2 },
            { name: 'COP', accuracy: 99.1 },
            { name: 'SA', accuracy: 97.5 },
            { name: 'SIEM', accuracy: 99.9 }
          ]
        }
      })
    }, 200)
  })
}

/**
 * @brief 获取最近未关闭的告警
 * @details 返回最近未关闭的告警列表
 * @param {Object} params 查询参数
 * @param {Number} params.limit 返回数量限制，默认3
 * @return {Promise} 返回告警列表
 */
export const getRecentOpenAlerts = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mockAlerts = [
        {
          id: 1,
          severity: 'critical',
          name: 'Potential Ransomware Activity Detected',
          timestamp: '2024-05-27 10:45:12',
          sourceIp: '198.51.100.23',
          status: 'new'
        },
        {
          id: 2,
          severity: 'high',
          name: 'Multiple Failed Login Attempts',
          timestamp: '2024-05-27 10:42:55',
          sourceIp: '203.0.113.10',
          status: 'inProgress'
        },
        {
          id: 3,
          severity: 'medium',
          name: 'Anomalous Network Traffic to C2 Server',
          timestamp: '2024-05-27 10:39:01',
          sourceIp: '10.1.1.54',
          status: 'new'
        }
      ]
      
      resolve({
        data: mockAlerts.slice(0, params.limit || 3),
        total: mockAlerts.length
      })
    }, 200)
  })
}

/**
 * @brief 获取最近未关闭的漏洞
 * @details 返回最近未关闭的漏洞列表
 * @param {Object} params 查询参数
 * @param {Number} params.limit 返回数量限制，默认3
 * @return {Promise} 返回漏洞列表
 */
export const getRecentOpenVulnerabilities = (params = {}) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mockVulnerabilities = [
        {
          id: 1,
          cvss: 9.8,
          cvssLevel: 'critical',
          name: 'CVE-2024-1086: Linux Kernel Double Free',
          affectedAsset: 'linux-db-server-01',
          discoveryTime: '2024-05-27 08:12:30'
        },
        {
          id: 2,
          cvss: 8.8,
          cvssLevel: 'high',
          name: 'CVE-2023-38408: OpenSSH Remote Code Execution',
          affectedAsset: 'jump-host-2',
          discoveryTime: '2024-05-26 15:45:00'
        },
        {
          id: 3,
          cvss: 6.5,
          cvssLevel: 'medium',
          name: 'CVE-2024-21626: runC Process Escape',
          affectedAsset: 'k8s-node-03',
          discoveryTime: '2024-05-26 11:20:15'
        }
      ]
      
      resolve({
        data: mockVulnerabilities.slice(0, params.limit || 3),
        total: mockVulnerabilities.length
      })
    }, 200)
  })
}

