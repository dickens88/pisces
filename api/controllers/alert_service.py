from typing import List

import requests

from utils.app_config import config

import json

from utils.common_utils import get_date_range
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics


class AlertService:

    @staticmethod
    def list_alerts(conditions: List, time_range=1, limit=50, offset=0):
        from_date, to_date = get_date_range(time_range)

        conditions, logics = build_conditions_and_logics(conditions)

        base_url = config.get('application.secmaster.base_url')
        project_id = config.get('application.secmaster.project_id')
        workspace_id = config.get('application.secmaster.workspace_id')
        base_url = f"{base_url}/v1/{project_id}/workspaces/{workspace_id}/soc/alerts/search"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": project_id}
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

        # print("**url**:", base_url)
        # print("**headers**:", headers)
        # print("**body**:", body)
        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        return resp.json()