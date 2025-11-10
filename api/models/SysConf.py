from datetime import datetime

from sqlalchemy import Column, String, BigInteger, DateTime

from utils import mysql_conn
from utils.mysql_conn import Base


class SystemConfig(Base):
    __tablename__ = 't_system_config'

    id = Column(BigInteger(), primary_key=True)
    key_name = Column(String(200))
    key_value = Column(String(500))
    last_update_time = Column(DateTime(), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self):
        return {
            "key": self.key_name,
            "value": self.key_value
        }

    @staticmethod
    def get(key):
        s = mysql_conn.Session()
        try:
            item = s.query(SystemConfig).filter(SystemConfig.key_name == key).first()
            return item.key_value
        except Exception as ex:
            raise ex
        finally:
            s.close()

    @staticmethod
    def list():
        s = mysql_conn.Session()
        try:
            items = s.query(SystemConfig).all()
            return [i.to_dict() for i in items]
        except Exception as ex:
            raise ex
        finally:
            s.close()

    @staticmethod
    def add(key_name, key_value):
        s = mysql_conn.Session()
        try:
            s.add(SystemConfig(key_name=key_name, key_value=key_value))
            s.commit()
        except Exception as ex:
            raise ex
        finally:
            s.close()

    @staticmethod
    def update(key_name, key_value):
        s = mysql_conn.Session()
        try:
            s.query(SystemConfig).filter_by(key_name=key_name).update({SystemConfig.key_value: key_value})
            s.commit()
        except Exception as ex:
            raise ex
        finally:
            s.close()

    @staticmethod
    def delete(key_name):
        s = mysql_conn.Session()
        try:
            s.query(SystemConfig).filter_by(key_name=key_name).delete()
            s.commit()
        except Exception as ex:
            raise ex
        finally:
            s.close()