from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.incident_service import IncidentService
from utils.logger_init import logger

import json


class IncidentView(Resource):

    @jwt_required()
    def post(self, incident_id=None):
        data = json.loads(request.data)
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        time_range = int(data.get('time_range', 1))
        conditions = data.get('conditions', [])
        action = data.get('action')
        search_vulscan = data.get('search_vulscan', False)

        try:
            if action == "list":
                data, total = IncidentService.list_incidents(conditions, time_range, limit, offset, search_vulscan)
                return {"data": data, "total": total}, 200
            elif action == "create":
                """
                body = {
                    "action": "create",
                    "title": "test123",
                    "description": "test123",
                    "create_time": "2025-11-14T23:00:00Z+0800",
                    "resource_list": [{
                        "owner": "123",
                        "responsible_person": "MyXXX",
                        "responsible_dept": "123",
                        "root_cause": "123",
                        "category": "123"
                    }]
                }
                """
                # add a label for incident
                data["labels"] = IncidentService.VULSCAN_LABEL if search_vulscan else "security_incident"
                result = IncidentService.create_incident(data)
                return {"data": data, "total": result}, 201
            elif action == "convert":
                # covert alerts to incident, means create a new incident and associate alerts to it
                ids = data.get('ids', [])
                if not ids:
                    raise Exception("ids parameter is required")

                # 1. create an incident
                data["labels"] = IncidentService.VULSCAN_LABEL if search_vulscan else "security_incident"
                incident = IncidentService.create_incident(data)
                incident_id = incident["data"]["data_object"]["id"]

                # 2. create relation between alerts and incident
                IncidentService.associate_alerts_to_incident(incident_id, ids)

                # 3. close alerts with comment
                result = AlertService.batch_close_alert(alert_ids=ids, close_reason="Resolved", comment="Associate alerts to incident: " + incident_id)

                return {"data": data, "total": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @jwt_required()
    def put(self, incident_id):
        data = json.loads(request.data)
        try:
            result = IncidentService.update_incident(data, incident_id)
            return {"data": data, "total": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @jwt_required()
    def get(self, incident_id):
        try:
            data = IncidentService.retrieve_incident_by_id(incident_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class IncidentRelations(Resource):

    @jwt_required()
    def post(self, incident_id):
        try:
            data = json.loads(request.data)
            ids = data.get('ids')

            if ids:
                # create relation between alerts and incident
                IncidentService.associate_alerts_to_incident(incident_id, ids)

                # close alerts with comment
                result = AlertService.batch_close_alert(alert_ids=ids, close_reason="Resolved", comment="Associate alerts to incident: " + incident_id)

                return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500