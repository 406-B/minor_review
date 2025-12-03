"""
DeepSeek API 测试脚本
用于测试 DeepSeek API 是否正常工作
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-1b99a2e2a88441239e2988bdda668e63",
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "system", "content": "你是一个专业的美食文案编辑，擅长撰写简洁、吸引人的菜品描述。"},
        {"role": "user", "content": "请为菜品「可乐鸡翅」撰写一段60-100字的描述，要求：1）突出菜品特色和口感；2）描述食材和烹饪方法；3）语言生动诱人。直接输出描述内容，不要有其他多余的话。"},
    ],
    stream=False,
    temperature=0.8
)

print(response.choices[0].message.content)