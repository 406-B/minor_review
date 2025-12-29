import pytest

from list.models import Canteen, Dish, Floor, Window, Review


@pytest.mark.django_db
def test_create_and_list_reviews(api_client, django_user_model):
    """实现：创建用户、菜品，通过 `/api/v1/dishes/<id>/reviews/create/` 创建评论并通过 `/api/v1/dishes/<id>/reviews/` 列出。"""
    # 创建用户并认证（使用 Django AuthUser 映射）
    user = django_user_model.objects.create_user(username='rev_tpl', password='pass123')
    api_client.force_authenticate(user=user)

    # 创建菜品依赖对象
    canteen = Canteen.objects.create(name='ReviewCanteen', address='addr')
    floor = Floor.objects.create(name='F', canteen=canteen, order=1)
    window = Window.objects.create(name='W', floor=floor, order=1)
    dish = Dish.objects.create(name='R', canteen=canteen, window=window, price=1.0, view_count=0, rating=0)

    # 在创建评论前先创建 Rating（create_review 要求已评分）
    from list.models import Rating
    rating = Rating.objects.create(user=user, dish=dish, score=4.0)

    # monkeypatch 审核函数以通过审核
    from utils import audit as audit_mod
    import types
    def fake_audit(content, content_type, title):
        return True, ''
    # 将 audit_content 替换
    try:
        audit_mod.audit_content
        monkeypatch = None
    except Exception:
        pass

    # Create payload for review
    payload = {'content': '很好吃，很推荐，值得一试', 'images': [], 'published_score': 4.0}
    create_url = f'/api/v1/dishes/{dish.id}/reviews/create/'
    # patch audit_content via import path used in view (utils.audit.audit_content)
    from utils.audit import audit_content as _orig_audit
    import utils.audit as _audit_mod
    _audit_mod.audit_content = lambda **kwargs: (True, '') if False else (True, '')

    r = api_client.post(create_url, payload, format='json')
    assert r.status_code in (200, 201)

    # 确认数据库中已有该评论记录（方便调试，如果没有则在断言信息中包含 POST 返回体）
    from list.models import Review as _Review
    exists = _Review.objects.filter(dish=dish, user=user).exists()
    assert exists, f"Review not saved, POST response: {getattr(r, 'data', getattr(r, 'content', r.status_code))}"

    # 列出该菜品的评论
    list_url = f'/api/v1/dishes/{dish.id}/reviews/'
    rr = api_client.get(list_url)
    assert rr.status_code == 200
    assert 'reviews' in rr.data['data'] or isinstance(rr.data['data'], list)
    # 确保新创建的评论内容可见
    found = False
    reviews = rr.data['data']['reviews'] if isinstance(rr.data['data'], dict) and 'reviews' in rr.data['data'] else rr.data['data']
    for it in reviews:
        if it.get('content') == '很好吃，值得一试' or it.get('content') == '很好吃，很推荐，值得一试' or it.get('content') == '很好吃':
            found = True
            break
    if not found:
        # 收集调试信息
        db_reviews = list(Review.objects.filter(dish=dish, user=user).values('id', 'content', 'status'))
        debug = {
            'post_status': r.status_code,
            'post_data': getattr(r, 'data', getattr(r, 'content', None)),
            'get_status': rr.status_code,
            'get_data': getattr(rr, 'data', getattr(rr, 'content', None)),
            'db_reviews': db_reviews,
        }
        assert False, f"Review not present in GET result: {debug}"
    assert found
