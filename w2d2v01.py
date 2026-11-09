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
       # {"role": "system", "content": "你是严格的代码审查员，只说问题，不夸奖，每条不超过 20 字。"},
        {"role": "user", "content": "def add(a,b): return a+b"}
    ],
    stream=False
)
print(response.choices[0].message.content)