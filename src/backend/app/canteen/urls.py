"""
食堂消费数据URL配置
"""
from django.urls import path
from . import views

urlpatterns = [
    path('consumption/', views.get_consumption, name='get_consumption'),
    path('bind/', views.bind_idserial, name='bind_idserial'),
    path('refresh/', views.refresh_consumption, name='refresh_consumption'),
    path('unbind/', views.unbind, name='unbind_consumption'),
    
    # 自动登录相关API
    path('auto-login/start/', views.start_auto_login, name='start_auto_login'),
    path('auto-login/submit-code/', views.submit_verification, name='submit_verification'),
    path('auto-login/status/', views.check_auto_login_status, name='check_auto_login_status'),
    path('fetch-with-cookie/', views.fetch_consumption_with_cookie, name='fetch_with_cookie'),
]

