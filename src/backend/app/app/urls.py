"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # API 路由
    path("api/", include("list.urls")),
    path("api/v1/", include("list.urls")),
    # 登录注册路由（修正为 /api/v1/ 前缀）
    path("api/v1/", include("login.urls")),
    # 用户个人资料路由 11/2 yyf
    path("api/v1/", include("profile.urls")),
    # 社区论坛路由 11/3 yyf
    path("api/v1/", include("post.urls")),
    # 食堂消费数据路由
    path("api/v1/canteen/", include("canteen.urls")),
]

# 在开发环境中提供media文件服务 11/2 yyf
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
