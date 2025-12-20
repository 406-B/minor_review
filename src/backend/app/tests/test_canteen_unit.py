import pytest
from unittest.mock import patch, MagicMock
from canteen.services import fetch_canteen_data, decrypt_aes_ecb
from canteen.controllers import bind_idserial_and_fetch
from canteen.models import CanteenConsumption
from login.models import User
from django.contrib.auth.models import User as AuthUser
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

@pytest.fixture
def mock_user():
    auth_user = AuthUser.objects.create_user(username='unit_test_user', password='password')
    user = User.objects.create(id=auth_user.id, username='unit_test_user', nickname='Unit Test User')
    return user

def encrypt_aes_ecb(data, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')

class TestCanteenServices:
    
    def test_decrypt_aes_ecb(self):
        key = "1234567890123456"
        data = "test_data"
        encrypted = encrypt_aes_ecb(data, key)
        # The service expects key + encrypted_base64
        input_str = key + encrypted
        
        decrypted = decrypt_aes_ecb(input_str)
        assert decrypted == data

    @patch('canteen.services.requests.post')
    def test_fetch_canteen_data_success(self, mock_post):
        # Prepare mock response
        key = "1234567890123456"
        
        # The service expects specific structure inside decrypted data
        # And filters by name ending with "园"
        # And expects amount in cents (txamt)
        decrypted_data_dict = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_Window 1", "txamt": 5000}, # 50.00
                    {"mername": "桃李园-Window 2", "txamt": 5000}, # 50.00
                    {"mername": "超市", "txamt": 1000} # Should be ignored
                ]
            }
        }
        
        encrypted_data = encrypt_aes_ecb(json.dumps(decrypted_data_dict), key)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            "data": key + encrypted_data
        })
        mock_post.return_value = mock_response
        
        result = fetch_canteen_data("2023000001", "mock_cookie")
        
        assert result['success'] is True
        # Verify parsed data
        assert result['data']['canteen_count'] == 2
        assert result['data']['total_amount'] == 100.0
        
    @patch('canteen.services.requests.post')
    def test_fetch_canteen_data_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = fetch_canteen_data("2023000001", "mock_cookie")
        assert result['success'] is False
        assert "HTTP请求失败" in result['error']

@pytest.mark.django_db
class TestCanteenControllers:

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_bind_idserial_and_fetch_success(self, mock_fetch, mock_user):
        mock_fetch.return_value = {
            "success": True,
            "idserial": "2023000001",
            "servicehall": "new_cookie",
            "data": {
                "total_amount": 100.0,
                "canteen_count": 1,
                "canteens": {"Canteen A": 100.0}
            }
        }
        
        success, message, data = bind_idserial_and_fetch(mock_user, "2023000001")
        
        assert success is True
        assert "绑定成功" in message
        assert data['idserial'] == "2023000001"
        
        # Verify DB
        consumption = CanteenConsumption.objects.get(user=mock_user)
        assert consumption.idserial == "2023000001"
        assert consumption.servicehall_cookie == "new_cookie"

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_bind_idserial_and_fetch_fail(self, mock_fetch, mock_user):
        mock_fetch.return_value = {
            "success": False,
            "error": "Fetch failed"
        }
        
        success, message, data = bind_idserial_and_fetch(mock_user, "2023000001")
        
        assert success is False
        assert "Fetch failed" in message
