from django.apps import AppConfig


class ListConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "list"

    def ready(self):
        """应用启动时注册信号"""
        import list.signals  # 导入信号处理模块
