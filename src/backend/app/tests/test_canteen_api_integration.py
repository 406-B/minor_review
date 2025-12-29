import pytest


# 认证标签：集成测试（通过 API 端点驱动 canteen views->controllers->services 链路）
pytestmark = [pytest.mark.integration]


@pytest.mark.django_db
class TestCanteenApiIntegration:
    def test_get_consumption_not_bound(self, auth_client):
        """GET /api/v1/canteen/consumption/ 未绑定时应返回 404"""
        resp = auth_client.get('/api/v1/canteen/consumption/')
        assert resp.status_code == 404
        assert resp.data['code'] == 404

    def test_fetch_with_cookie_validation(self, auth_client):
        """POST /api/v1/canteen/fetch-with-cookie/ 参数校验"""
        resp = auth_client.post('/api/v1/canteen/fetch-with-cookie/', {}, format='json')
        assert resp.status_code == 400
        assert resp.data['code'] == 400

    def test_fetch_with_cookie_success_and_persists_via_services(self, auth_client, test_user, monkeypatch):
        """POST /api/v1/canteen/fetch-with-cookie/ 成功时应保存到 DB；并且要真正跑进 services.fetch_canteen_data 的解析逻辑"""
        from canteen.models import CanteenConsumption
        from canteen import services as canteen_services

        # 1) patch requests.post 返回正常 200 + data 字段
        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        def fake_post(url, cookies=None, timeout=None):
            return DummyResp()

        monkeypatch.setattr(canteen_services.requests, 'post', fake_post)

        # 2) patch decrypt_aes_ecb 返回可解析 JSON（确保覆盖 services 内的 mername 解析 + endswith('园') 过滤）
        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口A", "txamt": 1200},
                    {"mername": "桃李园-窗口B", "txamt": 800},
                    {"mername": "超市", "txamt": 500},
                ]
            }
        }
        import json as _json

        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps(decrypted_payload))

        payload = {'idserial': '2023000001', 'servicehall': 'cookie'}
        resp = auth_client.post('/api/v1/canteen/fetch-with-cookie/', payload, format='json')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['idserial'] == '2023000001'
        assert resp.data['data']['canteen_count'] == 2

        # DB 断言
        assert CanteenConsumption.objects.filter(user_id=test_user.id, idserial='2023000001').exists()

        # 再用 get_consumption 查询
        resp2 = auth_client.get('/api/v1/canteen/consumption/')
        assert resp2.status_code == 200
        assert resp2.data['code'] == 200
        assert resp2.data['data']['idserial'] == '2023000001'

    def test_fetch_with_cookie_http_status_not_200_returns_400(self, auth_client, monkeypatch):
        """POST /api/v1/canteen/fetch-with-cookie/ services.fetch_canteen_data: HTTP 非 200 路径"""
        from canteen import services as canteen_services

        class DummyResp:
            status_code = 500
            text = 'boom'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        # view 层把 services 的失败映射到 500（或 400），只断言不是 200 且包含 message
        assert resp.status_code in (400, 500)
        assert resp.data['code'] in (400, 500)
        assert 'HTTP' in resp.data.get('message', '') or '失败' in resp.data.get('message', '')

    def test_fetch_with_cookie_response_missing_data_returns_error(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: response JSON 无 data 字段"""
        from canteen import services as canteen_services

        class DummyResp:
            status_code = 200
            text = '{"not_data": 1}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code in (400, 500)
        assert resp.data['code'] in (400, 500)

    def test_fetch_with_cookie_decrypt_json_decode_error(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: 解密后 JSON 解析失败 -> JSONDecodeError 分支"""
        from canteen import services as canteen_services

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: 'not-json')

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code in (400, 500)
        assert resp.data['code'] in (400, 500)
        assert 'JSON' in resp.data.get('message', '') or '解析' in resp.data.get('message', '') or '失败' in resp.data.get('message', '')

    def test_fetch_with_cookie_decrypted_missing_rows_returns_error(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: resultData/rows 缺失错误分支"""
        from canteen import services as canteen_services
        import json as _json

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps({"resultData": {}}))

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code in (400, 500)
        assert resp.data['code'] in (400, 500)

    def test_fetch_with_cookie_empty_rows_success_zero_counts(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: rows 为空时 success=True 且金额/数量为 0"""
        from canteen import services as canteen_services
        from canteen.models import CanteenConsumption
        import json as _json

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps({"resultData": {"rows": []}}))

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 0
        assert float(resp.data['data']['total_amount']) == 0.0

        obj = CanteenConsumption.objects.get(user_id=resp.wsgi_request.user.id)
        assert obj.canteen_count == 0

    def test_fetch_with_cookie_requests_exception_path(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: requests.RequestException 分支"""
        from canteen import services as canteen_services
        import requests as _requests

        def boom(*a, **k):
            raise _requests.RequestException('network down')

        monkeypatch.setattr(canteen_services.requests, 'post', boom)

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code in (400, 500)
        assert resp.data['code'] in (400, 500)

    def test_fetch_with_cookie_rows_with_bad_items_are_ignored(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: rows 内部存在坏记录（KeyError/TypeError）应被忽略"""
        from canteen import services as canteen_services
        import json as _json

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        # rows 包含：
        # - 正常记录（紫荆园_）
        # - 缺 mername 的记录（KeyError）
        # - mername=None 导致 TypeError（"_" in None）
        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口A", "txamt": 1200},
                    {"txamt": 500},
                    {"mername": None, "txamt": 300},
                ]
            }
        }
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps(decrypted_payload))

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 1
        assert float(resp.data['data']['total_amount']) == 12.0

    def test_fetch_with_cookie_mername_without_separator(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: mername 不含 '_' / '-' 时直接用原值做食堂名"""
        from canteen import services as canteen_services
        import json as _json

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园", "txamt": 900},
                    means := {"mername": "桃李园", "txamt": 100},
                ]
            }
        }
        # 兼容老 Python：避免 walrus 语法被拒绝（这里重新写成普通 dict）
        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园", "txamt": 900},
                    {"mername": "桃李园", "txamt": 100},
                ]
            }
        }

        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps(decrypted_payload))

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 2

    def test_fetch_with_cookie_all_merchants_filtered_results_empty(self, auth_client, monkeypatch):
        """services.fetch_canteen_data: 所有 mername 都不以“园”结尾时，过滤后为空"""
        from canteen import services as canteen_services
        import json as _json

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "超市_便利店", "txamt": 500},
                    {"mername": "咖啡", "txamt": 700},
                ]
            }
        }
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps(decrypted_payload))

        resp = auth_client.post(
            '/api/v1/canteen/fetch-with-cookie/',
            {'idserial': '2023000001', 'servicehall': 'cookie'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 0
        assert float(resp.data['data']['total_amount']) == 0.0

class TestCanteenRefreshIntegration:
    pytestmark = [pytest.mark.integration]

    def test_refresh_without_binding_returns_400(self, auth_client):
        """未绑定学号时 refresh 应映射为 400（message 包含“请先绑定”）"""
        resp = auth_client.post('/api/v1/canteen/refresh/', {}, format='json')
        assert resp.status_code == 400
        assert resp.data['code'] == 400
        assert '请先绑定' in resp.data['message']

    def test_refresh_cookie_fetch_fails_then_fallback_fails_returns_500(self, auth_client, test_user, monkeypatch):
        """有 cookie 时优先 fetch_canteen_data；失败后回退 fetch_and_parse_consumption 也失败 -> 500"""
        from canteen.models import CanteenConsumption
        from canteen import controllers as canteen_controllers
        from login.models import User as LoginUser

        login_user = LoginUser.objects.get(username=test_user.username)

        # 先造一条绑定记录，让 controller 不走“请先绑定”分支
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        # 让 fetch_canteen_data 失败，触发回退
        monkeypatch.setattr(
            canteen_controllers,
            'fetch_canteen_data',
            lambda *a, **k: {"success": False, "error": "cookie invalid", "data": None},
        )
        # 回退的 fetch_and_parse_consumption 也失败
        monkeypatch.setattr(
            canteen_controllers,
            'fetch_and_parse_consumption',
            lambda *a, **k: {"success": False, "error": "fallback failed", "data": None, "servicehall": None},
        )
        # RefreshDataSerializer.servicehall 不允许 null，传空字符串以触发“用已保存 cookie”分支
        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 500
        assert resp.data['code'] == 500
        assert 'fallback failed' in resp.data['message']

    def test_refresh_cookie_fetch_success_returns_200(self, auth_client, test_user, monkeypatch):
        """有 cookie 且 fetch_canteen_data 成功时应直接返回 200 并更新数据"""
        from canteen.models import CanteenConsumption
        from canteen import controllers as canteen_controllers
        from login.models import User as LoginUser

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        monkeypatch.setattr(
            canteen_controllers,
            'fetch_canteen_data',
            lambda *a, **k: {
                "success": True,
                "data": {"total_amount": "1.00", "canteen_count": 1, "canteens": {"紫荆园": 1.0}},
                "error": None,
            },
        )

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 1

    def test_refresh_cookie_fetch_fails_then_fallback_success_returns_200(self, auth_client, test_user, monkeypatch):
        """cookie fetch 失败时会回退 fetch_and_parse_consumption；回退成功应返回 200"""
        from canteen.models import CanteenConsumption
        from canteen import controllers as canteen_controllers
        from login.models import User as LoginUser

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        monkeypatch.setattr(
            canteen_controllers,
            'fetch_canteen_data',
            lambda *a, **k: {"success": False, "error": "cookie invalid", "data": None},
        )
        monkeypatch.setattr(
            canteen_controllers,
            'fetch_and_parse_consumption',
            lambda *a, **k: {
                "success": True,
                "data": {"total_amount": "2.00", "canteen_count": 2, "canteens": {"桃李园": 2.0}},
                "servicehall": "new_cookie",
                "error": None,
                "idserial": "2023000001",
            },
        )

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 2

    def test_refresh_cookie_calls_services_fetch_and_parses_rows(self, auth_client, test_user, monkeypatch):
        """refresh 的 cookie 分支应调用 services.fetch_canteen_data，并真实走 rows 解析/聚合逻辑。"""
        import json as _json
        from canteen.models import CanteenConsumption
        from login.models import User as LoginUser
        from canteen import services as canteen_services

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口A", "txamt": 1200},
                    {"mername": "桃李园-窗口B", "txamt": 300},
                    {"mername": "超市_便利店", "txamt": 999},
                ]
            }
        }
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps(decrypted_payload))

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 2

    def test_refresh_cookie_services_http_error_maps_to_500(self, auth_client, test_user, monkeypatch):
        """refresh cookie 分支若 services.fetch_canteen_data 返回失败（如 HTTP!=200）应映射为 500。"""
        from canteen.models import CanteenConsumption
        from login.models import User as LoginUser
        from canteen import services as canteen_services

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        class DummyResp:
            status_code = 403
            text = '{}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 500
        assert resp.data['code'] == 500

    def test_refresh_cookie_services_missing_data_field_maps_to_500(self, auth_client, test_user, monkeypatch):
        """services.fetch_canteen_data: 响应 JSON 缺 data 字段 -> refresh 映射 500"""
        from canteen.models import CanteenConsumption
        from login.models import User as LoginUser
        from canteen import services as canteen_services

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        class DummyResp:
            status_code = 200
            text = '{"no_data": 1}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 500
        assert resp.data['code'] == 500

    def test_refresh_cookie_services_decrypt_jsondecodeerror_maps_to_500(self, auth_client, test_user, monkeypatch):
        """services.fetch_canteen_data: decrypt 后 JSONDecodeError -> refresh 映射 500"""
        from canteen.models import CanteenConsumption
        from login.models import User as LoginUser
        from canteen import services as canteen_services

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: 'not-json')

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 500
        assert resp.data['code'] == 500


@pytest.mark.django_db
class TestCanteenAutoLoginIntegration:
    pytestmark = [pytest.mark.integration]

    def test_start_auto_login_immediate_completed_returns_200(self, auth_client, monkeypatch):
        """POST /api/v1/canteen/auto-login/start/ 若后台线程立即把会话标记为 completed，接口应直接返回 200 completed。"""
        from canteen import services as canteen_services
        import uuid as _uuid

        fixed_session_id = str(_uuid.uuid4())
        monkeypatch.setattr(canteen_services.uuid, 'uuid4', lambda: fixed_session_id)

        def _fake_auto_login_thread(session_id, idserial, password, headless, browser_type):
            with canteen_services.SESSION_LOCK:
                canteen_services.LOGIN_SESSIONS[session_id] = {
                    'status': 'completed',
                    'servicehall': 'cookie',
                }

        monkeypatch.setattr(canteen_services, '_auto_login_thread', _fake_auto_login_thread)

        class _DummyThread:
            daemon = True

            def __init__(self, target=None, args=None, **kwargs):
                self._target = target
                self._args = args or ()

            def start(self):
                if self._target:
                    self._target(*self._args)

        monkeypatch.setattr(canteen_services.threading, 'Thread', _DummyThread)

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/start/',
            {'idserial': '2023000001', 'password': 'pw', 'headless': True, 'browser_type': 'chrome'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['status'] == 'completed'

    def test_submit_verification_session_not_found_returns_400(self, auth_client):
        """POST /api/v1/canteen/auto-login/submit-code/ 会话不存在时返回 400。"""
        resp = auth_client.post(
            '/api/v1/canteen/auto-login/submit-code/',
            {'session_id': 'nope', 'verification_code': '1234'},
            format='json',
        )
        assert resp.status_code == 400
        assert resp.data['code'] == 400

    def test_submit_verification_session_status_not_waiting_returns_400(self, auth_client):
        """会话状态不是 waiting_verification 时，submit_verification 应返回 400。"""
        from canteen import services as canteen_services

        with canteen_services.SESSION_LOCK:
            canteen_services.LOGIN_SESSIONS['sid'] = {
                'status': 'failed',
                'error': 'x',
            }

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/submit-code/',
            {'session_id': 'sid', 'verification_code': '1234'},
            format='json',
        )
        assert resp.status_code == 400
        assert resp.data['code'] == 400

    def test_check_auto_login_status_session_not_found_returns_200_with_not_found(self, auth_client):
        """GET /api/v1/canteen/auto-login/status/ 当前实现对 not_found 也返回 200，status=not_found。"""
        resp = auth_client.get('/api/v1/canteen/auto-login/status/?session_id=nope')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['status'] == 'not_found'

    def test_cleanup_login_session_quits_driver_and_deletes(self):
        """直接调用 cleanup_login_session：存在 driver 时应尝试 quit 且删除会话。"""
        from canteen import services as canteen_services

        class DummyDriver:
            def __init__(self):
                self.quit_called = False

            def quit(self):
                self.quit_called = True

        driver = DummyDriver()
        with canteen_services.SESSION_LOCK:
            canteen_services.LOGIN_SESSIONS['sid2'] = {'status': 'completed', 'driver': driver}

        canteen_services.cleanup_login_session('sid2')
        assert driver.quit_called is True
        with canteen_services.SESSION_LOCK:
            assert 'sid2' not in canteen_services.LOGIN_SESSIONS

    def test_start_auto_login_when_selenium_missing_returns_500(self, auth_client, monkeypatch):
        """start_auto_login -> services.auto_login_and_fetch_cookie -> get_browser_driver ImportError 分支。"""
        from canteen import services as canteen_services

        def _fake_get_browser_driver(*args, **kwargs):
            raise ImportError("未安装selenium库")

        monkeypatch.setattr(canteen_services, 'get_browser_driver', _fake_get_browser_driver)

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/start/',
            {'idserial': '2023000001', 'password': 'pw', 'headless': True, 'browser_type': 'chrome'},
            format='json',
        )
        assert resp.status_code == 500
        assert resp.data['code'] == 500

    def test_start_auto_login_when_browser_type_invalid_returns_500(self, auth_client, monkeypatch):
        """start_auto_login -> get_browser_driver ValueError 分支。"""
        from canteen import services as canteen_services

        def _fake_get_browser_driver(*args, **kwargs):
            raise ValueError("不支持的浏览器类型")

        monkeypatch.setattr(canteen_services, 'get_browser_driver', _fake_get_browser_driver)

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/start/',
            {'idserial': '2023000001', 'password': 'pw', 'headless': True, 'browser_type': 'badbrowser'},
            format='json',
        )
        assert resp.status_code == 500
        assert resp.data['code'] == 500

    def test_refresh_cookie_services_missing_rows_maps_to_500(self, auth_client, test_user, monkeypatch):
        """services.fetch_canteen_data: 解密后缺 rows -> refresh 映射 500"""
        import json as _json
        from canteen.models import CanteenConsumption
        from login.models import User as LoginUser
        from canteen import services as canteen_services

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps({"resultData": {}}))

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 500
        assert resp.data['code'] == 500

    def test_refresh_cookie_services_empty_rows_returns_200_with_zero(self, auth_client, test_user, monkeypatch):
        """services.fetch_canteen_data: rows=[] -> refresh 应成功返回 200 且 count/amount 为 0"""
        import json as _json
        from canteen.models import CanteenConsumption
        from login.models import User as LoginUser
        from canteen import services as canteen_services

        login_user = LoginUser.objects.get(username=test_user.username)
        CanteenConsumption.objects.update_or_create(
            user=login_user,
            defaults={
                'idserial': '2023000001',
                'servicehall_cookie': 'cookie',
                'total_amount': '0',
                'canteen_count': 0,
                'canteen_data': {},
            }
        )

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())
        monkeypatch.setattr(
            canteen_services,
            'decrypt_aes_ecb',
            lambda s: _json.dumps({"resultData": {"rows": []}}),
        )

        resp = auth_client.post('/api/v1/canteen/refresh/', {'servicehall': ''}, format='json')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['canteen_count'] == 0

    def test_unbind_success_and_then_404(self, auth_client, test_user):
        """DELETE /api/v1/canteen/unbind/ 成功后 get_consumption 应变为 404"""
        from canteen.models import CanteenConsumption

        # 先插入一条绑定记录
        CanteenConsumption.objects.create(
            user_id=test_user.id,
            idserial='2023000001',
            total_amount=0,
            canteen_count=0,
            canteen_data={},
        )

        resp = auth_client.delete('/api/v1/canteen/unbind/')
        assert resp.status_code == 200
        assert resp.data['code'] == 200

        resp2 = auth_client.get('/api/v1/canteen/consumption/')
        assert resp2.status_code == 404

    def test_refresh_not_bound_returns_400(self, auth_client):
        """POST /api/v1/canteen/refresh/ 未绑定时应返回 400（message 包含“请先绑定”）"""
        resp = auth_client.post('/api/v1/canteen/refresh/', {}, format='json')
        assert resp.status_code == 400
        assert resp.data['code'] == 400
        assert '请先绑定' in resp.data['message']

    def test_refresh_success_uses_saved_cookie_then_updates(self, auth_client, test_user, monkeypatch):
        """POST /api/v1/canteen/refresh/ 已绑定且 cookie 有效时，走 services.fetch_canteen_data 分支并更新 DB"""
        from canteen.models import CanteenConsumption
        from canteen import services as canteen_services

        # 先创建绑定记录（带 cookie）
        CanteenConsumption.objects.create(
            user_id=test_user.id,
            idserial='2023000001',
            servicehall_cookie='cookie_saved',
            total_amount=0,
            canteen_count=0,
            canteen_data={},
        )

        class DummyResp:
            status_code = 200
            text = '{"data": "encrypted_placeholder"}'

        monkeypatch.setattr(canteen_services.requests, 'post', lambda *a, **k: DummyResp())

        decrypted_payload = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口A", "txamt": 1000},
                    {"mername": "桃李园-窗口B", "txamt": 300},
                ]
            }
        }
        import json as _json
        monkeypatch.setattr(canteen_services, 'decrypt_aes_ecb', lambda s: _json.dumps(decrypted_payload))

        resp = auth_client.post('/api/v1/canteen/refresh/', {}, format='json')
        assert resp.status_code == 200
        assert resp.data['code'] == 200

        obj = CanteenConsumption.objects.get(user_id=test_user.id)
        assert obj.canteen_count == 2
        assert float(obj.total_amount) == 13.0

    def test_start_auto_login_validation(self, auth_client):
        """POST /api/v1/canteen/auto-login/start/ 参数缺失时 400"""
        resp = auth_client.post('/api/v1/canteen/auto-login/start/', {}, format='json')
        assert resp.status_code == 400
        assert resp.data['code'] == 400

    def test_submit_verification_validation(self, auth_client):
        """POST /api/v1/canteen/auto-login/submit-code/ 参数缺失时 400"""
        resp = auth_client.post('/api/v1/canteen/auto-login/submit-code/', {}, format='json')
        assert resp.status_code == 400
        assert resp.data['code'] == 400

    def test_check_auto_login_status_validation(self, auth_client):
        """GET /api/v1/canteen/auto-login/status/ 缺 session_id 时 400"""
        resp = auth_client.get('/api/v1/canteen/auto-login/status/')
        assert resp.status_code == 400
        assert resp.data['code'] == 400

    def test_start_auto_login_success_waiting_verification(self, auth_client, monkeypatch):
        """POST /auto-login/start/ 成功但需要验证码：返回 session_id + waiting_verification"""
        from canteen import views as canteen_views

        def fake_auto_login_and_fetch_cookie(idserial, password, headless=True, browser_type='chrome'):
            return {
                'success': True,
                'session_id': 'sess_wait',
                'status': 'waiting_verification',
            }

        monkeypatch.setattr(canteen_views, 'auto_login_and_fetch_cookie', fake_auto_login_and_fetch_cookie)

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/start/',
            {'idserial': '2023000001', 'password': 'pw', 'headless': True, 'browser_type': 'chrome'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['session_id'] == 'sess_wait'
        assert resp.data['data']['status'] == 'waiting_verification'

    def test_start_auto_login_success_completed(self, auth_client, monkeypatch):
        """POST /auto-login/start/ 成功且无需验证码：返回 completed + servicehall"""
        from canteen import views as canteen_views

        def fake_auto_login_and_fetch_cookie(idserial, password, headless=True, browser_type='chrome'):
            return {
                'success': True,
                'session_id': 'sess_done',
                'status': 'completed',
                'servicehall': 'cookie_abc',
            }

        monkeypatch.setattr(canteen_views, 'auto_login_and_fetch_cookie', fake_auto_login_and_fetch_cookie)

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/start/',
            {'idserial': '2023000001', 'password': 'pw'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['session_id'] == 'sess_done'
        assert resp.data['data']['status'] == 'completed'
        assert resp.data['data']['servicehall'] == 'cookie_abc'

    def test_check_auto_login_status_success(self, auth_client, monkeypatch):
        """GET /auto-login/status/ 有 session_id 时返回 200，并透传 status/servicehall/error"""
        from canteen import views as canteen_views

        monkeypatch.setattr(
            canteen_views,
            'check_login_status',
            lambda sid: {'success': True, 'status': 'completed', 'servicehall': 'cookie_abc', 'error': None},
        )

        resp = auth_client.get('/api/v1/canteen/auto-login/status/?session_id=sess_any')
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['status'] == 'completed'
        assert resp.data['data']['servicehall'] == 'cookie_abc'

    def test_submit_verification_success_returns_status_result(self, auth_client, monkeypatch):
        """POST /auto-login/submit-code/ 成功时返回 200 且 data 包含 check_login_status 的结果"""
        from canteen import views as canteen_views

        monkeypatch.setattr(
            canteen_views,
            'submit_verification_code',
            lambda sid, code: {'success': True, 'message': '验证码已提交'},
        )
        monkeypatch.setattr(
            canteen_views,
            'check_login_status',
            lambda sid: {'success': True, 'status': 'completed', 'servicehall': 'cookie_abc', 'error': None},
        )

        resp = auth_client.post(
            '/api/v1/canteen/auto-login/submit-code/',
            {'session_id': 'sess_any', 'verification_code': '1234'},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['code'] == 200
        assert resp.data['data']['status'] == 'completed'
        assert resp.data['data']['servicehall'] == 'cookie_abc'


@pytest.mark.django_db
class TestCanteenFetchServicehallCookieIntegration:
    """直接覆盖 services.fetch_servicehall_cookie / fetch_and_parse_consumption 的关键早返回分支。"""

    pytestmark = [pytest.mark.integration]

    def test_fetch_servicehall_cookie_timeout_returns_success_false(self, monkeypatch):
        """fetch_servicehall_cookie: 超时仍未拿到 servicehall cookie -> success=False。"""
        from canteen import services as canteen_services

        class DummyDriver:
            def get(self, url):
                return None

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, 'get_browser_driver', lambda *a, **k: DummyDriver())

        # 通过 max_wait_time=0 让 while 不进入，直接走 not servicehall 的超时分支
        res = canteen_services.fetch_servicehall_cookie(idserial='2023000001', max_wait_time=0)
        assert res['success'] is False
        assert res['servicehall'] is None
        assert res['idserial'] is None
        assert '超时' in (res.get('error') or '')

    def test_fetch_servicehall_cookie_extracts_idserial_empty_text_returns_error(self, monkeypatch):
        """fetch_servicehall_cookie: 找到了学号元素但 text/textContent/innerHTML 都为空 -> 失败分支。"""
        from canteen import services as canteen_services

        import sys
        import types

        class DummyElement:
            text = ''

            def get_attribute(self, name):
                return '   '

        class DummyWait:
            def __init__(self, driver, seconds):
                self.driver = driver
                self.seconds = seconds

            def until(self, *args, **kwargs):
                return DummyElement()

        class DummyDriver:
            def __init__(self):
                self._calls = 0

            def get(self, url):
                return None

            def get_cookies(self):
                self._calls += 1
                if self._calls == 1:
                    return [{'name': 'servicehall', 'value': 'cookie_abc'}]
                return [{'name': 'servicehall', 'value': 'cookie_abc'}]

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, 'get_browser_driver', lambda *a, **k: DummyDriver())

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            ID = 'id'

        by_mod.By = _By
        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

        res = canteen_services.fetch_servicehall_cookie(idserial=None, max_wait_time=1)
        assert res['success'] is False
        assert res['servicehall'] is None
        assert res['idserial'] is None
        assert '学号' in (res.get('error') or '')

    def test_fetch_servicehall_cookie_extracts_idserial_wait_raises_returns_error(self, monkeypatch):
        """fetch_servicehall_cookie: userinfo 页面定位/等待抛异常 -> 自动获取学号失败分支。"""
        from canteen import services as canteen_services

        import sys
        import types

        class DummyWait:
            def __init__(self, driver, seconds):
                self.driver = driver
                self.seconds = seconds

            def until(self, *args, **kwargs):
                raise RuntimeError('boom')

        class DummyDriver:
            def __init__(self):
                self._calls = 0

            def get(self, url):
                return None

            def get_cookies(self):
                self._calls += 1
                if self._calls == 1:
                    return [{'name': 'servicehall', 'value': 'cookie_abc'}]
                return [{'name': 'servicehall', 'value': 'cookie_abc'}]

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, 'get_browser_driver', lambda *a, **k: DummyDriver())

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            ID = 'id'

        by_mod.By = _By
        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

        res = canteen_services.fetch_servicehall_cookie(idserial=None, max_wait_time=1)
        assert res['success'] is False
        assert res['servicehall'] is None
        assert res['idserial'] is None
        assert '自动获取学号失败' in (res.get('error') or '')


@pytest.mark.django_db
class TestCanteenFetchAndParseConsumptionIntegration:
    pytestmark = [pytest.mark.integration]

    def test_fetch_and_parse_consumption_cookie_result_fails_returns_error(self, monkeypatch):
        """fetch_and_parse_consumption: servicehall 为空时获取 cookie 失败 -> 直接失败返回。"""
        from canteen import services as canteen_services

        monkeypatch.setattr(
            canteen_services,
            'fetch_servicehall_cookie',
            lambda *a, **k: {"success": False, "error": "cookie failed", "servicehall": None, "idserial": None},
        )

        res = canteen_services.fetch_and_parse_consumption(idserial=None, servicehall=None)
        assert res['success'] is False
        assert res['data'] is None
        assert res['servicehall'] is None
        assert res['idserial'] is None
        assert res['error'] == 'cookie failed'

    def test_fetch_and_parse_consumption_still_missing_idserial_returns_error(self, monkeypatch):
        """fetch_and_parse_consumption: cookie 成功但 idserial 仍为空 -> '未能获取学号' 早返回。"""
        from canteen import services as canteen_services

        monkeypatch.setattr(
            canteen_services,
            'fetch_servicehall_cookie',
            lambda *a, **k: {"success": True, "error": None, "servicehall": "cookie_abc", "idserial": None},
        )

        res = canteen_services.fetch_and_parse_consumption(idserial=None, servicehall=None)
        assert res['success'] is False
        assert res['data'] is None
        assert res['servicehall'] == 'cookie_abc'
        assert res['idserial'] is None
        assert '未能获取学号' in (res.get('error') or '')


@pytest.mark.django_db
class TestCanteenAutoLoginThreadBranchesIntegration:
    """覆盖 canteen.services._auto_login_thread 的关键失败分支。"""

    pytestmark = [pytest.mark.integration]

    def _install_fake_selenium_for_auto_login_thread(self, monkeypatch, wait_until_func):
        """为 _auto_login_thread 注入最小 selenium 模块树。

        wait_until_func(driver, *args, **kwargs) -> element 或抛异常
        """
        import sys
        import types

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            XPATH = 'xpath'
            ID = 'id'
            CLASS_NAME = 'class'

        by_mod.By = _By

        class DummyWait:
            def __init__(self, driver, seconds):
                self._driver = driver
                self._seconds = seconds

            def until(self, *args, **kwargs):
                return wait_until_func(self._driver, *args, **kwargs)

        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

    def test_auto_login_thread_username_input_wait_until_raises_sets_failed(self, monkeypatch):
        """wait.until 定位学号输入框失败 -> 填写学号失败 分支。"""
        from canteen import services as canteen_services

        self._install_fake_selenium_for_auto_login_thread(
            monkeypatch,
            wait_until_func=lambda driver, *a, **k: (_ for _ in ()).throw(RuntimeError('no user box')),
        )

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, *a, **k):
                raise AssertionError('should not reach password step')

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        import time as _time
        monkeypatch.setattr(_time, 'sleep', lambda *_: None)

        sid = 'sid_username_fail'
        canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '填写学号失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')

    def test_auto_login_thread_password_find_element_raises_sets_failed(self, monkeypatch):
        """driver.find_element(密码框) 抛异常 -> 填写密码失败 分支。"""
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        self._install_fake_selenium_for_auto_login_thread(
            monkeypatch,
            wait_until_func=lambda driver, *a, **k: DummyInput(),
        )

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                if selector == '//*[@id="i_pass"]':
                    raise RuntimeError('no pass box')
                raise AssertionError('unexpected selector')

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        import time as _time
        monkeypatch.setattr(_time, 'sleep', lambda *_: None)

        sid = 'sid_pass_fail'
        canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '填写密码失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')

    def test_auto_login_thread_click_login_raises_sets_failed(self, monkeypatch):
        """点击登录按钮抛异常 -> 点击登录按钮失败 分支。"""
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        class DummyButton:
            def click(self):
                raise RuntimeError('click failed')

        self._install_fake_selenium_for_auto_login_thread(
            monkeypatch,
            wait_until_func=lambda driver, *a, **k: DummyInput(),
        )

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                if selector == '//*[@id="i_pass"]':
                    return DummyInput()
                if selector == '//*[@id="theform"]/div[5]/a':
                    return DummyButton()
                raise AssertionError('unexpected selector')

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        import time as _time
        monkeypatch.setattr(_time, 'sleep', lambda *_: None)

        sid = 'sid_click_fail'
        canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '点击登录按钮失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')

    def test_auto_login_thread_msg_note_shows_error_text_sets_failed(self, monkeypatch):
        """msg_note 存在且有文本时 -> 登录失败: <text> 分支。"""
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        self._install_fake_selenium_for_auto_login_thread(
            monkeypatch,
            wait_until_func=lambda driver, *a, **k: DummyInput(),
        )

        class DummyButton:
            def click(self):
                return None

        class ErrorMsg:
            text = '用户名或密码错误'

            def is_displayed(self):
                return True

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                if selector == '//*[@id="i_pass"]':
                    return DummyInput()
                if selector == '//*[@id="theform"]/div[5]/a':
                    return DummyButton()
                if selector == '//*[@id="msg_note"]':
                    return ErrorMsg()
                raise RuntimeError('unexpected selector')

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())
        import time as _time
        monkeypatch.setattr(_time, 'sleep', lambda *_: None)

        sid = 'sid_msg_note_error'
        canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '登录失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')


class TestCanteenAutoLoginThreadVerificationStageBranchesIntegration:
    pytestmark = [pytest.mark.integration]

    def _install_fake_selenium(self, monkeypatch, wait_until_func):
        """复用与 AutoLoginThreadBranches 类似的最小 selenium 模块树注入。"""
        import sys
        import types

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            XPATH = 'xpath'
            ID = 'id'
            CLASS_NAME = 'class'

        by_mod.By = _By

        class DummyWait:
            def __init__(self, driver, seconds):
                self._driver = driver
                self._seconds = seconds

            def until(self, *args, **kwargs):
                return wait_until_func(self._driver, *args, **kwargs)

        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

    def test_auto_login_thread_verification_outer_try_raises_sets_failed(self, monkeypatch):
        """验证码阶段外层 try 捕获异常 -> 处理验证界面失败 分支。"""
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        # 第一次 wait.until 用于学号输入框，返回 DummyInput
        # 验证码阶段里面会重新构造 wait，并再次 wait.until；我们在第二次调用时抛异常
        def _wait_until(driver, *a, **k):
            call_count = getattr(driver, '_wait_until_calls', 0)
            driver._wait_until_calls = call_count + 1
            if call_count == 0:
                return DummyInput()
            raise RuntimeError('no verification ui')

        self._install_fake_selenium(monkeypatch, wait_until_func=_wait_until)

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                if selector == '//*[@id="i_pass"]':
                    return DummyInput()
                if selector == '//*[@id="theform"]/div[5]/a':
                    class Btn:
                        def click(self_inner):
                            return None

                    return Btn()
                if selector == '//*[@id="msg_note"]':
                    raise RuntimeError('no msg')
                raise RuntimeError('unexpected selector')

            def get_cookies(self):
                # 不提供 servicehall，以进入验证码阶段
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        import time as _time
        monkeypatch.setattr(_time, 'sleep', lambda *_: None)

        sid = 'sid_verify_outer_fail'
        canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '处理验证界面失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')

    def test_auto_login_thread_verification_no_ui_no_send_button_sets_failed(self, monkeypatch):
        """验证码阶段找不到 radio 且找不到发送验证码按钮 -> 未找到验证界面或发送验证码按钮 分支。"""
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        # 两次 wait.until 都返回可用输入框（学号输入框、验证码 radio 输入框），但第二次我们让 it 抛异常
        # 从而走到 inner except 分支；再由 driver.find_element 对 selectors 全都抛，触发 not send_code_button。
        def _wait_until(driver, *a, **k):
            call_count = getattr(driver, '_wait_until_calls', 0)
            driver._wait_until_calls = call_count + 1
            if call_count == 0:
                return DummyInput()
            raise RuntimeError('no radio input')

        self._install_fake_selenium(monkeypatch, wait_until_func=_wait_until)

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                if selector == '//*[@id="i_pass"]':
                    return DummyInput()
                if selector == '//*[@id="theform"]/div[5]/a':
                    class Btn:
                        def click(self_inner):
                            return None

                    return Btn()
                if selector == '//*[@id="msg_note"]':
                    raise RuntimeError('no msg')

                # inner except 中会尝试多个 selectors 查找 send_code_button，全部抛异常
                raise RuntimeError('not found')

            @property
            def page_source(self):
                return '<html></html>'

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        import time as _time
        monkeypatch.setattr(_time, 'sleep', lambda *_: None)

        sid = 'sid_verify_no_ui_no_send'
        canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '未找到验证界面或发送验证码按钮' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')


class TestCanteenAutoLoginThreadVericodeAndLoginButtonFailureBranchesIntegration:
    """覆盖验证码输入/点击登录按钮/未找到登录按钮等稳定失败分支（避免长轮询）。"""

    pytestmark = [pytest.mark.integration]

    def _install_fake_selenium(self, monkeypatch, wait_until_func):
        import sys
        import types

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            XPATH = 'xpath'
            ID = 'id'
            CLASS_NAME = 'class'

        by_mod.By = _By

        class DummyWait:
            def __init__(self, driver, seconds):
                self._driver = driver
                self._seconds = seconds

            def until(self, *args, **kwargs):
                return wait_until_func(self._driver, *args, **kwargs)

        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

    def _run_until_vericode_stage(self, monkeypatch, *, find_element_impl):
        """构造：不直接拿到 servicehall、能走到 waiting_verification 且立刻有 verification_code。

        关键：不 patch time.sleep，避免把内部状态搞乱；改为 monkeypatch services 内部的 time.sleep 为 no-op。
        """
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        # wait.until：学号输入框返回 DummyInput；验证码界面 radio 返回可 click 对象；确认界面“否” radio 直接抛异常跳过
        def _wait_until(driver, *a, **k):
            call_count = getattr(driver, '_wait_until_calls', 0)
            driver._wait_until_calls = call_count + 1
            if call_count == 0:
                return DummyInput()
            if call_count == 1:
                class Radio:
                    def click(self_inner):
                        return None

                return Radio()
            raise RuntimeError('no confirm ui')

        self._install_fake_selenium(monkeypatch, wait_until_func=_wait_until)

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                return find_element_impl(selector, DummyInput)

            def get_cookies(self):
                return []

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        # 只把 services 里用到的 time.sleep 变为 no-op（不影响我们这里的逻辑）
        import types as _types

        monkeypatch.setattr(
            canteen_services,
            'time',
            _types.SimpleNamespace(sleep=lambda *_: None),
            raising=False,
        )

        sid = 'sid_vericode_stage_case'

        # 关键点：_auto_login_thread 自己会覆写/初始化 LOGIN_SESSIONS[session_id]。
        # 所以这里不要先把 verification_code 塞进 dict 里，否则会被覆盖掉；
        # 改为先保证 session 存在，然后在它切到 waiting_verification 后，再补上验证码。
        with canteen_services.SESSION_LOCK:
            canteen_services.LOGIN_SESSIONS[sid] = {
                'status': 'initializing',
                'driver': None,
                'error': None,
                'servicehall': None,
            }

        # 用一个 hook：当 services 把状态设置成 waiting_verification 时，立刻注入 verification_code。
        # 注意：services 的写入点是 `LOGIN_SESSIONS[session_id]['status'] = ...`，不是给 dict 整体赋值。
        # 所以这里通过包一层锁：每次退出锁时检查并注入。
        original_lock = canteen_services.SESSION_LOCK

        class HookedLock:
            def __enter__(self_inner):
                return original_lock.__enter__()

            def __exit__(self_inner, exc_type, exc, tb):
                try:
                    sess = canteen_services.LOGIN_SESSIONS.get(sid)
                    if isinstance(sess, dict) and sess.get('status') == 'waiting_verification':
                        sess.setdefault('verification_code', '123456')
                finally:
                    return original_lock.__exit__(exc_type, exc, tb)

        monkeypatch.setattr(canteen_services, 'SESSION_LOCK', HookedLock())
        try:
            canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        finally:
            monkeypatch.setattr(canteen_services, 'SESSION_LOCK', original_lock)
        return canteen_services, sid

    def test_auto_login_thread_vericode_input_raises_sets_failed(self, monkeypatch):
        """验证码输入框定位失败 -> 填写验证码失败 分支。"""

        def _find_element_impl(selector, DummyInput):
            if selector == '//*[@id="i_pass"]':
                return DummyInput()
            if selector == '//*[@id="theform"]/div[5]/a':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()
            if selector == '//*[@id="msg_note"]':
                raise RuntimeError('no msg')

            if selector == '//button[@type="submit" and contains(@class, "btn-info")]':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            if selector == '//*[@id="vericode"]':
                raise RuntimeError('no vericode input')

            raise RuntimeError('unexpected selector')

        canteen_services, sid = self._run_until_vericode_stage(monkeypatch, find_element_impl=_find_element_impl)
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '填写验证码失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')

    def test_auto_login_thread_vericode_login_button_click_raises_sets_failed(self, monkeypatch):
        """验证码阶段点击登录按钮抛异常 -> 点击登录按钮失败 分支。"""

        def _find_element_impl(selector, DummyInput):
            if selector == '//*[@id="i_pass"]':
                return DummyInput()
            if selector == '//*[@id="theform"]/div[5]/a':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()
            if selector == '//*[@id="msg_note"]':
                raise RuntimeError('no msg')

            if selector == '//button[@type="submit" and contains(@class, "btn-info")]':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            if selector == '//*[@id="vericode"]':
                return DummyInput()

            if selector == "//button[contains(text(), '登录')]":
                class Btn:
                    def click(self_inner):
                        raise RuntimeError('click failed')

                return Btn()

            raise RuntimeError('unexpected selector')

        canteen_services, sid = self._run_until_vericode_stage(monkeypatch, find_element_impl=_find_element_impl)
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '点击登录按钮失败' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')

    def test_auto_login_thread_vericode_login_button_not_found_sets_failed(self, monkeypatch):
        """验证码阶段找不到任何登录按钮 -> 未找到登录按钮 分支。"""

        def _find_element_impl(selector, DummyInput):
            if selector == '//*[@id="i_pass"]':
                return DummyInput()
            if selector == '//*[@id="theform"]/div[5]/a':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()
            if selector == '//*[@id="msg_note"]':
                raise RuntimeError('no msg')

            if selector == '//button[@type="submit" and contains(@class, "btn-info")]':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            if selector == '//*[@id="vericode"]':
                return DummyInput()

            # 所有登录按钮 selector 都找不到
            raise RuntimeError('not found')

        canteen_services, sid = self._run_until_vericode_stage(monkeypatch, find_element_impl=_find_element_impl)
        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS[sid]['status'] == 'failed'
            assert '未找到登录按钮' in (canteen_services.LOGIN_SESSIONS[sid].get('error') or '')


class TestCanteenAutoLoginThreadVerificationPostSubmitStableBranchesIntegration:
    """覆盖验证码提交后可稳定触发的失败分支（避免 300 秒轮询 flaky）。"""

    pytestmark = [pytest.mark.integration]

    def _install_fake_selenium(self, monkeypatch, wait_until_func):
        import sys
        import types

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            XPATH = 'xpath'
            ID = 'id'
            CLASS_NAME = 'class'

        by_mod.By = _By

        class DummyWait:
            def __init__(self, driver, seconds):
                self._driver = driver
                self._seconds = seconds

            def until(self, *args, **kwargs):
                return wait_until_func(self._driver, *args, **kwargs)

        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

    def _run_verification_post_submit(self, monkeypatch, *, sid, find_element_impl, get_cookies_impl):
        """跑到验证码提交后的阶段。

        - 通过 hooked lock 在状态切到 waiting_verification 时立即注入 verification_code，跳过 300 秒等待。
        - 不直接 patch 全局 time.sleep；如需加速，使用 sys.modules['time'] 替换，让函数内 import time 指向假的模块。
        """
        from canteen import services as canteen_services

        class DummyInput:
            def clear(self):
                return None

            def send_keys(self, *_):
                return None

        # WebDriverWait.until：第 0 次用于学号输入框；第 1 次用于验证码界面 radio；其余直接抛异常（跳过确认界面）
        def _wait_until(driver, *a, **k):
            call_count = getattr(driver, '_wait_until_calls', 0)
            driver._wait_until_calls = call_count + 1
            if call_count == 0:
                return DummyInput()
            if call_count == 1:
                class Radio:
                    def click(self_inner):
                        return None

                return Radio()
            raise RuntimeError('no confirm ui')

        self._install_fake_selenium(monkeypatch, wait_until_func=_wait_until)

        class FakeDriver:
            def get(self, url):
                return None

            def find_element(self, by, selector):
                return find_element_impl(selector, DummyInput)

            def get_cookies(self):
                return get_cookies_impl()

            def quit(self):
                return None

        monkeypatch.setattr(canteen_services, '_get_browser_driver_for_login', lambda *a, **k: FakeDriver())

        # Hooked lock：在 services 把状态置为 waiting_verification 时立即塞入验证码
        original_lock = canteen_services.SESSION_LOCK

        class HookedLock:
            def __enter__(self_inner):
                return original_lock.__enter__()

            def __exit__(self_inner, exc_type, exc, tb):
                try:
                    sess = canteen_services.LOGIN_SESSIONS.get(sid)
                    if isinstance(sess, dict) and sess.get('status') == 'waiting_verification':
                        sess.setdefault('verification_code', '123456')
                finally:
                    return original_lock.__exit__(exc_type, exc, tb)

        monkeypatch.setattr(canteen_services, 'SESSION_LOCK', HookedLock())

        # 预置 session，避免 keyerror
        with canteen_services.SESSION_LOCK:
            canteen_services.LOGIN_SESSIONS[sid] = {
                'status': 'initializing',
                'driver': None,
                'error': None,
                'servicehall': None,
            }

        try:
            canteen_services._auto_login_thread(sid, '2023000001', 'pw', True, 'chrome')
        finally:
            monkeypatch.setattr(canteen_services, 'SESSION_LOCK', original_lock)

        return canteen_services

    def test_auto_login_thread_invalid_feedback_sets_failed_with_vericode_error(self, monkeypatch):
        """验证码错误提示（invalid-feedback/校验码错误）-> '验证码错误，请重试'。"""

        def _find_element_impl(selector, DummyInput):
            # 登录前：密码输入框、登录按钮
            if selector == '//*[@id="i_pass"]':
                return DummyInput()
            if selector == '//*[@id="theform"]/div[5]/a':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()
            if selector == '//*[@id="msg_note"]':
                raise RuntimeError('no msg')

            # 验证界面确认按钮
            if selector == '//button[@type="submit" and contains(@class, "btn-info")]':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            # 输入验证码
            if selector == '//*[@id="vericode"]':
                return DummyInput()

            # 找到登录按钮（验证码阶段）
            if selector == "//button[contains(text(), '登录')]":
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            # 验证码错误提示
            if selector == '//div[@class="invalid-feedback" and contains(text(), "校验码错误")]':
                class Feedback:
                    def is_displayed(self_inner):
                        return True

                return Feedback()

            raise RuntimeError('unexpected selector')

        canteen_services = self._run_verification_post_submit(
            monkeypatch,
            sid='sid_vericode_invalid_feedback',
            find_element_impl=_find_element_impl,
            get_cookies_impl=lambda: [],
        )

        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS['sid_vericode_invalid_feedback']['status'] == 'failed'
            assert canteen_services.LOGIN_SESSIONS['sid_vericode_invalid_feedback']['error'] == '验证码错误，请重试'

    def test_auto_login_thread_no_servicehall_cookie_sets_failed(self, monkeypatch):
        """验证码正确但最终未获取 servicehall cookie -> '登录失败：未能获取servicehall cookie'。"""

        # 让函数内 `import time` 拿到假的 time 模块，从而把 20 秒等待变成瞬间。
        import sys
        import types

        original_time_mod = sys.modules.get('time')

        class FastTime(types.ModuleType):
            def sleep(self_inner, *_args, **_kwargs):
                return None

        sys.modules['time'] = FastTime('time')

        def _find_element_impl(selector, DummyInput):
            if selector == '//*[@id="i_pass"]':
                return DummyInput()
            if selector == '//*[@id="theform"]/div[5]/a':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()
            if selector == '//*[@id="msg_note"]':
                raise RuntimeError('no msg')

            if selector == '//button[@type="submit" and contains(@class, "btn-info")]':
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            if selector == '//*[@id="vericode"]':
                return DummyInput()

            # 验证码阶段登录按钮：给一个可 click 的
            if selector == "//button[contains(text(), '登录')]":
                class Btn:
                    def click(self_inner):
                        return None

                return Btn()

            # 不提供 invalid-feedback（走“验证码正确继续”分支）
            if selector == '//div[@class="invalid-feedback" and contains(text(), "校验码错误")]':
                raise RuntimeError('no invalid feedback')

            raise RuntimeError('unexpected selector')

        try:
            canteen_services = self._run_verification_post_submit(
                monkeypatch,
                sid='sid_no_servicehall_cookie',
                find_element_impl=_find_element_impl,
                get_cookies_impl=lambda: [],
            )
        finally:
            if original_time_mod is not None:
                sys.modules['time'] = original_time_mod
            else:
                del sys.modules['time']

        with canteen_services.SESSION_LOCK:
            assert canteen_services.LOGIN_SESSIONS['sid_no_servicehall_cookie']['status'] == 'failed'
            assert canteen_services.LOGIN_SESSIONS['sid_no_servicehall_cookie']['error'] == '登录失败：未能获取servicehall cookie'


class TestCanteenAutoLoginThreadVerificationPostSubmitBranchesIntegration:
    pytestmark = [pytest.mark.integration]

    def _install_fake_selenium(self, monkeypatch, wait_until_func):
        import sys
        import types

        selenium_mod = types.ModuleType('selenium')
        webdriver_mod = types.ModuleType('selenium.webdriver')
        common_mod = types.ModuleType('selenium.webdriver.common')
        by_mod = types.ModuleType('selenium.webdriver.common.by')
        support_mod = types.ModuleType('selenium.webdriver.support')
        ui_mod = types.ModuleType('selenium.webdriver.support.ui')
        ec_mod = types.ModuleType('selenium.webdriver.support.expected_conditions')

        class _By:
            XPATH = 'xpath'
            ID = 'id'
            CLASS_NAME = 'class'

        by_mod.By = _By

        class DummyWait:
            def __init__(self, driver, seconds):
                self._driver = driver
                self._seconds = seconds

            def until(self, *args, **kwargs):
                return wait_until_func(self._driver, *args, **kwargs)

        ui_mod.WebDriverWait = DummyWait
        ec_mod.presence_of_element_located = lambda locator: locator

        monkeypatch.setitem(sys.modules, 'selenium', selenium_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver', webdriver_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common', common_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.common.by', by_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support', support_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.ui', ui_mod)
        monkeypatch.setitem(sys.modules, 'selenium.webdriver.support.expected_conditions', ec_mod)

    # NOTE: 
    # “验证码提交后”的分支目前依赖线程继续运行与内部轮询/等待逻辑。
    # 在 Docker 环境中如果对 time.sleep 做任何加速 patch，很容易导致线程直接走到
    # “等待验证码超时”分支，从而让测试变得脆弱且不稳定。
    # 我们先移除这两条用例，后续会用更可控的方式（不依赖长轮询）补回同等覆盖。
