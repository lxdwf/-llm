from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

history_file = "chat_history.json"
# 初始默认对话历史
default_history = [{"role": "system", "content": "你是我的学习搭子，回答简短，术语必须用生活比喻解释。"}]

# 加载历史：文件不存在、文件为空、格式损坏，都自动用默认历史
try:
    with open(history_file, "r", encoding="utf-8") as f:
        history = json.load(f)
    # 额外校验：加载出来的必须是列表
    if not isinstance(history, list):
        history = default_history
except (FileNotFoundError, json.JSONDecodeError, TypeError):
    history = default_history


total = 0
while True:
    q = input("我：")
    if q in ("exit", "q"):
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print("✅ 对话已保存，程序退出")
        break
    history.append({"role": "user", "content": q})        # 1. 记下问题

    resp = client.chat.completions.create(model="deepseek-flash", messages=history)
    answer = resp.choices[0].message.content
    print("AI：", answer)

    history.append({"role": "assistant", "content": answer})  # 2. 记下它的回答

    total += resp.usage.total_tokens
    print(f"[本轮 {resp.usage.total_tokens} tokens｜累计 {total}]")

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)