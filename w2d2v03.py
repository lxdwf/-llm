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
        {"role": "user", "content": "从 1 数到 20，每行一个"}
    ],
    stream=True,
)
for chunk in response:
    text = chunk.choices[0].delta.content
    if text:
        print(text, end="", flush=True)