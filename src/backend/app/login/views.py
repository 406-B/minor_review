import json

from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.jwt import encrypt_password, generate_jwt, login_required
from utils.register_params_check import register_params_check

from .controllers import create_user, get_user, get_user_with_pass
from .models import User


@extend_schema(
    responses={
        200: OpenApiResponse(
            description="获取用户信息成功",
            response={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "用户ID"},
                    "username": {"type": "string", "description": "用户名"},
                    "nickname": {"type": "string", "description": "用户昵称"},
                    "created": {
                        "type": "string",
                        "format": "date-time",
                        "description": "用户创建时间",
                    },
                    # 仅保留必要字段
                },
            },
        ),
        401: OpenApiResponse(description="未登录"),
    },
    description="获取当前登录用户信息",
    summary="获取当前用户信息",
    operation_id="get_user_info",
)
@api_view(["GET"])
@login_required
def get_user_info(request):
    """
    获取当前登录用户信息
    """
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "created": user.created,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="userId",
            type=int,
            location=OpenApiParameter.PATH,
            description="用户ID",
        )
    ],
    request={
        "application/json": {
            "type": "object",
        }
    },
    responses={
        200: OpenApiResponse(
            description="获取用户信息成功",
            response={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "用户ID"},
                    "nickname": {"type": "string", "description": "用户昵称"},
                    "created": {
                        "type": "string",
                        "format": "date-time",
                        "description": "用户创建时间",
                    },
                },
            },
        ),
        401: OpenApiResponse(description="未登录"),
        404: OpenApiResponse(description="用户不存在"),
        500: OpenApiResponse(description="服务器内部错误"),
    },
    description="获取用户昵称",
    summary="获取用户昵称",
)
@api_view(["GET"])
@login_required
def get_user_info_by_id(request, userId):
    """
    获取指定用户信息
    """
    try:
        user, result = get_user(userId)
        if result:
            return Response(
                {
                    "id": user.id,
                    "nickname": user.nickname,
                    "created": user.created,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"message": user}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    """
    用户登录视图类
    """

    # permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "用户名"},
                    "password": {"type": "string", "description": "密码"},
                },
                "required": ["username", "password"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="登录成功",
                response={
                    "type": "object",
                    "properties": {
                        "jwt": {"type": "string", "description": "JWT令牌"},
                        "userId": {"type": "integer", "description": "用户ID"},
                        "username": {"type": "string", "description": "用户名"},
                        "nickname": {"type": "string", "description": "用户昵称"},
                    },
                },
            ),
            401: OpenApiResponse(description="无效的凭证"),
            405: OpenApiResponse(description="方法不允许"),
            400: OpenApiResponse(description="无效的参数"),
        },
        description="用户登录接口",
        summary="用户登录",
    )
    def patch(self, request, *args, **kwargs):
        """
        处理用户登录请求
        """
        try:
            content = request.data
            username = content.get("username")
            password = content.get("password")

            user, result = get_user_with_pass(
                username=username, password=encrypt_password(password)
            )
            if result:
                jwt = generate_jwt({"user_id": user.id, "nickname": user.nickname})
                return Response(
                    {
                        "jwt": jwt,
                        "userId": user.id,
                        "username": user.username,
                        "nickname": user.nickname,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except json.JSONDecodeError:
            return Response({"message": "Bad arguments"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=["OPTIONS"],
        request=None,
        responses={204: OpenApiResponse(description="成功的预检请求")},
        description="处理OPTIONS请求",
        summary="OPTIONS请求",
    )
    def options(self, request, *args, **kwargs):
        """
        处理OPTIONS请求，用于获取允许的HTTP方法
        """
        return HttpResponse(status=204)


@extend_schema(
    request=None,
    responses={
        200: OpenApiResponse(description="登出成功"),
        401: OpenApiResponse(description="未登录"),
    },
    description="用户登出接口",
    summary="用户登出",
)
@api_view(["POST"])
@login_required
def logout(request):
    """
    登出
    本次作业中简化，不做任何操作
    """
    return Response({"message": "ok"}, status=status.HTTP_200_OK)


@extend_schema(
    request={
        "application/json": {
            "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "用户名"},
                    "password": {"type": "string", "description": "密码"},
                    "confirm_password": {"type": "string", "description": "确认密码"},
                    "nickname": {"type": "string", "description": "昵称"},
                },
            "required": ["username", "password", "confirm_password", "nickname"],
        }
    },
    responses={
        200: OpenApiResponse(description="用户注册成功"),
        400: OpenApiResponse(description="无效的参数"),
        405: OpenApiResponse(description="方法不允许"),
        500: OpenApiResponse(description="服务器内部错误"),
    },
    description="用户注册接口，用于创建新用户",
    summary="用户注册",
)
@api_view(["POST"])
def register_user(request):
    """
    用户注册
    """
    if request.method != "POST":
        return Response(
            {"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        content = request.data

        key, passed = register_params_check(content)
        if not passed:
            if key == "confirm_password":
                return Response(
                    {"message": "密码不一致，请仔细检查！"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": f"Invalid arguments: {key}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = content.get("username")
        password = content.get("password")
        nickname = content.get("nickname")

        result = create_user(
            username=username,
            password=encrypt_password(password),
            nickname=nickname,
        )
        if result is True:
            return Response({"message": "ok"}, status=status.HTTP_200_OK)
        elif result == "username_exists":
            return Response({"message": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except json.JSONDecodeError:
        return Response({"message": "Bad arguments"}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"message": "Bad arguments"}, status=status.HTTP_400_BAD_REQUEST)
