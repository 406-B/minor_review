import pytest
import json

from canteen import services


@pytest.mark.django_db
def test_fetch_canteen_data_parsing(monkeypatch):
    """集成测试：模拟外部加密数据，验证解析与聚合逻辑"""
    # 构造解密后返回的数据格式
    payload = {
        "resultData": {
            "rows": [
                {"mername": "第一食堂园_窗口", "txamt": 1200},
                {"mername": "第一食堂园-窗口B", "txamt": 800},
                {"mername": "其他商家园", "txamt": 500}
            ]
        }
    }

    class DummyResponse:
        status_code = 200
        text = json.dumps({"data": "encrypted_placeholder"})

    def fake_post(*args, **kwargs):
        return DummyResponse()

    # 模拟 decrypt_aes_ecb 返回 JSON 字符串
    monkeypatch.setattr(services, 'requests', type('R', (), {'post': staticmethod(fake_post)}))
    monkeypatch.setattr(services, 'decrypt_aes_ecb', lambda s: json.dumps(payload))

    res = services.fetch_canteen_data('20210001', 'cookie_val')
    assert res['success']
    data = res['data']
    # total_amount: (1200+800+500)/100 = 25.0
    assert abs(data['total_amount'] - 25.0) < 0.01
    assert data['canteen_count'] >= 1
    # 服务端保留了包含“园”后缀的商家名称
    assert '第一食堂园' in data['canteens']
