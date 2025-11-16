import json
from typing import List

import requests

from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from models.alert import Alert
from utils.app_config import config
from utils.common_utils import get_date_range
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics, SECMASTER_INCIDENT_TEMPLATE


class IncidentService:
    base_url = config.get('application.secmaster.base_url')
    project_id = config.get('application.secmaster.project_id')
    workspace_id = config.get('application.secmaster.workspace_id')

    VULSCAN_LABEL = "vulscan"

    @classmethod
    def list_incidents(cls, conditions: List, time_range=1, limit=50, offset=1, search_vulscan=False):
        """
        search incident list
        """
        from_date, to_date = get_date_range(time_range)

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
            "from_date": from_date,
            "to_date": to_date
        }
        body = json.dumps(body)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)
        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        data = json.loads(resp.text)
        result = []
        total = data['total']
        for item in data['data']:
            if search_vulscan:
                if cls.VULSCAN_LABEL not in item['data_object'].get('labels'):
                    continue
            else:
                if cls.VULSCAN_LABEL in item['data_object']['labels']:
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

            row["owner"] = row["owner"] if row.get("owner") else row["creator"]
            result.append(row)

        return result, total


    @classmethod
    def retrieve_incident_by_id(cls, incident_id):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        base_url, headers = wrap_http_auth_headers("GET", base_url, headers)
        resp = requests.get(url=base_url, headers=headers, proxies=None, verify=False, timeout=30)
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

        row["owner"] = row["owner"] if row.get("owner") else row["creator"]

        # retrieve complete associated alert by id
        # Try to get from database first, fallback to API if not found
        associated_alerts = []
        associated_ids = item['data_object'].get('alert_list', [])
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

        # sort by create_time in descending order
        associated_alerts.sort(key=lambda x: x.get('create_time', ''), reverse=True)
        row["associated_alerts"] = associated_alerts

        # retrieve comments by current alert ID
        row["comments"] = cls._extract_info_from_comment(CommentService.retrieve_comments(incident_id))
        return row

    @classmethod
    def create_incident(cls, data):
        """Create a new incident."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        SECMASTER_INCIDENT_TEMPLATE.update(data)
        payload = {"data_object": SECMASTER_INCIDENT_TEMPLATE}
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)
        resp = requests.post(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
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

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers, body)
        resp = requests.put(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        result = json.loads(resp.text)
        return result

    @classmethod
    def associate_alerts_to_incident(cls, incident_id: str, alert_ids: list):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}/alerts"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = json.dumps({"ids": alert_ids})

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)

        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)
        return json.loads(resp.text)

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
            
            # Query file information by comment_id associated with id
            if 'id' in item:
                comment_id = str(item['id'])
                file_info = CommentService.get_comment_file_info(comment_id)
                if file_info:
                    row["file"] = file_info
            
            result.append(row)
        return result