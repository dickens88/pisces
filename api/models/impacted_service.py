from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum
from sqlalchemy.sql import func

from utils.logger_init import logger
from utils.mysql_conn import Base, Session


class ImpactedService(Base):
    __tablename__ = 't_impacted_services'

    id = Column(Integer(), primary_key=True)
    incident_id = Column(String(40), nullable=False)
    type = Column(Enum('impacted_service', 'incident_brief', name='item_type'), nullable=False, default='impacted_service')
    # 影响服务字段
    service = Column(String(255))
    measure = Column(Text())
    sla = Column(String(100))
    planned_completion_time = Column(String(40))
    # 事件简报字段
    event = Column(String(255))
    notification_type = Column(String(50))
    next_plan = Column(Text())
    # 通用字段
    owner = Column(String(255))
    progress = Column(String(50))
    remark = Column(Text())
    create_time = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_update_time = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    def to_dict(self):
        """转换为字典，根据类型返回不同的字段"""
        base_dict = {
            "id": self.id,
            "incident_id": self.incident_id,
            "owner": self.owner,
            "progress": self.progress,
            "remark": self.remark,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None
        }
        
        if self.type == 'impacted_service':
            # 影响服务字段
            base_dict.update({
                "service": self.service,
                "measure": self.measure,
                "sla": self.sla,
                "plannedCompletionTime": self.planned_completion_time,
            })
        elif self.type == 'incident_brief':
            # 事件简报字段
            # 注意：前端使用"type"字段表示通报类型（firstNotification等），不是数据库的type字段
            base_dict.update({
                "event": self.event,
                "type": self.notification_type,  # 前端使用的type字段（通报类型）
                "notification_type": self.notification_type,  # 同时保留notification_type字段
                "nextPlan": self.next_plan,
            })
        
        return base_dict

    @classmethod
    def get_by_incident_id(cls, incident_id: str, item_type: str = None):
        """根据事件ID获取数据，可选的按类型过滤"""
        session = Session()
        try:
            query = session.query(cls).filter_by(incident_id=incident_id)
            if item_type:
                query = query.filter_by(type=item_type)
            items = query.all()
            return [item.to_dict() for item in items]
        finally:
            session.close()

    @classmethod
    def get_by_id(cls, service_id: int):
        """根据ID获取单个影响服务"""
        session = Session()
        try:
            service = session.query(cls).filter_by(id=service_id).first()
            return service.to_dict() if service else None
        finally:
            session.close()

    @classmethod
    def create(cls, incident_id: str, data: dict, item_type: str = 'impacted_service'):
        """创建新记录（影响服务或事件简报）"""
        session = Session()
        try:
            item = cls(
                incident_id=incident_id,
                type=item_type
            )
            
            if item_type == 'impacted_service':
                # 影响服务字段
                item.service = data.get('service')
                item.measure = data.get('measure')
                item.sla = data.get('sla')
                item.planned_completion_time = data.get('plannedCompletionTime') or data.get('planned_completion_time')
            elif item_type == 'incident_brief':
                # 事件简报字段
                item.event = data.get('event')
                item.notification_type = data.get('type') or data.get('notification_type')
                item.next_plan = data.get('nextPlan') or data.get('next_plan')
            
            # 通用字段
            item.owner = data.get('owner')
            item.progress = data.get('progress')
            item.remark = data.get('remark')
            
            session.add(item)
            session.commit()
            session.refresh(item)
            logger.info(f"Created {item_type} for incident {incident_id}: id={item.id}")
            return item.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(f"Failed to create {item_type} for incident {incident_id}: {ex}")
            raise
        finally:
            session.close()

    @classmethod
    def update(cls, item_id: int, data: dict):
        """更新记录（影响服务或事件简报）"""
        session = Session()
        try:
            item = session.query(cls).filter_by(id=item_id).first()
            if not item:
                raise ValueError(f"Record with id {item_id} not found")
            
            # 根据类型更新相应字段
            if item.type == 'impacted_service':
                if 'service' in data:
                    item.service = data['service']
                if 'measure' in data:
                    item.measure = data['measure']
                if 'sla' in data:
                    item.sla = data['sla']
                if 'plannedCompletionTime' in data or 'planned_completion_time' in data:
                    item.planned_completion_time = data.get('plannedCompletionTime') or data.get('planned_completion_time')
            elif item.type == 'incident_brief':
                if 'event' in data:
                    item.event = data['event']
                if 'type' in data or 'notification_type' in data:
                    item.notification_type = data.get('type') or data.get('notification_type')
                if 'nextPlan' in data or 'next_plan' in data:
                    item.next_plan = data.get('nextPlan') or data.get('next_plan')
            
            # 通用字段
            if 'owner' in data:
                item.owner = data['owner']
            if 'progress' in data:
                item.progress = data['progress']
            if 'remark' in data:
                item.remark = data['remark']
            
            session.commit()
            session.refresh(item)
            logger.info(f"Updated {item.type}: id={item_id}")
            return item.to_dict()
        except Exception as ex:
            session.rollback()
            logger.exception(f"Failed to update record {item_id}: {ex}")
            raise
        finally:
            session.close()

    @classmethod
    def delete(cls, item_id: int):
        """删除记录（影响服务或事件简报）"""
        session = Session()
        try:
            item = session.query(cls).filter_by(id=item_id).first()
            if not item:
                raise ValueError(f"Record with id {item_id} not found")
            
            incident_id = item.incident_id
            item_type = item.type
            session.delete(item)
            session.commit()
            logger.info(f"Deleted {item_type}: id={item_id}, incident_id={incident_id}")
            return True
        except Exception as ex:
            session.rollback()
            logger.exception(f"Failed to delete record {item_id}: {ex}")
            raise
        finally:
            session.close()

    @classmethod
    def delete_by_incident_id(cls, incident_id: str, item_type: str = None):
        """删除事件的所有记录，可选的按类型过滤"""
        session = Session()
        try:
            query = session.query(cls).filter_by(incident_id=incident_id)
            if item_type:
                query = query.filter_by(type=item_type)
            deleted = query.delete(synchronize_session=False)
            session.commit()
            logger.info(f"Deleted {deleted} records (type={item_type or 'all'}) for incident {incident_id}")
            return deleted
        except Exception as ex:
            session.rollback()
            logger.exception(f"Failed to delete records for incident {incident_id}: {ex}")
            raise
        finally:
            session.close()

