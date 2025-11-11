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


class MockIncidentListView(Resource):
    """获取事件列表"""
    
    def get(self):
        try:
            params = request.args.to_dict()
            search = params.get('search', '')
            severity = params.get('severity', 'all')
            status = params.get('status', 'all')
            page = int(params.get('page', 1))
            page_size = int(params.get('pageSize', 10))
            
            filtered_incidents = [incident.copy() for incident in mock_incidents]
            
            # 搜索过滤
            if search:
                search_lower = search.lower()
                filtered_incidents = [
                    incident for incident in filtered_incidents
                    if search_lower in incident['name'].lower() or
                    (incident.get('responsibleDepartment') and search_lower in incident['responsibleDepartment'].lower()) or
                    (incident.get('rootCause') and search_lower in incident['rootCause'].lower())
                ]
            
            # 严重等级过滤
            if severity and severity != 'all':
                filtered_incidents = [
                    incident for incident in filtered_incidents
                    if incident['severity'] == severity
                ]
            
            # 状态过滤
            if status and status != 'all':
                filtered_incidents = [
                    incident for incident in filtered_incidents
                    if incident['status'] == status
                ]
            
            # 分页
            total = len(filtered_incidents)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_data = filtered_incidents[start:end]
            
            return {
                "data": paginated_data,
                "total": total,
                "page": page,
                "pageSize": page_size
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class MockIncidentDetailView(Resource):
    """获取事件详情"""
    
    def get(self, incident_id):
        try:
            incident_id_int = int(incident_id)
            
            # 如果是73519，返回详细数据
            if incident_id_int == 73519:
                return {"data": MOCK_INCIDENT_DETAIL.copy()}, 200
            
            # 为其他ID生成模拟数据
            base_incident = next((i for i in mock_incidents if i['id'] == incident_id_int), None)
            if base_incident:
                # 映射 rootCause 的中文到英文
                root_cause_map = {
                    '弱口令': 'weakPassword',
                    '弱配置': 'weakConfig',
                    '高危端口暴露': 'exposedPort',
                    '未授权接口': 'unauthorizedApi',
                    '历史漏洞': 'historicalVulnerability'
                }
                
                incident_detail = MOCK_INCIDENT_DETAIL.copy()
                incident_detail.update({
                    **base_incident,
                    "eventId": base_incident['id'],
                    "title": base_incident.get('name') or base_incident.get('fullName', ''),
                    "name": base_incident.get('name') or base_incident.get('fullName', ''),
                    "category": base_incident.get('category', 'platform'),
                    "responsibleDepartment": base_incident.get('responsibleDepartment', '安全运营部'),
                    "responsiblePerson": base_incident.get('responsiblePerson', '系统管理员'),
                    "rootCause": root_cause_map.get(base_incident.get('rootCause'), base_incident.get('rootCause', 'weakPassword')),
                    "occurrenceTime": base_incident.get('occurrenceTime', '2023-10-27T14:30:15'),
                    "createTime": base_incident.get('createTime') or base_incident.get('occurrenceTime', '2023-10-27T14:30:15'),
                    "updateTime": base_incident.get('updateTime') or base_incident.get('occurrenceTime', '2023-10-27T14:30:15'),
                    "description": base_incident.get('description', incident_detail.get('description', ''))
                })
                
                return {"data": incident_detail}, 200
            else:
                return {"error_message": "Incident not found"}, 404
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


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

