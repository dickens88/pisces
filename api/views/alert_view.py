from datetime import datetime

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from controllers.alert_service import AlertService
from utils.logger_init import logger

import json


class AlertView(Resource):

    # @jwt_required()
    def post(self, alert_id=None):
        data = json.loads(request.data)
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        time_range = int(data.get('time_range', 1))
        conditions = data.get('conditions', [])

        try:
            data, total = AlertService.list_alerts(conditions, time_range, limit, offset)
            return {"data": data, "total": total}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    # @jwt_required()
    def get(self, alert_id):
        try:
            data = AlertService.retrieve_alert_by_id(alert_id)
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


class AlertCountBySourceView(Resource):

    # @jwt_required()
    def get(self):
        start_date_str = request.args.get("start_date")
        if not start_date_str:
            return {"error_message": "start_date is required"}, 400

        try:
            start_date = datetime.fromisoformat(start_date_str)
        except ValueError:
            return {"error_message": "start_date must be in ISO 8601 format"}, 400

        try:
            data = AlertService.get_alert_count_by_product_name(start_date)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class AlertCreateFromSecmasterView(Resource):

    # @jwt_required()
    def post(self):
        payload = json.loads(request.data)
        print(payload)
        alert_id = payload.get("alert_id")
        if not alert_id:
            return {"error_message": "alert_id is required"}, 400

        try:
            result = AlertService.create_alert_from_secmaster(alert_id)
            response_body = {"message": "Alert synchronized successfully"}
            if result is not None:
                response_body["data"] = result
            return response_body, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500