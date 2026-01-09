from datetime import datetime

from flask import request
from flask_restful import Resource

from controllers.stats_service import StatisticsService
from utils.common_utils import parse_datetime_with_timezone, format_utc_datetime_to_db_string
from utils.auth_util import auth_required
from utils.logger_init import logger


class AlertCountBySourceView(Resource):

    @auth_required
    def get(self, username=None):
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        chart_name_raw = request.args.get("chart")
        chart_name = (chart_name_raw or "").strip()
        chart_name_normalized = chart_name.lower()
        status = request.args.get("status")  # Get status filter parameter

        if not start_date_str:
            return {"error_message": "start_date is required"}, 400

        try:
            # Parse datetime with timezone and convert to UTC
            start_date = parse_datetime_with_timezone(start_date_str)
            if start_date is None:
                return {"error_message": "start_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
        except Exception as e:
            return {"error_message": f"Invalid start_date format: {str(e)}"}, 400

        try:
            if chart_name_normalized == "automation-closure-rate":
                # For automation-closure-rate chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for automation-closure-rate chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_automation_closure_rate(start_date, end_date)
                return {
                    "data": data,
                    "description": "Trend of alerts automatically closed by automation in the selected time range.",
                }, 200
            elif chart_name_normalized == "ai-judgment-coverage-rate":
                # For ai-judgment-coverage-rate chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for ai-judgment-coverage-rate chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_ai_judgment_coverage_rate(start_date, end_date)
                return {
                    "data": data,
                    "description": "AI judgment coverage rate in the selected time range.",
                }, 200
            elif chart_name_normalized == "ai-judgment-accuracy-rate":
                # For ai-judgment-accuracy-rate chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for ai-judgment-accuracy-rate chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_ai_judgment_accuracy_rate(start_date, end_date)
                return {
                    "data": data,
                    "description": "AI judgment accuracy rate in the selected time range.",
                }, 200
            elif chart_name_normalized == "data-source-count":
                # end_date is optional for data-source-count chart
                end_date = None
                if end_date_str:
                    try:
                        end_date = parse_datetime_with_timezone(end_date_str)
                        if end_date is None:
                            return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                    except Exception as e:
                        return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                # Get additional filter parameters
                severity = request.args.get("severity")
                auto_close = request.args.get("auto_close")
                verification_state = request.args.get("verification_state")
                risk_mode = request.args.get("risk_mode")
                search_keywords_str = request.args.get("search_keywords")
                search_keywords = []
                if search_keywords_str:
                    try:
                        import json
                        search_keywords = json.loads(search_keywords_str)
                    except:
                        pass
                data = StatisticsService.get_alert_count_by_product_name(
                    start_date, end_date=end_date, status=status, severity=severity,
                    auto_close=auto_close, verification_state=verification_state,
                    risk_mode=risk_mode, search_keywords=search_keywords
                )
                return {
                    "data": data,
                    "description": "Alert counts by data source / product in the selected time range.",
                }, 200
            elif chart_name_normalized == "alert-trend":
                # For trend chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for alert-trend chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_alert_trend(start_date, end_date)
                return {
                    "data": data,
                    "description": "Time trend of alert volume in the selected time range.",
                }, 200
            elif chart_name_normalized == "incident-trend":
                # For incident trend chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for incident-trend chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_incident_trend(start_date, end_date)
                return {
                    "data": data,
                    "description": "Time trend of incident volume in the selected time range.",
                }, 200
            elif chart_name_normalized == "vulnerability-trend":
                # For vulnerability trend chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for vulnerability-trend chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_vulnerability_trend(start_date, end_date)
                return {
                    "data": data,
                    "description": "Time trend of vulnerability volume in the selected time range.",
                }, 200
            elif chart_name_normalized == "vulnerability-trend-by-severity":
                # For vulnerability trend by severity chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for vulnerability-trend-by-severity chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_vulnerability_trend_by_severity(start_date, end_date)
                return {
                    "data": data,
                    "description": "Time trend of vulnerabilities by severity level in the selected time range.",
                }, 200
            elif chart_name_normalized == "vulnerability-department-distribution":
                # For vulnerability department distribution chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for vulnerability-department-distribution chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_vulnerability_department_distribution(start_date, end_date)
                return {
                    "data": data,
                    "description": "Distribution of vulnerabilities by department / business unit.",
                }, 200
            elif chart_name_normalized == "incident-trend-by-severity":
                # For incident trend by severity chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for incident-trend-by-severity chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_incident_trend_by_severity(start_date, end_date)
                return {
                    "data": data,
                    "description": "Time trend of incidents by severity level in the selected time range.",
                }, 200
            elif chart_name_normalized == "incident-department-distribution":
                # For incident department distribution chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for incident-department-distribution chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_incident_department_distribution(start_date, end_date)
                return {
                    "data": data,
                    "description": "Distribution of incidents by department / business unit grouped by severity.",
                }, 200
            elif chart_name_normalized == "incident-root-cause-distribution":
                # For incident root cause distribution chart, end_date is required
                if not end_date_str:
                    return {"error_message": "end_date is required for incident-root-cause-distribution chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                data = StatisticsService.get_incident_root_cause_distribution(start_date, end_date)
                return {
                    "data": data,
                    "description": "Distribution of incidents by root cause.",
                }, 200
            elif chart_name_normalized in (
                "ai-model-accuracy",
                "ai_model_accuracy",
                "aiaccuracy",
                "ai-accuracy",
            ):
                if not end_date_str:
                    return {"error_message": "end_date is required for ai-model-accuracy chart"}, 400

                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400

                limit = request.args.get("limit", default=10, type=int)
                data = StatisticsService.get_ai_accuracy_by_model(start_date, end_date, limit=limit or 10)
                return {
                    "data": data,
                    "description": "Accuracy of each AI model in the selected time range.",
                }, 200
            elif chart_name_normalized == "alert-status-by-severity":
                if not end_date_str:
                    return {"error_message": "end_date is required for alert-status-by-severity chart"}, 400
                try:
                    end_date = parse_datetime_with_timezone(end_date_str)
                    if end_date is None:
                        return {"error_message": "end_date must be in format YYYY-MM-DDTHH:mm:ss.SSSZ+HHmm"}, 400
                except Exception as e:
                    return {"error_message": f"Invalid end_date format: {str(e)}"}, 400
                status = request.args.get("status")  # Get status filter parameter
                # Get additional filter parameters
                severity = request.args.get("severity")
                auto_close = request.args.get("auto_close")
                verification_state = request.args.get("verification_state")
                risk_mode = request.args.get("risk_mode")
                search_keywords_str = request.args.get("search_keywords")
                search_keywords = []
                if search_keywords_str:
                    try:
                        import json
                        search_keywords = json.loads(search_keywords_str)
                    except:
                        pass
                data = StatisticsService.get_alert_status_by_severity(
                    start_date, end_date, status=status, severity=severity,
                    auto_close=auto_close, verification_state=verification_state,
                    risk_mode=risk_mode, search_keywords=search_keywords
                )
                return {
                    "data": data,
                    "description": "Distribution of alert statuses by severity in the selected time range.",
                }, 200
            else:
                raise Exception("chart_name is invalid")
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
