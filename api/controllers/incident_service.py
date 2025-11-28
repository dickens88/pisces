import json
from threading import Lock, Thread
from typing import List

from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from controllers.event_graph_service import EventGraphService, EventGraphGenerationError
from models.alert import Alert
from models.incident import Incident
from utils.app_config import config
from utils.http_util import build_conditions_and_logics, SECMASTER_INCIDENT_TEMPLATE, request_with_auth
from utils.logger_init import logger


class IncidentService:
    base_url = config.get('application.secmaster.base_url')
    project_id = config.get('application.secmaster.project_id')
    workspace_id = config.get('application.secmaster.workspace_id')

    VULSCAN_LABEL = "vulscan_riskscan"
    _graph_job_lock = Lock()
    _graph_jobs = set()

    @classmethod
    def list_incidents(cls, conditions: List, limit=50, offset=1, search_vulscan=False,
                       start_time=None, end_time=None):
        """
        search incident list
        """

        conditions, logics = build_conditions_and_logics(conditions)

        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/search"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = {
            "limit": limit,
            "offset": offset,
            "sort_by": "create_time",
            "order": "DESC",
            "condition": {
                "conditions": conditions,
                "logics": logics
            },
            "from_date": start_time,
            "to_date": end_time
        }
        body = json.dumps(body)

        resp = request_with_auth("POST", url=base_url, data=body, headers=headers)
        if resp.status_code > 300:
            raise Exception(resp.text)

        data = json.loads(resp.text)
        result = []
        total = data['total']
        for item in data['data']:
            if search_vulscan:
                if cls.VULSCAN_LABEL not in item['data_object'].get('labels', '-'):
                    continue
            else:
                if cls.VULSCAN_LABEL in item['data_object'].get('labels', '-'):
                    continue

            row = {
                "id": item['id'],
                "create_time": item['data_object']['create_time'],
                "update_time": item['data_object']['update_time'],
                "close_time": item['data_object'].get('close_time', '-'),
                "handle_status": item['data_object']['handle_status'],
                "arrive_time": item['data_object']['arrive_time'],
                "labels": item['data_object'].get('labels', '-'),
                "close_reason": item['data_object'].get('close_reason'),
                "is_auto_closed": item['data_object'].get('is_auto_closed'),
                "title": item['data_object']['title'],
                "owner": item['data_object'].get('owner'),
                "actor": item['data_object'].get('actor'),
                "severity": item['data_object']['severity'],
                "close_comment": item['data_object'].get('close_comment'),
                "creator": item['data_object']['creator'],
                "ttd": item['data_object'].get('ttr'),
                "extend_properties": item['data_object'].get('extend_properties', []),
            }
            if item['data_object'].get('resource_list'):
                extra_info = item['data_object']['resource_list'][0]
                row['owner'] = extra_info.get('owner')
                row['responsible_person'] = extra_info.get('responsible_person')
                row['responsible_dept'] = extra_info.get('responsible_dept')
                row['root_cause'] = extra_info.get('root_cause')
                row['category'] = extra_info.get('category')

            row["actor"] = row["actor"] if row.get("actor") else row["creator"]
            result.append(row)

        return result, total


    @classmethod
    def retrieve_incident_by_id(cls, incident_id, *, include_graph=True, sync_local=True):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        resp = request_with_auth("GET", url=base_url, headers=headers)
        if resp.status_code > 300:
            raise Exception(resp.text)

        data = json.loads(resp.text)
        item = data['data']

        row = {
            "id": item['id'],
            "create_time": item['data_object']['create_time'],
            "update_time": item['data_object']['update_time'],
            "close_time": item['data_object'].get('close_time', '-'),
            "handle_status": item['data_object']['handle_status'],
            "arrive_time": item['data_object']['arrive_time'],
            "labels": item['data_object'].get('labels', '-'),
            "close_reason": item['data_object'].get('close_reason'),
            "is_auto_closed": item['data_object'].get('is_auto_closed'),
            "title": item['data_object']['title'],
            "severity": item['data_object']['severity'],
            "close_comment": item['data_object'].get('close_comment'),
            "actor": item['data_object'].get('actor'),
            "creator": item['data_object']['creator'],
            "ttd": item['data_object'].get('ttr'),
            "description": item['data_object'].get('description'),
            "extend_properties": item['data_object'].get('extend_properties', []),
        }

        if item['data_object'].get('resource_list'):
            extra_info = item['data_object']['resource_list'][0]
            row['owner'] = extra_info.get('owner')
            row['responsible_person'] = extra_info.get('responsible_person')
            row['responsible_dept'] = extra_info.get('responsible_dept')
            row['root_cause'] = extra_info.get('root_cause')
            row['category'] = extra_info.get('category')

        row["actor"] = row["actor"] if row.get("actor") else row["creator"]

        # retrieve complete associated alert by id
        # Try to get from database first, fallback to API if not found
        associated_alerts = []
        associated_ids = item['data_object'].get('alert_list', [])
        # Add alert_list to row for database storage
        row["alert_list"] = associated_ids
        for alert_id in associated_ids:
            # Try to get from database first
            db_alert = Alert.get_alert_by_id(alert_id)
            if db_alert:
                # Convert database record to API format
                alert = cls._convert_db_alert_to_api_format(db_alert)
                associated_alerts.append(alert)
            else:
                # Fallback to API if not found in database
                alert = AlertService.retrieve_alert_by_id(alert_id)
                associated_alerts.append(alert)

                # Cache alert locally for next retrieval
                try:
                    Alert.upsert_alert(alert)
                except Exception as exc:
                    logger.warning("[Incident] Failed to cache alert %s locally: %s", alert_id, exc)

        # sort by create_time in descending order
        associated_alerts.sort(key=lambda x: x.get('create_time', ''), reverse=True)
        row["associated_alerts"] = associated_alerts

        # retrieve comments by current alert ID
        row["comments"] = cls._extract_info_from_comment(CommentService.retrieve_comments(incident_id))

        # Persist or update the incident snapshot locally so we can attach graph metadata.
        if sync_local:
            try:
                Incident.upsert_incident(row)
            except Exception as exc:
                logger.warning("[Incident] Failed to sync incident %s locally: %s", incident_id, exc)

        if include_graph:
            graph_bundle = Incident.get_graph_bundle(incident_id)
            graph_data = graph_bundle.get("graph_data") if graph_bundle else None
            graph_summary = graph_bundle.get("graph_summary") if graph_bundle else None

            if graph_data:
                graph_status = "ready"
            else:
                if EventGraphService.is_configured():
                    graph_status = "processing"
                    cls._schedule_graph_generation(incident_id, row, associated_alerts, force=False)
                else:
                    graph_status = "disabled"

            row["graph_data"] = graph_data
            row["graph_summary"] = graph_summary
            row["graph_status"] = graph_status
        else:
            row["graph_data"] = None
            row["graph_summary"] = None
            row["graph_status"] = "skipped"
        return row

    @classmethod
    def create_incident(cls, data):
        """Create a new incident."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        SECMASTER_INCIDENT_TEMPLATE.update(data)
        payload = {"data_object": SECMASTER_INCIDENT_TEMPLATE}
        body = json.dumps(payload)

        resp = request_with_auth("POST", url=base_url, headers=headers, data=body)
        if resp.status_code >= 300:
            raise Exception(resp.text)

        result = json.loads(resp.text)
        return result

    @classmethod
    def update_incident(cls, data, incident_id):
        """update a new incident."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = json.dumps({"data_object": data})

        resp = request_with_auth("PUT", url=base_url, headers=headers, data=body)
        if resp.status_code > 300:
            raise Exception(resp.text)

        result = json.loads(resp.text)
        return result

    @classmethod
    def associate_alerts_to_incident(cls, incident_id: str, alert_ids: list):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}/alerts"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = json.dumps({"ids": alert_ids})

        resp = request_with_auth("POST", url=base_url, data=body, headers=headers)
        if resp.status_code > 300:
            raise Exception(resp.text)
        return json.loads(resp.text)

    @classmethod
    def disassociate_alerts_from_incident(cls, incident_id: str, alert_ids: list):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}/alerts"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = json.dumps({"ids": alert_ids})

        resp = request_with_auth("DELETE", url=base_url, data=body, headers=headers)
        if resp.status_code > 300:
            raise Exception(resp.text)
        return json.loads(resp.text)

    @classmethod
    def delete_incidents(cls, batch_ids):
        """Delete incidents."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {"batch_ids": batch_ids}

        body = json.dumps(payload)

        resp = request_with_auth("DELETE", url=base_url, headers=headers, data=body)
        if resp.status_code > 300:
            raise Exception(resp.text)

        Incident.delete_incidents(batch_ids)

        result = json.loads(resp.text)
        return result

    @staticmethod
    def _convert_db_alert_to_api_format(db_alert: dict) -> dict:
        """Convert database alert record to API format."""
        # Parse description if it's a JSON string
        description = db_alert.get('description')
        if description and isinstance(description, str):
            try:
                description = json.loads(description)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return {
            "id": db_alert.get('alert_id'),
            "create_time": db_alert.get('create_time', '-'),
            "update_time": db_alert.get('last_update_time', '-'),
            "close_time": db_alert.get('close_time', '-'),
            "handle_status": db_alert.get('handle_status', '-'),
            "arrive_time": '-',  # Not stored in database
            "labels": '-',  # Not stored in database
            "close_reason": db_alert.get('close_reason'),
            "is_auto_closed": db_alert.get('is_auto_closed'),
            "title": db_alert.get('title', ''),
            "owner": db_alert.get('owner'),
            "severity": db_alert.get('severity', '-'),
            "close_comment": db_alert.get('close_comment'),
            "creator": db_alert.get('creator'),
            "ttr": '-',  # Not stored in database
            "data_source_product_name": db_alert.get('data_source_product_name'),
            "description": description
        }

    @staticmethod
    def _extract_info_from_comment(comment: dict):
        result = []
        for item in comment['data']:
            row = {
                "id": item.get('id'),
                "author": item['content']['come_from'],
                "create_time": item['content']['occurred_time'],
                "content": item["content"]["value"]
            }
            owner = CommentService.extract_owner_from_content(row["content"])
            row["author"] = owner if owner else row["author"]
            
            # Query file information by comment_id associated with id
            if 'id' in item:
                comment_id = str(item['id'])
                file_info = CommentService.get_comment_file_info(comment_id)
                if file_info:
                    row["file"] = file_info
            
            result.append(row)
        return result

    @classmethod
    def _schedule_graph_generation(cls, incident_id: str, incident_payload: dict, associated_alerts: List[dict], force: bool = False):
        if not EventGraphService.is_configured():
            return False

        with cls._graph_job_lock:
            if incident_id in cls._graph_jobs:
                return False
            cls._graph_jobs.add(incident_id)

        if force:
            try:
                Incident.clear_graph_bundle(incident_id)
            except Exception as exc:
                logger.warning("[EventGraph] Failed to clear existing graph cache for %s: %s", incident_id, exc)

        payload_copy = json.loads(json.dumps(incident_payload))
        alerts_copy = json.loads(json.dumps(associated_alerts))

        def worker():
            try:
                graph_data, graph_summary = EventGraphService.generate_graph_bundle(payload_copy, alerts_copy)
                Incident.update_graph_bundle(incident_id, graph_data=graph_data, graph_summary=graph_summary)
                logger.info("[EventGraph] Stored graph data for incident %s", incident_id)
            except EventGraphGenerationError as exc:
                logger.warning("[EventGraph] Failed to build graph for incident %s: %s", incident_id, exc)
            except Exception:
                logger.exception("[EventGraph] Unexpected error while building graph for incident %s", incident_id)
            finally:
                with cls._graph_job_lock:
                    cls._graph_jobs.discard(incident_id)

        thread = Thread(target=worker, daemon=True)
        thread.start()
        return True

    @classmethod
    def regenerate_graph(cls, incident_id: str) -> bool:
        payload = cls.retrieve_incident_by_id(incident_id, include_graph=False)
        associated_alerts = payload.get("associated_alerts", [])
        return cls._schedule_graph_generation(incident_id, payload, associated_alerts, force=True)
