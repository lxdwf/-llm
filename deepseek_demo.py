from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "你是一名乐于助人的助手"},
        {"role": "user", "content": "你好"}
    ],
    stream=False
)
print(response.choices[0].message.content)
print(response.choices[0].message)       # 看它长什么样
print(response.choices[0].message.role)  # assistant 还是 user？
print(response.usage)
