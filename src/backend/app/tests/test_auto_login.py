"""
测试 auto_login.py 模块
"""
import unittest
from unittest.mock import patch, Mock, MagicMock
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import sys

# 需要导入auto_login模块
import importlib.util
spec = importlib.util.spec_from_file_location("auto_login", "auto_login.py")
auto_login = importlib.util.module_from_spec(spec)
sys.modules['auto_login'] = auto_login

# Mock selenium模块
mock_selenium = MagicMock()
sys.modules['selenium'] = mock_selenium
sys.modules['selenium.webdriver'] = MagicMock()
sys.modules['selenium.webdriver.chrome'] = MagicMock()
sys.modules['selenium.webdriver.chrome.options'] = MagicMock()

spec.loader.exec_module(auto_login)


class TestDecryptAESECB(unittest.TestCase):
    """测试AES ECB解密函数"""

    def test_decrypt_aes_ecb_success(self):
        """测试成功解密"""
        key = b'1234567890123456'
        plaintext = '{"test": "data"}'

        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
        encrypted_data = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        result = auto_login.decrypt_aes_ecb(encrypted_data)
        self.assertEqual(result, plaintext)


class TestGetCanteenData(unittest.TestCase):
    """测试获取食堂消费数据函数"""

    @patch('auto_login.requests.post')
    def test_get_canteen_data_success(self, mock_post):
        """测试成功获取食堂数据"""
        idserial = '2023000001'
        servicehall = 'test_cookie'

        test_data = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口1", "txamt": 1500},
                    {"mername": "桃李园-窗口2", "txamt": 2000},
                    {"mername": "丁香园", "txamt": 1000},
                ]
            }
        }

        key = b'1234567890123456'
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(json.dumps(test_data).encode('utf-8'), AES.block_size))
        encrypted_string = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"data": encrypted_string})
        mock_post.return_value = mock_response

        result = auto_login.get_canteen_data(idserial, servicehall)

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["idserial"], idserial)
        self.assertIn("total_amount", result["data"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_http_error(self, mock_post):
        """测试HTTP错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = auto_login.get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("HTTP请求失败", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_no_data_field(self, mock_post):
        """测试响应中没有data字段"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"error": "no data"})
        mock_post.return_value = mock_response

        result = auto_login.get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("响应数据格式错误", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_invalid_format(self, mock_post):
        """测试解密后数据格式错误"""
        key = b'1234567890123456'
        invalid_data = json.dumps({"invalid": "data"})
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(invalid_data.encode('utf-8'), AES.block_size))
        encrypted_string = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"data": encrypted_string})
        mock_post.return_value = mock_response

        result = auto_login.get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("解密后数据格式错误", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_json_decode_error(self, mock_post):
        """测试JSON解析错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "invalid json"
        mock_post.return_value = mock_response

        result = auto_login.get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("JSON解析错误", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_exception(self, mock_post):
        """测试一般异常"""
        mock_post.side_effect = Exception("未知错误")

        result = auto_login.get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("数据获取失败", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_exception_in_loop(self, mock_post):
        """测试循环中发生异常"""
        test_data = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园", "txamt": 1000},  # 正常
                    {"invalid": "data"},  # 会触发异常
                ]
            }
        }

        key = b'1234567890123456'
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(json.dumps(test_data).encode('utf-8'), AES.block_size))
        encrypted_string = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"data": encrypted_string})
        mock_post.return_value = mock_response

        result = auto_login.get_canteen_data('2023000001', 'test_cookie')

        # 应该忽略错误记录，返回成功
        self.assertTrue(result["success"])


class TestGetServicehallCookie(unittest.TestCase):
    """测试获取servicehall cookie函数"""

    @patch('auto_login.webdriver.Chrome')
    @patch('auto_login.Options')
    @patch('auto_login.time.sleep')
    @patch('auto_login.time.time')
    def test_get_servicehall_cookie_success(self, mock_time, mock_sleep, mock_options_class, mock_chrome):
        """测试成功获取cookie"""
        mock_driver = Mock()
        mock_driver.get_cookies.return_value = [
            {'name': 'servicehall', 'value': 'test_cookie_value'},
        ]
        mock_chrome.return_value = mock_driver
        mock_options = Mock()
        mock_options_class.return_value = mock_options

        # 模拟时间：第一次返回0（开始时间），第二次返回1（循环中检查时间）
        mock_time.side_effect = [0, 1]

        result = auto_login.get_servicehall_cookie('2023000001')

        self.assertTrue(result["success"])
        self.assertEqual(result["servicehall"], 'test_cookie_value')
        mock_driver.quit.assert_called_once()

    @patch('auto_login.webdriver.Chrome')
    @patch('auto_login.Options')
    @patch('auto_login.time.sleep')
    @patch('auto_login.time.time')
    def test_get_servicehall_cookie_timeout(self, mock_time, mock_sleep, mock_options_class, mock_chrome):
        """测试获取cookie超时"""
        mock_driver = Mock()
        mock_driver.get_cookies.return_value = []  # 没有servicehall cookie
        mock_chrome.return_value = mock_driver
        mock_options = Mock()
        mock_options_class.return_value = mock_options

        # 模拟时间流逝：第一次返回0（开始时间），之后每次返回301（超过300秒超时时间）
        mock_time.side_effect = [0, 301]

        result = auto_login.get_servicehall_cookie('2023000001')

        self.assertFalse(result["success"])
        self.assertIn("超时", result["error"])
        mock_driver.quit.assert_called_once()

    @patch('auto_login.webdriver.Chrome')
    @patch('auto_login.Options')
    def test_get_servicehall_cookie_exception(self, mock_options_class, mock_chrome):
        """测试浏览器操作异常"""
        mock_chrome.side_effect = Exception("浏览器启动失败")
        mock_options = Mock()
        mock_options_class.return_value = mock_options

        result = auto_login.get_servicehall_cookie('2023000001')

        self.assertFalse(result["success"])
        self.assertIn("浏览器操作失败", result["error"])


if __name__ == '__main__':
    unittest.main()

