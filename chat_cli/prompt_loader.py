from pathlib import Path
import re

PROMPT_DIR = Path(__file__).parent / "prompts"      # ①


def load_prompt(name: str) -> str:                 # ②
    """读 prompts/<name>.md 全文，去掉 <!-- --> 注释"""
    text = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")   # ③
    return re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()  