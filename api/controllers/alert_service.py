from typing import List

import requests
import json

from controllers.comment_service import CommentService
from utils.app_config import config
from utils.common_utils import get_date_range
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics
from utils.logger_init import logger
from utils.mysql_conn import Session
from models.alert import Alert


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
            "ttd": item['data_object']['ttd'],
            "extend_properties": item['data_object']['extend_properties'],
        }
        try:
            row["description"] = json.loads(item['data_object']['description'])
        except Exception as ex:
            logger.error(ex)

        # retrieve comments by current alert ID
        comment = CommentService.retrieve_comments(alert_id)

        # extract key data objects from comment
        row.update(cls.extract_info_from_comment(comment))

        # extract key data object from alert description
        row["entities"] = cls.extract_entities_from_alert(row["description"])
        row["timeline"] = [
            {"time": row["create_time"], "event": "Alert Triggered"},
            {"time": row["close_time"], "event": "Close Alert"}
        ]
        return row

    @staticmethod
    def extract_info_from_comment(comment: dict):
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
    def extract_entities_from_alert(description: dict):
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
    def create_alert(cls, payload: dict) -> dict:
        """
        Create a new alert record in local DB.
        """
        session = Session()
        try:
            alert = Alert(
                alert_id=payload.get("alert_id"),
                create_time=payload.get("create_time"),
                last_update_time=payload.get("last_update_time"),
                close_time=payload.get("close_time"),
                title=payload.get("title"),
                description=json.dumps(payload.get("description")) if isinstance(payload.get("description"), (dict, list)) else payload.get("description"),
                severity=payload.get("severity", "MEDIUM"),
                handle_status=payload.get("handle_status", "Open"),
                owner=payload.get("owner"),
                creator=payload.get("creator"),
                close_reason=payload.get("close_reason"),
                close_comment=payload.get("close_comment"),
                data_source_product_name=payload.get("data_source_product_name"),
            )
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