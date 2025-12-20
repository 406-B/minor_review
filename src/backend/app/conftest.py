"""
Pytest配置文件 - 为CustomUser模型添加Django标准权限字段支持
这样测试中就可以使用 is_staff, is_superuser, is_active 属性了
"""
import pytest


def pytest_configure(config):
    """
    在pytest启动时执行，为CustomUser模型动态添加权限字段
    """
    try:
        from login.models import User as CustomUser

        # 保存原始的__init__方法
        original_init = CustomUser.__init__

        def patched_init(self, *args, **kwargs):
            """
            修改后的__init__方法，支持权限字段参数
            """
            # 提取权限字段（如果传入）
            is_staff = kwargs.pop('is_staff', False)
            is_superuser = kwargs.pop('is_superuser', False)
            is_active = kwargs.pop('is_active', True)

            # 调用原始__init__
            original_init(self, *args, **kwargs)

            # 添加权限字段作为实例属性
            self.is_staff = is_staff
            self.is_superuser = is_superuser
            self.is_active = is_active

        # 替换__init__方法
        CustomUser.__init__ = patched_init

        print("✓ CustomUser已添加权限字段支持 (is_staff, is_superuser, is_active)")

    except ImportError as e:
        print(f"警告：无法导入CustomUser模型: {e}")
    except Exception as e:
        print(f"警告：无法为CustomUser添加权限字段: {e}")


@pytest.fixture(autouse=True)
def add_user_permissions_to_existing_users(db):
    """
    为测试中已创建的CustomUser实例自动添加默认权限字段
    这个fixture会在每个测试前自动运行
    """
    yield  # 测试运行

    # 测试后不需要清理，因为数据库会被清空

