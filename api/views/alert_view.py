from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from controllers.alert_service import AlertService
from utils.logger_init import logger

import json


class AlertView(Resource):

    # @jwt_required()
    def post(self):
        data = json.loads(request.data)
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        time_range = data.get('time_range', 1)
        conditions = data.get('conditions', [])

        try:
            data = AlertService.list_alerts(conditions, time_range, limit, offset)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500