from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus as urlquote
from utils.app_config import config as conf
from utils.common_utils import decrypt


engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'
                       .format(conf.get('application.mysql.db_user'),
                               urlquote(decrypt(conf.get('application.mysql.db_password'))),
                               conf.get('application.mysql.db_host'),
                               conf.get('application.mysql.db_port'),
                               conf.get('application.mysql.db_name')),
                       pool_size=50,
                       pool_recycle=300,
                       max_overflow=20,
                       pool_pre_ping=True,
                       pool_timeout=30)

Session = sessionmaker(bind=engine)
Base = declarative_base()
