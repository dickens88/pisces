import json
from flask import request
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.incident_service import IncidentService
from models.alert import Alert
from models.incident import Incident
from utils.logger_init import logger


class CallbackMessageHandler(Resource):

    # @jwt_required()
    def post(self):
        payload = json.loads(request.data)
        event_id = payload.get("event_id")
        action = payload.get("action")
        event_type = payload.get("event_type")

        try:
            if event_type == "alert":
                result = AlertService.retrieve_alert_by_id(event_id)
                if action in ("create", "update"):
                    Alert.upsert_alert(result)

            elif event_type == "incident":
                result = IncidentService.retrieve_incident_by_id(event_id)
                if action in ("create", "update"):
                    Incident.upsert_incident(result)

            logger.info(f"[Callback] processed: event_id={event_id}, action={action}, event_type={event_type}")
            result = {"message": f"{event_type.capitalize()} synchronized successfully"}
            return {"data": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500