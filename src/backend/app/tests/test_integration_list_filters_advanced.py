import pytest

from list.models import Canteen, Dish, Tag, Floor, Window


@pytest.mark.django_db
def test_tag_ids_csv_and_array(api_client):
    canteen = Canteen.objects.create(name="食堂A", address="地址A")
    floor = Floor.objects.create(name="F1", canteen=canteen, order=1)
    window = Window.objects.create(name="W1", floor=floor, order=1)

    d1 = Dish.objects.create(name="辣A", canteen=canteen, window=window, price=10.0, view_count=1, rating=4.0)
    d2 = Dish.objects.create(name="素B", canteen=canteen, window=window, price=8.0, view_count=2, rating=3.0)
    t1 = Tag.objects.create(name="辣")
    t2 = Tag.objects.create(name="素")
    d1.tags.add(t1)
    d2.tags.add(t2)

    # CSV 形式
    url = f"/api/v1/dishes/?tag_ids={t1.id},{t2.id}"
    r = api_client.get(url)
    assert r.status_code == 200
    names = [it['name'] for it in r.data['data']]
    assert "辣A" in names and "素B" in names

    # array 形式
    url2 = f"/api/v1/dishes/?tag_ids[]={t1.id}"
    r2 = api_client.get(url2)
    assert r2.status_code == 200
    names2 = [it['name'] for it in r2.data['data']]
    assert "辣A" in names2 and "素B" not in names2


@pytest.mark.django_db
def test_price_and_rating_filter(api_client):
    canteen = Canteen.objects.create(name="食堂B", address="地址B")
    floor = Floor.objects.create(name="F2", canteen=canteen, order=1)
    window = Window.objects.create(name="W2", floor=floor, order=1)

    Dish.objects.create(name="X", canteen=canteen, window=window, price=5.0, view_count=1, rating=2.0)
    Dish.objects.create(name="Y", canteen=canteen, window=window, price=15.0, view_count=2, rating=4.5)

    url = '/api/v1/dishes/?min_price=10&min_rating=4'
    resp = api_client.get(url)
    assert resp.status_code == 200
    names = [it['name'] for it in resp.data['data']]
    assert 'Y' in names and 'X' not in names
