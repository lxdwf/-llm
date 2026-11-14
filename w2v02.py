from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import time


load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def extract_json(client, jd, system, retries=3):
    """
    从 JD 中抽取结构化 JSON，失败自动重试
    :param client: OpenAI 客户端实例
    :param jd: 待抽取的原文
    :param system: 系统提示词
    :param retries: 最大重试次数
    :return: 解析成功的 dict；全部失败返回 None
    """
    for i in range(retries):
        # 第2次重试开始，自动加强prompt约束
        current_system = system
        if i >= 1:
            current_system = system + "\n严格注意：只输出纯JSON，禁止任何解释、前言、注释，输出必须可以直接被json.loads解析。"

        # 第2次重试开始，自动加大token上限，避免截断
        current_max_tokens = 800
        if i >= 1:
            current_max_tokens = 1500

        # 1. 请求层兜底
        try:
            resp = client.chat.completions.create(
                model="deepseek-flash",
                messages=[
                    {"role": "system", "content": current_system},
                    {"role": "user", "content": jd}
                ],
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
                max_tokens=current_max_tokens,
                timeout=60,
            )
        except Exception as e:
            print(f"[第{i+1}次] 请求失败：{type(e).__name__}: {e}")
            # 第一次失败不等待，从第二次开始指数退避
            if i > 0:
              time.sleep(2 ** i + random.uniform(0, 1)) 
            continue

        # 2. 空内容兜底（服务端清洗后只剩空格）
        text = resp.choices[0].message.content
        clean_text = text.strip() if text else ""
        if not clean_text:
            print(f"[第{i+1}次] 返回空内容（已被清洗为空格），重试")
            if i > 0:
                time.sleep(2 ** i)
            continue

        # 3. 解析层兜底
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            finish_reason = resp.choices[0].finish_reason
            reason_desc = "token截断" if finish_reason == "length" else "格式错误"
            print(f"[第{i+1}次] JSON解析失败({reason_desc})：{e}｜原文前80字：{clean_text[:80]}")
            if i > 0:
                time.sleep(2 ** i)

    print("全部重试失败，返回 None")
    return None

# ============== 通用的弱约束提示词（更容易触发错误） ==============
bad_system = "抽取信息输出JSON。"

# ============== 测试场景 1：完全无效的输入，触发「空内容（全是空格）」 ==============
print("====== 测试1：完全无关的输入，模型输出自然语言，被清洗成空格 ======")
test_jd_1 = "今天中午吃什么好吃的？"
result1 = extract_json(client, test_jd_1, bad_system, retries=3)
print("最终结果：", result1)
print("\n" + "="*60 + "\n")

# ============== 测试场景 2：强制极小 token，触发「截断导致解析失败」 ==============
print("====== 测试2：token额度极小，JSON写一半被掐断 ======")
# 这里我们临时改小max_tokens，强制截断
def extract_json_truncate(client, jd, system, retries=3):
    for i in range(retries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-flash",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": jd}],
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
                max_tokens=30,  # 故意给极小额度，必截断
                timeout=60,
            )
        except Exception as e:
            print(f"[第{i+1}次] 请求失败：{e}")
            continue

        text = resp.choices[0].message.content
        clean_text = text.strip()
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            print(f"[第{i+1}次] 解析失败，finish_reason={resp.choices[0].finish_reason}")
            print(f"    半截内容：{repr(text)}")

test_jd_2 = "招聘Java开发，北京，薪资20k，要求会SpringBoot、MySQL"
result2 = extract_json_truncate(client, test_jd_2, "输出JSON，包含岗位、城市、薪资、技能", retries=2)
print("最终结果：", result2)
print("\n" + "="*60 + "\n")

# ============== 测试场景 3：模拟请求层错误（故意写错地址） ==============
print("====== 测试3：请求层错误（网络/地址错误） ======")
bad_client = OpenAI(
    api_key="sk-fake-key-123",
    base_url="https://api.deepseek.com"  # 密钥是错的，会触发鉴权失败
)
test_jd_3 = "随便什么内容"
result3 = extract_json(bad_client, test_jd_3, "输出JSON", retries=2)
print("最终结果：", result3)
