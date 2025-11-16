import json
from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP
from sqlalchemy.sql import func

from utils.logger_init import logger
from utils.mysql_conn import Base, Session


class Incident(Base):
    __tablename__ = 't_incidents'

    id = Column(Integer(), primary_key=True)
    incident_id = Column(Text())

    create_time = Column(String(40))
    last_update_time = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    close_time = Column(String(40))
    arrive_time = Column(String(40))

    title = Column(Text())
    description = Column(Text())

    severity = Column(String(10))
    handle_status = Column(String(10))

    owner = Column(Text())
    creator = Column(Text())
    responsible_person = Column(Text())
    responsible_dept = Column(Text())

    close_reason = Column(Enum('False positive', 'Resolved', 'Repeated', 'Other', name='close_reason_enum'))
    close_comment = Column(Text())

    labels = Column(Text())
    root_cause = Column(Text())
    category = Column(Text())
    ttd = Column(String(40))
    is_auto_closed = Column(String(10))
    extend_properties = Column(Text())

    def to_dict(self):
        extend_properties = None
        if self.extend_properties:
            try:
                extend_properties = json.loads(self.extend_properties)
            except:
                extend_properties = self.extend_properties

        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "create_time": self.create_time,
            "last_update_time": self.last_update_time,
            "close_time": self.close_time,
            "arrive_time": self.arrive_time,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "handle_status": self.handle_status,
            "owner": self.owner,
            "creator": self.creator,
            "responsible_person": self.responsible_person,
            "responsible_dept": self.responsible_dept,
            "close_reason": self.close_reason,
            "close_comment": self.close_comment,
            "labels": self.labels,
            "root_cause": self.root_cause,
            "category": self.category,
            "ttd": self.ttd,
            "is_auto_closed": self.is_auto_closed,
            "extend_properties": extend_properties
        }

    @classmethod
    def upsert_incident(cls, payload: dict) -> dict:
        """Insert or update an incident record in local DB by incident_id (upsert)."""
        session = Session()
        try:
            incident_id = payload.get("id")
            if not incident_id:
                raise ValueError("incident_id is required for upsert")
            
            incident = session.query(cls).filter_by(incident_id=incident_id).first()
            new_incident_entity = cls._build_incident_entity(payload)
            
            if incident:
                # Update existing record
                incident.create_time = new_incident_entity.create_time
                incident.close_time = new_incident_entity.close_time
                incident.arrive_time = new_incident_entity.arrive_time
                incident.title = new_incident_entity.title
                incident.description = new_incident_entity.description
                incident.severity = new_incident_entity.severity
                incident.handle_status = new_incident_entity.handle_status
                incident.owner = new_incident_entity.owner
                incident.creator = new_incident_entity.creator
                incident.responsible_person = new_incident_entity.responsible_person
                incident.responsible_dept = new_incident_entity.responsible_dept
                incident.close_reason = new_incident_entity.close_reason
                incident.close_comment = new_incident_entity.close_comment
                incident.labels = new_incident_entity.labels
                incident.root_cause = new_incident_entity.root_cause
                incident.category = new_incident_entity.category
                incident.ttd = new_incident_entity.ttd
                incident.is_auto_closed = new_incident_entity.is_auto_closed
                incident.extend_properties = new_incident_entity.extend_properties
                logger.debug(f"Updating incident in local DB: incident_id={incident_id}")
            else:
                # Create new record
                incident = new_incident_entity
                session.add(incident)
                logger.debug(f"Creating incident in local DB: incident_id={incident_id}")
            
            session.commit()
            session.refresh(incident)
            return incident.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def save_incident(cls, payload: dict) -> dict:
        """Create a new incident record in local DB. (Deprecated: use upsert_incident instead)"""
        return cls.upsert_incident(payload)

    @classmethod
    def update_incident(cls, payload: dict) -> dict:
        """Update an existing incident record in local DB by incident_id. (Deprecated: use upsert_incident instead)"""
        return cls.upsert_incident(payload)

    @staticmethod
    def _build_incident_entity(payload: dict):
        """Build Incident ORM instance from payload without persisting."""
        severity = payload.get("severity")
        handle_status = payload.get("handle_status")
        close_reason = payload.get("close_reason")

        close_reason_choices = set(Incident.__table__.columns['close_reason'].type.enums)
        if close_reason not in close_reason_choices:
            if close_reason:
                logger.warning(
                    "Unsupported close_reason '%s' received for incident %s, storing as NULL",
                    close_reason,
                    payload.get("id"),
                )
            close_reason = None

        description = payload.get("description")
        if isinstance(description, (dict, list)):
            description = json.dumps(description)

        extend_properties = payload.get("extend_properties")
        if isinstance(extend_properties, (dict, list)):
            extend_properties = json.dumps(extend_properties)

        # Handle labels - could be string or list
        labels = payload.get("labels")
        if isinstance(labels, list):
            labels = ",".join(labels) if labels else None
        elif labels == '-':
            labels = None

        return Incident(
            incident_id=payload.get("id"),
            create_time=payload.get("create_time"),
            # last_update_time is automatically set by database
            close_time=payload.get("close_time") if payload.get("close_time") != '-' else None,
            arrive_time=payload.get("arrive_time"),
            title=payload.get("title"),
            description=description,
            severity=severity,
            handle_status=handle_status,
            owner=payload.get("owner"),
            creator=payload.get("creator"),
            responsible_person=payload.get("responsible_person"),
            responsible_dept=payload.get("responsible_dept"),
            close_reason=close_reason,
            close_comment=payload.get("close_comment"),
            labels=labels,
            root_cause=payload.get("root_cause"),
            category=payload.get("category"),
            ttd=str(payload.get("ttd")) if payload.get("ttd") else None,
            is_auto_closed=str(payload.get("is_auto_closed")) if payload.get("is_auto_closed") is not None else None,
            extend_properties=extend_properties,
        )

