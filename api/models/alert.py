import json
from datetime import datetime
from typing import List, Tuple
from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, Boolean, or_
from sqlalchemy.sql import func

from controllers.ai_decision_service import AiDecisionService
from utils.logger_init import logger
from utils.mysql_conn import Base, Session
from utils.common_utils import parse_datetime_with_timezone, format_utc_datetime_to_db_string


class Alert(Base):
    __tablename__ = 't_alerts'

    id = Column(Integer(), primary_key=True)
    alert_id = Column(Text())

    create_time = Column(String(40))
    last_update_time = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    close_time = Column(String(40))

    title = Column(Text())
    description = Column(Text())

    severity = Column(String(10))
    handle_status = Column(String(10))

    owner = Column(Text())
    creator = Column(Text())
    actor = Column(Text())

    close_reason = Column()
    close_comment = Column(Text())

    is_auto_closed = Column(String(50))
    data_source_product_name = Column(Text())
    model_name = Column(String(50))
    is_ai_decision_correct = Column(String(10), default = None)
    tta = Column(Integer(), default=0)

    verification_state = Column(String(50))
    ipdrr_phase = Column(String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "create_time": self.create_time,
            "close_time": self.close_time,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "handle_status": self.handle_status,
            "owner": self.owner,
            "creator": self.creator,
            "actor": self.actor,
            "close_reason": self.close_reason,
            "close_comment": self.close_comment,
            "is_auto_closed": self.is_auto_closed,
            "data_source_product_name": self.data_source_product_name,
            "model_name": self.model_name,
            "is_ai_decision_correct": self.is_ai_decision_correct,
            "tta": self.tta,
            "verification_state": self.verification_state,
            "ipdrr_phase": self.ipdrr_phase,
        }

    @classmethod
    def upsert_alert(cls, payload: dict) -> dict:
        """Insert or update an alert record in local DB by alert_id (upsert)."""
        session = Session()
        try:
            alert_id = payload.get("id")
            if not alert_id:
                raise ValueError("alert_id is required for upsert")
            
            alert = session.query(cls).filter_by(alert_id=alert_id).first()
            new_alert_entity = cls._build_alert_entity(payload)
            
            if alert:
                for column in cls.__table__.columns:
                    setattr(alert, column.name, getattr(new_alert_entity, column.name))
                logger.debug(f"Updating alert in local DB: alert_id={alert_id}")
            else:
                # Create new record
                alert = new_alert_entity
                session.add(alert)
                logger.debug(f"Creating alert in local DB: alert_id={alert_id}")
            
            session.commit()
            return alert.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def save_alert(cls, payload: dict) -> dict:
        """Create a new alert record in local DB. (Deprecated: use upsert_alert instead)"""
        return cls.upsert_alert(payload)

    @classmethod
    def update_alert(cls, payload: dict) -> dict:
        """Update an existing alert record in local DB by alert_id. (Deprecated: use upsert_alert instead)"""
        return cls.upsert_alert(payload)

    @classmethod
    def get_alert_by_id(cls, alert_id: str) -> dict:
        """Get alert record from local DB by alert_id. Returns None if not found."""
        session = Session()
        try:
            alert = session.query(cls).filter_by(alert_id=alert_id).first()
            if alert:
                return alert.to_dict()
            return None
        except Exception as ex:
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def list_alerts(cls, conditions: List = None, limit: int = 50, offset: int = 0, 
                    start_time: str = None, end_time: str = None) -> Tuple[List[dict], int]:

        session = Session()
        try:
            query = session.query(cls)

            # Parse and normalize time strings to UTC format for comparison
            if start_time:
                start_dt = parse_datetime_with_timezone(start_time)
                if start_dt:
                    start_time_str = format_utc_datetime_to_db_string(start_dt)
                    query = query.filter(cls.create_time >= start_time_str)
            if end_time:
                end_dt = parse_datetime_with_timezone(end_time)
                if end_dt:
                    end_time_str = format_utc_datetime_to_db_string(end_dt)
                    query = query.filter(cls.create_time <= end_time_str)

            # Apply conditions
            for cond in conditions or []:
                if not isinstance(cond, dict):
                    continue
                for key, value in cond.items():
                    if value is None:
                        continue
                    val_str = str(value)
                    key_lower = key.lower()
                    if key_lower == 'title':
                        query = query.filter(cls.title.ilike(f"%{val_str}%"))
                    elif key_lower == 'creator':
                        query = query.filter(cls.creator.ilike(f"%{val_str}%"))
                    elif key_lower == 'actor':
                        query = query.filter(cls.actor.ilike(f"%{val_str}%"))
                    elif key_lower in ('model', 'model_name'):
                        query = query.filter(cls.model_name == val_str)
                    elif key_lower in ('handle_status', 'status'):
                        query = query.filter(cls.handle_status == val_str)
                    elif key_lower == 'severity':
                        query = query.filter(cls.severity == val_str)
                    elif key_lower == 'id':
                        query = query.filter(cls.alert_id == val_str)
                    elif key_lower == 'verification_state':
                        query = query.filter(cls.verification_state == val_str)
                    elif key_lower == 'verification_state!=':
                        query = query.filter(cls.verification_state != val_str)
                    elif key_lower == 'ipdrr_phase':
                        query = query.filter(cls.ipdrr_phase == val_str)
                    elif key_lower == 'is_ai_decision_correct':
                        if val_str == '':
                            query = query.filter(
                                or_(
                                    cls.is_ai_decision_correct == None,
                                    cls.is_ai_decision_correct == ''
                                )
                            )
                        else:
                            query = query.filter(cls.is_ai_decision_correct == val_str)
                    elif key_lower == 'close_reason':
                        query = query.filter(cls.close_reason == val_str)

            total = query.count()
            rows = (
                query
                .order_by(cls.create_time.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            result = [item.to_dict() for item in rows]
            return result, total
        except Exception as ex:
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def delete_alerts(cls, alert_ids):
        """Delete alerts from local DB by their alert_ids."""
        if not alert_ids:
            return 0
        session = Session()
        try:
            deleted = session.query(cls).filter(cls.alert_id.in_(alert_ids)).delete(synchronize_session=False)
            session.commit()
            logger.debug("Deleted %s alerts from local DB", deleted)
            return deleted
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @staticmethod
    def _build_alert_entity(payload: dict):
        """Build Alert ORM instance from payload without persisting."""
        severity = payload.get("severity")
        handle_status = payload.get("handle_status")
        close_reason = payload.get("close_reason")

        close_reason_choices = set(Alert.__table__.columns['close_reason'].type.enums)
        if close_reason not in close_reason_choices:
            if close_reason:
                logger.warning(
                    "Unsupported close_reason '%s' received for alert %s, storing as NULL",
                    close_reason,
                    payload.get("id"),
                )
            close_reason = None

        description = payload.get("description")
        model_name = description.get("model_name") if description else "UNKNOWN"
        logger.debug("The value of model_name is: %s", model_name)
        is_ai_decision_correct = None
        if handle_status == "Closed":
            is_ai_decision_correct = AiDecisionService.evaluate_ai_decision(payload)
        if isinstance(description, (dict, list)):
            description = json.dumps(description)

        # Handle data_source_product_name from different payload formats
        data_source_product_name = None
        if "data_source" in payload and isinstance(payload.get("data_source"), dict):
            data_source_product_name = payload.get("data_source", {}).get("product_name")
        elif "data_source_product_name" in payload:
            data_source_product_name = payload.get("data_source_product_name")

        # Calculate TTA (Time To Acknowledge): close_time - create_time
        tta = 0
        close_time = payload.get("close_time")
        create_time = payload.get("create_time")
        # Only calculate TTA if close_time is not empty and not the default placeholder '-'
        if close_time and create_time:
            try:
                close_dt = datetime.fromisoformat(close_time.split('+')[0].split('Z')[0])
                create_dt = datetime.fromisoformat(create_time.split('+')[0].split('Z')[0])
                # Calculate difference in seconds
                tta = int((close_dt - create_dt).total_seconds())
                if tta < 0:
                    logger.warning(f"TTA calculation resulted in negative value for alert {payload.get('id')}, setting to 0")
                    tta = 0
            except Exception as e:
                logger.warning(f"Failed to calculate TTA for alert {payload.get('id')}: {e}. close_time: {close_time}, create_time: {create_time}")
                tta = 0

        return Alert(
            alert_id=payload.get("id"),
            create_time=payload.get("create_time"),
            close_time=payload.get("close_time"),
            title=payload.get("title"),
            description=description,
            severity=severity,
            handle_status=handle_status,
            owner=payload.get("owner"),
            creator=payload.get("creator"),
            actor=payload.get("actor"),
            close_reason=close_reason,
            close_comment=payload.get("close_comment"),
            is_auto_closed=payload.get("is_auto_closed"),
            data_source_product_name=data_source_product_name,
            model_name=model_name,
            is_ai_decision_correct = is_ai_decision_correct,
            tta=tta,
            verification_state=payload.get("verification_state"),
            ipdrr_phase=payload.get("ipdrr_phase"),
        )
