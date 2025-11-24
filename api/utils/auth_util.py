import json
import time
from functools import wraps
from hashlib import md5

import requests
from cacheout import LRUCache
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restful import reqparse

from utils.app_config import config
from utils.common_utils import Singleton
from utils.logger_init import logger


def auth_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_disabled = config.get("application.disabled", False)

        if auth_disabled:
            kwargs.setdefault("username", "debug")
            return func(*args, **kwargs)

        if config.get("application.auth.method", "jwt") == "jwt":
            verify_jwt_in_request()
            username = get_jwt_identity()

            kwargs.setdefault("username", username)
            return func(*args, **kwargs)
        else:
            request = reqparse.request
            if request is None:
                return {"error_message": "can't get request."}, 400

            token_data = parse_w3_token(request)

            # 1. check cache if user has login
            user = TokenCache().get_token(token=token_data)
            if user:
                # refresh ttl in cache
                TokenCache().set_token(token=token_data, user=user)
                kwargs["user"] = user
                return func(*args, **kwargs)

            # 2. invoke w3 api for authentication
            resp = requests.request(method="PUT",
                                    url="https://login.huawei.com/login/rest/token",
                                    headers={"Host": "login.huawei.com", "Content-Type": "application/json"},
                                    data=json.dumps(token_data))
            if resp.status_code == 200:
                # record user action
                user = json.loads(resp.text)
                logger.info(f'[AUTH] Request w3 new token for user={user["user"]["cn"]},status={resp.status_code}')
                user = user["user"]
                TokenCache().set_token(token=token_data, user=user)
                kwargs.setdefault("username", user.get("cn", "debug"))
                return func(*args, **kwargs)
            else:
                logger.info(f'[AUTH] Fail to request w3 token, status={resp.status_code}')
                return {"error_message": resp.text}, 401

    return wrapper


def parse_w3_token(request):
    hwsso_login = request.cookies.get("hwsso_login")
    hwssot = request.cookies.get("hwssot")
    hwssotinter3 = request.cookies.get("hwssotinter3")
    login_uid = request.cookies.get("login_uid")

    return {
        "token": {
            "hwsso_login": hwsso_login,
            "hwssot": hwssot,
            "hwssotinter3": hwssotinter3,
            "login_uid": login_uid
        },
        "url": "http://w3.huawei.com/"
    }

@Singleton
class TokenCache:
    cache = LRUCache(maxsize=512, ttl=14400, timer=time.time)

    def set_token(self, token, user):
        key = md5(str(token).encode("utf-8")).hexdigest()
        self.cache.set(key, user)

    def get_token(self, token):
        key = md5(str(token).encode("utf-8")).hexdigest()
        cached_user = self.cache.get(key)
        # refresh ttl if hit
        if cached_user:
            self.cache.set(key, cached_user, ttl=3600)
        return cached_user
