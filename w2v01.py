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
    messages=[{"role": "user", "content": "说三个字"}],
)
print(type(response))
print(response.choices[0].message)      # 看它长什么样
print(response.choices[0].message.content) 
print(response.usage)
print(response.choices[0].finish_reason)