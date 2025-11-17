from flask import request
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.stats_service import StatisticsService
from utils.jwt_helper import auth_required
from utils.logger_init import logger

import json


class AlertView(Resource):

    @auth_required
    def post(self, username=None, alert_id=None):
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

    @auth_required
    def get(self, username=None, alert_id=None):
        try:
            data = AlertService.retrieve_alert_and_comments(alert_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, alert_id=None):
        data = json.loads(request.data)
        action = data.get("action")

        try:
            if not alert_id and "batch_ids" in data:
                # batch close alerts
                data_obj = data.get("data_object") or data.get("data", {})
                close_reason = data_obj.get("close_reason")
                close_comment = data_obj.get("close_comment")
                result = AlertService.batch_close_alert(data["batch_ids"],
                                                        close_reason=close_reason,
                                                        comment=close_comment,
                                                        owner=username)
                return {"data": result}, 200
            if action == "update":
                # update alert by id
                update_info = data["data"]
                update_info["actor"] = username
                result = AlertService.update_alert(alert_id, update_info)
                return {"data": result}, 200
            elif action == "close":
                # close alert by id
                close_reason = data["data"]["close_reason"]
                close_comment = data["data"]["close_comment"]
                result = AlertService.close_alert(alert_id=alert_id,
                                                  close_reason=close_reason,
                                                  comment=close_comment,
                                                  owner=username)
                return {"data": result}, 200
            else:
                raise Exception(f"The action {action} is not supported")
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class AlertStatisticsView(Resource):
    """View for alert statistics."""
    
    @auth_required
    def get(self, username=None):
        """Get alert statistics including automation closure rate."""
        try:
            data = StatisticsService.get_automation_closure_rate()
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
