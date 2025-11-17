import json

from flask import request
from flask_restful import Resource

from models.SysConf import SystemConfig
from utils.jwt_helper import auth_required
from utils.logger_init import logger


class Setting(Resource):
    @auth_required
    def get(self, username=None):
        try:
            return {"data": SystemConfig.list()}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500

    @auth_required
    def post(self, username=None):
        try:
            data = json.loads(request.data)
            SystemConfig.add(data["key"], data["value"])
            return {"message": "ok"}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500

    @auth_required
    def put(self, username=None):
        try:
            data = json.loads(request.data)
            SystemConfig.update(data["key"], data["value"])
            return {"message": "ok"}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500

    @auth_required
    def delete(self, username=None):
        try:
            data = json.loads(request.data)
            SystemConfig.delete(data["key"])
            return 204
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500


class SystemInfo(Resource):

    @auth_required
    def get(self, username=None):
        try:
            version = SystemConfig.get("sys_version")

            return {
                "data": {
                    "username": username,
                    "version": version
                }
            }, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
