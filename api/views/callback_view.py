import json
from flask import request
from flask_restful import Resource

from controllers.alert_service import AlertService
from models.alert import Alert
from utils.logger_init import logger


class AlertCreateFromSecmasterView(Resource):

    # @jwt_required()
    def post(self):
        payload = json.loads(request.data)
        print(payload)
        alert_id = payload.get("alert_id")
        if not alert_id:
            return {"error_message": "alert_id is required"}, 400

        try:
            result = AlertService.retrieve_alert_by_id(alert_id)

            Alert.save_alert(result)
            response_body = {"message": "Alert synchronized successfully"}
            if result is not None:
                response_body["data"] = result
            return response_body, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500