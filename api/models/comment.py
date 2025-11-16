import json
from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime
from datetime import datetime

from utils.logger_init import logger
from utils.mysql_conn import Base, Session


class Comment(Base):
    __tablename__ = 't_comments'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    event_id = Column(String(255))
    comment_id = Column(String(255), unique=True, nullable=False)
    owner = Column(String(255))
    create_time = Column(DateTime(), default=datetime.now)
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
            "create_time": self.create_time.isoformat() if self.create_time else None,
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
    def create_comment(cls, event_id, comment_id, owner, message, file_type=None, file_name=None, file_obj=None):
        """创建评论记录"""
        session = Session()
        try:
            comment = cls(
                event_id=event_id,
                comment_id=comment_id,
                owner=owner,
                message=message,
                file_type=file_type,
                file_name=file_name,
                file_obj=file_obj,
                create_time=datetime.now(),
                last_update_time=datetime.now()
            )
            session.add(comment)
            session.commit()
            session.refresh(comment)
            return comment
        except Exception as ex:
            session.rollback()
            logger.exception(ex)
            raise
        finally:
            session.close()

