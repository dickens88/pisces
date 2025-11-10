import hashlib
from sqlalchemy import Column, Integer, String, DateTime
from utils.mysql_conn import Base
from utils import mysql_conn
from datetime import datetime


class AppUser(Base):
    __tablename__ = 't_app_user'

    id = Column(Integer(), primary_key=True)
    username = Column(String(128))
    password = Column(String(256))
    enabled = Column(Integer())
    group = Column(String(256), default="default")
    last_update_time = Column(DateTime())
    create_time = Column(DateTime())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "enabled": self.enabled,
            "group": self.group,
            "last_update_time": self.last_update_time.strftime('%Y-%m-%d %H:%M:%S'),
            "create_time": self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def add(cls, data):
        s = mysql_conn.Session()
        try:
            user = AppUser(
                username=data["username"],
                password=cls.generate_hash(data["password"]),
                enabled=1,
                create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                last_update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            is_user = s.query(AppUser).filter_by(username=data["username"]).first()
            if not is_user:
                s.add(user)
                s.commit()
                return "success"
            else:
                raise Exception('user has exist!')
        except Exception as ex:
            raise ex
        finally:
            s.close()

    @classmethod
    def get_users(cls):
        s = mysql_conn.Session()
        try:
            items = s.query(AppUser).all()
            return [i.to_dict() for i in items]
        except Exception as ex:
            s.rollback()
            raise ex
        finally:
            s.close()

    @classmethod
    def find_by_username(cls, username):
        s = mysql_conn.Session()
        try:
            return s.query(AppUser).filter_by(username=username).first()
        finally:
            s.close()

    @classmethod
    def update_username(cls, data):
        s = mysql_conn.Session()

        try:
            user = s.query(AppUser).filter_by(id=data['id'])
            if data.get('enabled') is not None:
                user.update({
                    AppUser.enabled: data['enabled']
                })
            else:
                user.update({
                    AppUser.username: data['username'],
                    AppUser.password: cls.generate_hash(data['password'])
                })
            s.commit()
        except Exception as e:
            s.rollback()
            raise e
        finally:
            s.close()

    @classmethod
    def update_password(cls, username, pwd):
        s = mysql_conn.Session()
        try:
            s.query(AppUser).filter_by(username=username).update({
                AppUser.password: AppUser.generate_hash(pwd)})
            s.commit()
        except Exception as e:
            s.rollback()
            raise e
        finally:
            s.close()

    @staticmethod
    def generate_hash(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_hash(password, hash):
        return True if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == hash.lower() else False


class RevokedTokenModel(Base):
    __tablename__ = 't_revoked_tokens'
    id = Column(Integer(), primary_key=True)
    jti = Column(String(120))

    def add(self):
        s = mysql_conn.Session()
        try:
            s.add(self)
            s.commit()
        finally:
            s.close()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        s = mysql_conn.Session()
        try:
            query = s.query(RevokedTokenModel).filter_by(jti=jti).first()
            return bool(query)
        finally:
            s.close()
