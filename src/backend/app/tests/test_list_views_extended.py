import pytest
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from rest_framework.test import APIClient

from list.models import Canteen, Dish, Rating


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]


@pytest.mark.django_db
class TestListViewsExtended:
    def setup_method(self):
        self.client = APIClient()
        self.canteen = Canteen.objects.create(name="Test Canteen")
        self.dish1 = Dish.objects.create(name="Dish A", canteen=self.canteen, price=10.0)
        self.dish2 = Dish.objects.create(name="Dish B", canteen=self.canteen, price=20.0)
        self.dish3 = Dish.objects.create(name="Dish C", canteen=self.canteen, price=15.0)

    def _items(self, payload):
        # list app uses {code, message, data} wrapper
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload

    def test_dish_list_basic(self):
        url = reverse('list:dish-list')
        resp = self.client.get(url)
        assert resp.status_code == 200

        items = self._items(resp.json())
        assert isinstance(items, list)
        names = {d.get('name') for d in items if isinstance(d, dict)}
        assert {'Dish A', 'Dish B', 'Dish C'}.issubset(names)

    def test_dish_detail_not_found(self):
        url = reverse('list:dish-detail', args=[99999])
        resp = self.client.get(url)
        assert resp.status_code == 404

    def test_canteen_list_basic(self):
        Canteen.objects.create(name="Another Canteen")
        url = reverse('list:canteen-list')
        resp = self.client.get(url)
        assert resp.status_code == 200

        items = self._items(resp.json())
        assert isinstance(items, list)
        names = {c.get('name') for c in items if isinstance(c, dict)}
        assert 'Test Canteen' in names
        assert 'Another Canteen' in names

    def test_review_list_anon_allowed(self):
        auth_user = AuthUser.objects.create(username='u1')
        Rating.objects.create(dish=self.dish1, user=auth_user, score=5)

        url = reverse('list:review-list', args=[self.dish1.id])
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_dish_list_invalid_tag_ids_are_ignored(self):
        """tag_ids 解析 int 失败应被 ignore（except 分支），仍返回 200。"""
        url = reverse('list:dish-list')
        resp = self.client.get(url, {'tag_ids': 'not-an-int'})
        assert resp.status_code == 200

    def test_canteen_detail_invalid_tag_ids_are_ignored(self):
        """canteen_detail 的 tag_ids 解析失败走 except 分支，仍返回 200。"""
        url = reverse('list:canteen-detail', args=[self.canteen.id])
        resp = self.client.get(url, {'tag_ids': 'x,y'})
        assert resp.status_code == 200
        payload = resp.json()
        assert payload.get('code') == 200

    def test_my_reviews_pagination_and_invalid_ordering(self):
        """my_reviews：非法 ordering 不生效，分页参数生效。"""
        from login.models import User as LoginUser
        from utils.jwt import encrypt_password, generate_jwt
        from list.models import Review

        username = 'mr_user'
        password = 'pw'
        auth_user = AuthUser.objects.create_user(username=username, password=password)
        LoginUser.objects.create(
            id=auth_user.id,
            username=username,
            password=encrypt_password(password),
            nickname='MR',
        )
        token = generate_jwt({'user_id': auth_user.id, 'username': username})
        authed = APIClient()
        authed.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # 准备数据：API 查询 my_reviews -> view + ORM + serializer
        rating_obj = Rating.objects.create(dish=self.dish1, user=auth_user, score=4)
        for i in range(3):
            Review.objects.create(
                dish=self.dish1,
                user=auth_user,
                content=f'c{i}',
                rating=rating_obj,
                published_score=rating_obj.score,
                status='approved',
            )

        url = reverse('list:my-reviews')
        resp = authed.get(url, {'page': 1, 'page_size': 2, 'ordering': 'invalid-field'})
        assert resp.status_code == 200
        data = resp.json().get('data', {})
        assert data.get('page') == 1
        assert data.get('page_size') == 2
        assert len(data.get('reviews', [])) <= 2
