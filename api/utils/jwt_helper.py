from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from utils.app_config import config


def auth_required(func):
    """
    可切换的认证装饰器：
    - 当 application.jwt_disabled 为 True 时跳过 JWT 校验
    - 否则执行 JWT 校验，并把用户名通过关键字参数传给被修饰函数
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        jwt_disabled = config.get("application.jwt_disabled", False)

        if jwt_disabled:
            kwargs.setdefault("username", "debug")
            return func(*args, **kwargs)

        verify_jwt_in_request()
        username = get_jwt_identity()

        # 通过关键字参数传递，避免覆盖 methods 的 self
        kwargs.setdefault("username", username)
        return func(*args, **kwargs)

    return wrapper


