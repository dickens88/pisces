import json
from typing import Dict, Any, Optional
import requests
from requests.auth import HTTPBasicAuth

from utils.logger_init import logger


class ToolkitAPIEngine:
    def __init__(self, toolkit_config: Dict[str, Any]):
        self.config = toolkit_config
        self.app_id = toolkit_config.get("app_id")
        self.app_type = toolkit_config.get("app_type")
        
    def call_api(self, params: Dict[str, Any], alert_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            url = self._build_url()
            headers = self._build_headers()
            body = self._build_request_body(params, alert_context)
            response = self._send_request(url, headers, body)
            return self._parse_response(response)
        except Exception as e:
            logger.exception(f"[ToolkitAPI] Failed to call API for app_id={self.app_id}: {e}")
            raise
    
    def _build_url(self) -> str:
        api_config = self.config.get("api", {})
        base_url = api_config.get("base_url", "")
        endpoint = api_config.get("endpoint", "")
        
        url_vars = api_config.get("url_variables", {})
        for key, value in url_vars.items():
            endpoint = endpoint.replace(f"{{{key}}}", str(value))
        
        if base_url and endpoint:
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        elif base_url:
            url = base_url
        elif endpoint:
            url = endpoint
        else:
            raise ValueError("API base_url or endpoint must be configured")
        
        return url
    
    def _build_headers(self) -> Dict[str, str]:
        api_config = self.config.get("api", {})
        headers = {"Content-Type": "application/json"}
        
        custom_headers = api_config.get("headers", {})
        headers.update(custom_headers)
        
        auth_config = api_config.get("auth", {})
        auth_type = auth_config.get("type", "none")
        
        if auth_type == "api_key":
            key_name = auth_config.get("key_name", "X-API-Key")
            key_value = auth_config.get("key_value", "")
            if key_value:
                headers[key_name] = key_value
        elif auth_type == "bearer_token":
            token = auth_config.get("token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "basic_auth":
            pass
        elif auth_type == "custom":
            custom_auth_headers = auth_config.get("headers", {})
            headers.update(custom_auth_headers)
        
        return headers
    
    def _build_request_body(self, params: Dict[str, Any], alert_context: Optional[Dict[str, Any]] = None) -> str:
        api_config = self.config.get("api", {})
        body_config = api_config.get("request_body", {})
        field_mapping = body_config.get("field_mapping", {})
        
        all_params = {}
        if alert_context:
            all_params.update(alert_context)
        all_params.update(params)
        
        body = self._build_json_body(field_mapping, all_params)
        return json.dumps(body, ensure_ascii=False)
    
    def _build_json_body(self, field_mapping: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        if not field_mapping:
            return params
        
        body = {}
        for target_field, mapping_config in field_mapping.items():
            if isinstance(mapping_config, str):
                # If string exists in params, use it as param name; otherwise use as fixed value
                if mapping_config in params:
                    value = params.get(mapping_config)
                else:
                    value = mapping_config
                if "." in target_field:
                    self._set_nested_field(body, target_field, value)
                else:
                    body[target_field] = value
            elif isinstance(mapping_config, dict):
                source_field = mapping_config.get("source", mapping_config.get("from"))
                default_value = mapping_config.get("default")
                transform = mapping_config.get("transform")
                
                value = params.get(source_field, default_value)
                
                if transform and value is not None:
                    value = self._apply_transform(transform, value, params)
                
                if "." in target_field:
                    self._set_nested_field(body, target_field, value)
                else:
                    body[target_field] = value
            else:
                if "." in target_field:
                    self._set_nested_field(body, target_field, mapping_config)
                else:
                    body[target_field] = mapping_config
        
        return body
    
    def _set_nested_field(self, data: Dict[str, Any], key: str, value: Any):
        keys = key.split(".")
        current = data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    def _apply_transform(self, transform_name: str, value: Any, params: Dict[str, Any]) -> Any:
        transforms = {
            "to_string": lambda v: str(v),
            "to_int": lambda v: int(v) if v else 0,
            "to_float": lambda v: float(v) if v else 0.0,
            "to_list": lambda v: [v] if not isinstance(v, list) else v,
            "join": lambda v: ",".join(v) if isinstance(v, list) else str(v),
        }
        
        transform_func = transforms.get(transform_name)
        if transform_func:
            try:
                return transform_func(value)
            except Exception as e:
                logger.warning(f"Transform {transform_name} failed: {e}")
                return value
        return value
    
    def _send_request(self, url: str, headers: Dict[str, str], body: str) -> requests.Response:
        api_config = self.config.get("api", {})
        method = api_config.get("method", "POST").upper()
        timeout = api_config.get("timeout", 30)
        
        auth = None
        auth_config = api_config.get("auth", {})
        if auth_config.get("type") == "basic_auth":
            username = auth_config.get("username", "")
            password = auth_config.get("password", "")
            if username and password:
                auth = HTTPBasicAuth(username, password)
        
        # proxies = get_proxy()
        
        if method == "POST":
            response = requests.post(
                url, 
                json=json.loads(body),
                headers=headers, 
                auth=auth,
                # proxies=proxies,
                verify=False, 
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}, only POST is supported")
        
        return response
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        api_config = self.config.get("api", {})
        response_config = api_config.get("response", {})
        
        expected_status = response_config.get("expected_status", [200])
        if response.status_code not in expected_status:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            logger.error(f"[ToolkitAPI] {error_msg}")
            raise Exception(error_msg)
        
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            error_msg = f"API response is not valid JSON: {str(e)}. Response text: {response.text[:200]}"
            logger.error(f"[ToolkitAPI] {error_msg}")
            raise Exception(error_msg)
        
        error_path = response_config.get("error_path", "")
        if error_path:
            error = self._extract_result(response_data, error_path)
            if error:
                error_msg = response_config.get("error_message_template", "API error: {error}").format(error=error)
                raise Exception(error_msg)
        
        result_path = response_config.get("result_path", "")
        if result_path:
            result = self._extract_result(response_data, result_path)
            if result is None:
                logger.warning(f"[ToolkitAPI] Result path '{result_path}' not found in response, returning full response")
                result = response_data
        else:
            result = response_data
        
        return {
            "success": True,
            "status_code": response.status_code,
            "data": result,
            "raw_response": response_data
        }
    
    def _extract_result(self, data: Any, path: str) -> Any:
        if not path:
            return data
        
        keys = path.split(".")
        value = data
        
        for key in keys:
            if value is None:
                return None
                
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                if key.isdigit():
                    index = int(key)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        return None
                else:
                    return None
            else:
                return None
                
        return value


def load_toolkit_config(app_id: str, app_type: str = None) -> Optional[Dict[str, Any]]:
    try:
        import os
        config_file = "resources/toolkit_configs.json"
        
        if not os.path.exists(config_file):
            logger.warning(f"Toolkit config file not found: {config_file}")
            return None
        
        with open(config_file, "r", encoding="utf-8") as f:
            all_configs = json.load(f)
        
        tools = all_configs.get("tools", [])
        for tool in tools:
            if tool.get("app_id") == app_id:
                if app_type is None or tool.get("app_type") == app_type:
                    return tool
        
        logger.warning(f"Toolkit config not found for app_id={app_id}, app_type={app_type}")
        return None
        
    except Exception as e:
        logger.exception(f"Failed to load toolkit config: {e}")
        return None


def call_toolkit_api(app_id: str, app_type: str, params: Dict[str, Any], 
                    alert_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    toolkit_config = load_toolkit_config(app_id, app_type)
    if not toolkit_config:
        raise ValueError(f"Toolkit config not found for app_id={app_id}, app_type={app_type}")
    
    engine = ToolkitAPIEngine(toolkit_config)
    return engine.call_api(params, alert_context)
