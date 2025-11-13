import json
from typing import List

import requests
from sqlalchemy import func, DateTime, cast

from controllers.comment_service import CommentService
from models.alert import Alert
from utils.app_config import config
from utils.common_utils import get_date_range
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics
from utils.logger_init import logger
from utils.mysql_conn import Session


class AlertService:
    base_url = config.get('application.secmaster.base_url')
    project_id = config.get('application.secmaster.project_id')
    workspace_id = config.get('application.secmaster.workspace_id')

    @classmethod
    def list_alerts(cls, conditions: List, time_range=1, limit=50, offset=1):
        from_date, to_date = get_date_range(time_range)

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
            "from_date": from_date,
            "to_date": to_date
        }
        body = json.dumps(body)


        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)

        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        data = json.loads(resp.text)
        result = []
        total = data['total']
        for item in data['data']:
            row = {
                "id": item['id'],
                "create_time": item['data_object']['create_time'],
                "update_time": item['data_object']['update_time'],
                "close_time": item['data_object']['close_time'],
                "handle_status": item['data_object']['handle_status'],
                "arrive_time": item['data_object']['arrive_time'],
                "labels": item['data_object']['labels'],
                "close_reason": item['data_object']['close_reason'],
                "is_auto_closed": item['data_object']['is_auto_closed'],
                "title": item['data_object']['title'],
                "owner": item['data_object']['owner'],
                "severity": item['data_object']['severity'],
                "close_comment": item['data_object']['close_comment'],
                "creator": item['data_object']['creator'],
                "ttr": item['data_object']['ttr'],
                "extend_properties": item['data_object']['extend_properties'],
            }
            try:
                row["description"] = json.loads(item['data_object']['description'])
            except Exception as ex:
                logger.error(ex)
            result.append(row)

        return result, total


    @classmethod
    def retrieve_alert_by_id(cls, alert_id):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        base_url, headers = wrap_http_auth_headers("GET", base_url, headers)
        resp = requests.get(url=base_url, headers=headers, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        data = json.loads(resp.text)
        item = data['data']

        alert_content = {
            "id": item['id'],
            "create_time": item['data_object']['create_time'],
            "update_time": item['data_object']['update_time'],
            "close_time": item['data_object']['close_time'],
            "handle_status": item['data_object']['handle_status'],
            "arrive_time": item['data_object']['arrive_time'],
            "labels": item['data_object']['labels'],
            "close_reason": item['data_object']['close_reason'],
            "is_auto_closed": item['data_object']['is_auto_closed'],
            "title": item['data_object']['title'],
            "owner": item['data_object']['owner'],
            "severity": item['data_object']['severity'],
            "close_comment": item['data_object']['close_comment'],
            "creator": item['data_object']['creator'],
            "ttd": item['data_object']['ttd'],
            "extend_properties": item['data_object']['extend_properties'],
            "data_source_product_name" : item['data_object']['data_source']['product_name'],
        }
        try:
            alert_content["description"] = json.loads(item['data_object']['description'])
        except Exception as ex:
            logger.error(ex)
        return alert_content

    @classmethod
    def retrieve_alert_and_comments(cls, alert_id):
        alert = cls.retrieve_alert_by_id(alert_id)

        # retrieve comments by current alert ID
        comment = CommentService.retrieve_comments(alert_id)

        # extract key data objects from comment
        alert.update(cls._extract_info_from_comment(comment))

        # extract key data object from alert description
        alert["entities"] = cls._extract_entities_from_alert(alert["description"])
        alert["timeline"] = [
            {"time": alert["create_time"], "event": "Alert Triggered"},
            {"time": alert["close_time"], "event": "Close Alert"}
        ]
        return alert

    @classmethod
    def close_alert(cls, alert_id, close_reason, comment):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {
            "data_object": {
                "handle_status": "Closed",
                "close_reason": close_reason,
                "close_comment": comment
            }
        }
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)
        resp = requests.post(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        return json.loads(resp.text)

    @classmethod
    def update_alert(cls, alert_id, update_info):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {"data_object": update_info}
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers, body)
        resp = requests.put(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        return json.loads(resp.text)

    @classmethod
    def convert_alert_to_incident(cls, alert_ids):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/batch-order"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        payload = {
            "ids": []
        }
        body = json.dumps(payload)

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers, body)
        resp = requests.put(url=base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        return json.loads(resp.text)

    @classmethod
    def associate_alert(cls, alert_id):
        pass

    @staticmethod
    def _extract_info_from_comment(comment: dict):
        result = {
            "comments": [],
            "intelligence": [],
            "ai": [],
            "historic": []
        }
        for item in comment['data']:
            row = {
                "author": item['content']['come_from'],
                "create_time": item['content']['occurred_time'],
                "content": item["content"]["value"]
            }
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
    def _extract_entities_from_alert(description: dict):
        entities = []
        
        for key, value in description.items():
            key_lower = key.lower()
            
            if not value:
                continue
            
            if "ip" in key_lower:
                entity = {
                    "type": "ip",
                    "name": str(value),
                    "from": "Source IP"
                }
                entities.append(entity)
            elif "host" in key_lower:
                entity = {
                    "type": "host",
                    "name": str(value),
                    "from": "Host"
                }
                entities.append(entity)
            elif "user" in key_lower:
                entity = {
                    "type": "user",
                    "name": str(value),
                    "from": "Target User"
                }
                entities.append(entity)
        
        return entities

    @classmethod
    def build_alert_entity(cls, payload: dict) -> Alert:
        """
        Create an `Alert` ORM instance from payload data without persisting it.
        """
        severity_choices = set(Alert.__table__.columns['severity'].type.enums)
        handle_status_choices = set(Alert.__table__.columns['handle_status'].type.enums)
        close_reason_choices = set(Alert.__table__.columns['close_reason'].type.enums)

        severity_default = 'MEDIUM'
        handle_status_default = 'Open'

        severity = payload.get("severity", severity_default)
        if severity not in severity_choices:
            if severity:
                logger.warning(
                    "Unsupported severity '%s' received for alert %s, defaulting to '%s'",
                    severity,
                    payload.get("id"),
                    severity_default,
                )
            severity = severity_default

        handle_status = payload.get("handle_status", handle_status_default)
        if handle_status not in handle_status_choices:
            if handle_status:
                logger.warning(
                    "Unsupported handle_status '%s' received for alert %s, defaulting to '%s'",
                    handle_status,
                    payload.get("id"),
                    handle_status_default,
                )
            handle_status = handle_status_default

        close_reason = payload.get("close_reason")
        if close_reason not in close_reason_choices:
            if close_reason:
                logger.warning(
                    "Unsupported close_reason '%s' received for alert %s, storing as NULL",
                    close_reason,
                    payload.get("id"),
                )
            close_reason = None

        description = payload.get("description")
        if isinstance(description, (dict, list)):
            description = json.dumps(description)

        return Alert(
            alert_id=payload.get("id"),
            create_time=payload.get("create_time"),
            last_update_time=payload.get("update_time"),
            close_time=payload.get("close_time"),
            title=payload.get("title"),
            description=description,
            severity=severity,
            handle_status=handle_status,
            owner=payload.get("owner"),
            creator=payload.get("creator"),
            close_reason=close_reason,
            close_comment=payload.get("close_comment"),
            data_source_product_name=payload["data_source"]["product_name"],
        )

    @classmethod
    def create_alert(cls, payload: dict) -> dict:
        """
        Create a new alert record in local DB.
        """
        session = Session()
        try:
            alert = cls.build_alert_entity(payload)
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return alert.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def change_alert_status(cls, id: str, status: str, close_comment: str = None, close_reason: str = None):
        session = Session()
        alert = session.query(Alert).get(id)
        payload= {
            "data_object":{
                "handle_status": status,
            }
        }
        if close_comment:
            payload["data_object"]["close_comment"] = close_comment

        if close_reason:
            payload["data_object"]["close_reason"] = close_reason

        body = json.dumps(payload)

        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/alerts/{alert_id}"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}

        base_url, headers = wrap_http_auth_headers("PUT", base_url, headers)

        resp = requests.put(base_url, headers=headers, data=body, proxies=None, verify=False, timeout=30)

        resp.raise_for_status()

        data = json.loads(resp.text)
        new_alert_content = data["data_object"]

        new_alert = cls.build_alert_entity(new_alert_content)

        for col in alert.table.columns.keys():
            if col != "id":
                setattr(alert, col, getattr(new_alert, col, getattr(alert, col)))

        session.commit()
        session.close()


    @classmethod
    def get_alert_count_by_product_name(cls, start_date):
        session = Session()


        results = (
            session.query(Alert.data_source_product_name, func.count(Alert.id))
            .filter(cast(Alert.create_time, DateTime)>=start_date)
            .group_by(Alert.data_source_product_name)
            .all()
        )
        