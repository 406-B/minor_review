"""
DeepSeek API 测试脚本
用于测试 DeepSeek API 是否正常工作
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-1b99a2e2a88441239e2988bdda668e63",
    base_url="https://api.deepseek.com")

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

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "user", "content": f"你是一个审核员，{AUDIT_PROMPT_TEMPLATE.format(content_type='general', title='', content='习近平是中国的领导人')}"},
    ],
    stream=False,
    temperature=0.8
)

print(response.choices[0].message.content)