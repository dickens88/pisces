import json

from flask import request
from flask_restful import Resource

from models.tookits import ToolkitRecord
from utils.auth_util import auth_required
from utils.logger_init import logger
from utils.toolkit_api_engine import call_toolkit_api, load_toolkit_config


def _extract_params_from_field_mapping(field_mapping):
    """Extract params from field_mapping configuration"""
    params = []
    seen_params = set()
    
    for target_field, mapping_config in field_mapping.items():
        param_name = None
        default_value = None
        required = True
        
        if isinstance(mapping_config, str):
            param_name = mapping_config
        elif isinstance(mapping_config, dict):
            param_name = mapping_config.get("source") or mapping_config.get("from")
            default_value = mapping_config.get("default")
            required = default_value is None
        
        if param_name and param_name not in seen_params:
            seen_params.add(param_name)
            param = {
                "name": param_name,
                "label": param_name.replace("_", " ").title()
            }
            if default_value is not None:
                param["default_value"] = default_value
            param["required"] = required
            params.append(param)
    
    return params


def _build_tool_from_config(toolkit_config, username=None):
    """Build tool object from toolkit_config"""
    tool = {
        "app_id": toolkit_config.get("app_id"),
        "app_type": toolkit_config.get("app_type"),
        "title": toolkit_config.get("title")
    }
    
    field_mapping = toolkit_config.get("api", {}).get("request_body", {}).get("field_mapping", {})
    tool["params"] = _extract_params_from_field_mapping(field_mapping)
    
    # Auto-set default value for username parameter from current user
    if username:
        for param in tool["params"]:
            if param.get("name") == "username":
                param["default_value"] = username
                param["required"] = False
                break
    
    return tool


class ToolkitsView(Resource):

    @auth_required
    def get(self, username=None):
        try:
            with open("resources/toolkit_configs.json", "r", encoding="utf-8") as f:
                all_configs = json.load(f)
            
            tools = []
            for toolkit_config in all_configs.get("tools", []):
                tool = _build_tool_from_config(toolkit_config, username)
                tools.append(tool)
            
            return {"tools": tools}, 200
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

            toolkit_record = ToolkitRecord.create_toolkit_record({
                "title": data.get("title"),
                "app_id": data.get("app_id"),
                "app_type": data.get("app_type", ""),
                "params": data.get("params", {}),
                "status": "running",
                "result": None,
                "owner": username,
                "event_id": alert_id
            })
            record_id = toolkit_record["id"]
            logger.info(f"[Toolkit] Created record id={record_id} for alert_id={alert_id} [{username}]")

            try:
                api_result = call_toolkit_api(
                    app_id=data.get("app_id"),
                    app_type=data.get("app_type"),
                    params=data.get("params", {})
                )
                status, result = "completed", json.dumps(api_result) if isinstance(api_result, dict) else str(api_result)
            except Exception as api_ex:
                logger.exception(f"[Toolkit] API call failed for record id={record_id}: {api_ex}")
                status, result = "failed", json.dumps({"error": str(api_ex)})

            updated_record = ToolkitRecord.update_toolkit_record(record_id, {"status": status, "result": result})
            logger.info(f"[Toolkit] Updated record id={record_id} with status={status} [{username}]")
            
            if status == "completed":
                return {"data": updated_record}, 201
            else:
                return {"data": updated_record, "error_message": f"API call failed"}, 500
                
        except Exception as ex:
            logger.exception(ex)
            return {"error_message": str(ex)}, 500
    
