# -*- coding: utf-8 -*-
import base64
import datetime

import jwt
import scrypt
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from login.controllers import get_user


def generate_jwt(payload, expiry=None):
    """
    生成jwt
    :param payload: dict 载荷
    :param expiry: datetime 有效期
    :return: 生成jwt
    """
    if expiry is None:
        now = datetime.datetime.now()
        expire_hours = int(settings.JWT_EXPIRE_HOURS) if int(settings.JWT_EXPIRE_HOURS) > 0 else 1
        expiry = now + datetime.timedelta(hours=expire_hours)
        print("now:", now)
        print("expiry:", expiry)

    _payload = {"exp": expiry}
    _payload.update(payload)

    secret = settings.JWT_SECRET

    token = jwt.encode(_payload, secret, algorithm="HS256")

    return token


def verify_jwt(token):
    """
    校验jwt
    :param token: jwt
    :return: dict: payload
    """
    secret = settings.JWT_SECRET

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        payload = None

    return payload


def encrypt_password(password):
    salt = settings.SALT
    key = scrypt.hash(password, salt, 32768, 8, 1, 32)
    return base64.b64encode(key).decode("ascii")


def jwt_authentication(request):
    """
    根据jwt验证用户身份
    支持两种格式：
    1. Authorization: <token>
    2. Authorization: Bearer <token>
    """
    request.user = None
    token = request.headers.get("Authorization")
    if token: # jwt 认证方式不规范 11/2 yyf
        # 处理 "Bearer <token>" 格式
        if token.startswith("Bearer "):
            token = token[7:]  # 移除 "Bearer " 前缀（7个字符）
        elif token.startswith("bearer "):
            token = token[7:]  # 兼容小写
        
        payload = verify_jwt(token)
        if payload:
            user_id = payload.get("user_id")
            user, result = get_user(user_id)
            if result:
                request.user = user


def login_required(func):
    """
    用户必须登录装饰器
    使用方法：放在 method_decorators 中
    """

    # @wraps(func)
    def wrapper(*args, **kwargs):
        # 兼容 APIView.method(self, request, ...) 与函数视图(request, ...)
        if len(args) >= 2 and hasattr(args[1], 'META'):
            request = args[1]  # APIView 方法：self, request, ...
        else:
            request = args[0]  # 函数视图：request, ...

        jwt_authentication(request)
        if not request.user:
            return Response(
                {"message": "User must be authorized."}, status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            return func(*args, **kwargs)

    return wrapper



