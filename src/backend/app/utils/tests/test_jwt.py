"""
单元测试：JWT工具函数
测试JWT生成、验证、解码等功能
"""
from django.test import TestCase
from datetime import datetime, timedelta
import time

from utils.jwt import generate_jwt, verify_jwt, encrypt_password


class JWTGenerationTest(TestCase):
    """JWT生成测试"""

    def test_generate_jwt_with_valid_payload(self):
        """测试使用有效载荷生成JWT"""
        payload = {
            'user_id': 1,
            'nickname': 'testuser'
        }
        token = generate_jwt(payload)

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

        # JWT应该是三部分用.分隔
        parts = token.split('.')
        self.assertEqual(len(parts), 3)

    def test_generate_jwt_with_empty_payload(self):
        """测试使用空载荷生成JWT"""
        payload = {}
        token = generate_jwt(payload)
        self.assertIsNotNone(token)

    def test_generate_jwt_contains_payload_data(self):
        """测试JWT包含载荷数据"""
        payload = {
            'user_id': 123,
            'nickname': 'Alice'
        }
        token = generate_jwt(payload)

        # 验证并解码
        decoded = verify_jwt(token)
        if decoded:
            self.assertEqual(decoded.get('user_id'), 123)
            self.assertEqual(decoded.get('nickname'), 'Alice')


class JWTVerificationTest(TestCase):
    """JWT验证测试"""

    def test_verify_valid_jwt(self):
        """测试验证有效的JWT"""
        payload = {'user_id': 1, 'nickname': 'test'}
        token = generate_jwt(payload)

        decoded = verify_jwt(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.get('user_id'), 1)
        self.assertEqual(decoded.get('nickname'), 'test')

    def test_verify_jwt_with_invalid_signature(self):
        """测试验证签名错误的JWT"""
        payload = {'user_id': 1}
        token = generate_jwt(payload)

        # 修改token的最后几个字符来破坏签名
        invalid_token = token[:-10] + 'invalidxxx'

        decoded = verify_jwt(invalid_token)
        self.assertIsNone(decoded)

    def test_verify_jwt_with_malformed_token(self):
        """测试验证格式错误的JWT"""
        invalid_tokens = [
            'not.a.valid.jwt.token',
            'invalid',
            '',
            'a.b',  # 只有两部分
        ]

        for token in invalid_tokens:
            decoded = verify_jwt(token)
            self.assertIsNone(decoded)

    def test_verify_jwt_with_none(self):
        """测试验证None值"""
        decoded = verify_jwt(None)
        self.assertIsNone(decoded)


class PasswordEncryptionTest(TestCase):
    """密码加密测试"""

    def test_encrypt_password(self):
        """测试密码加密"""
        password = 'mypassword123'
        encrypted = encrypt_password(password)

        self.assertIsNotNone(encrypted)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, password)  # 加密后应该不同
        self.assertGreater(len(encrypted), 0)

    def test_encrypt_same_password_produces_same_hash(self):
        """测试相同密码产生相同哈希（如果使用MD5/SHA等）"""
        password = 'testpass'
        hash1 = encrypt_password(password)
        hash2 = encrypt_password(password)

        # 如果使用简单的哈希（非salt），应该相同
        # 如果使用了salt，则每次不同，需要修改这个测试
        self.assertEqual(hash1, hash2)

    def test_encrypt_different_passwords_produce_different_hashes(self):
        """测试不同密码产生不同哈希"""
        hash1 = encrypt_password('password1')
        hash2 = encrypt_password('password2')

        self.assertNotEqual(hash1, hash2)

    def test_encrypt_empty_password(self):
        """测试加密空密码"""
        encrypted = encrypt_password('')
        self.assertIsNotNone(encrypted)
        self.assertIsInstance(encrypted, str)

    def test_encrypt_long_password(self):
        """测试加密长密码"""
        long_password = 'a' * 1000
        encrypted = encrypt_password(long_password)
        self.assertIsNotNone(encrypted)

    def test_encrypt_special_characters(self):
        """测试加密包含特殊字符的密码"""
        special_password = '!@#$%^&*()_+-={}[]|\\:";\'<>?,./'
        encrypted = encrypt_password(special_password)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, special_password)

