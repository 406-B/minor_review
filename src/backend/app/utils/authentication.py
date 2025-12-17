from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .jwt import verify_jwt, get_user


class JWTAuthentication(BaseAuthentication):
    """自定义 JWT 认证类
    支持 Authorization 头格式：
    - Authorization: Bearer <token>
    - Authorization: <token>
    成功时返回 (user, payload)，失败抛出 AuthenticationFailed。
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        token = auth_header
        if token.lower().startswith("bearer "):
            token = token[7:]

        payload = verify_jwt(token)
        # 无效/过期 token：返回 None，让其它认证继续；AllowAny 不受影响
        if not payload:
            return None

        user_id = payload.get("user_id")
        user, result = get_user(user_id)
        if not result:
            return None

        # 自定义 User 模型不继承 AbstractBaseUser，补充 is_authenticated 属性供 DRF 权限使用
        if not hasattr(user, 'is_authenticated'):
            # 简单赋值；若后续需要区分匿名用户可引入包装类
            user.is_authenticated = True  # type: ignore

        return (user, payload)
