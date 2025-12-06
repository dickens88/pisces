"""
工具API调用引擎 - 基于配置的通用第三方API调用系统
支持通过配置文件适配不同格式的RESTful API（仅支持JSON格式）
"""
import json
from typing import Dict, Any, Optional
import requests
from requests.auth import HTTPBasicAuth

from utils.logger_init import logger
from utils.common_utils import get_proxy


class ToolkitAPIEngine:
    """工具API调用引擎，根据配置调用第三方API"""
    
    def __init__(self, toolkit_config: Dict[str, Any]):
        """
        初始化引擎
        
        Args:
            toolkit_config: 工具配置字典，包含API调用所需的所有配置
        """
        self.config = toolkit_config
        self.app_id = toolkit_config.get("app_id")
        self.app_type = toolkit_config.get("app_type")
        
    def call_api(self, params: Dict[str, Any], alert_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        调用第三方API
        
        Args:
            params: 用户传入的参数
            alert_context: 告警上下文信息（可选），可用于参数模板变量替换
            
        Returns:
            API响应结果字典
        """
        try:
            # 1. 构建请求URL
            url = self._build_url()
            
            # 2. 构建请求头
            headers = self._build_headers()
            
            # 3. 构建请求体
            body = self._build_request_body(params, alert_context)
            
            # 4. 发送请求
            response = self._send_request(url, headers, body)
            
            # 5. 解析响应
            result = self._parse_response(response)
            
            return result
            
        except Exception as e:
            logger.exception(f"[ToolkitAPI] Failed to call API for app_id={self.app_id}: {e}")
            raise
    
    def _build_url(self) -> str:
        """构建请求URL"""
        api_config = self.config.get("api", {})
        base_url = api_config.get("base_url", "")
        endpoint = api_config.get("endpoint", "")
        
        # 支持URL中的变量替换（从配置中读取）
        url_vars = api_config.get("url_variables", {})
        for key, value in url_vars.items():
            endpoint = endpoint.replace(f"{{{key}}}", str(value))
        
        # 拼接完整URL
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
        """构建请求头"""
        api_config = self.config.get("api", {})
        headers = {}
        
        # 基础Content-Type（固定为JSON）
        headers["Content-Type"] = "application/json"
        
        # 自定义请求头
        custom_headers = api_config.get("headers", {})
        headers.update(custom_headers)
        
        # 处理认证
        auth_config = api_config.get("auth", {})
        auth_type = auth_config.get("type", "none")
        
        if auth_type == "api_key":
            # API Key认证
            key_name = auth_config.get("key_name", "X-API-Key")
            key_value = auth_config.get("key_value", "")
            if key_value:
                headers[key_name] = key_value
                
        elif auth_type == "bearer_token":
            # Bearer Token认证
            token = auth_config.get("token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
                
        elif auth_type == "basic_auth":
            # Basic Auth认证（在发送请求时处理）
            pass
            
        elif auth_type == "custom":
            # 自定义认证头
            custom_auth_headers = auth_config.get("headers", {})
            headers.update(custom_auth_headers)
        
        return headers
    
    def _build_request_body(self, params: Dict[str, Any], alert_context: Optional[Dict[str, Any]] = None) -> str:
        """
        构建JSON格式的请求体
        
        Args:
            params: 用户传入的参数
            alert_context: 告警上下文信息
        """
        api_config = self.config.get("api", {})
        body_config = api_config.get("request_body", {})
        
        # 获取字段映射配置
        field_mapping = body_config.get("field_mapping", {})
        
        # 合并参数和上下文
        all_params = {}
        if alert_context:
            all_params.update(alert_context)
        all_params.update(params)
        
        # 构建JSON请求体
        body = self._build_json_body(field_mapping, all_params)
        return json.dumps(body, ensure_ascii=False)
    
    def _build_json_body(self, field_mapping: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """构建JSON请求体"""
        if not field_mapping:
            # 如果没有映射配置，直接使用params
            return params
        
        body = {}
        for target_field, mapping_config in field_mapping.items():
            if isinstance(mapping_config, str):
                # 简单映射：直接使用字符串作为源字段名
                body[target_field] = params.get(mapping_config)
            elif isinstance(mapping_config, dict):
                # 复杂映射：支持更多配置选项
                source_field = mapping_config.get("source", mapping_config.get("from"))
                default_value = mapping_config.get("default")
                transform = mapping_config.get("transform")  # 转换函数名
                
                value = params.get(source_field, default_value)
                
                # 应用转换函数
                if transform and value is not None:
                    value = self._apply_transform(transform, value, params)
                
                # 支持嵌套字段
                if "." in target_field:
                    self._set_nested_field(body, target_field, value)
                else:
                    body[target_field] = value
            else:
                # 固定值
                body[target_field] = mapping_config
        
        return body
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """获取嵌套字典的值，支持点号分隔的键路径"""
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
            if value is None:
                return None
        return value
    
    def _set_nested_field(self, data: Dict[str, Any], key: str, value: Any):
        """设置嵌套字典的字段"""
        keys = key.split(".")
        current = data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    def _apply_transform(self, transform_name: str, value: Any, params: Dict[str, Any]) -> Any:
        """应用转换函数"""
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
        """发送HTTP请求（仅支持POST + JSON格式）"""
        api_config = self.config.get("api", {})
        method = api_config.get("method", "POST").upper()
        timeout = api_config.get("timeout", 30)
        
        # 处理Basic Auth
        auth = None
        auth_config = api_config.get("auth", {})
        if auth_config.get("type") == "basic_auth":
            username = auth_config.get("username", "")
            password = auth_config.get("password", "")
            if username and password:
                auth = HTTPBasicAuth(username, password)
        
        proxies = get_proxy()
        
        if method == "POST":
            # 使用json参数自动序列化并设置Content-Type
            response = requests.post(
                url, 
                json=json.loads(body),  # 将JSON字符串解析为字典，让requests自动处理
                headers=headers, 
                auth=auth,
                proxies=proxies, 
                verify=False, 
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}, only POST is supported")
        
        return response
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """解析API响应"""
        api_config = self.config.get("api", {})
        response_config = api_config.get("response", {})
        
        # 检查HTTP状态码
        expected_status = response_config.get("expected_status", [200])
        if response.status_code not in expected_status:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            logger.error(f"[ToolkitAPI] {error_msg}")
            raise Exception(error_msg)
        
        # 解析响应体
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw": response.text}
        else:
            response_data = {"raw": response.text}
        
        # 提取结果字段
        result_path = response_config.get("result_path", "")
        if result_path:
            result = self._extract_result(response_data, result_path)
        else:
            result = response_data
        
        # 检查业务层面的错误
        error_path = response_config.get("error_path", "")
        if error_path:
            error = self._extract_result(response_data, error_path)
            if error:
                error_msg = response_config.get("error_message_template", "API error: {error}").format(error=error)
                raise Exception(error_msg)
        
        # 构建标准化的返回结果
        return {
            "success": True,
            "status_code": response.status_code,
            "data": result,
            "raw_response": response_data
        }
    
    def _extract_result(self, data: Any, path: str) -> Any:
        """从响应数据中提取指定路径的值，支持点号分隔的路径"""
        if not path:
            return data
        
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                value = value[int(key)] if int(key) < len(value) else None
            else:
                return None
            if value is None:
                return None
        return value


def load_toolkit_config(app_id: str, app_type: str = None) -> Optional[Dict[str, Any]]:
    """
    从配置文件加载工具配置
    
    Args:
        app_id: 应用ID
        app_type: 应用类型（可选）
        
    Returns:
        工具配置字典，如果未找到则返回None
    """
    try:
        import os
        config_file = "resources/toolkit_configs.json"
        
        if not os.path.exists(config_file):
            logger.warning(f"Toolkit config file not found: {config_file}")
            return None
        
        with open(config_file, "r", encoding="utf-8") as f:
            all_configs = json.load(f)
        
        # 查找匹配的配置
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
    """
    调用工具API的便捷函数
    
    Args:
        app_id: 应用ID
        app_type: 应用类型
        params: 用户传入的参数
        alert_context: 告警上下文信息（可选）
        
    Returns:
        API响应结果
    """
    # 加载配置
    toolkit_config = load_toolkit_config(app_id, app_type)
    if not toolkit_config:
        raise ValueError(f"Toolkit config not found for app_id={app_id}, app_type={app_type}")
    
    # 创建引擎并调用
    engine = ToolkitAPIEngine(toolkit_config)
    return engine.call_api(params, alert_context)

