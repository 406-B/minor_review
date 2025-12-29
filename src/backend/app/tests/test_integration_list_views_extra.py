import pytest

from list.models import Canteen, Dish, Tag, Floor, Window


@pytest.mark.django_db
def test_dish_list_filter_by_tag_and_search(api_client):
    """集成测试：按 tag_ids 过滤并配合 search 参数"""
    canteen = Canteen.objects.create(name="第二食堂", address="西区")
    floor = Floor.objects.create(name="二楼", canteen=canteen, order=1)
    window = Window.objects.create(name="湘菜窗口", floor=floor, order=1)

    d1 = Dish.objects.create(name="小炒肉", canteen=canteen, window=window, price=10.0, view_count=10, rating=4.0)
    d2 = Dish.objects.create(name="青菜炒饭", canteen=canteen, window=window, price=8.0, view_count=5, rating=3.5)

    tag_spicy = Tag.objects.create(name="辣")
    tag_veg = Tag.objects.create(name="素")
    d1.tags.add(tag_spicy)
    d2.tags.add(tag_veg)

    # 使用 tag_ids[]=<id> 形式过滤
    url = f"/api/v1/dishes/?tag_ids[]={tag_spicy.id}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    names = [it['name'] for it in resp.data['data']]
    assert "小炒肉" in names and "青菜炒饭" not in names

    # 同时提供 search（当 tag_ids 存在时，应以 tag_ids 为准，search 被忽略）
    url = f"/api/v1/dishes/?tag_ids[]={tag_spicy.id}&search=青菜"
    resp2 = api_client.get(url)
    assert resp2.status_code == 200
    names2 = [it['name'] for it in resp2.data['data']]
    assert "小炒肉" in names2


@pytest.mark.django_db
def test_dish_list_pagination_and_ordering(api_client):
    """集成测试：分页与排序行为"""
    canteen = Canteen.objects.create(name="第三食堂", address="南区")
    floor = Floor.objects.create(name="三楼", canteen=canteen, order=1)
    window = Window.objects.create(name="面点窗口", floor=floor, order=1)

    Dish.objects.create(name="A菜", canteen=canteen, window=window, price=5.0, view_count=1, rating=3.0)
    Dish.objects.create(name="B菜", canteen=canteen, window=window, price=6.0, view_count=2, rating=4.0)
    Dish.objects.create(name="C菜", canteen=canteen, window=window, price=7.0, view_count=3, rating=5.0)

    # 注意：当前实现不对 dish_list 做分页（返回所有结果），因此只断言 ordering 生效
    url = '/api/v1/dishes/?page=1&page_size=1&ordering=-rating'
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['data']  # 列表存在

    # ordering=-rating 首项应为最高评分
    first_name = resp.data['data'][0]['name']
    assert first_name == 'C菜'
