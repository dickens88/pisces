from flask import request
from flask_restful import Resource

from models.ai_finetune import AiFineTuneResult
from utils.auth_util import auth_required
from utils.logger_init import logger


class AlertAiFineTuneView(Resource):
    """
    API endpoint to save the latest AI Fine-tune result for an alert.

    URL: POST /alerts/<alert_id>/ai-finetune
    Body JSON fields:
      - workflow_id (str, optional)
      - agent_name (str, optional)
      - is_threat (str, optional)
      - confidence_score (str, optional)
      - reason (str, optional)
      - raw_text (str, required)
      - raw_json (object or str, optional)
    """

    @auth_required
    def post(self, username=None, alert_id=None):
        data = request.get_json(force=True, silent=True) or {}

        workflow_id = data.get("workflow_id")
        # Accept both agent_name (preferred) and legacy model_name
        agent_name = data.get("agent_name") or data.get("model_name")
        is_threat = data.get("is_threat")
        confidence_score = data.get("confidence_score")
        reason = data.get("reason")
        raw_text = data.get("raw_text") or ""

        try:
            result = AiFineTuneResult.upsert_for_alert(
                alert_id=alert_id,
                workflow_id=workflow_id,
                agent_name=agent_name,
                is_threat=is_threat,
                confidence_score=confidence_score,
                reason=reason,
                raw_text=raw_text,
            )

            logger.info(
                "[AI Fine-tune] Saved result for alert_id=%s, workflow_id=%s by %s",
                alert_id,
                workflow_id,
                username,
            )

            return {"data": result}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def get(self, username=None, alert_id=None):
        """
        API endpoint to retrieve the latest AI Fine-tune result for an alert.

        URL: GET /alerts/<alert_id>/ai-finetune
        Returns: The latest fine-tune result for the alert
        """
        try:
            result = AiFineTuneResult.get_latest_for_alert(alert_id=alert_id)
            
            if result:
                return {"data": result}, 200
            else:
                return {"data": None}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


