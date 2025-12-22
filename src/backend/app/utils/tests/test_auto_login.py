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
import os

# Mock selenium模块以避免导入错误
mock_selenium = MagicMock()
sys.modules['selenium'] = mock_selenium
sys.modules['selenium.webdriver'] = MagicMock()
sys.modules['selenium.webdriver.chrome'] = MagicMock()
sys.modules['selenium.webdriver.chrome.options'] = MagicMock()

# 导入被测试的模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from auto_login import decrypt_aes_ecb, get_canteen_data


class TestDecryptAESECB(unittest.TestCase):
    """测试AES ECB解密函数"""

    def test_decrypt_aes_ecb_success(self):
        """测试成功解密"""
        # 创建测试数据
        key = b'1234567890123456'  # 16字节密钥
        plaintext = '{"test": "data"}'

        # 加密数据
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
        encrypted_data = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        # 解密
        result = decrypt_aes_ecb(encrypted_data)

        # 验证
        self.assertEqual(result, plaintext)

    def test_decrypt_aes_ecb_different_key(self):
        """测试不同密钥的解密"""
        key1 = b'1234567890123456'
        key2 = b'abcdefghijklmnop'
        plaintext = 'test data'

        # 使用key1加密
        cipher = AES.new(key1, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
        encrypted_data = key1.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        # 使用key1解密应该成功
        result = decrypt_aes_ecb(encrypted_data)
        self.assertEqual(result, plaintext)


class TestGetCanteenData(unittest.TestCase):
    """测试获取食堂消费数据函数"""

    @patch('auto_login.requests.post')
    def test_get_canteen_data_success(self, mock_post):
        """测试成功获取食堂数据"""
        # 准备测试数据
        idserial = '2023000001'
        servicehall = 'test_cookie'

        # 创建加密的响应数据
        test_data = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口1", "txamt": 1500},  # 15元
                    {"mername": "桃李园-窗口2", "txamt": 2000},  # 20元
                    {"mername": "丁香园", "txamt": 1000},  # 10元
                ]
            }
        }

        # 加密数据
        key = b'1234567890123456'
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(json.dumps(test_data).encode('utf-8'), AES.block_size))
        encrypted_string = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"data": encrypted_string})
        mock_post.return_value = mock_response

        # 调用函数
        result = get_canteen_data(idserial, servicehall)

        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["idserial"], idserial)
        self.assertEqual(result["data"]["total_amount"], 45.0)  # 15+20+10
        self.assertEqual(result["data"]["canteen_count"], 3)
        self.assertIn("紫荆园", result["data"]["canteens"])
        self.assertIn("桃李园", result["data"]["canteens"])
        self.assertIn("丁香园", result["data"]["canteens"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_http_error(self, mock_post):
        """测试HTTP错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("HTTP请求失败", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_no_data_field(self, mock_post):
        """测试响应中没有data字段"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"error": "no data"})
        mock_post.return_value = mock_response

        result = get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("未找到data字段", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_invalid_json(self, mock_post):
        """测试无效的JSON响应"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "invalid json"
        mock_post.return_value = mock_response

        result = get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("JSON解析错误", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_invalid_decrypted_format(self, mock_post):
        """测试解密后数据格式错误"""
        idserial = '2023000001'
        servicehall = 'test_cookie'

        # 创建无效的加密数据
        key = b'1234567890123456'
        cipher = AES.new(key, AES.MODE_ECB)
        invalid_data = json.dumps({"invalid": "data"})
        encrypted_bytes = cipher.encrypt(pad(invalid_data.encode('utf-8'), AES.block_size))
        encrypted_string = key.decode('utf-8') + base64.b64encode(encrypted_bytes).decode('utf-8')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"data": encrypted_string})
        mock_post.return_value = mock_response

        result = get_canteen_data(idserial, servicehall)

        self.assertFalse(result["success"])
        self.assertIn("解密后数据格式错误", result["error"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_merchant_name_parsing(self, mock_post):
        """测试商户名称解析（下划线、横线、无分隔符）"""
        idserial = '2023000001'
        servicehall = 'test_cookie'

        test_data = {
            "resultData": {
                "rows": [
                    {"mername": "紫荆园_窗口1", "txamt": 1000},
                    {"mername": "桃李园-窗口2", "txamt": 2000},
                    {"mername": "丁香园", "txamt": 3000},
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

        result = get_canteen_data(idserial, servicehall)

        self.assertTrue(result["success"])
        # 验证食堂名称正确提取
        self.assertIn("紫荆园", result["data"]["canteens"])
        self.assertIn("桃李园", result["data"]["canteens"])
        self.assertIn("丁香园", result["data"]["canteens"])

    @patch('auto_login.requests.post')
    def test_get_canteen_data_request_exception(self, mock_post):
        """测试网络请求异常"""
        import requests
        mock_post.side_effect = requests.RequestException("网络错误")

        result = get_canteen_data('2023000001', 'test_cookie')

        self.assertFalse(result["success"])
        self.assertIn("数据获取失败", result["error"])


if __name__ == '__main__':
    unittest.main()

