import logging.handlers
import os.path

logger = logging.getLogger()
logger.setLevel('INFO')
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler()
chlr.setFormatter(formatter)
logger.addHandler(chlr)

if not os.path.exists("logs"):
    os.mkdir("logs")
fhlr = logging.handlers.TimedRotatingFileHandler(filename="logs/app.log", when='D', interval=1, backupCount=7)
fhlr.setFormatter(formatter)
logger.addHandler(fhlr)
