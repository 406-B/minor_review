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
from .models import CanteenConsumption
from .serializers import (
    BindIdserialSerializer,
    CanteenConsumptionSerializer,
    RefreshDataSerializer,
)
from .services import (
    auto_login_and_fetch_cookie,
    check_login_status,
    cleanup_login_session,
    fetch_canteen_data,
    submit_verification_code,
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
                "idserial": {
                    "type": "string",
                    "description": "学号(可选,不填则系统从一卡通userinfo页面自动提取)"
                },
                "browser_type": {
                    "type": "string",
                    "enum": ["chrome", "firefox", "edge", "safari"],
                    "default": "chrome",
                    "description": "浏览器类型"
                }
            }
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
    
    # idserial可选,不填则由系统自动提取
    idserial = serializer.validated_data.get("idserial") or None
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


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "required": ["idserial", "password"],
            "properties": {
                "idserial": {
                    "type": "string",
                    "description": "学号"
                },
                "password": {
                    "type": "string",
                    "description": "密码"
                },
                "headless": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否使用无头模式"
                },
                "browser_type": {
                    "type": "string",
                    "enum": ["chrome", "firefox", "edge"],
                    "default": "chrome",
                    "description": "浏览器类型"
                }
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="登录流程已启动，等待验证码",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                    "message": {"type": "string"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "status": {"type": "string"}
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
        500: OpenApiResponse(description="启动登录失败"),
    },
    description="自动登录一卡通系统并获取cookie（需要后续提交验证码）",
    summary="开始自动登录",
    operation_id="start_auto_login",
    tags=["Canteen"],
)
@api_view(["POST"])
@login_required
def start_auto_login(request):
    """
    开始自动登录流程
    
    返回session_id，用于后续提交验证码
    """
    idserial = request.data.get("idserial")
    password = request.data.get("password")
    headless = request.data.get("headless", True)
    browser_type = request.data.get("browser_type", "chrome")
    
    if not idserial or not password:
        return Response(
            {
                "code": 400,
                "message": "学号和密码不能为空",
                "data": None
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = auto_login_and_fetch_cookie(
        idserial=idserial,
        password=password,
        headless=headless,
        browser_type=browser_type
    )
    
    if result["success"]:
        # 检查是否已完成（无需验证码）
        if result["status"] == "completed":
            return Response(
                {
                    "code": 200,
                    "message": "登录成功，无需验证码",
                    "data": {
                        "session_id": result["session_id"],
                        "status": result["status"],
                        "servicehall": result.get("servicehall"),
                        "idserial": idserial
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            # 需要验证码
            return Response(
                {
                    "code": 200,
                    "message": "登录流程已启动，请提交验证码",
                    "data": {
                        "session_id": result["session_id"],
                        "status": result["status"]
                    }
                },
                status=status.HTTP_200_OK
            )
    else:
        return Response(
            {
                "code": 500,
                "message": result.get("error", "启动登录失败"),
                "data": None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "required": ["session_id", "verification_code"],
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "登录会话ID"
                },
                "verification_code": {
                    "type": "string",
                    "description": "验证码"
                }
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="验证码已提交",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        ),
        400: OpenApiResponse(description="参数错误或会话状态错误"),
        401: OpenApiResponse(description="未登录"),
    },
    description="提交验证码到登录会话",
    summary="提交验证码",
    operation_id="submit_verification",
    tags=["Canteen"],
)
@api_view(["POST"])
@login_required
def submit_verification(request):
    """
    提交验证码
    """
    session_id = request.data.get("session_id")
    verification_code = request.data.get("verification_code")
    
    if not session_id or not verification_code:
        return Response(
            {
                "code": 400,
                "message": "会话ID和验证码不能为空"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = submit_verification_code(session_id, verification_code)
    
    if result["success"]:
        # 返回更新后的会话状态，便于前端立即判断是否已登录完成并拿到 servicehall
        status_result = check_login_status(session_id)
        return Response(
            {
                "code": 200,
                "message": result["message"],
                "data": status_result
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                "code": 400,
                "message": result["message"]
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    parameters=[
        {
            "name": "session_id",
            "in": "query",
            "required": True,
            "schema": {"type": "string"},
            "description": "登录会话ID"
        }
    ],
    responses={
        200: OpenApiResponse(
            description="获取登录状态成功",
            response={
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                    "message": {"type": "string"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "servicehall": {"type": "string"},
                            "error": {"type": "string"}
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
    },
    description="检查自动登录的状态",
    summary="检查登录状态",
    operation_id="check_auto_login_status",
    tags=["Canteen"],
)
@api_view(["GET"])
@login_required
def check_auto_login_status(request):
    """
    检查登录状态
    """
    session_id = request.query_params.get("session_id")
    
    if not session_id:
        return Response(
            {
                "code": 400,
                "message": "会话ID不能为空",
                "data": None
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = check_login_status(session_id)
    
    # NOTE: 不在此处立即清理会话，保留会话以便前端可以在登录完成后获取到返回的 servicehall 并进行后续绑定。
    # 会话的清理应由绑定流程（如 fetch-with-cookie）或超时/后台任务负责，避免在并发轮询中产生竞态条件。
    
    return Response(
        {
            "code": 200,
            "message": "获取状态成功",
            "data": {
                "status": result["status"],
                "servicehall": result.get("servicehall"),
                "error": result.get("error")
            }
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "required": ["idserial", "servicehall"],
            "properties": {
                "idserial": {
                    "type": "string",
                    "description": "学号"
                },
                "servicehall": {
                    "type": "string",
                    "description": "servicehall cookie值"
                }
            }
        }
    },
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
                            "idserial": {"type": "string"},
                            "total_amount": {"type": "number"},
                            "canteen_count": {"type": "integer"},
                            "canteens": {"type": "object"}
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description="参数错误"),
        401: OpenApiResponse(description="未登录"),
        500: OpenApiResponse(description="获取数据失败"),
    },
    description="使用cookie直接获取食堂消费数据（不保存到数据库）",
    summary="直接获取消费数据",
    operation_id="fetch_consumption_with_cookie",
    tags=["Canteen"],
)
@api_view(["POST"])
@login_required
def fetch_consumption_with_cookie(request):
    """
    使用cookie直接获取消费数据并绑定到用户账号
    """
    idserial = request.data.get("idserial")
    servicehall = request.data.get("servicehall")
    
    if not idserial or not servicehall:
        return Response(
            {
                "code": 400,
                "message": "学号和servicehall不能为空",
                "data": None
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = fetch_canteen_data(idserial, servicehall)
    
    if result["success"]:
        # 保存绑定到数据库
        from django.db import transaction
        try:
            with transaction.atomic():
                consumption, created = CanteenConsumption.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'idserial': idserial,
                        'servicehall_cookie': servicehall,
                        'total_amount': result["data"]["total_amount"],
                        'canteen_count': result["data"]["canteen_count"],
                        'canteen_data': result["data"]["canteens"]
                    }
                )
            action = "绑定" if created else "更新"
            message = f"{action}成功并获取消费数据"
        except Exception as e:
            message = f"获取成功但保存失败: {str(e)}"
        
        return Response(
            {
                "code": 200,
                "message": message,
                "data": {
                    **result["data"],
                    "idserial": idserial
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                "code": 500,
                "message": result.get("error", "获取数据失败"),
                "data": None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

