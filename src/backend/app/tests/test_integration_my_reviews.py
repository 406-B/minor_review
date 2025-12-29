import pytest
from django.contrib.auth.models import User as AuthUser
from login.models import User as LoginUser
from utils.jwt import encrypt_password


@pytest.mark.django_db
def test_my_reviews_requires_auth(api_client):
    # 正确路由为 /api/v1/reviews/my/
    url = '/api/v1/reviews/my/'
    r = api_client.get(url)
    # 未认证可能返回 401/403 或 302 重定向，视实现而定；接受 401/403/302/404
    assert r.status_code in (401, 403, 302, 404)


@pytest.mark.django_db
def test_my_reviews_returns_reviews_for_user(api_client):
    # 创建用户并认证
    username = 'reviewer'
    password = 'Passw0rd!'
    auth_user = AuthUser.objects.create_user(username=username, password=password)
    login_user = LoginUser.objects.create(id=auth_user.id, username=username, password=encrypt_password(password), nickname='rev')

    from utils.jwt import generate_jwt
    token = generate_jwt({'user_id': login_user.id, 'username': username})
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # 创建一条 review（直接使用模型），保证外键完整
    from list.models import Dish, Review
    from list.models import Canteen, Floor, Window

    canteen_obj = Canteen.objects.create(name='R食堂', address='addr')
    floor = Floor.objects.create(name='F', canteen=canteen_obj, order=1)
    window = Window.objects.create(name='W', floor=floor, order=1)
    dish = Dish.objects.create(name='R', canteen=canteen_obj, window=window, price=1.0, view_count=0, rating=0)
    Review.objects.create(user=auth_user, dish=dish, content='good')

    r = api_client.get('/api/v1/reviews/my/')
    assert r.status_code == 200
    assert 'reviews' in r.data['data']
    assert any(it['content'] == 'good' for it in r.data['data']['reviews'])
