"""
内容审核服务
使用 DeepSeek API 对用户提交的内容进行审核
"""
import requests
import json
import logging
from typing import Dict, Tuple, Optional
from django.conf import settings
# import time

logger = logging.getLogger(__name__)


class ContentAuditService:
    """内容审核服务"""

    # DeepSeek API 配置
    API_BASE_URL = "https://api.deepseek.com/v1"
    MODEL = "deepseek-chat"

    # 审核提示词模板
    AUDIT_PROMPT_TEMPLATE = """
请审核以下用户提交的内容是否符合社区规范。社区规范包括：
1. 不包含暴力、色情、赌博等违法内容
2. 不包含辱骂、人身攻击等不文明语言
3. 不包含广告、垃圾信息等
4. 不包含政治相关内容
5. 不包含虚假信息、谣言等
6. 不包括任何谐音、隐晦表达等变相违规内容

请严格审核内容，如果发现任何违规情况，请明确指出违规类型和具体原因。
如果内容合规，请回复"通过"。

内容类型: {content_type}
内容标题: {title}
内容详情: {content}

请以JSON格式回复：
{{"status": "通过"|"不通过", "reason": "原因描述（如果不通过）"}}
"""

    def __init__(self):
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not configured, audit service will not work")

    def audit_content(self, content: str, content_type: str = "general",
                     title: str = "") -> Tuple[bool, str]:
        """
        审核内容

        Args:
            content: 要审核的内容
            content_type: 内容类型 (post/comment/tag/review等)
            title: 内容标题 (可选)

        Returns:
            Tuple[bool, str]: (是否通过, 原因描述)
        """
        logger.info(f"[审核开始] 类型={content_type}, 标题={title}, 内容={content[:1000]}")
        
        if not self.api_key:
            logger.warning("[审核失败] 未配置DEEPSEEK_API_KEY")
            return False, "审核服务未配置"

        try:
            # 构建提示词
            prompt = self.AUDIT_PROMPT_TEMPLATE.format(
                content_type=content_type,
                title=title,
                content=content[:1000]  # 限制内容长度
            )
            
            # 调用 DeepSeek API
            logger.info(f"[审核] 调用DeepSeek API...")
            response = self._call_deepseek_api(prompt)

            if not response:
                logger.error("[审核失败] 未能从DeepSeek API获取响应")
                return False, "审核服务无响应"

            logger.info(f"[审核] API响应: {response[:200]}")

            # 解析响应
            result = self._parse_response(response)
            if not result:
                logger.error(f"[审核失败] 无法解析API响应: {response}")
                return False, "审核结果解析失败"

            logger.info(f"[审核] 解析结果: {result}")

            status = result.get('status', '不通过')  # 默认不通过
            reason = result.get('reason', '审核结果格式错误')
            
            is_passed = status == "通过"
            
            # 限制原因长度
            full_reason = reason
            if reason and len(reason) > 15:
                reason = reason[:15] + "..."

            if is_passed:
                logger.info(f"[审核通过] 类型={content_type}, 标题={title}")
            else:
                logger.warning(f"[审核不通过] 类型={content_type}, 标题={title}, 原因={full_reason}")

            return is_passed, reason

        except Exception as e:
            logger.error(f"[审核异常] 类型={content_type}, 错误={str(e)}", exc_info=True)
            return False, "审核服务异常"

    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """调用 DeepSeek API"""
        try:
            url = f"{self.API_BASE_URL}/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.1  # 降低随机性，提高一致性
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return content.strip()
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            logger.error(f"Request to DeepSeek API failed: {str(e)}")
            return None

    def _parse_response(self, response: str) -> Optional[Dict]:
        """解析 API 响应"""
        try:
            # 尝试直接解析 JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果不是纯 JSON，尝试提取 JSON 部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            logger.warning(f"Could not parse response as JSON: {response}")
            return None


# 全局审核服务实例
audit_service = ContentAuditService()


def audit_content(content: str, content_type: str = "general",
                 title: str = "") -> Tuple[bool, str]:
    """
    审核内容的便捷函数

    Args:
        content: 要审核的内容
        content_type: 内容类型
        title: 内容标题

    Returns:
        Tuple[bool, str]: (是否通过, 原因描述)
    """
    return audit_service.audit_content(content, content_type, title)
