from models.impacted_service import ImpactedService
from utils.logger_init import logger


class ImpactedServiceService:
    """影响服务和事件简报业务逻辑服务类"""

    @classmethod
    def list_items(cls, incident_id: str, item_type: str = None):
        """获取事件的所有记录，可选的按类型过滤"""
        try:
            items = ImpactedService.get_by_incident_id(incident_id, item_type=item_type)
            return items
        except Exception as ex:
            logger.exception(f"Failed to list items for incident {incident_id}: {ex}")
            raise

    @classmethod
    def list_services(cls, incident_id: str):
        """获取事件的所有影响服务（兼容方法）"""
        return cls.list_items(incident_id, item_type='impacted_service')

    @classmethod
    def list_notifications(cls, incident_id: str):
        """获取事件的所有事件简报"""
        return cls.list_items(incident_id, item_type='incident_brief')

    @classmethod
    def get_item(cls, item_id: int):
        """获取单个记录"""
        try:
            item = ImpactedService.get_by_id(item_id)
            if not item:
                raise ValueError(f"Record with id {item_id} not found")
            return item
        except Exception as ex:
            logger.exception(f"Failed to get record {item_id}: {ex}")
            raise

    @classmethod
    def get_service(cls, service_id: int):
        """获取单个影响服务（兼容方法）"""
        return cls.get_item(service_id)

    @classmethod
    def create_item(cls, incident_id: str, data: dict, item_type: str = 'impacted_service'):
        """创建新记录（影响服务或事件简报）"""
        try:
            if item_type == 'impacted_service':
                # 验证必填字段
                if not data.get('service'):
                    raise ValueError("服务名称不能为空")
            elif item_type == 'incident_brief':
                # 验证必填字段
                if not data.get('event'):
                    raise ValueError("通报事件不能为空")
            
            item = ImpactedService.create(incident_id, data, item_type=item_type)
            return item
        except Exception as ex:
            logger.exception(f"Failed to create {item_type} for incident {incident_id}: {ex}")
            raise

    @classmethod
    def create_service(cls, incident_id: str, data: dict):
        """创建新的影响服务（兼容方法）"""
        return cls.create_item(incident_id, data, item_type='impacted_service')

    @classmethod
    def create_notification(cls, incident_id: str, data: dict):
        """创建新的事件简报"""
        return cls.create_item(incident_id, data, item_type='incident_brief')

    @classmethod
    def update_item(cls, item_id: int, data: dict):
        """更新记录（影响服务或事件简报）"""
        try:
            item = ImpactedService.update(item_id, data)
            return item
        except Exception as ex:
            logger.exception(f"Failed to update record {item_id}: {ex}")
            raise

    @classmethod
    def update_service(cls, service_id: int, data: dict):
        """更新影响服务（兼容方法）"""
        return cls.update_item(service_id, data)

    @classmethod
    def update_notification(cls, notification_id: int, data: dict):
        """更新事件简报"""
        return cls.update_item(notification_id, data)

    @classmethod
    def delete_item(cls, item_id: int):
        """删除记录（影响服务或事件简报）"""
        try:
            ImpactedService.delete(item_id)
            return True
        except Exception as ex:
            logger.exception(f"Failed to delete record {item_id}: {ex}")
            raise

    @classmethod
    def delete_service(cls, service_id: int):
        """删除影响服务（兼容方法）"""
        return cls.delete_item(service_id)

    @classmethod
    def delete_notification(cls, notification_id: int):
        """删除事件简报"""
        return cls.delete_item(notification_id)

