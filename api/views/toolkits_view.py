import json

from flask import request
from flask_restful import Resource

from models.tookits import ToolkitRecord
from utils.auth_util import auth_required
from utils.logger_init import logger
from utils.toolkit_api_engine import call_toolkit_api, load_toolkit_config


def _get_param_mapping_info(field_mapping, param_name):
    """从 field_mapping 中查找参数映射信息，返回 (source_field, default_value)"""
    for mapping_config in field_mapping.values():
        if isinstance(mapping_config, str):
            if mapping_config == param_name:
                return param_name, None
        elif isinstance(mapping_config, dict):
            source = mapping_config.get("source") or mapping_config.get("from")
            if source == param_name:
                return param_name, mapping_config.get("default")
    return None, None


def _enrich_tool_params(tool, toolkit_config):
    """为工具参数添加 required 和 default_value 字段"""
    field_mapping = toolkit_config.get("api", {}).get("request_body", {}).get("field_mapping", {})
    
    for param in tool.get("params", []):
        param_name = param.get("name")
        if not param_name:
            param["required"] = True
            continue
        
        source_field, default_value = _get_param_mapping_info(field_mapping, param_name)
        
        if source_field:
            param["required"] = default_value is None
            if default_value is not None:
                param["default_value"] = default_value
        else:
            param["required"] = True


class ToolkitsView(Resource):

    @auth_required
    def get(self, username=None):
        try:
            with open("resources/response_toolkits.json", "r", encoding="utf-8") as f:
                toolkits_data = json.loads(f.read())
            
            for tool in toolkits_data.get("tools", []):
                app_id = tool.get("app_id")
                if not app_id:
                    continue
                
                toolkit_config = load_toolkit_config(app_id)
                if toolkit_config:
                    _enrich_tool_params(tool, toolkit_config)
                else:
                    for param in tool.get("params", []):
                        param.setdefault("required", True)
            
            return toolkits_data, 200
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
    
