from datetime import datetime

from flask import request
from flask_restful import Resource

from controllers.stats_service import StatisticsService
from utils.logger_init import logger


class AlertCountBySourceView(Resource):

    # @jwt_required()
    def get(self):
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        chart_name = request.args.get("chart")
        status = request.args.get("status")  # Get status filter parameter

        if not start_date_str:
            return {"error_message": "start_date is required"}, 400

        try:
            start_date = datetime.fromisoformat(start_date_str)
        except ValueError:
            return {"error_message": "start_date must be in ISO 8601 format"}, 400

        try:
            if chart_name == "data-source-count":
                # end_date is optional for data-source-count chart
                end_date = None
                if end_date_str:
                    try:
                        end_date = datetime.fromisoformat(end_date_str)
                    except ValueError:
                        return {"error_message": "end_date must be in ISO 8601 format"}, 400
                data = StatisticsService.get_alert_count_by_product_name(start_date, end_date=end_date, status=status)
                return {"data": data}, 200
            elif chart_name == "alert-trend":
                # For trend chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for alert-trend chart"}, 400
                try:
                    end_date = datetime.fromisoformat(end_date_str)
                except ValueError:
                    return {"error_message": "end_date must be in ISO 8601 format"}, 400
                data = StatisticsService.get_alert_trend(start_date, end_date)
                return {"data": data}, 200
            elif chart_name == "incident-trend":
                # For incident trend chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for incident-trend chart"}, 400
                try:
                    end_date = datetime.fromisoformat(end_date_str)
                except ValueError:
                    return {"error_message": "end_date must be in ISO 8601 format"}, 400
                data = StatisticsService.get_incident_trend(start_date, end_date)
                return {"data": data}, 200
            else:
                raise Exception("chart_name is invalid")
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500