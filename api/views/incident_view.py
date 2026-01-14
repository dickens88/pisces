import json

from flask import request
from flask_restful import Resource

from controllers.comment_service import CommentService
from controllers.incident_service import IncidentService
from models.incident import Incident
from utils.auth_util import auth_required
from utils.common_utils import get_workspace_id
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
        workspace_id = get_workspace_id("asm" if search_vulscan else None)

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
                    end_time=end_time,
                    workspace_id=workspace_id
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
                result = IncidentService.create_incident(data, workspace_id=workspace_id)
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
                incident = IncidentService.create_incident(data, workspace_id=workspace_id)
                incident_id = incident["data"]["data_object"]["id"]

                # 2. create relation between alerts and incident, and close alart
                result = IncidentService.convert_alerts_to_incident(actor=username,
                                                                    incident_id=incident_id,
                                                                    alert_ids=ids,
                                                                    workspace_id=workspace_id)
                logger.info(f"[Incident] Converted Alerts to Incident: {incident_id} successfully.[{username}]")
                return {"data": data, "total": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, incident_id=None):
        data = json.loads(request.data)
        search_vulscan = data.get('search_vulscan', False)
        workspace_id = get_workspace_id("asm" if search_vulscan else None)
        action = data.get('action', 'update')

        try:
            if action == "update":
                data["labels"] = IncidentService.VULSCAN_LABEL if search_vulscan else "security_incident"
                result = IncidentService.update_incident(data, incident_id, workspace_id=workspace_id)

                CommentService.create_comment(event_id=incident_id,
                                              comment=f"{username} updated the incident",
                                              workspace_id=workspace_id,
                                              note_type="update")
                logger.info(f"[Incident] Updated Incident: {incident_id} successfully.[{username}]")
                return {"data": data, "total": result}, 200
            elif action == "close":
                close_reason = data["close_reason"]
                close_comment = data["close_comment"]
                result = IncidentService.close_incident(incident_id=incident_id,
                                                        close_reason=close_reason,
                                                        comment=close_comment,
                                                        actor=username,
                                                        workspace_id=workspace_id)
                logger.info(f"[Incident] Updated Incident: {incident_id} successfully.[{username}]")
                return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def get(self, username=None, incident_id=None):
        try:
            workspace_id = get_workspace_id(request.args.get('workspace'))
            data = IncidentService.retrieve_incident_by_id(incident_id, workspace_id=workspace_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def delete(self, username=None):
        data = json.loads(request.data)
        workspace_id = get_workspace_id(data.get('workspace'))
        try:
            ids = data["batch_ids"]
            result = IncidentService.delete_incidents(ids, workspace_id=workspace_id)
            logger.warn(f"[Incident] Delete Incidents successfully. ids: {ids}. [{username}]")
            return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class AlertRelations(Resource):

    @auth_required
    def get(self, username=None, alert_id=None):
        try:
            workspace_id = get_workspace_id(request.args.get('workspace'))

            resp = IncidentService.query_object_relations(alert_id=alert_id, workspace_id=workspace_id)
            if resp["data"]:
                return {"data": {"incident_id": resp["data"][0]["id"]}}, 200
            else:
                return {"data": None}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class IncidentRelations(Resource):

    @auth_required
    def post(self, username=None, incident_id=None):
        try:
            data = json.loads(request.data)
            ids = data.get('ids')
            workspace_id = get_workspace_id(data.get('workspace'))

            if ids:
                # create relation between alerts and incident, and close alart
                result = IncidentService.convert_alerts_to_incident(actor=username,
                                                                    incident_id=incident_id,
                                                                    alert_ids=ids,
                                                                    workspace_id=workspace_id)

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
            workspace_id = get_workspace_id(data.get('workspace'))

            if ids:
                # create relation between alerts and incident
                IncidentService.disassociate_alerts_from_incident(incident_id, ids, workspace_id=workspace_id)

                # leave a comment
                result = CommentService.create_comment(event_id=ids,
                                                       comment="Disassociate alerts from incident: " + incident_id,
                                                       workspace_id=workspace_id,
                                                       note_type="update",
                                                       actor=username)

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


class IncidentTask(Resource):

    @auth_required
    def get(self, username=None, incident_id=None):
        """Get stored project_uuid for an incident from local DB."""
        try:
            record = Incident.get_by_incident_id(incident_id)
            project_uuid = record.project_uuid if record else None
            return {"data": {"project_uuid": project_uuid}}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def put(self, username=None, incident_id=None):
        """Update stored project_uuid for an incident in local DB.
        Supports both single project_uuid (string) and multiple project UUIDs (list)."""
        try:
            data = json.loads(request.data or "{}")
            project_uuid = data.get("project_uuid")
            # 支持接收warroom_ids字段（多个project UUID数组，向后兼容）
            if "warroom_ids" in data:
                project_uuid = data.get("warroom_ids")
            result = Incident.update_project_uuid(incident_id, project_uuid)
            logger.info(f"[Incident] Updated project_uuid for incident {incident_id} to {project_uuid!r}.[{username}]")
            return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
