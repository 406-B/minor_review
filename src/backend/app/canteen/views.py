"""
食堂消费数据API视图
"""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.jwt import login_required

from .controllers import (
    bind_idserial_and_fetch,
    get_user_consumption,
    refresh_consumption_data,
    unbind_consumption,
)
from .serializers import (
    BindIdserialSerializer,
    CanteenConsumptionSerializer,
    RefreshDataSerializer,
)


@extend_schema(
    responses={
        200: OpenApiResponse(
            description="获取消费数据成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                    "message": {"type": "string"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "username": {"type": "string"},
                            "idserial": {"type": "string"},
                            "total_amount": {"type": "string"},
                            "canteen_count": {"type": "integer"},
                            "canteen_data": {"type": "object"},
                            "last_fetched": {"type": "string"},
                            "created": {"type": "string"},
                        }
                    }
                }
            }
        ),
        401: OpenApiResponse(description="未登录"),
        404: OpenApiResponse(description="未绑定学号"),
    },
    description="获取当前用户的食堂消费数据",
    summary="获取消费数据",
    operation_id="get_consumption",
    tags=["Canteen"],
)
@api_view(["GET"])
@login_required
def get_consumption(request):
    """
    获取当前用户的食堂消费数据
    """
    consumption = get_user_consumption(request.user)
    
    if not consumption:
        return Response(
            {
                "code": 404,
                "message": "未绑定学号，请先绑定",
                "data": None
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CanteenConsumptionSerializer(consumption)
    return Response(
        {
            "code": 200,
            "message": "获取成功",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "idserial": {"type": "string", "description": "学号"},
                "browser_type": {
                    "type": "string",
                    "enum": ["chrome", "firefox", "edge", "safari"],
                    "default": "chrome",
                    "description": "浏览器类型"
                }
            },
            "required": ["idserial"]
        }
    },
    responses={
        200: OpenApiResponse(description="绑定成功"),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
        500: OpenApiResponse(description="绑定失败"),
    },
    description="绑定学号并获取食堂消费数据（会自动打开浏览器让用户登录）",
    summary="绑定学号",
    operation_id="bind_idserial",
    tags=["Canteen"],
)
@api_view(["POST"])
@login_required
def bind_idserial(request):
    """
    绑定学号并获取消费数据
    会自动打开浏览器，等待用户登录一卡通系统
    """
    serializer = BindIdserialSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                "code": 400,
                "message": "参数错误",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    idserial = serializer.validated_data.get("idserial")
    browser_type = serializer.validated_data.get("browser_type", "chrome")
    
    success, message, data = bind_idserial_and_fetch(
        request.user,
        idserial,
        browser_type
    )
    
    if success:
        return Response(
            {
                "code": 200,
                "message": message,
                "data": data
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                "code": 500,
                "message": message,
                "data": None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "servicehall": {
                    "type": "string",
                    "description": "servicehall cookie（可选）"
                },
                "browser_type": {
                    "type": "string",
                    "enum": ["chrome", "firefox", "edge", "safari"],
                    "default": "chrome",
                    "description": "浏览器类型（当需要重新获取cookie时）"
                }
            }
        }
    },
    responses={
        200: OpenApiResponse(description="刷新成功"),
        400: OpenApiResponse(description="参数错误或未绑定学号"),
        401: OpenApiResponse(description="未登录"),
        500: OpenApiResponse(description="刷新失败"),
    },
    description="刷新食堂消费数据（优先使用已保存的cookie，失效则重新获取）",
    summary="刷新消费数据",
    operation_id="refresh_consumption",
    tags=["Canteen"],
)
@api_view(["POST"])
@login_required
def refresh_consumption(request):
    """
    刷新消费数据
    优先使用保存的cookie，如果失效则自动打开浏览器重新获取
    """
    serializer = RefreshDataSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                "code": 400,
                "message": "参数错误",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    servicehall = serializer.validated_data.get("servicehall")
    browser_type = serializer.validated_data.get("browser_type", "chrome")
    
    success, message, data = refresh_consumption_data(
        request.user,
        servicehall,
        browser_type
    )
    
    if success:
        return Response(
            {
                "code": 200,
                "message": message,
                "data": data
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                "code": 400 if "请先绑定" in message else 500,
                "message": message,
                "data": None
            },
            status=status.HTTP_400_BAD_REQUEST if "请先绑定" in message 
                   else status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={
        200: OpenApiResponse(description="解绑成功"),
        400: OpenApiResponse(description="未绑定学号"),
        401: OpenApiResponse(description="未登录"),
        500: OpenApiResponse(description="解绑失败"),
    },
    description="解绑学号并删除食堂消费数据",
    summary="解绑学号",
    operation_id="unbind_consumption",
    tags=["Canteen"],
)
@api_view(["DELETE"])
@login_required
def unbind(request):
    """
    解绑学号并删除消费数据
    """
    success, message = unbind_consumption(request.user)
    
    if success:
        return Response(
            {
                "code": 200,
                "message": message
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                "code": 400 if "未绑定" in message else 500,
                "message": message
            },
            status=status.HTTP_400_BAD_REQUEST if "未绑定" in message
                   else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
