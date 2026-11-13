"""W2-D6 · Prompt A/B 对比

同一段 JD，只换 system 提示词，看输出质量差多少。
BAD  = 一句话指令
GOOD = prompts/jd_parse.md 五段模板
"""
from prompt_loader import load_prompt
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],   # 缺配置立刻 KeyError
    base_url="https://api.deepseek.com",
)

# 待测的 JD：两组用同一份，变量只留 system 一个
JD = """AI应用开发实习生，长沙，本科，熟悉 Python，
了解 LangChain/Dify，有 RAG 项目经验优先，薪资 150-200/天。"""

# 要对比的两份提示词，装在字典里：key 是标签，value 是提示词正文
PROMPTS = {
    "BAD": "抽取信息输出JSON。",                 # 一句话，没有角色/上下文/字段名
    "GOOD": load_prompt("jd_parse"),           # 五段模板，从文件读
}


def ask(system: str):
    """发一次请求。成功返回 dict，失败返回 None"""
    resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": JD},
        ],
        response_format={"type": "json_object"},          # 强制输出 JSON
        extra_body={"thinking": {"type": "disabled"}},    # 关思考，排除干扰
        max_tokens=800,
    )
    text = resp.choices[0].message.content
    if not text or not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def score(data):
    """四项各 1 分，返回 (总分, 逐项结果)"""
    if not isinstance(data, dict):
        return 0, ["✗ 连 JSON 都没解析出来"]

    detail = []

    # 第 1 项：能解析成 dict
    detail.append("✓ JSON 可解析")

    # 第 2 项：四个字段名齐全（这批字段名由 prompt 的输出格式段决定）
    need = {"硬性要求", "我满足", "我缺", "一句话结论"}
    if need <= set(data.keys()):
        detail.append("✓ 四个字段齐全")
    else:
        detail.append(f"✗ 字段缺失，实际只有：{list(data.keys())}")

    # 第 3 项：「我缺」说中了真实短板
    gaps = str(data.get("我缺", ""))
    if any(k in gaps for k in ("RAG", "LangChain", "Dify", "项目", "实习")):
        detail.append("✓ 说中真实短板")
    else:
        detail.append(f"✗ 短板说得含糊：{gaps[:40]}")

    # 第 4 项：结论明确，不是「看个人情况」
    concl = str(data.get("一句话结论", ""))
    if any(k in concl for k in ("可投", "不建议", "建议投")):
        detail.append("✓ 结论明确")
    else:
        detail.append(f"✗ 结论含糊：{concl[:40]}")

    return sum(1 for d in detail if d.startswith("✓")), detail


# ---- 主流程：两组跑一遍，各自打分 ----
results = {}
for label, system in PROMPTS.items():
    print("=" * 60)
    print(f"【{label}】提示词：{system[:40].strip()}...")
    data = ask(system)
    total, detail = score(data)
    results[label] = total

    print(f"得分：{total}/4")
    for line in detail:
        print("  " + line)
    print("原始输出：")
    print(json.dumps(data, ensure_ascii=False, indent=2))

print("=" * 60)
print(f"汇总：BAD {results.get('BAD', 0)}/4 ｜ GOOD {results.get('GOOD', 0)}/4")
