from typing import List

import requests
import json

from utils.app_config import config
from utils.common_utils import get_date_range
from utils.http_util import wrap_http_auth_headers, build_conditions_and_logics
from utils.logger_init import logger


class CommentService:
    base_url = config.get('application.secmaster.base_url')
    project_id = config.get('application.secmaster.project_id')
    workspace_id = config.get('application.secmaster.workspace_id')

    @classmethod
    def retrieve_comments(cls, event_id):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/notes/search"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = {
            "war_room_id": event_id
        }
        body = json.dumps(body)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)

        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        return json.loads(resp.text)

    @classmethod
    def create_comment(cls, event_id, comment, owner):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/notes"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = {
            "type": "textMessage",
            "content": comment,
            "war_room_id": event_id,
            "noteType": owner
        }
        body = json.dumps(body)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)

        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        resp.raise_for_status()

        return json.loads(resp.text)