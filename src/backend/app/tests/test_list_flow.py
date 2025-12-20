import pytest
from list.models import Canteen, Dish, Tag, Rating, Review, Floor, Window
from django.contrib.auth.models import User as AuthUser
from login.models import User as LoginUser
from utils.jwt import encrypt_password

@pytest.mark.django_db
class TestListFlow:
    """
    集成测试：食堂/菜品/评价流程
    """

    @pytest.fixture
    def user_client(self, api_client):
        """创建一个普通用户并返回已认证的客户端"""
        from utils.jwt import generate_jwt
        
        username = 'listuser'
        password = 'password123'
        
        # Auth User
        auth_user = AuthUser.objects.create_user(username=username, password=password)
        
        # Login User
        login_user = LoginUser.objects.create(
            id=auth_user.id,
            username=username,
            password=encrypt_password(password),
            nickname='List User'
        )
        
        # 生成 Token
        payload = {'user_id': login_user.id, 'username': login_user.username}
        token = generate_jwt(payload)
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return api_client, auth_user

    @pytest.fixture
    def setup_canteen_data(self):
        """准备食堂和菜品数据"""
        canteen = Canteen.objects.create(name="第一食堂", address="东区")
        floor = Floor.objects.create(name="一楼", canteen=canteen, order=1)
        window = Window.objects.create(name="川菜窗口", floor=floor, order=1)
        
        dish1 = Dish.objects.create(
            name="宫保鸡丁",
            canteen=canteen,
            window=window,
            price=15.0,
            description="经典川菜",
            view_count=100,
            rating=4.5
        )
        
        dish2 = Dish.objects.create(
            name="麻婆豆腐",
            canteen=canteen,
            window=window,
            price=12.0,
            description="麻辣鲜香",
            view_count=50,
            rating=4.0
        )
        
        tag = Tag.objects.create(name="辣")
        dish1.tags.add(tag)
        dish2.tags.add(tag)
        
        return canteen, dish1, dish2, tag

    def test_canteen_list_and_detail(self, api_client, setup_canteen_data):
        """测试获取食堂列表和详情"""
        canteen, _, _, _ = setup_canteen_data
        
        # 1. 列表
        url = '/api/v1/canteens/'
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['data']) >= 1
        assert response.data['data'][0]['name'] == canteen.name
        
        # 2. 详情
        url = f'/api/v1/canteens/{canteen.id}/'
        response = api_client.get(url)
        assert response.status_code == 200
        # 修正：详情接口返回结构为 {'canteen': {...}, 'dishes': [...]}
        assert response.data['data']['canteen']['name'] == canteen.name
        
        # 3. 楼层
        url = f'/api/v1/canteens/{canteen.id}/floors/'
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['data']) >= 1
        assert response.data['data'][0]['name'] == "一楼"

    def test_dish_list_and_detail(self, api_client, setup_canteen_data):
        """测试获取菜品列表和详情"""
        _, dish1, _, _ = setup_canteen_data
        
        # 1. 列表
        url = '/api/v1/dishes/'
        response = api_client.get(url)
        assert response.status_code == 200
        # 修正：列表接口直接返回列表
        assert len(response.data['data']) >= 2
        
        # 2. 详情
        url = f'/api/v1/dishes/{dish1.id}/'
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['data']['name'] == dish1.name
        
        # 3. 热门菜品
        url = '/api/v1/dishes/hot/'
        response = api_client.get(url)
        assert response.status_code == 200
        # 宫保鸡丁 view_count=100 应该在前面
        assert response.data['data'][0]['name'] == dish1.name

    def test_rate_dish(self, user_client, setup_canteen_data):
        """测试给菜品评分"""
        client, _ = user_client
        _, dish1, _, _ = setup_canteen_data
        
        url = f'/api/v1/dishes/{dish1.id}/rate/'
        # 修正：接口接收 'rating' 字段
        data = {'rating': 5}
        
        response = client.post(url, data, format='json')
        assert response.status_code == 200
        
        # 验证评分已保存
        assert Rating.objects.filter(dish=dish1, score=5).exists()
        
        # 验证重复评分（应该更新）
        data = {'rating': 4}
        response = client.post(url, data, format='json')
        assert response.status_code == 200
        assert Rating.objects.filter(dish=dish1, score=4).exists()
        assert not Rating.objects.filter(dish=dish1, score=5).exists()

    def test_add_tag_to_dish(self, user_client, setup_canteen_data):
        """测试给菜品添加标签"""
        client, _ = user_client
        _, dish1, _, _ = setup_canteen_data
        
        url = f'/api/v1/dishes/{dish1.id}/tags/'
        data = {'tag_name': '超好吃'}
        
        response = client.post(url, data, format='json')
        assert response.status_code == 200
        
        # 验证标签进入待审核列表（假设默认需要审核，或者直接添加，视具体实现而定）
        # 根据之前的 audit 测试，似乎是进入 pending_tags
        dish1.refresh_from_db()
        # 检查是否在 pending_tags 或 tags 中
        tag = Tag.objects.get(name='超好吃')
        in_pending = tag in dish1.pending_tags.all()
        in_tags = tag in dish1.tags.all()
        assert in_pending or in_tags

    def test_create_and_list_reviews(self, user_client, setup_canteen_data):
        """测试发表评论和获取评论列表"""
        client, auth_user = user_client
        _, dish1, _, _ = setup_canteen_data
        
        # 0. 先评分（接口要求必须先评分）
        Rating.objects.create(dish=dish1, user=auth_user, score=4.5)

        # 1. 发表评论
        url = f'/api/v1/dishes/{dish1.id}/reviews/create/'
        data = {
            'content': '味道不错，分量足',
        }
        
        response = client.post(url, data, format='json')
        assert response.status_code == 201
        
        # 2. 获取评论列表
        url = f'/api/v1/dishes/{dish1.id}/reviews/'
        response = client.get(url)
        assert response.status_code == 200
        reviews = response.data['data']['reviews']
        assert len(reviews) >= 1
        assert reviews[0]['content'] == '味道不错，分量足'
