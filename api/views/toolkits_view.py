import json
from flask import request
from flask_restful import Resource

from models.tookits import ToolkitRecord
from utils.auth_util import auth_required
from utils.logger_init import logger


class ToolkitsView(Resource):

    @auth_required
    def get(self, username=None):
        try:
            with open("resources/response_toolkits.json", "r", encoding="utf-8") as f:
                toolkits = json.loads(f.read())
            return toolkits, 200
        except Exception as e:
            logger.exception(e)
            return {"message": str(e)}, 500

class ToolkitRecordView(Resource):

    @auth_required
    def get(self, username=None, alert_id=None):
        """Query toolkit records by alert_id (event_id)."""
        try:
            if not alert_id:
                return {"error_message": "alert_id is required"}, 400
            
            # Query records by event_id (which stores alert_id)
            records = ToolkitRecord.list_toolkit_records(event_id=alert_id)
            return {"data": records, "total": len(records)}, 200
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500

    @auth_required
    def post(self, username=None, alert_id=None):
        """Create a new toolkit record, call 3rd party API, and update the result."""
        try:
            data = json.loads(request.data or "{}")
            
            # Step 1: Create a new record in database with initial status "running"
            toolkit_payload = {
                "title": data.get("title"),
                "app_id": data.get("app_id"),
                "app_type": data.get("app_type", ""),
                "params": data.get("params", {}),
                "status": "running",
                "result": None,
                "owner": username,
                "event_id": alert_id
            }
            
            toolkit_record = ToolkitRecord.create_toolkit_record(toolkit_payload)
            record_id = toolkit_record["id"]
            logger.info(f"[Toolkit] Created toolkit record id={record_id} for alert_id={alert_id} with status=running. [{username}]")
            
            # Step 2: Call 3rd party API (mock implementation for now)
            try:
                # TODO: Replace this with actual 3rd party API call
                # For now, using mock response
                api_result = self._call_toolkit_api_mock(
                    app_id=data.get("app_id"),
                    app_type=data.get("app_type"),
                    params=data.get("params", {})
                )
                
                # Step 3: Update the record with result and status
                update_payload = {
                    "status": "completed",
                    "result": json.dumps(api_result) if isinstance(api_result, dict) else str(api_result)
                }
                updated_record = ToolkitRecord.update_toolkit_record(record_id, update_payload)
                logger.info(f"[Toolkit] Updated toolkit record id={record_id} with result. Status=completed. [{username}]")
                
                return {"data": updated_record}, 201
                
            except Exception as api_ex:
                # If API call fails, update status to "failed"
                logger.exception(f"[Toolkit] Failed to call 3rd party API for record id={record_id}: {api_ex}")
                update_payload = {
                    "status": "failed",
                    "result": json.dumps({"error": str(api_ex)})
                }
                updated_record = ToolkitRecord.update_toolkit_record(record_id, update_payload)
                return {"data": updated_record, "error_message": f"API call failed: {str(api_ex)}"}, 500
                
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
    
    def _call_toolkit_api_mock(self, app_id, app_type, params):
        """Mock implementation for 3rd party API call.
        
        TODO: Replace this with actual API call when ready.
        Example implementation:
        - Use requests library to call the actual API
        - Handle authentication if needed
        - Parse and return the response
        """
        # Mock response for now
        return {
            "success": True,
            "result": "Mock toolkit execution result",
        }
