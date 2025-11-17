import base64
import json
import re

import requests

from models.comment import Comment
from utils.app_config import config
from utils.http_util import wrap_http_auth_headers
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
        if resp.status_code > 300:
            raise Exception(resp.text)

        return json.loads(resp.text)

    @classmethod
    def create_comment(cls, event_id, comment, owner):
        base_url = f"{cls.base_url}/v1/{cls.project_id}/workspaces/{cls.workspace_id}/soc/notes"
        headers = {"Content-Type": "application/json;charset=utf8", "X-Project-Id": cls.project_id}
        body = {
            "type": "textMessage",
            "content": f"【@{owner}】: {comment}",
            "war_room_id": event_id,
            "note_type": "pisces"
        }
        body = json.dumps(body)

        base_url, headers = wrap_http_auth_headers("POST", base_url, headers, body)

        resp = requests.post(url=base_url, data=body, headers=headers, proxies=None, verify=False, timeout=30)
        if resp.status_code > 300:
            raise Exception(resp.text)

        return json.loads(resp.text)

    @classmethod
    def get_comment_by_comment_id(cls, comment_id):
        """根据 comment_id 查询本地数据库中的评论记录"""
        return Comment.get_by_comment_id(comment_id)

    @staticmethod
    def extract_owner_from_content(content):
        if not isinstance(content, str):
            return None

        match = re.search(r'【@([^】]+)】', content)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def get_comment_file_info(comment_id: str) -> dict:
        """
        Get file information by comment ID.

        Args:
            comment_id: Comment ID

        Returns:
            dict: Dictionary containing file information, format:
                - If image: {"type": "image/...", "data": "data:image/...;base64,...", "is_image": True}
                - If other file: {"type": "...", "download_url": "/api/comments/{comment_id}/download", "is_image": False}
                - If not found or no file: {}
        """

        try:
            db_comment = CommentService.get_comment_by_comment_id(comment_id)

            if not db_comment or not db_comment.file_obj:
                return {}

            # Determine file type
            file_type = db_comment.file_type or ''

            # If image type
            if file_type.startswith('image/'):
                # Convert binary data to base64
                file_base64 = base64.b64encode(db_comment.file_obj).decode('utf-8')
                return {
                    "type": file_type,
                    "file_name": db_comment.file_name,
                    "data": f"data:{file_type};base64,{file_base64}",
                    "is_image": True
                }
            else:
                # Non-image file, generate download link
                return {
                    "type": file_type,
                    "file_name": db_comment.file_name,
                    "download_url": f"/api/comments/{comment_id}/download",
                    "is_image": False
                }
        except Exception as ex:
            logger.warning(f"Failed to get comment file info for comment_id={comment_id}: {ex}")
            return {}