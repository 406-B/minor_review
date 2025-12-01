"""
食堂消费数据业务逻辑控制器
"""
from typing import Dict, Optional, Tuple
from django.db import transaction
from login.models import User
from .models import CanteenConsumption
from .services import fetch_and_parse_consumption, fetch_canteen_data


def get_user_consumption(user: User) -> Optional[CanteenConsumption]:
    """
    获取用户的食堂消费记录
    
    Args:
        user: 用户对象
        
    Returns:
        CanteenConsumption对象或None
    """
    try:
        return CanteenConsumption.objects.get(user=user)
    except CanteenConsumption.DoesNotExist:
        return None


def bind_idserial_and_fetch(
    user: User,
    idserial: str,
    browser_type: str = 'chrome'
) -> Tuple[bool, str, Optional[Dict]]:
    """
    绑定学号并获取消费数据
    
    Args:
        user: 用户对象
        idserial: 学号
        browser_type: 浏览器类型
        
    Returns:
        (成功标志, 消息, 数据字典或None)
    """
    try:
        # 获取消费数据（会自动打开浏览器获取cookie）
        result = fetch_and_parse_consumption(
            idserial=idserial,
            browser_type=browser_type
        )
        
        if not result["success"]:
            return False, result["error"], None
        
        # 保存或更新消费记录
        with transaction.atomic():
            consumption, created = CanteenConsumption.objects.update_or_create(
                user=user,
                defaults={
                    'idserial': idserial,
                    'servicehall_cookie': result["servicehall"],
                    'total_amount': result["data"]["total_amount"],
                    'canteen_count': result["data"]["canteen_count"],
                    'canteen_data': result["data"]["canteens"]
                }
            )
        
        action = "绑定" if created else "更新"
        return True, f"{action}成功", result["data"]
        
    except Exception as e:
        return False, f"操作失败: {str(e)}", None


def refresh_consumption_data(
    user: User,
    servicehall: Optional[str] = None,
    browser_type: str = 'chrome'
) -> Tuple[bool, str, Optional[Dict]]:
    """
    刷新用户的消费数据
    
    Args:
        user: 用户对象
        servicehall: servicehall cookie（可选）
        browser_type: 浏览器类型（当需要重新获取cookie时）
        
    Returns:
        (成功标志, 消息, 数据字典或None)
    """
    try:
        # 获取现有记录
        consumption = get_user_consumption(user)
        if not consumption:
            return False, "请先绑定学号", None
        
        # 如果没有提供servicehall，尝试使用保存的cookie
        if not servicehall:
            servicehall = consumption.servicehall_cookie
        
        # 如果仍然没有cookie，需要通过浏览器获取
        if not servicehall:
            result = fetch_and_parse_consumption(
                idserial=consumption.idserial,
                browser_type=browser_type
            )
        else:
            # 直接使用提供的或保存的cookie获取数据
            result = fetch_canteen_data(consumption.idserial, servicehall)
            if result["success"]:
                result = {
                    "success": True,
                    "data": result["data"],
                    "servicehall": servicehall,
                    "error": None
                }
            else:
                # Cookie失效，尝试重新获取
                result = fetch_and_parse_consumption(
                    idserial=consumption.idserial,
                    browser_type=browser_type
                )
        
        if not result["success"]:
            return False, result["error"], None
        
        # 更新消费记录
        with transaction.atomic():
            consumption.servicehall_cookie = result["servicehall"]
            consumption.total_amount = result["data"]["total_amount"]
            consumption.canteen_count = result["data"]["canteen_count"]
            consumption.canteen_data = result["data"]["canteens"]
            consumption.save()
        
        return True, "刷新成功", result["data"]
        
    except Exception as e:
        return False, f"刷新失败: {str(e)}", None


def unbind_consumption(user: User) -> Tuple[bool, str]:
    """
    解绑用户的食堂消费记录
    
    Args:
        user: 用户对象
        
    Returns:
        (成功标志, 消息)
    """
    try:
        consumption = get_user_consumption(user)
        if not consumption:
            return False, "未绑定学号"
        
        consumption.delete()
        return True, "解绑成功"
        
    except Exception as e:
        return False, f"解绑失败: {str(e)}"
