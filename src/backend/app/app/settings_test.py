"""
Django settings for testing - 使用 SQLite 作为测试数据库
"""
from .settings import *

# 覆盖数据库配置为 SQLite（测试用）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # 使用内存数据库，测试更快
    }
}

# 禁用迁移（测试时）
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 测试时禁用某些中间件以提高速度
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# 测试时使用更简单的密码验证
AUTH_PASSWORD_VALIDATORS = []

