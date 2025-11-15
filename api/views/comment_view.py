import json

from flask import request
from flask_restful import Resource

from controllers.comment_service import CommentService
from utils.logger_init import logger


class CommentView(Resource):

    # @jwt_required()
    def post(self, event_id=None):
        data = json.loads(request.data)
        event_id = data['event_id']
        comment = data['comment']

        try:
            result = CommentService.create_comment(event_id=event_id, comment=comment, owner="charles liu")
            return {"data": result}, 201
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


    # @jwt_required()
    def get(self, event_id):

        try:
            data = CommentService.retrieve_comments(event_id=event_id)
            return {"data": data}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
