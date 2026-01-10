import json

from flask import request
from flask_restful import Resource

from controllers.impacted_service_service import ImpactedServiceService
from utils.auth_util import auth_required
from utils.logger_init import logger


class ImpactedServiceView(Resource):
    """影响服务和事件简报视图类"""

    @auth_required
    def get(self, username=None, incident_id=None, service_id=None):
        """获取记录列表或单个记录"""
        try:
            if service_id:
                # 获取单个记录
                item = ImpactedServiceService.get_item(service_id)
                return {"data": item}, 200
            else:
                # 获取事件的所有记录
                if not incident_id:
                    return {"error_message": "incident_id is required"}, 400
                # 默认获取影响服务（向后兼容）
                items = ImpactedServiceService.list_services(incident_id)
                return {"data": items}, 200
        except ValueError as ex:
            logger.warning(f"[ImpactedService] {str(ex)}")
            return {"error_message": str(ex)}, 404
        except Exception as ex:
            logger.exception(f"[ImpactedService] Failed to get items: {ex}")
            return {"error_message": str(ex)}, 500

    @auth_required
    def post(self, username=None, incident_id=None):
        """创建新记录（影响服务）"""
        try:
            if not incident_id:
                return {"error_message": "incident_id is required"}, 400
            
            data = json.loads(request.data or "{}")
            item = ImpactedServiceService.create_service(incident_id, data)
            logger.info(f"[ImpactedService] Created impacted service for incident {incident_id} by {username}")
            return {"data": item}, 201
        except ValueError as ex:
            logger.warning(f"[ImpactedService] {str(ex)}")
            return {"error_message": str(ex)}, 400
        except Exception as ex:
            logger.exception(f"[ImpactedService] Failed to create impacted service: {ex}")
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, incident_id=None, service_id=None):
        """更新记录（影响服务）"""
        try:
            if not service_id:
                return {"error_message": "service_id is required"}, 400
            
            data = json.loads(request.data or "{}")
            item = ImpactedServiceService.update_service(service_id, data)
            logger.info(f"[ImpactedService] Updated impacted service {service_id} by {username}")
            return {"data": item}, 200
        except ValueError as ex:
            logger.warning(f"[ImpactedService] {str(ex)}")
            return {"error_message": str(ex)}, 404
        except Exception as ex:
            logger.exception(f"[ImpactedService] Failed to update impacted service: {ex}")
            return {"error_message": str(ex)}, 500

    @auth_required
    def delete(self, username=None, incident_id=None, service_id=None):
        """删除记录（影响服务）"""
        try:
            if not service_id:
                return {"error_message": "service_id is required"}, 400
            
            ImpactedServiceService.delete_service(service_id)
            logger.info(f"[ImpactedService] Deleted impacted service {service_id} by {username}")
            return {"message": "Impacted service deleted successfully"}, 200
        except ValueError as ex:
            logger.warning(f"[ImpactedService] {str(ex)}")
            return {"error_message": str(ex)}, 404
        except Exception as ex:
            logger.exception(f"[ImpactedService] Failed to delete impacted service: {ex}")
            return {"error_message": str(ex)}, 500


class IncidentBriefView(Resource):
    """事件简报视图类"""

    @auth_required
    def get(self, username=None, incident_id=None, notification_id=None):
        """获取事件简报列表或单个简报"""
        try:
            if notification_id:
                # 获取单个简报
                notification = ImpactedServiceService.get_item(notification_id)
                return {"data": notification}, 200
            else:
                # 获取事件的所有事件简报
                if not incident_id:
                    return {"error_message": "incident_id is required"}, 400
                notifications = ImpactedServiceService.list_notifications(incident_id)
                return {"data": notifications}, 200
        except ValueError as ex:
            logger.warning(f"[IncidentBrief] {str(ex)}")
            return {"error_message": str(ex)}, 404
        except Exception as ex:
            logger.exception(f"[IncidentBrief] Failed to get notifications: {ex}")
            return {"error_message": str(ex)}, 500

    @auth_required
    def post(self, username=None, incident_id=None):
        """创建新的事件简报"""
        try:
            if not incident_id:
                return {"error_message": "incident_id is required"}, 400
            
            data = json.loads(request.data or "{}")
            notification = ImpactedServiceService.create_notification(incident_id, data)
            logger.info(f"[IncidentBrief] Created notification for incident {incident_id} by {username}")
            return {"data": notification}, 201
        except ValueError as ex:
            logger.warning(f"[IncidentBrief] {str(ex)}")
            return {"error_message": str(ex)}, 400
        except Exception as ex:
            logger.exception(f"[IncidentBrief] Failed to create notification: {ex}")
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, incident_id=None, notification_id=None):
        """更新事件简报"""
        try:
            if not notification_id:
                return {"error_message": "notification_id is required"}, 400
            
            data = json.loads(request.data or "{}")
            notification = ImpactedServiceService.update_notification(notification_id, data)
            logger.info(f"[IncidentBrief] Updated notification {notification_id} by {username}")
            return {"data": notification}, 200
        except ValueError as ex:
            logger.warning(f"[IncidentBrief] {str(ex)}")
            return {"error_message": str(ex)}, 404
        except Exception as ex:
            logger.exception(f"[IncidentBrief] Failed to update notification: {ex}")
            return {"error_message": str(ex)}, 500

    @auth_required
    def delete(self, username=None, incident_id=None, notification_id=None):
        """删除事件简报"""
        try:
            if not notification_id:
                return {"error_message": "notification_id is required"}, 400
            
            ImpactedServiceService.delete_notification(notification_id)
            logger.info(f"[IncidentBrief] Deleted notification {notification_id} by {username}")
            return {"message": "Notification deleted successfully"}, 200
        except ValueError as ex:
            logger.warning(f"[IncidentBrief] {str(ex)}")
            return {"error_message": str(ex)}, 404
        except Exception as ex:
            logger.exception(f"[IncidentBrief] Failed to delete notification: {ex}")
            return {"error_message": str(ex)}, 500

