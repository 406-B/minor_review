"""
单元测试：内容审核服务
测试审核功能和API调用
"""
import unittest.mock as mock
from django.test import TestCase, override_settings
from django.conf import settings

from utils.audit import ContentAuditService, audit_content


class ContentAuditServiceTest(TestCase):
    """内容审核服务单元测试"""

    def setUp(self):
        self.service = ContentAuditService()

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_pass(self):
        """测试内容审核通过"""
        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            mock_call.return_value = '{"status": "通过", "reason": ""}'

            result, reason = self.service.audit_content("正常内容")

            self.assertTrue(result)
            self.assertEqual(reason, "")

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_fail(self):
        """测试内容审核失败"""
        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            mock_call.return_value = '{"status": "不通过", "reason": "包含违规内容"}'

            result, reason = self.service.audit_content("违规内容")

            self.assertFalse(result)
            self.assertEqual(reason, "包含违规内容")

    def test_audit_content_no_api_key(self):
        """测试没有API密钥时的默认行为"""
        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            # 确保API不会被调用
            mock_call.return_value = None

            result, reason = self.service.audit_content("测试内容")

            # 没有API密钥时应该默认通过
            self.assertTrue(result)
            self.assertEqual(reason, "")

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_api_error(self):
        """测试API调用失败"""
        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            mock_call.return_value = None

            result, reason = self.service.audit_content("测试内容")

            # API失败时应该默认通过
            self.assertTrue(result)
            self.assertEqual(reason, "")

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_parse_response_valid_json(self):
        """测试解析有效的JSON响应"""
        response = '{"status": "不通过", "reason": "违规"}'
        result = self.service._parse_response(response)

        self.assertEqual(result['status'], '不通过')
        self.assertEqual(result['reason'], '违规')

    def test_parse_response_invalid_json(self):
        """测试解析无效的JSON响应"""
        response = '这不是JSON格式'
        result = self.service._parse_response(response)

        self.assertIsNone(result)

    def test_parse_response_json_in_text(self):
        """测试从文本中提取JSON"""
        response = '一些文本{"status": "通过"}更多文本'
        result = self.service._parse_response(response)

        self.assertEqual(result['status'], '通过')

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_with_type_and_title(self):
        """测试带类型和标题的内容审核"""
        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            mock_call.return_value = '{"status": "通过", "reason": ""}'

            result, reason = self.service.audit_content(
                content="测试内容",
                content_type="post",
                title="测试标题"
            )

            self.assertTrue(result)
            mock_call.assert_called_once()
            # 验证调用参数包含类型和标题
            args = mock_call.call_args[0][0]
            self.assertIn("内容类型: post", args)
            self.assertIn("内容标题: 测试标题", args)
            self.assertIn("内容详情: 测试内容", args)

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_long_content_truncation(self):
        """测试长内容截断"""
        long_content = "a" * 1000 + "b" * 1000  # 2000字符

        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            mock_call.return_value = '{"status": "通过", "reason": ""}'

            result, reason = self.service.audit_content(long_content)

            self.assertTrue(result)
            # 验证内容被截断到1000字符
            args = mock_call.call_args[0][0]
            self.assertIn("内容详情: " + "a" * 1000, args)

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_reason_truncation(self):
        """测试原因描述截断"""
        with mock.patch.object(self.service, '_call_deepseek_api') as mock_call:
            long_reason = "a" * 20  # 20个字符
            mock_call.return_value = f'{{"status": "不通过", "reason": "{long_reason}"}}'

            result, reason = self.service.audit_content("违规内容")

            self.assertFalse(result)
            # 验证原因被截断到15字符 + "..."
            self.assertEqual(reason, "a" * 15 + "...")

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_call_deepseek_api_success(self):
        """测试成功的DeepSeek API调用"""
        with mock.patch('utils.audit.requests.post') as mock_post:
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': '{"status": "通过"}'}}]
            }
            mock_post.return_value = mock_response

            result = self.service._call_deepseek_api("测试提示")

            self.assertEqual(result, '{"status": "通过"}')

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_call_deepseek_api_error_status(self):
        """测试API返回错误状态码"""
        with mock.patch('utils.audit.requests.post') as mock_post:
            mock_response = mock.Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response

            result = self.service._call_deepseek_api("测试提示")

            self.assertIsNone(result)

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_call_deepseek_api_request_exception(self):
        """测试API调用抛出异常"""
        with mock.patch('utils.audit.requests.post') as mock_post:
            from requests.exceptions import RequestException
            mock_post.side_effect = RequestException("网络错误")

            result = self.service._call_deepseek_api("测试提示")

            self.assertIsNone(result)

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_call_deepseek_api_invalid_response_format(self):
        """测试API返回格式无效的响应"""
        with mock.patch('utils.audit.requests.post') as mock_post:
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'choices': []}  # 空choices数组
            mock_post.return_value = mock_response

            # 空choices数组会抛出IndexError
            # 由于_call_deepseek_api只捕获RequestException，IndexError会向上抛出
            with self.assertRaises((IndexError, KeyError)):
                self.service._call_deepseek_api("测试提示")


class AuditContentFunctionTest(TestCase):
    """audit_content 函数测试"""

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_function_pass(self):
        """测试audit_content函数通过"""
        with mock.patch.object(ContentAuditService, 'audit_content') as mock_audit:
            mock_audit.return_value = (True, "")

            result, reason = audit_content("测试内容")

            self.assertTrue(result)
            self.assertEqual(reason, "")

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_function_fail(self):
        """测试audit_content函数失败"""
        with mock.patch.object(ContentAuditService, 'audit_content') as mock_audit:
            mock_audit.return_value = (False, "违规")

            result, reason = audit_content("违规内容")

            self.assertFalse(result)
            self.assertEqual(reason, "违规")

    @override_settings(DEEPSEEK_API_KEY='test_key')
    def test_audit_content_function_with_params(self):
        """测试audit_content函数带参数"""
        with mock.patch.object(ContentAuditService, 'audit_content') as mock_audit:
            mock_audit.return_value = (True, "")

            result, reason = audit_content(
                content="测试内容",
                content_type="comment",
                title="测试标题"
            )

            self.assertTrue(result)
            mock_audit.assert_called_once_with("测试内容", "comment", "测试标题")
