import pytest

from login.models import User as LoginUser


@pytest.mark.django_db
def test_register_and_login_flow(api_client):
    """实现：使用 `/api/v1/register` 与 `/api/v1/login` 进行注册与登录（部分实现可能返回 token/ access）。"""
    # register_params_check 要求：username = letters+digits, length 5-12；password 含特定符号
    payload = {
        'username': 'User01',
        'password': 'Passw0rd-',
        'confirm_password': 'Passw0rd-',
        'nickname': 'Nick'
    }

    # 注册
    r = api_client.post('/api/v1/register', payload, format='json')
    assert r.status_code in (200, 201)

    # 登录（LoginView 使用 PATCH 方法）
    login = api_client.patch('/api/v1/login', {'username': payload['username'], 'password': payload['password']}, format='json')
    assert login.status_code in (200, 201)
    # 登录成功应返回 jwt 字段
    assert 'jwt' in getattr(login, 'data', {})
