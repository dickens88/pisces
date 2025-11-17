import json
import os
import uuid
from io import BytesIO

from flask import request, send_file
from flask_restful import Resource
from werkzeug.utils import secure_filename

from controllers.comment_service import CommentService
from models.comment import Comment
from utils.jwt_helper import auth_required
from utils.logger_init import logger

# 文件大小限制：500KB
MAX_FILE_SIZE = 500 * 1024

# 允许的文件扩展名（可选，用于额外安全检查）
ALLOWED_EXTENSIONS = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],
    'application/pdf': ['.pdf'],
    'application/zip': ['.zip'],
    'text/plain': ['.txt'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
}


class CommentView(Resource):

    @staticmethod
    def _validate_filename(filename):
        """
        Validate filename security using werkzeug.utils.secure_filename.
        
        Args:
            filename: Original filename
            
        Returns:
            tuple: (is_valid, sanitized_filename, error_message)
        """
        if not filename:
            return False, None, "文件名不能为空"
        
        # Use secure_filename to sanitize filename (removes dangerous chars, path separators, etc.)
        sanitized = secure_filename(filename)
        
        # Check if sanitized filename is valid
        # secure_filename may return empty string if all chars are dangerous
        if not sanitized or sanitized.strip() == '':
            logger.warning(f"Filename sanitization resulted in empty string: {filename}")
            return False, None, "文件名无效或包含非法字符"
        
        # Check filename length (standard filesystem limit)
        if len(sanitized) > 255:
            return False, None, "文件名过长"
        
        return True, sanitized, None

    @staticmethod
    def _extract_comment_id(result):
        """
        Extract comment_id from external API response.
        
        Args:
            result: Response from external API
            
        Returns:
            str: comment_id or None
        """
        if not result:
            return None
        
        if isinstance(result, dict):
            if 'data' in result and isinstance(result['data'], dict):
                return str(result['data'].get('id', '')) or None
            return str(result.get('id', '')) or None
        
        return None

    @staticmethod
    def _validate_file(file):
        """
        Validate uploaded file (size and filename).
        
        Args:
            file: File object from request.files
            
        Returns:
            tuple: (is_valid, file_data, file_type, error_message)
        """
        if file.filename == '':
            return False, None, None, "No file selected"
        
        # Validate filename
        is_valid, sanitized_filename, error_msg = CommentView._validate_filename(file.filename)
        if not is_valid:
            logger.warning(f"Invalid filename rejected: {file.filename}, reason: {error_msg}")
            return False, None, None, error_msg or "文件名不安全"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size exceeded limit: {file_size} bytes, max: {MAX_FILE_SIZE} bytes")
            return False, None, None, f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024}KB）"
        
        # Read file content
        file_data = file.read()
        file_type = file.content_type or 'application/octet-stream'
        
        # Verify actual data size (prevent client from faking Content-Length)
        if len(file_data) > MAX_FILE_SIZE:
            logger.warning(f"File data size exceeded limit: {len(file_data)} bytes")
            return False, None, None, f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024}KB）"
        
        return True, file_data, file_type, None

    @auth_required
    def post(self, username=None, event_id=None):
        try:
            # Parse request data
            if 'file' in request.files:
                # Multipart form data (with file)
                event_id = request.form.get('event_id')
                comment = request.form.get('comment', '')
                file = request.files['file']
            else:
                # JSON data (text only)
                data = json.loads(request.data)
                event_id = data['event_id']
                comment = data['comment']
                file = None
            
            if not event_id:
                return {"error_message": "event_id is required"}, 400
            
            # Validate file if present
            file_data = None
            file_type = None
            file_name = None
            if file:
                is_valid, file_data, file_type, error_msg = self._validate_file(file)
                if not is_valid:
                    return {"error_message": error_msg}, 400
                # 获取并验证文件名
                _, sanitized_filename, _ = self._validate_filename(file.filename)
                file_name = sanitized_filename
            
            # Step 1: Create comment via external API
            result = CommentService.create_comment(event_id=event_id, comment=comment, owner=username)
            
            # Step 2: Extract comment_id from response
            comment_id = self._extract_comment_id(result)
            if not comment_id:
                # Generate UUID if external API didn't return ID
                comment_id = str(uuid.uuid4())
                logger.warning(f"External API did not return comment_id, using generated UUID: {comment_id}")
            
            # Step 3: Save to local database only if file is uploaded
            if file_data:
                Comment.create_comment(
                    event_id=event_id,
                    comment_id=comment_id,
                    owner=username,
                    message=comment,
                    file_type=file_type,
                    file_name=file_name,
                    file_obj=file_data
                )
            
            return {"data": result}, 201
            
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def get(self, username=None, event_id=None, comment_id=None):
        try:
            if event_id:
                # 获取事件的所有评论
                data = CommentService.retrieve_comments(event_id=event_id)
                return {"data": data}, 200
            else:
                return {"error_message": "event_id is required"}, 400
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500


class CommentDownloadView(Resource):
    """For attachment download"""
    
    @auth_required
    def get(self, username=None, comment_id=None):
        try:
            # 根据 comment_id 获取单个评论（用于下载文件）
            db_comment = CommentService.get_comment_by_comment_id(comment_id)
            if not db_comment or not db_comment.file_obj:
                return {"error_message": "Comment or file not found"}, 404
            
            # 返回文件
            file_obj = BytesIO(db_comment.file_obj)
            # 优先使用保存的文件名，如果没有则根据文件类型生成
            if db_comment.file_name:
                filename = db_comment.file_name
            else:
                filename = f"file_{comment_id}"
                # 根据文件类型设置扩展名
                if db_comment.file_type:
                    ext_map = {
                        'image/jpeg': '.jpg',
                        'image/png': '.png',
                        'image/gif': '.gif',
                        'application/pdf': '.pdf',
                        'application/zip': '.zip',
                    }
                    ext = ext_map.get(db_comment.file_type, '')
                    filename += ext
            
            return send_file(
                file_obj,
                mimetype=db_comment.file_type or 'application/octet-stream',
                as_attachment=True,
                download_name=filename
            )
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
