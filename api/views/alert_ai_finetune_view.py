from flask import request
from flask_restful import Resource

from models.alert_ai_finetune import AlertAiFineTuneResult
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
            result = AlertAiFineTuneResult.upsert_for_alert(
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
        API endpoint to retrieve AI Fine-tune results for an alert.

        URL: GET /alerts/<alert_id>/ai-finetune
        Returns: List of fine-tune results for the alert (latest per workflow_id)
        """
        try:
            from utils.mysql_conn import Session
            
            session = Session()
            try:
                results = (
                    session.query(AlertAiFineTuneResult)
                    .filter_by(alert_id=str(alert_id))
                    .order_by(AlertAiFineTuneResult.updated_at.desc())
                    .all()
                )
                
                # Group by workflow_id and keep only the latest per workflow
                latest_by_workflow = {}
                for result in results:
                    workflow_key = result.workflow_id or '__no_workflow__'
                    if workflow_key not in latest_by_workflow:
                        latest_by_workflow[workflow_key] = result.to_dict()
                
                return {"data": list(latest_by_workflow.values())}, 200
            finally:
                session.close()
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


