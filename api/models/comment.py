import json
from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime
from datetime import datetime, timezone
import re

from utils.logger_init import logger
from utils.mysql_conn import Base, Session
from utils.common_utils import format_utc_datetime_to_db_string


class Comment(Base):
    __tablename__ = 't_comments'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    event_id = Column(String(255))
    comment_id = Column(String(255), unique=True, nullable=False)
    owner = Column(String(255))
    create_time = Column(String(40))
    message = Column(Text())
    comment_type = Column(String(50), default='comment')
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
            "comment_type": self.comment_type or 'comment',
            "file_type": self.file_type,
            "file_name": self.file_name,
            "has_file": self.file_obj is not None,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None
        }

    @staticmethod
    def _normalize_datetime_string(dt_str):
        """
        将各种时间格式转换为数据库需要的格式 YYYY-MM-DD HH:MM:SS
        
        Args:
            dt_str: 时间字符串，可能是以下格式：
                - ISO8601: 2026-01-06T16:51:17.263Z+0000
                - ISO8601: 2026-01-06T16:51:17Z
                - 数据库格式: 2025-11-16 06:24:30
        
        Returns:
            String in format YYYY-MM-DD HH:MM:SS
        """
        if not dt_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 如果已经是数据库格式，直接返回
        if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', dt_str):
            return dt_str
        
        try:
            # 处理 ISO8601 格式: 2026-01-06T16:59:50.816Z+0000
            # 使用正则表达式提取日期和时间部分（忽略毫秒和时区）
            match = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', dt_str)
            if match:
                return f"{match.group(1)} {match.group(2)}"
            
            # 如果正则匹配失败，尝试手动处理
            dt_str_clean = dt_str.replace('Z+0000', '').replace('Z', '').strip()
            if '.' in dt_str_clean:
                if 'T' in dt_str_clean:
                    parts = dt_str_clean.split('T')
                    if len(parts) == 2:
                        return f"{parts[0]} {parts[1].split('.')[0]}"
                else:
                    parts = dt_str_clean.split(' ')
                    if len(parts) >= 2:
                        return f"{parts[0]} {parts[1].split('.')[0]}"
            
            # 最后尝试使用 strptime
            if 'T' in dt_str_clean:
                dt_str_clean = dt_str_clean.replace('T', ' ')
            dt = datetime.strptime(dt_str_clean.split('.')[0], '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as ex:
            logger.warning(f"Failed to parse datetime string '{dt_str}': {ex}")
            # 如果解析失败，尝试提取日期时间部分
            match = re.search(r'(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})', dt_str)
            if match:
                return f"{match.group(1)} {match.group(2)}"
            # 如果都失败了，返回当前时间
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    def create_comment(cls, event_id, comment_id, owner, message, file_type=None, file_name=None, file_obj=None, comment_type='comment'):
        """创建评论记录"""
        session = Session()
        try:
            # 使用数据库格式 YYYY-MM-DD HH:MM:SS
            create_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            comment = cls(
                event_id=event_id,
                comment_id=comment_id,
                owner=owner,
                message=message,
                comment_type=comment_type or 'comment',
                file_type=file_type,
                file_name=file_name,
                file_obj=file_obj,
                create_time=create_time_str,
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

    @classmethod
    def upsert_comment(cls, comment_data: dict, event_id: str):
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
            # 将外部系统返回的时间字符串转换为数据库格式
            if create_time_raw:
                create_time = cls._normalize_datetime_string(create_time_raw)
            else:
                create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            existing_comment = session.query(cls).filter_by(comment_id=comment_id).first()
            
            comment_type = comment_data.get("comment_type") or comment_data.get("type") or 'comment'
            
            if existing_comment:
                existing_comment.event_id = event_id
                existing_comment.owner = owner
                existing_comment.message = content
                existing_comment.comment_type = comment_type
                existing_comment.create_time = create_time
                existing_comment.last_update_time = datetime.now()
                session.commit()
                return existing_comment
            
            new_comment = cls(
                event_id=event_id,
                comment_id=comment_id,
                owner=owner,
                message=content,
                comment_type=comment_type,
                create_time=create_time,
                last_update_time=datetime.now()
            )
            session.add(new_comment)
            session.commit()
            session.refresh(new_comment)
            return new_comment
        except Exception as ex:
            session.rollback()
            logger.exception(f"Failed to upsert comment: {ex}")
            raise
        finally:
            session.close()

