import json

from flask import request
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from controllers.incident_service import IncidentService
from utils.auth_util import auth_required
from utils.logger_init import logger


class IncidentView(Resource):

    @auth_required
    def post(self, username=None, incident_id=None):
        data = json.loads(request.data)
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        conditions = data.get('conditions', [])
        action = data.get('action')
        search_vulscan = data.get('search_vulscan', False)

        try:
            if action == "list":
                if not start_time or not end_time:
                    return {"error_message": "start_time and end_time are required"}, 400

                data, total = IncidentService.list_incidents(
                    conditions,
                    limit=limit,
                    offset=offset,
                    search_vulscan=search_vulscan,
                    start_time=start_time,
                    end_time=end_time
                )
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
                data["actor"] = username
                data["labels"] = IncidentService.VULSCAN_LABEL if search_vulscan else "security_incident"
                result = IncidentService.create_incident(data)
                logger.info(f"[Incident] Created new Incident successfully.[{username}]")
                return {"data": data, "total": result}, 201
            elif action == "convert":
                # covert alerts to incident, means create a new incident and associate alerts to it
                ids = data.get('ids', [])
                if not ids:
                    raise Exception("ids parameter is required")

                # 1. create an incident
                data["actor"] = username
                data["labels"] = IncidentService.VULSCAN_LABEL if search_vulscan else "security_incident"
                incident = IncidentService.create_incident(data)
                incident_id = incident["data"]["data_object"]["id"]

                # 2. create relation between alerts and incident
                IncidentService.associate_alerts_to_incident(incident_id, ids)

                # 3. close alerts with comment
                result = AlertService.batch_close_alert(alert_ids=ids,
                                                        close_reason="Resolved",
                                                        comment="Associate alerts to incident: " + incident_id,
                                                        owner=username)
                logger.info(f"[Incident] Converted Alerts to Incident: {incident_id} successfully.[{username}]")
                return {"data": data, "total": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, incident_id=None):
        data = json.loads(request.data)
        search_vulscan = data.get('search_vulscan', False)

        try:
            data["labels"] = IncidentService.VULSCAN_LABEL if search_vulscan else "security_incident"
            result = IncidentService.update_incident(data, incident_id)
            logger.info(f"[Incident] Updated Incident: {incident_id} successfully.[{username}]")
            return {"data": data, "total": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def get(self, username=None, incident_id=None):
        try:
            data = IncidentService.retrieve_incident_by_id(incident_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def delete(self, username=None):
        data = json.loads(request.data)
        try:
            ids = data["batch_ids"]
            result = IncidentService.delete_incidents(ids)
            logger.warn(f"[Incident] Delete Incidents successfully. ids: {ids}. [{username}]")
            return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500



class IncidentRelations(Resource):

    @auth_required
    def post(self, username=None, incident_id=None):
        try:
            data = json.loads(request.data)
            ids = data.get('ids')

            if ids:
                # create relation between alerts and incident
                IncidentService.associate_alerts_to_incident(incident_id, ids)

                # close alerts with comment
                result = AlertService.batch_close_alert(alert_ids=ids,
                                                        close_reason="Resolved",
                                                        comment="Associate alerts to incident: " + incident_id,
                                                        owner=username)

                logger.warn(f"[Incident] Associated Alerts successfully. ids: {ids} -> {incident_id}. [{username}]")
                return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def delete(self, username=None, incident_id=None):
        try:
            data = json.loads(request.data)
            ids = data.get('ids')

            if ids:
                # create relation between alerts and incident
                IncidentService.disassociate_alerts_from_incident(incident_id, ids)

                # leave a comment
                result = CommentService.create_comment(event_id=ids,
                                                       comment="Disassociate alerts from incident: " + incident_id,
                                                       owner=username)

                logger.warn(f"[Incident] Disassociated Alerts successfully. ids: {ids} -> {incident_id}. [{username}]")
                return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class IncidentGraphView(Resource):

    @auth_required
    def post(self, username=None, incident_id=None):
        try:
            scheduled = IncidentService.regenerate_graph(incident_id)
            if scheduled:
                return {"message": "Graph regeneration started"}, 202
            else:
                return {"message": "Graph generation already in progress"}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
