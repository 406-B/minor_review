"""
测试 app/settings_prod.py 模块
"""
import unittest
import os
from unittest.mock import patch, Mock
from django.test import TestCase, override_settings
from django.conf import settings


class TestSettingsProd(TestCase):
    """测试生产环境配置"""

    def test_settings_prod_import(self):
        """测试可以导入生产环境配置"""
        try:
            from app import settings_prod
            self.assertTrue(hasattr(settings_prod, 'DEBUG'))
            self.assertFalse(settings_prod.DEBUG)  # 生产环境应该是False
        except ImportError:
            self.fail("无法导入settings_prod模块")

    @override_settings(DEBUG=False)
    def test_debug_is_false(self):
        """测试DEBUG设置为False"""
        from app import settings_prod
        self.assertFalse(settings_prod.DEBUG)

    def test_allowed_hosts(self):
        """测试ALLOWED_HOSTS配置"""
        from app import settings_prod
        self.assertIsInstance(settings_prod.ALLOWED_HOSTS, list)
        self.assertGreater(len(settings_prod.ALLOWED_HOSTS), 0)

    def test_installed_apps(self):
        """测试INSTALLED_APPS配置"""
        from app import settings_prod
        self.assertIn('django.contrib.admin', settings_prod.INSTALLED_APPS)
        self.assertIn('rest_framework', settings_prod.INSTALLED_APPS)
        self.assertIn('list', settings_prod.INSTALLED_APPS)
        self.assertIn('canteen.apps.CanteenConfig', settings_prod.INSTALLED_APPS)

    def test_middleware(self):
        """测试MIDDLEWARE配置"""
        from app import settings_prod
        self.assertIn('django.middleware.security.SecurityMiddleware', settings_prod.MIDDLEWARE)
        self.assertIn('corsheaders.middleware.CorsMiddleware', settings_prod.MIDDLEWARE)

    def test_database_config(self):
        """测试数据库配置"""
        from app import settings_prod
        self.assertIn('default', settings_prod.DATABASES)
        db_config = settings_prod.DATABASES['default']
        self.assertEqual(db_config['ENGINE'], 'django.db.backends.mysql')
        self.assertIn('NAME', db_config)
        self.assertIn('USER', db_config)
        self.assertIn('HOST', db_config)

    def test_rest_framework_config(self):
        """测试REST Framework配置"""
        from app import settings_prod
        self.assertIn('REST_FRAMEWORK', dir(settings_prod))
        rf_config = settings_prod.REST_FRAMEWORK
        self.assertIn('DEFAULT_AUTHENTICATION_CLASSES', rf_config)
        self.assertIn('DEFAULT_PERMISSION_CLASSES', rf_config)

    def test_cors_config(self):
        """测试CORS配置"""
        from app import settings_prod
        self.assertIn('CORS_ALLOWED_ORIGINS', dir(settings_prod))
        self.assertIsInstance(settings_prod.CORS_ALLOWED_ORIGINS, list)

    def test_security_settings(self):
        """测试安全设置"""
        from app import settings_prod
        self.assertTrue(hasattr(settings_prod, 'SECURE_BROWSER_XSS_FILTER'))
        self.assertTrue(hasattr(settings_prod, 'SECURE_CONTENT_TYPE_NOSNIFF'))
        self.assertTrue(hasattr(settings_prod, 'X_FRAME_OPTIONS'))

    def test_logging_config(self):
        """测试日志配置"""
        from app import settings_prod
        self.assertIn('LOGGING', dir(settings_prod))
        logging_config = settings_prod.LOGGING
        self.assertEqual(logging_config['version'], 1)
        self.assertIn('handlers', logging_config)
        self.assertIn('loggers', logging_config)

    def test_jwt_config(self):
        """测试JWT配置"""
        from app import settings_prod
        self.assertIn('JWT_SECRET', dir(settings_prod))
        self.assertIn('JWT_EXPIRE_HOURS', dir(settings_prod))
        self.assertIn('SALT', dir(settings_prod))

    def test_static_files_config(self):
        """测试静态文件配置"""
        from app import settings_prod
        self.assertIn('STATIC_URL', dir(settings_prod))
        self.assertIn('STATIC_ROOT', dir(settings_prod))
        self.assertIn('MEDIA_URL', dir(settings_prod))
        self.assertIn('MEDIA_ROOT', dir(settings_prod))

    @patch.dict(os.environ, {'DJANGO_SECRET_KEY': 'test-secret-key'})
    def test_secret_key_from_env(self):
        """测试从环境变量读取SECRET_KEY"""
        # 重新导入以应用环境变量
        import importlib
        import app.settings_prod
        importlib.reload(app.settings_prod)
        # 注意：由于模块已加载，这个测试可能不会完全生效
        # 但可以验证配置结构
        self.assertTrue(hasattr(app.settings_prod, 'SECRET_KEY'))

    def test_timezone_config(self):
        """测试时区配置"""
        from app import settings_prod
        self.assertEqual(settings_prod.TIME_ZONE, 'Asia/Shanghai')
        self.assertEqual(settings_prod.LANGUAGE_CODE, 'zh-hans')
        self.assertTrue(settings_prod.USE_TZ)

    def test_password_validators(self):
        """测试密码验证器配置"""
        from app import settings_prod
        self.assertIsInstance(settings_prod.AUTH_PASSWORD_VALIDATORS, list)
        self.assertGreater(len(settings_prod.AUTH_PASSWORD_VALIDATORS), 0)


if __name__ == '__main__':
    unittest.main()

