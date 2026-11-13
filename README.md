# DeepSeek API 练习 · chat_cli

用 **OpenAI 官方 SDK** 调 DeepSeek，从「打印一句话」一路长到「带提示词库的结构化抽取工具」。

两周前我没调过任何大模型 API。这里记的是全过程，**包括踩过的坑**。

> **为什么用 OpenAI 的库调 DeepSeek？**
> DeepSeek 没有自己的 SDK，它把接口做成了 OpenAI 的形状。所以只需要换三处：
> `api_key`（换钥匙）、`base_url`（换地址）、`model`（换脑子）。
> 「兼容」的意思就是**外壳一样，地址不同**。

---

## ① 这是什么

| 文件 | 干什么 | 对应练习 |
| --- | --- | --- |
| `chat_cli/v01_hello.py` | 最小调用：发一句话，打印回答 | D1 |
| `chat_cli/prompt_loader.py` | 从 `prompts/*.md` 读提示词，剥掉版本注释 | D6 |
| `chat_cli/prompts/jd_parse.md` | 五段模板：把招聘 JD 抽成结构化 JSON | D6 |
| `chat_cli/prompts/resume_review.md` | 五段模板：给简历挑刺 | D6 |
| `chat_cli/prompts/explain_like_im_12.md` | 五段模板：把报错/文档讲成人话 | D6 |
| `chat_cli/w2d6_json.py` | 单次跑：用模板抽取一段真实 JD | D6 |
| `chat_cli/w2d6_ab.py` | **A/B 对比**：差提示词 vs 模板提示词，自动打分 | D6 |
| `w2d2v01.py` | 有/无 `system` 的对照实验 | D2 |
| `w2d2v03.py` | 流式输出（打字机效果） | D2 |
| `w2d3v02_json_id.py` | 最早的 JSON 抽取（提示词硬编码在代码里） | D3 |
| `w2d4_chat.py` | 多轮对话 CLI，每轮打印 token 消耗 | D4 |
| `w2v02.py` | 重试 + 指数退避 + 三种失败场景复现 | D5 |

**核心思路**：提示词和代码分离。改提示词只动 `.md`，代码一行不用碰。

---

## ② 怎么跑

### 1. 装依赖

```bash
pip install -r requirements.txt
```

Python 3.13 实测可用。依赖只有两个：`openai`（DeepSeek 兼容它）、`python-dotenv`。

### 2. 配 key（二选一）

去 [platform.deepseek.com](https://platform.deepseek.com) 申请 API key。

**方式 A · `.env` 文件（本仓库用这个）**

在仓库根目录建 `.env`：

```
DEEPSEEK_API_KEY=sk-你的key
```

**方式 B · 系统环境变量**

```bash
setx DEEPSEEK_API_KEY "sk-你的key"
```

> ⚠️ 改完**必须关掉终端重新开**，老终端读不到新变量。这是新手最容易卡住的一步。

### 3. 验证 key 读到了没有

```bash
python -c "import os;print(os.environ.get('DEEPSEEK_API_KEY','没读到'))"
```

打出 `sk-...` 才算成功。

### 4. 跑

```bash
python chat_cli/w2d6_json.py    # 单次抽取
python chat_cli/w2d6_ab.py      # A/B 对比 + 打分
```

> `.env` 已在 `.gitignore` 里，不会被提交。需要什么变量看 `.env.example`。

---

## ③ 我踩过的 6 个坑

这一节比功能介绍值钱，都是真撞过的。

### 坑 1 · `KeyError: 'DEEPSEEK_API_KEY'`

**现象**：程序一行没跑就崩。
**原因**：`os.environ["X"]` 取不到变量直接抛异常。常见原因是 `setx` 之后没重开终端。
**解决**：关终端重开；或者用 `.env` + `load_dotenv()`。
**为什么故意用 `[]` 不用 `.get()`**：`.get()` 取不到返回 `None`，然后 SDK 抛一段通用英文报错，你还得猜是哪个变量没配。`[]` 直接告诉你缺哪个。**错得早，错得清楚。**

### 坑 2 · `deepseek-chat` 已经不能用了

**现象**：照着网上教程写 `model="deepseek-chat"`，报模型不存在。
**原因**：这个模型名已在 **2026-07-24 弃用**。现在用 `deepseek-flash`（快、便宜）或 `deepseek-v4-pro`。
**教训**：这个领域的中文教程大量过期。我搜过 5 篇"大模型 API 入门"，**3 篇代码里还是 `deepseek-chat`**。以官方文档的参数表为准。

### 坑 3 · 调 `temperature` 完全没反应

**现象**：`temperature` 从 0 改到 1.5，输出一模一样。
**原因**：**思考模式默认开启，开启时 `temperature` 不生效。**
**解决**：先关掉思考模式再调参：

```python
extra_body={"thinking": {"type": "disabled"}}
```

关掉之后 `temperature=0` 连跑 3 次结果几乎一致，改到 1.5 就开始飘了。**这不是玄学，是参数有没有生效的问题。**

### 坑 4 · 流式输出里 `content` 是 `None`

**现象**：`print(chunk.choices[0].delta.content)` 打出一堆 `None`。
**原因**：流式是一片一片给的，首片（只有 role）和尾片（只有结束标记）没有正文；而且**非流式叫 `message`，流式叫 `delta`**，不是同一个字段。
**解决**：

```python
for chunk in stream:
    text = chunk.choices[0].delta.content
    if text:                      # 判空，否则会打出 None
        print(text, end="", flush=True)
```

### 坑 5 · JSON 模式只保证「是合法 JSON」，不保证「是你要的字段」

**现象**：`json.loads` 成功了，但 `data["我缺"]` 报 `KeyError`。
**原因**：`response_format={"type": "json_object"}` 只保证输出能被解析，**字段名它自己定**。
实测：提示词只写「抽取信息输出JSON。」时，模型给出的是 `title` / `location` / `salary` 这种英文 key。
**解决**：在提示词的「输出格式」段**写死 key 名并给样例**。这就是「prompt 的输出格式段 = 代码接口定义」。

### 坑 6 · `FileNotFoundError`：代码写的目录名和磁盘上不一样

**现象**：`No such file or directory: '...\chat_cli\prompts\jd_parse.md'`
**原因**：代码里拼的是 `prompts`，磁盘上那个文件夹叫 `prompt_v01`。
**解决**：`mv` 改名。顺带学到一件好事：`Path(__file__).parent` 拼出来是**绝对路径**，报错里直接把完整路径打给你看，一眼能对比出差异。如果写相对路径，报错只显示 `'prompts/jd_parse.md'`，你还得自己想它在哪个目录下找。

---

## ④ 参数实验结论

| 实验 | 怎么做的 | 结论 |
| --- | --- | --- |
| **`system` 人设的威力** | 同一段 `def add(a,b): return a+b`，一次带 `system`（"严格的代码审查员，只说问题不夸奖，每条 20 字内"），一次不带 | **输出是两种完全不同的东西**：带 system 只列问题、极简；不带 system 长篇讲解还带夸奖。**同一份代码，人设直接决定输出的用途** |
| **`temperature` × 思考模式** | 关思考模式，`temperature=0` 连跑 3 次 → 改 `1.5` 再跑 3 次 | `0` 的 3 次几乎一致；`1.5` 的 3 次开始飘。**温度只在关掉思考模式后才生效** |
| **流式 vs 非流式** | 同一个问题分别用 `stream=False` / `stream=True` | 非流式等全部生成完一次性返回（`message`）；流式逐字返回（`delta`），首尾分片可能为空。**体验好，但要处理空值** |

> ⬜ 待补：开思考模式 + `temperature=1.5` 再跑 3 次做对照，把"温度无效"这半步的亲测证据补齐。

---

## ⑤ 花了多少钱

⬜ 待填。

**怎么查**：登录 [platform.deepseek.com](https://platform.deepseek.com) → 用量统计。

**更精确的做法**：在代码里读每次调用的 token 数，自己累加（见 `w2d4_chat.py`）：

```python
total += resp.usage.total_tokens
print(f"[本轮 {resp.usage.total_tokens} tokens｜累计 {total}]")
```

⚠️ **一个容易忽略的事实：多轮对话越聊越贵。** 因为服务器不记事，每轮都要把**整个 history 重发一遍**。聊到第 10 轮，第 1 句也还在里面占 token。
（这也是后面要做 RAG 的原因：不能把整本书塞进 messages，只能先检索出最相关的几段。）

---

## ⑥ 提示词 A/B 对比（同一个 JD，只换 `system`）

| | 提示词 | 得分 | 输出 |
| --- | --- | --- | --- |
| **BAD** | `"抽取信息输出JSON。"` | **1/4** | `{"title":"AI应用开发实习生","location":"长沙","skills":[...],"salary":"150-200/天"}` |
| **GOOD** | `prompts/jd_parse.md` 五段模板 | **4/4** | `{"硬性要求":[...],"我满足":[...],"我缺":[...],"一句话结论":"..."}` |

**四项打分表**（每项 1 分）：① JSON 可解析 ② 四个字段名齐全 ③「我缺」说中真实短板 ④ 结论明确。

**结论**：BAD 那 1 分只是「输出是合法 JSON」。它**内容抽得没错甚至更全**（连薪资都抽了），但字段名是自己发明的英文 key，**代码根本没法用**。

> 丢分不在"能力"，在"形状"。**所以提示词里最不能省的一段，是「输出格式」。**

复现：

```bash
python chat_cli/w2d6_ab.py
```

---

## 目录结构

```
github.api/
├── README.md
├── requirements.txt
├── .env.example            ← 只写变量名，不含真 key
├── .gitignore              ← 挡 .env / __pycache__ / .venv
├── chat_cli/
│   ├── v01_hello.py        ← D1 最小调用
│   ├── prompt_loader.py    ← D6 读提示词
│   ├── prompts/            ← D6 三份五段模板
│   ├── w2d6_json.py        ← D6 单次抽取
│   └── w2d6_ab.py          ← D6 A/B 打分
└── (根目录) w2d2*.py w2d3*.py w2d4_chat.py w2v0*.py   ← 前期按天练习的脚本，保留作过程记录
```

---

## 下一步

- [ ] 补 ⑤ 的真实花费数字
- [ ] 补 ④ 里「开思考模式 temperature 无效」的对照实验
- [ ] 仓库改名（`github.api` 太泛，改成 `deepseek-api-practice`）
- [ ] 进 RAG：在 JSON 抽取 + 多轮对话的基础上加检索
