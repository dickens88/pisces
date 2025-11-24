import json

import wrapt
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, create_refresh_token
from flask_restful import Resource, reqparse
from models.user import AppUser
from models.user import RevokedTokenModel
from utils.app_config import Configuration, config
from utils.auth_util import auth_required
from utils.logger_init import logger


class UserLogin(Resource):

    def post(self):
        data = json.loads(request.data)
        try:
            current_user = AppUser.find_by_username(data['username'])
            if current_user is None:
                logger.info(f'Wrong credentials.[{data["username"]}]')
                return {'message': 'Wrong credentials.'}, 401
            elif current_user.enabled == 0:
                logger.info(f'This user does not have permission.[{current_user.username}]')
                return {'message': 'This user does not have permission!'}, 402
            elif not current_user:
                logger.info(f'Wrong credentials.[{current_user.username}]')
                return {'message': 'Wrong credentials.'}, 401

            else:
                if AppUser.verify_hash(data['password'], current_user.password):
                    access_token = create_access_token(identity=data['username'])
                    refresh_token = create_refresh_token(identity=data['username'])
                    logger.info(f'Logged in success.[{current_user.username}]')
                    return {
                               'username': current_user.username,
                               'message': f'Logged in as {format(current_user.username)}',
                               'access_token': access_token,
                               'refresh_token': refresh_token
                           }, 200
                else:
                    logger.info(f'Wrong credentials.[{current_user.username}]')
                    return {'message': 'Wrong credentials'}, 401
        except Exception as ex:
            logger.exception(ex, [data['username']])
            return {"error_message": str(ex)}, 500


class UserRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        try:
            access_token = create_access_token(identity=current_user)
            refresh_token = create_refresh_token(identity=current_user)
            logger.info(f'Access token has been revoked.[{get_jwt_identity()}]')
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        except Exception as ex:
            logger.exception(ex)
            return {'message': 'Something went wrong'}, 500


class UserLogoutAccess(Resource):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            logger.info(f'Access token has been revoked.[{get_jwt_identity()}]')
            return {'message': 'Access token has been revoked'}, 200
        except Exception as ex:
            logger.exception(ex)
            return {'message': 'Something went wrong'}, 500


class UserView(Resource):

    @jwt_required()
    def put(self):
        try:
            data = json.loads(request.data)
            real_username = get_jwt_identity()
            current_user = AppUser.find_by_username(real_username)
            if AppUser.verify_hash(data['old_pwd'], current_user.password):
                AppUser.update_password(real_username, data['new_pwd'])
                logger.info(f'Update password success.[{get_jwt_identity()}]')
                return {"result_code": 'Update password success'}, 200
            else:
                logger.info(f'Wrong old password.[{get_jwt_identity()}]')
                return {"result_code": "Wrong old password"}, 203
        except Exception as ex:
            logger.exception(ex, [get_jwt_identity()])
            return {"error_message": str(ex)}, 500


class UserManagement(Resource):

    @jwt_required()
    def get(self):

        try:
            real_username = get_jwt_identity()
            if real_username == 'admin':
                users = AppUser.get_users()
                logger.info(f'Get all users.[{get_jwt_identity()}]')
                return {"message": "Get all users", "data": users}, 200
            else:
                logger.info(f'Permission denied.[{get_jwt_identity()}]')
                return {"result_code": "Permission denied"}, 403
        except Exception as ex:
            logger.exception(ex, [get_jwt_identity()])
            return {"error_message": str(ex)}, 500

    @jwt_required()
    def put(self):
        try:
            data = json.loads(request.data)
            real_username = get_jwt_identity()
            if real_username == 'admin':
                AppUser.update_username(data)
                logger.info(f'Update user success.[{get_jwt_identity()}]')
                return {"result": 'Success'}, 200
            else:
                logger.info(f'Update user permission denied.[{get_jwt_identity()}]')
                return {"result": "Permission denied"}, 403
        except Exception as ex:
            logger.exception(ex, [get_jwt_identity()])
            return {"error_message": str(ex)}, 500

    @jwt_required()
    def post(self):
        try:
            data = json.loads(request.data)
            real_username = get_jwt_identity()
            if real_username == 'admin':
                AppUser.add(data)
                logger.info(f'Add user success.[{get_jwt_identity()}]')
                return {"result": 'Success'}, 200
            else:
                logger.info(f'Add user permission denied.[{get_jwt_identity()}]')
                return {"result": "Permission denied"}, 403
        except Exception as ex:
            logger.exception(ex, [get_jwt_identity()])
            return {"error_message": str(ex)}, 500


@wrapt.decorator
def app_id_required(wrapped, instance, args, kwargs):
    request = reqparse.request
    if "appid" not in request.headers:
        return {"error_message": "didn't find valid appid."}, 401
    appid = request.headers["appid"]
    if appid == Configuration().app["application"].get("appid"):
        return wrapped(*args, **kwargs)
    else:
        logger.info(f'remote={request.remote_addr},url="{request.method} {request.url}",status="invalid appid"')
        return {"error_message": "the appid is invalid."}, 401


class LoginRestToken(Resource):
    """
    Lightweight endpoint that returns current authenticated user info.
    Works for both JWT (local) auth and Tianyan modes since it relies on
    the shared auth_required decorator.
    """

    @auth_required
    def get(self, username=None):
        if not username:
            return {"error_message": "Unauthorized"}, 401

        auth_method = config.get("application.auth.method", "jwt")
        return {
            "message": "Login success",
            "data": {
                "cn": username,
                "method": auth_method
            }
        }, 200
