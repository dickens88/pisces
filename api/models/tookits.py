import json
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func

from utils.logger_init import logger
from utils.mysql_conn import Base, Session
from utils.json_utils import parse_json_field, to_json_string


class ToolkitRecord(Base):
    __tablename__ = 't_toolkits_records'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(100))
    app_id = Column(String(100))
    app_type = Column(String(100))
    params = Column(Text())
    create_time = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_update_time = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    status = Column(String(50))
    result = Column(Text())
    owner = Column(String(255))
    event_id = Column(String(45))

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "app_id": self.app_id,
            "app_type": self.app_type,
            "params": parse_json_field(self.params),
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "status": self.status,
            "result": self.result,
            "owner": self.owner,
            "event_id": self.event_id
        }

    @classmethod
    def create_toolkit_record(cls, payload: dict) -> dict:
        """Create a new toolkit record in local DB."""
        session = Session()
        try:
            toolkit_record = cls._build_toolkit_entity(payload)
            session.add(toolkit_record)
            session.commit()
            session.refresh(toolkit_record)
            logger.debug(f"Creating toolkit record in local DB: id={toolkit_record.id}")
            return toolkit_record.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def get_toolkit_record_by_id(cls, record_id: int) -> dict:
        """Get toolkit record from local DB by id. Returns None if not found."""
        session = Session()
        try:
            toolkit_record = session.query(cls).filter_by(id=record_id).first()
            if toolkit_record:
                return toolkit_record.to_dict()
            return None
        except Exception as ex:
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def update_toolkit_record(cls, record_id: int, payload: dict) -> dict:
        """Update an existing toolkit record in local DB by id."""
        session = Session()
        try:
            toolkit_record = session.query(cls).filter_by(id=record_id).first()
            if not toolkit_record:
                raise ValueError(f"Toolkit record with id={record_id} not found")
            
            # Update fields from payload
            if "title" in payload:
                toolkit_record.title = payload.get("title")
            if "app_id" in payload:
                toolkit_record.app_id = payload.get("app_id")
            if "app_type" in payload:
                toolkit_record.app_type = payload.get("app_type")
            if "params" in payload:
                toolkit_record.params = to_json_string(payload.get("params"))
            if "status" in payload:
                toolkit_record.status = payload.get("status")
            if "result" in payload:
                toolkit_record.result = payload.get("result")
            if "owner" in payload:
                toolkit_record.owner = payload.get("owner")
            if "event_id" in payload:
                toolkit_record.event_id = payload.get("event_id")
            
            session.commit()
            session.refresh(toolkit_record)
            logger.debug(f"Updating toolkit record in local DB: id={record_id}")
            return toolkit_record.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def list_toolkit_records(cls, app_id=None, app_type=None, status=None, owner=None, event_id=None, limit=10, offset=0):
        """List toolkit records with optional filters. Returns list of dictionaries."""
        session = Session()
        try:
            query = session.query(cls)
            
            # Apply filters
            if app_id is not None:
                query = query.filter(cls.app_id == app_id)
            if app_type is not None:
                query = query.filter(cls.app_type == app_type)
            if status is not None:
                query = query.filter(cls.status == status)
            if owner is not None:
                query = query.filter(cls.owner == owner)
            if event_id is not None:
                query = query.filter(cls.event_id == event_id)
            
            # Order by create_time descending (newest first)
            query = query.order_by(cls.create_time.desc())

            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            records = query.all()
            return [record.to_dict() for record in records]
        except Exception as ex:
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def upsert_toolkit_record(cls, payload: dict) -> dict:
        """Insert or update a toolkit record in local DB by id (upsert)."""
        session = Session()
        try:
            record_id = payload.get("id")
            
            if record_id:
                # Try to update existing record
                toolkit_record = session.query(cls).filter_by(id=record_id).first()
                if toolkit_record:
                    # Update existing record
                    if "title" in payload:
                        toolkit_record.title = payload.get("title")
                    if "app_id" in payload:
                        toolkit_record.app_id = payload.get("app_id")
                    if "app_type" in payload:
                        toolkit_record.app_type = payload.get("app_type")
                    if "params" in payload:
                        toolkit_record.params = to_json_string(payload.get("params"))
                    if "status" in payload:
                        toolkit_record.status = payload.get("status")
                    if "result" in payload:
                        toolkit_record.result = payload.get("result")
                    if "owner" in payload:
                        toolkit_record.owner = payload.get("owner")
                    if "event_id" in payload:
                        toolkit_record.event_id = payload.get("event_id")
                    logger.debug(f"Updating toolkit record in local DB: id={record_id}")
                else:
                    # Create new record with specified id
                    toolkit_record = cls._build_toolkit_entity(payload)
                    toolkit_record.id = record_id
                    session.add(toolkit_record)
                    logger.debug(f"Creating toolkit record with specified id in local DB: id={record_id}")
            else:
                # Create new record
                toolkit_record = cls._build_toolkit_entity(payload)
                session.add(toolkit_record)
                logger.debug(f"Creating new toolkit record in local DB")
            
            session.commit()
            session.refresh(toolkit_record)
            return toolkit_record.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

    @staticmethod
    def _build_toolkit_entity(payload: dict):
        """Build ToolkitRecord ORM instance from payload without persisting."""
        return ToolkitRecord(
            title=payload.get("title"),
            app_id=payload.get("app_id"),
            app_type=payload.get("app_type"),
            params=to_json_string(payload.get("params")),
            # create_time and last_update_time are automatically set by database
            status=payload.get("status"),
            result=payload.get("result"),
            owner=payload.get("owner"),
            event_id=payload.get("event_id")
        )

