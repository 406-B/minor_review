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
]
