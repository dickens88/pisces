"""
仪表板相关的Mock API视图
实现前端dashboard.js中的所有mock接口
"""
from flask_restful import Resource
from data.mock_data import MOCK_ALERTS, MOCK_VULNERABILITIES
from utils.logger_init import logger


class MockDashboardStatisticsView(Resource):
    """获取Dashboard统计数据"""
    
    def get(self):
        try:
            return {
                "data": {
                    # 告警数量 (24小时)
                    "alertCount24h": 1258,
                    "alertCount24hChange": 12.5,
                    "alertCount24hTrend": "up",
                    
                    # 事件数 (24小时)
                    "incidentCount24h": 1283594,
                    "incidentCount24hChange": -2.1,
                    "incidentCount24hTrend": "down",
                    
                    # 漏洞数 (未关闭)
                    "vulnerabilityCount": 87,
                    "vulnerabilityCountChange": -5,
                    "vulnerabilityCountTrend": "down",
                    
                    # 平均检测时间 (MTTD)
                    "mttd": "12m 34s",
                    "mttdChange": -1.2,
                    "mttdTrend": "down",
                    
                    # 告警类型统计
                    "alertTypeStats": [
                        {"name": "IAM", "manual": 75, "auto": 40},
                        {"name": "HSS", "manual": 60, "auto": 60},
                        {"name": "NDR", "manual": 90, "auto": 30},
                        {"name": "COP", "manual": 50, "auto": 55},
                        {"name": "SA", "manual": 70, "auto": 45},
                        {"name": "SIEM", "manual": 85, "auto": 80}
                    ],
                    
                    # AI研判正确率
                    "aiAccuracy": [
                        {"name": "IAM", "accuracy": 99.8},
                        {"name": "HSS", "accuracy": 99.5},
                        {"name": "NDR", "accuracy": 98.2},
                        {"name": "COP", "accuracy": 99.1},
                        {"name": "SA", "accuracy": 97.5},
                        {"name": "SIEM", "accuracy": 99.9}
                    ]
                }
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockRecentOpenAlertsView(Resource):
    """获取最近未关闭的告警"""
    
    def get(self):
        try:
            from flask import request
            params = request.args.to_dict()
            limit = int(params.get('limit', 3))
            
            # 从mock数据中筛选未关闭的告警
            open_alerts = [alert for alert in MOCK_ALERTS if alert['status'] != 'closed']
            
            # 转换为前端需要的格式
            mock_alerts = [
                {
                    "id": alert['id'],
                    "severity": alert['severity'],
                    "name": alert['title'],
                    "timestamp": alert['createTime'],
                    "sourceIp": next(
                        (entity['name'] for entity in alert.get('associatedEntities', []) if entity['type'] == 'ip'),
                        'N/A'
                    ),
                    "status": alert['status']
                }
                for alert in open_alerts[:limit]
            ]
            
            # 如果数据不足，使用默认数据
            if len(mock_alerts) < limit:
                default_alerts = [
                    {
                        "id": 1,
                        "severity": "critical",
                        "name": "Potential Ransomware Activity Detected",
                        "timestamp": "2024-05-27 10:45:12",
                        "sourceIp": "198.51.100.23",
                        "status": "new"
                    },
                    {
                        "id": 2,
                        "severity": "high",
                        "name": "Multiple Failed Login Attempts",
                        "timestamp": "2024-05-27 10:42:55",
                        "sourceIp": "203.0.113.10",
                        "status": "inProgress"
                    },
                    {
                        "id": 3,
                        "severity": "medium",
                        "name": "Anomalous Network Traffic to C2 Server",
                        "timestamp": "2024-05-27 10:39:01",
                        "sourceIp": "10.1.1.54",
                        "status": "new"
                    }
                ]
                mock_alerts = default_alerts[:limit]
            
            return {
                "data": mock_alerts,
                "total": len(mock_alerts)
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockRecentOpenVulnerabilitiesView(Resource):
    """获取最近未关闭的漏洞"""
    
    def get(self):
        try:
            from flask import request
            params = request.args.to_dict()
            limit = int(params.get('limit', 3))
            
            # 从mock数据中筛选未关闭的漏洞
            open_vulnerabilities = [
                vuln for vuln in MOCK_VULNERABILITIES 
                if vuln['status'] not in ['fixed', 'ignored']
            ]
            
            # 转换为前端需要的格式
            mock_vulnerabilities = [
                {
                    "id": vuln['id'],
                    "cvss": 9.8 if vuln['riskLevel'] == 'critical' else (8.8 if vuln['riskLevel'] == 'high' else 6.5),
                    "cvssLevel": vuln['riskLevel'],
                    "name": vuln['name'],
                    "affectedAsset": vuln['affectedAsset'],
                    "discoveryTime": vuln['firstDiscoveryTime'] + " 00:00:00"
                }
                for vuln in open_vulnerabilities[:limit]
            ]
            
            # 如果数据不足，使用默认数据
            if len(mock_vulnerabilities) < limit:
                default_vulnerabilities = [
                    {
                        "id": 1,
                        "cvss": 9.8,
                        "cvssLevel": "critical",
                        "name": "CVE-2024-1086: Linux Kernel Double Free",
                        "affectedAsset": "linux-db-server-01",
                        "discoveryTime": "2024-05-27 08:12:30"
                    },
                    {
                        "id": 2,
                        "cvss": 8.8,
                        "cvssLevel": "high",
                        "name": "CVE-2023-38408: OpenSSH Remote Code Execution",
                        "affectedAsset": "jump-host-2",
                        "discoveryTime": "2024-05-26 15:45:00"
                    },
                    {
                        "id": 3,
                        "cvss": 6.5,
                        "cvssLevel": "medium",
                        "name": "CVE-2024-21626: runC Process Escape",
                        "affectedAsset": "k8s-node-03",
                        "discoveryTime": "2024-05-26 11:20:15"
                    }
                ]
                mock_vulnerabilities = default_vulnerabilities[:limit]
            
            return {
                "data": mock_vulnerabilities,
                "total": len(mock_vulnerabilities)
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

