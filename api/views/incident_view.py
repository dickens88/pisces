from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.incident_service import IncidentService
from utils.logger_init import logger

import json


class IncidentView(Resource):

    # @jwt_required()
    def post(self, alert_id=None):
        data = json.loads(request.data)
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        time_range = int(data.get('time_range', 1))
        conditions = data.get('conditions', [])

        try:
            data, total = IncidentService.list_incidents(conditions, time_range, limit, offset)
            return {"data": data, "total": total}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    # @jwt_required()
    def get(self, incident_id):
        try:
            data = IncidentService.retrieve_incident_by_id(incident_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class AlertCreateView(Resource):

    # @jwt_required()
    def post(self):
        try:
            payload = json.loads(request.data or "{}")
            created = AlertService.create_alert(payload)
            return {"data": created}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class AlertChangeStatusView(Resource):

    # @jwt_required()
    def put(self, alert_id):
        try:
            data = json.loads(request.data or "{}")
            status = data.get('status')
            if not status:
                return {"error_message": "status is required"}, 400

            close_comment = data.get('close_comment')
            close_reason = data.get('close_reason')

            AlertService.change_alert_status(alert_id, status, close_comment, close_reason)
            return {"message": "Alert status updated successfully"}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500