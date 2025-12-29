import pytest
import json

from canteen import services


@pytest.mark.django_db
def test_canteen_service_handles_empty_response(monkeypatch):
    """集成测试模板：外部服务返回空或错误，确保服务返回可控的错误结构。"""
    class DummyResponse:
        status_code = 500
        text = ''

    def fake_post(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr(services, 'requests', type('R', (), {'post': staticmethod(fake_post)}))
    # 如果 decrypt 返回空或抛异常，服务应捕获并返回 success=False
    monkeypatch.setattr(services, 'decrypt_aes_ecb', lambda s: json.dumps({}))

    res = services.fetch_canteen_data('20210001', 'cookie_tpl')
    assert isinstance(res, dict)
    # 期望服务在异常响应下返回 success=False 或等价错误结构
    assert res.get('success') in (False, None) or 'error' in res
