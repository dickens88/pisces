import json
import re
from flask import request
from flask_restful import Resource

from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from controllers.incident_service import IncidentService
from models.alert import Alert
from models.comment import Comment
from models.incident import Incident
from utils.logger_init import logger


class CallbackMessageHandler(Resource):

    @staticmethod
    def _extract_agent_name(comment_content: str) -> str:
        """Extract agent name from comment content that contains 【Dify AI Investigation】.
        
        Looks for patterns like [Created by]: or [{any text} by]: and returns the value after it.
        """
        if "【Dify AI Investigation】" not in comment_content:
            return None
        
        # Pattern to match [anything by]: followed by the agent name
        # Examples: [Created by]: AgentName, [Investigated by]: AgentName
        pattern = r'\[([^\]]+)\s+by\]:\s*(.+)'
        match = re.search(pattern, comment_content, re.IGNORECASE)
        
        if match:
            agent_name = match.group(2).strip()
            # Remove any trailing whitespace or newlines
            agent_name = agent_name.split('\n')[0].strip()
            logger.debug(f"Extracted agent_name: {agent_name}")
            return agent_name
        
        return None

    @staticmethod
    def _upsert_comments(event_id: str, event_type: str = None):
        """Retrieve and upsert comments for the given event_id"""
        try:
            comments = CommentService.retrieve_comments(event_id)
            for item in comments["data"]:
                content_value = item.get("content", {}).get("value", "")
                
                if "[剧本实例名称]" in content_value:
                    continue # 过滤云脑自动添加的评论
                
                Comment.upsert_comment(item, event_id)
                
                # Extract and update agent_name for alerts
                if event_type == "alert":
                    agent_name = CallbackMessageHandler._extract_agent_name(content_value)
                    if agent_name:
                        Alert.update_agent_name(event_id, agent_name)
                        logger.info(f"[Callback] Updated agent_name for alert_id={event_id}: {agent_name}")
        except Exception as ex:
            logger.warning(f"[Callback] Failed to upsert comments for event_id={event_id}: {ex}")

    def post(self):
        payload = json.loads(request.data)
        event_id = payload.get("event_id")
        action = payload.get("action")
        event_type = payload.get("event_type")

        try:
            if not event_id or len(event_id) < 5:
                return {"message": f"The event_id {event_id} is invalid"}, 400

            if event_type == "alert":
                result = AlertService.retrieve_alert_by_id(event_id)
                Alert.upsert_alert(result)
            elif event_type == "incident":
                result = IncidentService.retrieve_incident_by_id(event_id, include_graph=False)
                Incident.upsert_incident(result)

            self._upsert_comments(event_id, event_type)
            logger.info(f"[Callback] processed: event_id={event_id}, action={action}, event_type={event_type}")
            return {"data": {"message": f"{event_type.capitalize()} synchronized successfully"}}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500