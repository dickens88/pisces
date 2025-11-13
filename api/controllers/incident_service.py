from typing import List

import requests
import json

from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from utils.app_config import config
from utils.common_utils import get_date_range
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics
from utils.logger_init import logger
from utils.mysql_conn import Session
from models.alert import Alert


class IncidentService:
    base_url = config.get('application.secmaster.base_url')
    project_id = config.get('application.secmaster.project_id')
    workspace_id = config.get('application.secmaster.workspace_id')

    @classmethod
    def list_incidents(cls, conditions: List, time_range=1, limit=50, offset=1):
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
                "description": item['data_object']['description']
            }
            result.append(row)

        return result, total


    @classmethod
    def retrieve_incident_by_id(cls, incident_id):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/incidents/{incident_id}"
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
            "description": item['data_object']['description'],
            "data_source_product_name": item['data_object']['data_source']['product_name'],
        }

        # retrieve complete associated alert by id
        associated_alerts = []
        associated_ids = item['data_object']['alert_list']
        for alert_id in associated_ids:
            alert = AlertService.retrieve_alert_by_id(alert_id)
            associated_alerts.append(alert)
        row["associated_alerts"] = associated_alerts

        # retrieve comments by current alert ID
        row["comments"] = cls.extract_info_from_comment(CommentService.retrieve_comments(incident_id))
        return row

    @staticmethod
    def extract_info_from_comment(comment: dict):
        result = []
        for item in comment['data']:
            row = {
                "author": item['content']['come_from'],
                "create_time": item['content']['occurred_time'],
                "content": item["content"]["value"]
            }
            result.append(row)
        return result