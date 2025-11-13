from datetime import datetime

from flask import request
from flask_restful import Resource

from controllers.stats_service import StatisticsService
from utils.logger_init import logger


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
            data = StatisticsService.get_alert_count_by_product_name(start_date)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500