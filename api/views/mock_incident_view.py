"""
事件相关的Mock API视图
实现前端incidents.js中的所有mock接口
"""
import json
from datetime import datetime
from flask import request
from flask_restful import Resource
from data.mock_data import MOCK_INCIDENTS, MOCK_INCIDENT_DETAIL
from utils.logger_init import logger

# 使用列表副本以便修改
mock_incidents = [incident.copy() for incident in MOCK_INCIDENTS]


class MockBatchCloseIncidentsView(Resource):
    """批量关闭事件"""
    
    def post(self):
        try:
            data = json.loads(request.data)
            incident_ids = data.get('incidentIds', [])
            category = data.get('category', '')
            notes = data.get('notes', '')
            
            closed_count = 0
            for incident_id in incident_ids:
                incident = next((i for i in mock_incidents if i['id'] == incident_id), None)
                if incident:
                    incident['status'] = 'closed'
                    closed_count += 1
            
            return {
                "success": True,
                "message": f"Successfully closed {closed_count} incident(s)",
                "data": {
                    "closedCount": closed_count,
                    "category": category,
                    "notes": notes
                }
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockCreateIncidentView(Resource):
    """创建事件"""
    
    def post(self):
        try:
            data = json.loads(request.data)
            
            # 生成新的事件ID
            new_id = max([i['id'] for i in mock_incidents], default=73500) + 1
            
            now = datetime.now()
            occurrence_time = data.get('occurrenceTime', now.strftime('%Y-%m-%d %H:%M:%S'))
            
            new_incident = {
                "id": new_id,
                "severity": data.get('severity', 'medium'),
                "name": data.get('title', ''),
                "responsibleDepartment": data.get('responsibleDepartment', '-'),
                "rootCause": data.get('rootCause', '-'),
                "occurrenceTime": occurrence_time,
                "status": data.get('status', 'open'),
                "fullName": data.get('title', ''),
                "eventId": new_id
            }
            
            mock_incidents.insert(0, new_incident)
            
            return {
                "success": True,
                "message": "Successfully created incident",
                "data": new_incident
            }, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockUpdateIncidentView(Resource):
    """更新事件"""
    
    def put(self, incident_id):
        try:
            data = json.loads(request.data)
            incident = next((i for i in mock_incidents if i['id'] == int(incident_id)), None)
            
            if not incident:
                return {"error_message": "Incident not found"}, 404
            
            now = datetime.now().isoformat()
            
            # 更新事件字段
            if 'title' in data:
                incident['name'] = data['title']
                incident['fullName'] = data['title']
            if 'status' in data:
                incident['status'] = data['status']
            if 'category' in data:
                incident['category'] = data['category']
            if 'responsibleDepartment' in data:
                incident['responsibleDepartment'] = data['responsibleDepartment']
            if 'responsiblePerson' in data:
                incident['responsiblePerson'] = data['responsiblePerson']
            if 'rootCause' in data:
                incident['rootCause'] = data['rootCause']
            if 'occurrenceTime' in data:
                incident['occurrenceTime'] = data['occurrenceTime']
            if 'description' in data:
                incident['description'] = data['description']
            if 'createTime' in data:
                incident['createTime'] = data['createTime']
            else:
                incident['createTime'] = incident.get('createTime') or incident.get('occurrenceTime', now)
            incident['updateTime'] = now
            incident['affectedAssets'] = data.get('affectedAssets', 4)
            
            # 构建返回数据
            updated_incident = {
                "id": incident['id'],
                "eventId": incident['id'],
                "name": incident.get('name', ''),
                "title": incident.get('name', ''),
                "severity": incident.get('severity', 'high'),
                "status": incident.get('status', 'open'),
                "category": incident.get('category', 'platform'),
                "responsibleDepartment": incident.get('responsibleDepartment', ''),
                "responsiblePerson": incident.get('responsiblePerson', ''),
                "rootCause": incident.get('rootCause', ''),
                "occurrenceTime": incident.get('occurrenceTime', ''),
                "description": incident.get('description', ''),
                "fullName": incident.get('fullName', ''),
                "createTime": incident.get('createTime', now),
                "updateTime": incident.get('updateTime', now),
                "affectedAssets": incident.get('affectedAssets', 4)
            }
            
            return {
                "success": True,
                "message": "Successfully updated incident",
                "data": updated_incident
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

