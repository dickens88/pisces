from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func

from utils.mysql_conn import Base, Session
from utils.logger_init import logger


class AiFineTuneResult(Base):
    """
    Stores the latest AI Fine-tune result per (alert_id, workflow_id).
    Previous results for the same alert/workflow are overwritten.
    """

    __tablename__ = "t_alert_ai_finetune_result"

    id = Column(Integer, primary_key=True)

    # Identifiers
    alert_id = Column(String(255), nullable=False)   # matches t_alerts.alert_id
    workflow_id = Column(String(255), nullable=True)  # Dify workflow / app id
    agent_name = Column(String(100), nullable=True)   # human-readable agent name

    # Parsed structured fields from AI response
    is_threat = Column(String(50), nullable=True)
    confidence_score = Column(String(50), nullable=True)
    reason = Column(Text, nullable=True)

    # Raw data from workflow result
    raw_text = Column(Text, nullable=False)

    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "alert_id",
            "workflow_id",
            name="uq_alert_ai_finetune_alert_workflow",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "workflow_id": self.workflow_id,
            "agent_name": self.agent_name,
            "is_threat": self.is_threat,
            "confidence_score": self.confidence_score,
            "reason": self.reason,
            "raw_text": self.raw_text,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

    @classmethod
    def upsert_for_alert(
        cls,
        alert_id: str,
        workflow_id: str | None,
        agent_name: str | None,
        is_threat: str | None,
        confidence_score: str | None,
        reason: str | None,
        raw_text: str,
    ) -> dict:
        """
        Insert or update the latest Fine-tune result for a given (alert_id, workflow_id).

        - If a row exists for that pair, it is overwritten.
        - If not, a new row is created.
        """
        session = Session()
        try:
            if not alert_id:
                raise ValueError("alert_id is required for AI Fine-tune result")

            row = session.query(cls).filter_by(alert_id=str(alert_id), workflow_id=workflow_id).first()

            if not row:
                row = cls(alert_id=str(alert_id), workflow_id=workflow_id)

            row.agent_name = agent_name
            row.is_threat = is_threat or None
            row.confidence_score = confidence_score or None
            row.reason = reason or None
            row.raw_text = raw_text or ""

            session.add(row)
            session.commit()

            logger.debug(
                "Saved AI Fine-tune result: alert_id=%s, workflow_id=%s",
                alert_id,
                workflow_id,
            )

            return row.to_dict()
        except Exception:
            session.rollback()
            logger.exception(
                "Failed to upsert AI Fine-tune result for alert_id=%s, workflow_id=%s",
                alert_id,
                workflow_id,
            )
            raise
        finally:
            session.close()

    @classmethod
    def get_latest_for_alert(cls, alert_id: str) -> dict | None:
        """
        Get the latest AI Fine-tune result for a given alert_id.
        
        Args:
            alert_id: The alert ID to query
            
        Returns:
            dict: The latest result as a dictionary, or None if not found
        """
        session = Session()
        try:
            result = (
                session.query(cls)
                .filter_by(alert_id=str(alert_id))
                .order_by(cls.updated_at.desc())
                .first()
            )
            
            if result:
                return result.to_dict()
            return None
        except Exception:
            logger.exception(
                "Failed to get latest AI Fine-tune result for alert_id=%s",
                alert_id,
            )
            raise
        finally:
            session.close()


