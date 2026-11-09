from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

history = [{"role": "system", "content": "你是我的学习搭子，回答简短，术语必须用生活比喻解释。"}]

while True:
    q = input("我：")
    if q in ("exit", "q"):
        break
    history.append({"role": "user", "content": q})        # 1. 记下问题

    resp = client.chat.completions.create(model="deepseek-flash", messages=history)
    answer = resp.choices[0].message.content
    print("AI：", answer)

    history.append({"role": "assistant", "content": answer})  # 2. 记下它的回答
len(history)