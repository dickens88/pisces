import json
from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP
from sqlalchemy.sql import func

from utils.logger_init import logger
from utils.mysql_conn import Base, Session


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

    close_reason = Column(Enum('False positive', 'Resolved', 'Repeated', 'Other', name='close_reason_enum'))
    close_comment = Column(Text())

    is_auto_closed = Column(String(50))

    data_source_product_name = Column(Text())

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "create_time": self.create_time,
            "last_update_time": self.last_update_time,
            "close_time": self.close_time,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "handle_status": self.handle_status,
            "owner": self.owner,
            "creator": self.creator,
            "close_reason": self.close_reason,
            "close_comment": self.close_comment,
            "is_auto_closed": self.is_auto_closed,
            "data_source_product_name": self.data_source_product_name
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
                # Update existing record
                alert.create_time = new_alert_entity.create_time
                alert.close_time = new_alert_entity.close_time
                alert.title = new_alert_entity.title
                alert.description = new_alert_entity.description
                alert.severity = new_alert_entity.severity
                alert.handle_status = new_alert_entity.handle_status
                alert.owner = new_alert_entity.owner
                alert.creator = new_alert_entity.creator
                alert.close_reason = new_alert_entity.close_reason
                alert.close_comment = new_alert_entity.close_comment
                alert.is_auto_closed = new_alert_entity.is_auto_closed
                alert.data_source_product_name = new_alert_entity.data_source_product_name
                logger.debug(f"Updating alert in local DB: alert_id={alert_id}")
            else:
                # Create new record
                alert = new_alert_entity
                session.add(alert)
                logger.debug(f"Creating alert in local DB: alert_id={alert_id}")
            
            session.commit()
            session.refresh(alert)
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
        if isinstance(description, (dict, list)):
            description = json.dumps(description)

        # Handle data_source_product_name from different payload formats
        data_source_product_name = None
        if "data_source" in payload and isinstance(payload.get("data_source"), dict):
            data_source_product_name = payload.get("data_source", {}).get("product_name")
        elif "data_source_product_name" in payload:
            data_source_product_name = payload.get("data_source_product_name")

        return Alert(
            alert_id=payload.get("id"),
            create_time=payload.get("create_time"),
            # last_update_time is automatically set by database
            close_time=payload.get("close_time"),
            title=payload.get("title"),
            description=description,
            severity=severity,
            handle_status=handle_status,
            owner=payload.get("owner"),
            creator=payload.get("creator"),
            close_reason=close_reason,
            close_comment=payload.get("close_comment"),
            is_auto_closed=payload.get("is_auto_closed"),
            data_source_product_name=data_source_product_name,
        )
