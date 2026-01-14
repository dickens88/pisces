from flask import request
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from models.alert import Alert
from utils.auth_util import auth_required
from utils.logger_init import logger
from utils.common_utils import get_workspace_id

import json


class AlertView(Resource):

    @auth_required
    def post(self, username=None, alert_id=None):
        data = json.loads(request.data or "{}")
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        conditions = data.get('conditions', [])
        action = data.get('action')
        risk_mode = data.get('risk_mode')
        workspace_id = get_workspace_id(data.get('workspace'))

        try:
            if action == 'list':
                if not start_time or not end_time:
                    return {"error_message": "start_time and end_time are required"}, 400

                # Use workspace if provided, otherwise use default
                data, total = AlertService.list_alerts(
                    conditions,
                    limit=limit,
                    offset=offset,
                    start_time=start_time,
                    end_time=end_time,
                    high_risk=True if risk_mode == "highRisk" or risk_mode == "unclosedHighRisk" else False,
                    workspace_id=workspace_id,
                )
                return {"data": data, "total": total}, 200
            elif action == 'list_local':
                data, total = Alert.list_alerts(
                    conditions,
                    limit=limit,
                    offset=offset,
                    start_time=start_time,
                    end_time=end_time,
                    include_finetune=True,
                )
                return {"data": data, "total": total}, 200
            elif action == 'create':
                alert_data = data.get('data', data)
                created = AlertService.create_alert(alert_data, workspace_id=workspace_id)
                logger.info(f"[Alert] Create Alert: {alert_id} successfully.[{username}]")
                return {"data": created}, 201

        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def get(self, username=None, alert_id=None):
        try:
            action = request.args.get('action')
            workspace_id = get_workspace_id(request.args.get('workspace'))
            if action == "comments_extension":
                data = AlertService.retrieve_comments_and_timeline(alert_id, workspace_id=workspace_id)
            else:
                data = AlertService.retrieve_alert_and_entities(alert_id, workspace_id=workspace_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, alert_id=None):
        data = json.loads(request.data)
        action = data.get("action")
        workspace_id = get_workspace_id(data.get("workspace"))

        try:
            if not alert_id and "batch_ids" in data:
                # batch close alerts
                data_obj = data.get("data_object") or data.get("data", {})
                close_reason = data_obj.get("close_reason")
                close_comment = data_obj.get("close_comment")
                result = AlertService.batch_close_alert(data["batch_ids"],
                                                        close_reason=close_reason,
                                                        comment=close_comment,
                                                        actor=username,
                                                        workspace_id=workspace_id)
                logger.info(f"[Alert] Close Alerts: {data['batch_ids']} successfully.[{username}]")
                return {"data": result}, 200
            if action == "update":
                # update alert by id
                update_info = data["data"]
                update_info["actor"] = username
                result = AlertService.update_alert(alert_id, update_info, workspace_id=workspace_id)

                CommentService.create_comment(event_id=alert_id,
                                              comment=f"{username} updated the alert",
                                              workspace_id=workspace_id,
                                              note_type="update")
                logger.info(f"[Alert] Update Alert: {alert_id} successfully.[{username}]")
                return {"data": result}, 200
            elif action == "close":
                # close alert by id
                close_reason = data["data"]["close_reason"]
                close_comment = data["data"]["close_comment"]
                result = AlertService.close_alert(alert_id=alert_id,
                                                  close_reason=close_reason,
                                                  comment=close_comment,
                                                  actor=username,
                                                  workspace_id=workspace_id)
                logger.info(f"[Alert] Close Alert: {alert_id} successfully.[{username}]")
                return {"data": result}, 200
            else:
                raise Exception(f"The action {action} is not supported")
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def delete(self, username=None):
        data = json.loads(request.data)
        workspace_id = get_workspace_id(data.get("workspace"))

        try:
            ids = data["batch_ids"]
            result = AlertService.delete_alerts(ids, workspace_id=workspace_id)
            logger.warn(f"[Alert] Delete Alerts successfully. ids: {ids}. [{username}]")
            return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
