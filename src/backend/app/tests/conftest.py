import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from list.models import Canteen, Dish, Tag

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    # 创建 Django 内置 User (auth.User)
    # 因为 settings.AUTH_USER_MODEL 默认是 'auth.User'
    # 而 list 应用的模型外键指向 settings.AUTH_USER_MODEL
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='testuser', password='password123')
    return user

@pytest.fixture
def auth_client(api_client, test_user):
    # 使用自定义 JWT 生成逻辑
    from utils.jwt import generate_jwt, encrypt_password
    
    # 生成 token
    # 注意：utils.jwt.verify_jwt 会用 user_id 去 login.models.User 查询
    # 所以我们需要同时创建一个 login.models.User 以便 JWT 认证通过
    from login.models import User as LoginUser
    if not LoginUser.objects.filter(username=test_user.username).exists():
        LoginUser.objects.create(
            id=test_user.id, # 尝试同步 ID，或者让 JWT 使用 username
            username=test_user.username,
            password=encrypt_password('password123'), # 使用加密密码，以便测试修改密码等功能
            nickname='Test User'
        )
    
    # payload 使用 user_id，对应 login.models.User 的 ID
    # 假设两个表的 ID 可能不一致，我们需要确保 JWT 指向 login.User
    login_user = LoginUser.objects.get(username=test_user.username)
    
    payload = {'user_id': login_user.id, 'username': login_user.username}
    token = generate_jwt(payload)
    
    # 设置 Authorization 头
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

@pytest.fixture
def sample_canteen(db):
    return Canteen.objects.create(name="测试食堂")

@pytest.fixture
def sample_tag(db):
    return Tag.objects.create(name="辣")

@pytest.fixture
def sample_dish(db, sample_canteen, sample_tag):
    dish = Dish.objects.create(
        name="麻婆豆腐",
        canteen=sample_canteen,
        price=12.5,
        description="又麻又辣",
    )
    dish.tags.add(sample_tag)
    return dish
