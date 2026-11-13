import json 
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

jd = """AI应用开发实习生，长沙，本科，熟悉 Python，
了解 LangChain/Dify，有 RAG 项目经验优先，薪资 150-200/天。"""

system = """你是信息抽取器。用户给一段招聘 JD，你只输出 json，不要解释。
输出格式样例：
{"岗位": "AI应用开发实习生", "城市": "长沙", "技能": ["Python", "Dify"], "薪资": "150-200/天"}"""

resp = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "system", "content": system}, {"role": "user", "content": jd}],
    response_format={"type": "json_object"},   # 强制 JSON
    extra_body={"thinking": {"type": "disabled"}}, # 关闭思考，避免思考文本干扰
    max_tokens=800,   
)

text = resp.choices[0].message.content
if not text or not text.strip():               # 可能只回一堆空格
    print("返回空 JSON，重试一次")
else:
    data = json.loads(text)
    #print(data["技能"])
    print(data["岗位"])