from prompt_loader import load_prompt
import json 
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],   # 缺配置立刻 KeyError，别带着 None 去请求
    base_url="https://api.deepseek.com"
)

jd = """AI应用开发实习生，长沙，本科，熟悉 Python，
了解 LangChain/Dify，有 RAG 项目经验优先，薪资 150-200/天。"""

system = load_prompt("jd_parse")
print("读到的 prompt 前 50 字：", system[:50])

resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "system", "content": system}, {"role": "user", "content": jd}],
    response_format={"type": "json_object"},   # 强制 JSON
    extra_body={"thinking": {"type": "disabled"}}, # 关闭思考，避免思考文本干扰
    max_tokens=800,   
)

text = resp.choices[0].message.content
if not text or not text.strip():               # 可能只回一堆空格
    print("返回空内容，停止。重试逻辑 w2v02.py 里已经练过，D6 不再重复")
    raise SystemExit(1)                        # 直接退出，别让下面带着 None 继续跑

data = json.loads(text)
print(json.dumps(data, ensure_ascii=False, indent=2))   # 四个字段全打出来，A/B 打分要用