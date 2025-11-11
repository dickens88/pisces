"""
告警相关的Mock API视图
实现前端alerts.js中的所有mock接口
"""
import json
from datetime import datetime
from flask import request
from flask_restful import Resource
from data.mock_data import (
    MOCK_ALERTS,
    MOCK_THREAT_INTELLIGENCE,
    MOCK_ASSOCIATED_ALERTS
)
from utils.logger_init import logger

# 使用列表副本以便修改
mock_alerts = [alert.copy() for alert in MOCK_ALERTS]


class MockAlertListView(Resource):
    """获取告警列表"""
    
    def get(self):
        return self._handle_request()
    
    def post(self):
        return self._handle_request()
    
    def _handle_request(self):
        try:
            # 支持GET和POST请求
            if request.method == 'POST':
                params = json.loads(request.data) if request.data else {}
            else:
                params = request.args.to_dict()
            
            search_keywords = params.get('searchKeywords', '')
            status = params.get('status', 'all')
            page = int(params.get('page', 1))
            page_size = int(params.get('pageSize', 10))
            
            filtered_alerts = [alert.copy() for alert in mock_alerts]
            
            # 多关键字搜索过滤（AND逻辑：标题必须同时包含所有关键字）
            if search_keywords:
                if isinstance(search_keywords, str):
                    keywords = [k.strip() for k in search_keywords.split(',') if k.strip()]
                elif isinstance(search_keywords, list):
                    keywords = search_keywords
                else:
                    keywords = []
                
                if len(keywords) > 0:
                    filtered_alerts = [alert for alert in filtered_alerts 
                                     if all(keyword.lower() in alert['title'].lower() for keyword in keywords)]
            
            # 状态过滤
            if status and status != 'all':
                filtered_alerts = [alert for alert in filtered_alerts if alert['status'] == status]
            
            # 分页
            total = len(filtered_alerts)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_data = filtered_alerts[start:end]
            
            return {
                "data": paginated_data,
                "total": total,
                "page": page,
                "pageSize": page_size
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockAlertDetailView(Resource):
    """获取告警详情"""
    
    def get(self, alert_id):
        try:
            alert = next((a for a in mock_alerts if a['id'] == int(alert_id)), None)
            if alert:
                return {"data": alert}, 200
            else:
                return {"error_message": "Alert not found"}, 404
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockAlertStatisticsView(Resource):
    """获取告警统计数据"""
    
    def get(self):
        try:
            return {
                "data": {
                    "totalAlerts": 1230,
                    "trend": 5.2,
                    "alertCount": 894,
                    "alertTrend": -1.8,
                    "mttd": "4.5 hours",
                    "mttdChange": 0.5,
                    "typeStats": [
                        {"name": "Phishing", "value": 40},
                        {"name": "Malware", "value": 70},
                        {"name": "DDoS", "value": 20},
                        {"name": "Ransomware", "value": 60},
                        {"name": "Insider", "value": 30}
                    ]
                }
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockBatchCloseAlertsView(Resource):
    """批量关闭告警"""
    
    def post(self):
        try:
            data = json.loads(request.data)
            alert_ids = data.get('alertIds', [])
            category = data.get('category', '')
            notes = data.get('notes', '')
            
            closed_count = 0
            for alert_id in alert_ids:
                alert = next((a for a in mock_alerts if a['id'] == alert_id), None)
                if alert:
                    alert['status'] = 'closed'
                    closed_count += 1
            
            return {
                "success": True,
                "message": f"Successfully closed {closed_count} alert(s)",
                "data": {
                    "closedCount": closed_count,
                    "category": category,
                    "notes": notes
                }
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockOpenAlertView(Resource):
    """开启告警"""
    
    def post(self, alert_id):
        try:
            alert = next((a for a in mock_alerts if a['id'] == int(alert_id)), None)
            if alert:
                alert['status'] = 'open'
                return {
                    "success": True,
                    "message": "Successfully opened alert",
                    "data": {
                        "alertId": int(alert_id),
                        "status": "open"
                    }
                }, 200
            else:
                return {"error_message": "Alert not found"}, 404
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockAssociateAlertsToIncidentView(Resource):
    """关联告警到事件"""
    
    def post(self):
        try:
            data = json.loads(request.data)
            alert_ids = data.get('alertIds', [])
            incident_id = data.get('incidentId')
            
            return {
                "success": True,
                "message": f"Successfully associated {len(alert_ids)} alert(s) to incident {incident_id}",
                "data": {
                    "associatedCount": len(alert_ids),
                    "incidentId": incident_id
                }
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockThreatIntelligenceView(Resource):
    """获取告警的威胁情报信息"""
    
    def get(self, alert_id):
        try:
            threat_intel = MOCK_THREAT_INTELLIGENCE.get(int(alert_id), [])
            return {"data": threat_intel}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockAssociatedAlertsView(Resource):
    """获取告警的关联告警列表"""
    
    def get(self, alert_id):
        try:
            associated_alerts = MOCK_ASSOCIATED_ALERTS.get(int(alert_id), [])
            return {"data": associated_alerts}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockCreateAlertView(Resource):
    """创建告警"""
    
    def post(self):
        try:
            data = json.loads(request.data)
            
            # 生成新的告警ID
            new_id = max([a['id'] for a in mock_alerts], default=0) + 1
            
            # 处理时间戳
            timestamp = data.get('timestamp')
            if not timestamp:
                timestamp = datetime.now().isoformat() + ' UTC'
            elif isinstance(timestamp, str):
                pass  # 保持原样
            else:
                timestamp = timestamp.isoformat() + ' UTC'
            
            # 格式化创建时间
            now = datetime.now()
            create_time = now.strftime('%Y-%m-%d %H:%M:%S')
            
            # 创建新告警对象
            new_alert = {
                "id": new_id,
                "createTime": create_time,
                "title": data.get('title', ''),
                "riskLevel": data.get('riskLevel', 'medium'),
                "status": data.get('status', 'open'),
                "owner": data.get('owner', ''),
                "severity": data.get('riskLevel', 'medium'),
                "ruleName": data.get('ruleName', 'Manual Alert'),
                "timestamp": timestamp,
                "description": data.get('description', ''),
                "aiAnalysis": None,
                "associatedEntities": [],
                "timeline": [
                    {"time": timestamp, "event": "Alert Created"}
                ],
                "comments": []
            }
            
            # 添加到mock数据
            mock_alerts.insert(0, new_alert)
            
            return {
                "success": True,
                "message": "Successfully created alert",
                "data": new_alert
            }, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockUpdateAlertView(Resource):
    """更新告警"""
    
    def put(self, alert_id):
        try:
            data = json.loads(request.data)
            alert = next((a for a in mock_alerts if a['id'] == int(alert_id)), None)
            
            if not alert:
                return {"error_message": "Alert not found"}, 404
            
            # 更新告警字段
            if 'title' in data:
                alert['title'] = data['title']
            if 'riskLevel' in data:
                alert['riskLevel'] = data['riskLevel']
                alert['severity'] = data['riskLevel']  # 同时更新severity
            if 'status' in data:
                alert['status'] = data['status']
            if 'owner' in data:
                alert['owner'] = data['owner']
            if 'description' in data:
                alert['description'] = data['description']
            if 'ruleName' in data:
                alert['ruleName'] = data['ruleName']
            if 'timestamp' in data:
                timestamp = data['timestamp']
                if isinstance(timestamp, str):
                    alert['timestamp'] = timestamp
                else:
                    alert['timestamp'] = timestamp.isoformat() + ' UTC'
            
            return {
                "success": True,
                "message": "Successfully updated alert",
                "data": alert
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

