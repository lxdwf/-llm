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
    messages=[{"role": "user", "content": "随便说一句鼓励我的话"} ],
    temperature=1.5,
  extra_body={"thinking": {"type": "disabled"}},
    stream=False
)
print(response.choices[0].message.content)
