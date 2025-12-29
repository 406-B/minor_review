import pytest


pytestmark = [pytest.mark.integration]


@pytest.mark.django_db
class TestAppHealthIntegration:
    def test_health_check_healthy_when_db_ok(self, client):
        resp = client.get('/api/v1/health/')
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('status') == 'healthy'
        assert data.get('database') == 'connected'

    def test_health_check_unhealthy_when_db_cursor_raises(self, client, monkeypatch):
        # 通过让 connection.cursor() 抛异常，稳定命中 health_check 的 except 分支
        import app.health as health_mod

        def _raise_cursor():
            raise RuntimeError('db down')

        monkeypatch.setattr(health_mod.connection, 'cursor', _raise_cursor)

        resp = client.get('/api/v1/health/')
        assert resp.status_code == 503
        data = resp.json()
        assert data.get('status') == 'unhealthy'
        assert data.get('database') == 'disconnected'
        assert 'db down' in (data.get('error') or '')
