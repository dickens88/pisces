import json

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from models.SysConf import SystemConfig
from utils.logger_init import logger


class Setting(Resource):
    @jwt_required()
    def get(self):
        try:
            return {"data": SystemConfig.list()}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500

    @jwt_required()
    def post(self):
        try:
            data = json.loads(request.data)
            SystemConfig.add(data["key"], data["value"])
            return {"message": "ok"}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500

    @jwt_required()
    def put(self):
        try:
            data = json.loads(request.data)
            SystemConfig.update(data["key"], data["value"])
            return {"message": "ok"}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500

    @jwt_required()
    def delete(self):
        try:
            data = json.loads(request.data)
            SystemConfig.delete(data["key"])
            return 204
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": ex}, 500
