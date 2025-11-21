import json
from typing import List

import requests

from controllers.comment_service import CommentService
from utils.app_config import config
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics, SECMASTER_ALERT_TEMPLATE
from utils.logger_init import logger


class AlertService:
    base_url = config.get('application.secmaster.base_url')
    project_id = config.get('application.secmaster.project_id')
    workspace_id = config.get('application.secmaster.workspace_id')

    @classmethod
    def list_alerts(cls, conditions: List, limit=50, offset=1, start_time=None, end_time=None):
        """Search and list alerts with conditions."""

        conditions, logics = build_conditions_and_logics(conditions)

        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/search"
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


        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)

        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        data = json.loads(resp.text)
        result = []
        total = data['total']
        for item in data['data']:
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
                "ttr": item['data_object'].get('ttr'),
                "data_source_product_name": item['data_object']['data_source']['product_name'],
            }
            row["owner"] = row["actor"] if row["actor"] else row["owner"]
            result.append(row)

        return result, total

    @classmethod
    def retrieve_alert_by_id(cls, alert_id):
        """Get alert details by ID."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        base_url, headers = wrap_http_auth_headers("GET", base_url, headers)
        resp = requests.get(url=base_url, headers=headers, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(f"[Alert] Fail to retrieve alert  {alert_id}. {resp.text}")

        data = json.loads(resp.text)
        item = data['data']

        alert_content = {
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
            "owner": item['data_object']['owner'],
            "actor": item['data_object'].get('actor'),
            "severity": item['data_object']['severity'],
            "close_comment": item['data_object'].get('close_comment'),
            "creator": item['data_object']['creator'],
            "ttr": item['data_object'].get('ttr'),
            "data_source_product_name": item['data_object']['data_source']['product_name'],
        }
        alert_content["owner"] = alert_content["actor"] if alert_content["actor"] else alert_content["owner"]
        try:
            alert_content["description"] = json.loads(item['data_object']['description'])
            # standard model_name field
            model_name = alert_content["description"].get("model_name")
            alert_content["description"]["model_name"] = model_name if model_name else alert_content["description"]["modelname"]
        except Exception as ex:
            alert_content["description"] = item['data_object']['description']
            logger.error(ex)
        return alert_content

    @classmethod
    def retrieve_alert_and_comments(cls, alert_id):
        """Get alert with comments, entities, and timeline."""
        alert = cls.retrieve_alert_by_id(alert_id)

        # retrieve comments by current alert ID
        comment = CommentService.retrieve_comments(alert_id)

        # extract key data objects from comment
        alert.update(cls._extract_info_from_comment(comment))

        # extract key data object from alert description
        alert["entities"] = cls._extract_entities_from_alert(alert["description"])
        alert["timeline"] = cls._extract_timeline_from_alert(alert)
        return alert

    @classmethod
    def close_alert(cls, alert_id, close_reason, comment, owner=None):
        """
        Close an alert with reason and comment.
        close_reason:
        误检 - False detection
        已解决 - Resolved
        重复 - Repeated
        其他 - Other
        """
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {
            "data_object": {
                "handle_status": "Closed",
                "close_reason": close_reason,
                "close_comment": f"【@{owner}】: {comment}"
            }
        }
        if owner:
            payload["data_object"]["actor"] = owner
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers, body)
        resp = requests.put(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        return json.loads(resp.text)

    @classmethod
    def batch_close_alert(cls, alert_ids, close_reason, comment, owner="-"):
        """Close a batch of alerts with reason and comment."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/batch-update"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {
            "batch_ids": alert_ids,
            "data_object": {
                "handle_status": "Closed",
                "close_reason": close_reason,
                "close_comment": f"【@{owner}】: {comment}"
            }
        }
        if owner:
            payload["data_object"]["actor"] = owner
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)
        resp = requests.post(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        return json.loads(resp.text)

    @classmethod
    def update_alert(cls, alert_id, update_info):
        """Update alert information."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {"data_object": update_info}
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers, body)
        resp = requests.put(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        return json.loads(resp.text)

    @classmethod
    def convert_alert_to_incident(cls, alert_ids):
        """Convert alerts to incidents."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/batch-order"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {
            "ids": []
        }
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers, body)
        resp = requests.put(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        return json.loads(resp.text)

    @classmethod
    def create_alert(cls, alert_data):
        """Create a new alert."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        SECMASTER_ALERT_TEMPLATE.update(alert_data)
        payload = {"data_object": SECMASTER_ALERT_TEMPLATE}
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)
        resp = requests.post(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        result = json.loads(resp.text)
        return result

    @classmethod
    def delete_alerts(cls, alert_ids):
        """Delete alerts."""
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {"batch_ids": alert_ids}

        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("DELETE", base_url, headers, body)
        resp = requests.delete(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        result = json.loads(resp.text)
        return result

    @staticmethod
    def _extract_info_from_comment(comment: dict):
        """Extract and categorize info from comments."""
        result = {
            "comments": [],
            "intelligence": [],
            "ai": [],
            "historic": []
        }
        for item in comment['data']:
            row = {
                "id": item['id'],
                "author": item['content']['come_from'],
                "create_time": item['content']['occurred_time'],
                "content": item["content"]["value"]
            }
            owner = CommentService.extract_owner_from_content(row["content"])
            row["author"] = owner if owner else row["author"]
            
            # Query file information by comment_id associated with id
            comment_id = str(item['id'])
            file_info = CommentService.get_comment_file_info(comment_id)
            if file_info:
                row["file"] = file_info
            
            content = row["content"]
            if "Intelligence Information" in content:
                result["intelligence"].append(row)
            elif "AI" in content or "Dify" in content:
                result["ai"].append(row)
            elif "Historical" in content:
                result["historic"].append(row)
            else:
                result["comments"].append(row)
        return result

    @staticmethod
    def _extract_entities_from_alert(description):
        """Extract entities (IP, host, user) from alert description."""
        if not isinstance(description, dict):
            return []
        
        entities = []
        for key, value in description.items():
            key_lower = key.lower()

            if not value:
                continue

            if "ip" in key_lower:
                entities.append({"type": "ip", "name": str(value), "from": key_lower})
            elif "host" in key_lower:
                entities.append({"type": "host", "name": str(value), "from": key_lower})
            elif "domain" in key_lower:
                entities.append({"type": "domain", "name": str(value), "from": key_lower})

        return entities

    @staticmethod
    def _extract_timeline_from_alert(alert: dict):
        """Extract timeline from alert description."""
        events = [
            {"time": alert["create_time"], "event": "Alert Triggered"},
            {"time": alert["close_time"], "event": "Close Alert"}
        ]

        for intel in alert["intelligence"]:
            events.append({"time": intel["create_time"], "event": "Add Intelligence"})

        for ai in alert["ai"]:
            events.append({"time": ai["create_time"], "event": "AI Analysis"})

        for ai in alert["historic"]:
            events.append({"time": ai["create_time"], "event": "Find Similar Alerts"})

        for ai in alert["comments"]:
            events.append({"time": ai["create_time"], "event": "Add Comment"})

        sorted_events = sorted(events, key=lambda x: str(x.get("time", "")))

        return sorted_events