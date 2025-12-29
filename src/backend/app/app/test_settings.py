import os
from .settings import *
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 如果设置了 TEST_IN_DOCKER 环境变量，则使用 Docker 中的 MySQL
if os.environ.get('TEST_IN_DOCKER') == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'minor_review'),
            'USER': os.environ.get('MYSQL_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'database'),
            'HOST': os.environ.get('MYSQL_HOST', 'db'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'TEST': {
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_unicode_ci',
            },
        }
    }
else:
    # 本地测试默认使用 SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
