import urllib3
from omegaconf import OmegaConf
from urllib3.exceptions import InsecureRequestWarning

from utils.common_utils import singleton
from utils.logger_init import logger

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


@singleton
class Configuration:
    app = None

    def __init__(self):
        logger.info("*** Loading config yaml file.")
        self.app = OmegaConf.load("resources/config.yaml")

    def get(self, key, default=None):
        return OmegaConf.select(self.app, key, default=default)


config = Configuration()
