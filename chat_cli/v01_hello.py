import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],   # 从环境变量读，绝不写死
    base_url="https://api.deepseek.com",     # 换地址：指向 DeepSeek
)

response = client.chat.completions.create(
    model="deepseek-flash",                  # 换脑子：快且便宜
    messages=[{"role": "user", "content": "用一句话解释什么是 API"}],
)

print(response.choices[0].message.content)