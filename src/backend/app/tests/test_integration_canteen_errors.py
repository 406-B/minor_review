import pytest

from canteen import services


def test_fetch_canteen_data_http_failure(monkeypatch):
    class Dummy:
        status_code = 500
        text = ''

    def fake_post(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr(services, 'requests', type('R', (), {'post': staticmethod(fake_post)}))
    res = services.fetch_canteen_data('id', 'cookie')
    assert not res['success']
    assert 'HTTP' in (res.get('error') or '')


def test_fetch_canteen_data_bad_decrypt(monkeypatch):
    class Dummy:
        status_code = 200
        text = '{"data":"enc"}'

    def fake_post(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr(services, 'requests', type('R', (), {'post': staticmethod(fake_post)}))
    monkeypatch.setattr(services, 'decrypt_aes_ecb', lambda s: 'not-json')

    res = services.fetch_canteen_data('id', 'cookie')
    assert not res['success']
    assert 'JSON' in (res.get('error') or '') or '解密' in (res.get('error') or '')
