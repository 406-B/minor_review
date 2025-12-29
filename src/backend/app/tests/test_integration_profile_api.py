import pytest

from login.models import User as LoginUser


@pytest.mark.django_db
def test_profile_retrieve_and_update(api_client, django_user_model):
    """实现：通过 `/api/v1/profile` 与 `/api/v1/profile/update` 验证获取与更新个人资料接口。"""
    user = django_user_model.objects.create_user(username='prof_tpl', password='pwd')
    # 确保在 login.User 表中也有对应记录（profile serializer 可能回退到 login.User）
    LoginUser.objects.create(id=user.id, username=user.username, password='pwd', nickname='Old')

    # 登录生成 JWT（使用 utils.jwt.generate_jwt）
    from utils.jwt import generate_jwt
    token = generate_jwt({'user_id': user.id, 'username': user.username})
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    r = api_client.get('/api/v1/profile')
    assert r.status_code == 200

    update = api_client.patch('/api/v1/profile/update', {'nickname': 'NewNick'}, format='json')
    assert update.status_code in (200, 201, 204)
    # 确保昵称已更新（数据库侧）
    assert LoginUser.objects.filter(username=user.username, nickname='NewNick').exists()
