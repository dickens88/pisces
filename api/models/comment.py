import re
from datetime import datetime
from datetime import timezone

from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime

from utils.logger_init import logger
from utils.mysql_conn import Base, Session
from utils.common_utils import normalize_time_to_utc


class Comment(Base):
    __tablename__ = 't_comments'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    event_id = Column(String(255))
    comment_id = Column(String(255), unique=True, nullable=False)
    owner = Column(String(255))
    create_time = Column(String(40))
    message = Column(Text())
    file_type = Column(String(100))
    file_name = Column(String(500))
    file_obj = Column(LargeBinary())
    last_update_time = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "comment_id": self.comment_id,
            "owner": self.owner,
            "create_time": self.create_time,
            "message": self.message,
            "file_type": self.file_type,
            "file_name": self.file_name,
            "has_file": self.file_obj is not None,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None
        }


    @classmethod
    def get_by_comment_id(cls, comment_id):
        """根据 comment_id 查询记录"""
        session = Session()
        try:
            comment = session.query(cls).filter_by(comment_id=comment_id).first()
            return comment
        except Exception as ex:
            logger.exception(ex)
            raise
        finally:
            session.close()

    @classmethod
    def upsert_comment(cls, comment_data: dict, event_id: str, file_data=None, file_name=None, file_type=None):
        session = Session()
        try:
            comment_id = comment_data.get("id")
            if not comment_id:
                logger.warning(f"Comment data missing 'id' field, skipping: {comment_data}")
                return None
            
            content_info = comment_data.get("content", {})
            author = content_info.get('come_from')
            content = content_info.get("value")

            from controllers.comment_service import CommentService
            owner = CommentService.extract_owner_from_content(content) or author
            create_time_raw = comment_data.get("create_time")
            # Normalize time to UTC format for consistent storage and querying
            if create_time_raw:
                create_time = normalize_time_to_utc(create_time_raw)
            else:
                # If no create_time provided, use current UTC time
                create_time = normalize_time_to_utc(datetime.now(timezone.utc))
            
            existing_comment = session.query(cls).filter_by(comment_id=comment_id).first()
            if existing_comment:
                existing_comment.event_id = event_id
                existing_comment.owner = owner
                existing_comment.message = content
                existing_comment.create_time = create_time
                existing_comment.last_update_time = datetime.now()
                # update file info if has
                if file_data is not None:
                    existing_comment.file_obj = file_data
                    existing_comment.file_name = file_name
                    existing_comment.file_type = file_type
            else:
                new_comment = cls(
                    event_id=event_id,
                    comment_id=comment_id,
                    owner=owner,
                    message=content,
                    create_time=create_time,
                    last_update_time=datetime.now(),
                    file_obj=file_data,
                    file_name=file_name,
                    file_type=file_type
                )
                session.add(new_comment)
            session.commit()
        except Exception as ex:
            session.rollback()
            logger.exception(f"Failed to upsert comment: {ex}")
            raise
        finally:
            session.close()
