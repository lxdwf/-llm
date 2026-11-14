"""对比实验：正常结束 vs 被 max_tokens 掐断，看 finish_reason 怎么变。

这是 Q1 的实证：max_tokens 太低是"病因"，finish_reason 才是"诊断结果"。
运行：python w2d7_finish_reason.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# .env 在仓库根目录，本文件在 chat_cli/ 下 → 往上一级找
load_dotenv(Path(__file__).parent.parent / ".env")

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

QUESTION = "用三句话说明 Python 列表是什么，每句都要完整。"


def run(max_tokens: int) -> None:
    resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": QUESTION}],
        max_tokens=max_tokens,                              # 唯一的变量
        extra_body={"thinking": {"type": "disabled"}},       # 关思考，免得推理 token 占满预算
    )

    choice = resp.choices[0]                                 # 第 1 个候选
    text = choice.message.content or ""                      # 可能为 None，先兜底

    print(f"max_tokens={max_tokens:<4}  finish_reason={choice.finish_reason:<6} "
          f"completion_tokens={resp.usage.completion_tokens:<4} 正文长度={len(text)}")
    print(f"    正文结尾 30 字：{text[-30:]!r}")
    print()


if __name__ == "__main__":
    run(20)      # 故意给不够 → 预期 length
    run(800)     # 给够     → 预期 stop
