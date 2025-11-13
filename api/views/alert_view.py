from datetime import datetime

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from controllers.alert_service import AlertService
from utils.logger_init import logger

import json


class CreateAlertView(Resource):
    """Create alert view - handles POST /api/alerts/create"""
    
    # @jwt_required()
    def post(self):
        try:
            data = json.loads(request.data or "{}")
            created = AlertService.create_alert(data)
            return {"data": created}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class AlertView(Resource):

    # @jwt_required()
    def post(self, alert_id=None):
        data = json.loads(request.data or "{}")
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        time_range = int(data.get('time_range', 1))
        conditions = data.get('conditions', [])
        action = data.get('action')

        try:
            if action == 'list':
                data, total = AlertService.list_alerts(conditions, time_range, limit, offset)
                return {"data": data, "total": total}, 200
            elif action == 'create':
                # 从 data 中获取告警数据
                alert_data = data.get('data', data)
                created = AlertService.create_alert(alert_data)
                return {"data": created}, 201

        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    # @jwt_required()
    def get(self, alert_id):
        try:
            data = AlertService.retrieve_alert_and_comments(alert_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    # @jwt_required
    def put(self, alert_id):
        data = json.loads(request.data)
        action = data.get("action")

        try:
            if action == "update":
                update_info = data["data"]
                result = AlertService.update_alert(alert_id, update_info)
                return {"data": result}, 200
            elif action == "close":
                close_reason = data["data"]["close_reason"]
                close_comment = data["data"]["close_comment"]
                result = AlertService.close_alert(alert_id=alert_id, close_reason=close_reason, comment=close_comment)
                return {"data": result}, 200
            else:
                raise Exception(f"The action {action} is not supported")
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
