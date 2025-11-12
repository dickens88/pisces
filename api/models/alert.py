from sqlalchemy import Column, Integer, String, Text, Enum
from utils.mysql_conn import Base


class Alert(Base):
    __tablename__ = 't_alerts'

    id = Column(Integer(), primary_key=True)
    alert_id = Column(Text())

    # 使用字符串存储 ISO8601（含时区），与数据库中 VARCHAR(40)/TINYTEXT 对齐
    create_time = Column(String(40))
    last_update_time = Column(String(40))
    close_time = Column(String(40))

    title = Column(Text())
    description = Column(Text())

    severity = Column(Enum('TIPS', 'LOW', 'MEDIUM', 'HIGH', 'FATAL', name='severity_enum'), default='MEDIUM')
    handle_status = Column(Enum('Open', 'Block', 'Closed', name='handle_status_enum'), default='Open')

    owner = Column(Text())
    creator = Column(Text())

    close_reason = Column(Enum('False positive', 'Resolved', 'Repeated', 'Other', name='close_reason_enum'))
    close_comment = Column(Text())

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
            "data_source_product_name": self.data_source_product_name
        }


