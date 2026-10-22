# -*- coding: utf-8 -*-
"""
费曼实验课 · 千问评价代理（服务端）
- 服务端持有 DASHSCOPE_API_KEY，绝不下发前端
- 网关：token-plan.maas.qianwenaiapi.com/compatible-mode/v1
- 主评 qwen3.7-plus，边界复评 qwen3.7-max
- 复用已验证 rubric@1.0（见 evaluation/system_prompt.md）
"""
import os
import json
import urllib.request
import urllib.error

PROMPT_VERSION = "fe-rubric@1.1"
DEFAULT_BASE_URL = "https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1"
PRIMARY_MODEL = "qwen3.7-plus"
RECHECK_MODEL = "qwen3.7-max"

# 与 evaluation/system_prompt.md 保持一致
SYSTEM_PROMPT = """你是一名严格但鼓励性的「费曼学习法」评审教练。你扮演一个完全不懂该领域的外行听众，唯一目标是检验用户是否真的理解了某个概念——而不是检验他背得多像教科书。

# 评分维度（每项满分 25，总分 100）
1. 简洁性（讲给小孩听得懂）：是否避免了未解释的术语/行话？句子是否直白、一个意思只说一遍？外行能否不卡壳读完？
2. 完整性（概念讲通）：是否覆盖了「是什么 / 为什么 / 怎么用（含举例）」三要素？
3. 逻辑性（讲得通）：有没有自相矛盾、循环论证、因果倒置？因果链是否清晰可追？
4. 比喻力（原创类比）：是否用生活化、外行能秒懂的类比来解释？类比是否贴切（不牵强）？

# 行为锚定（每维度按 0/5/10/15/20/25 给分）
- 25 优秀：完全满足该维度要求
- 20 良好：基本满足，有亮眼之处
- 15 合格：满足主体，但有可指出的瑕疵
- 10 部分缺失：只覆盖一半或一个明显漏洞
- 5 明显不足：几乎没满足
- 0 完全缺失/错误：该维度完全没体现或事实错误

# 等级映射（良为及格线）
- 优 85–100（及格，直接结业）
- 良 70–84（及格；70–74 时请在 progress_note 提示「再修一轮可冲优」）
- 中 50–69（不及格，继续修正）
- 差 0–49（不及格，建议先补课后重来）
- 若总分落在 68–72，请在 boundary_recheck 置 true（下游会自动二次评价取中）。

# 输出要求（只输出下面的 JSON，前后不要加任何解释或 markdown 代码块）
{
  "overall_score": 0,
  "grade": "优|良|中|差",
  "summary": "一句话外行视角总评",
  "dimensions": {
    "simplicity":   {"score": 0, "comment": "该维度具体评价"},
    "completeness": {"score": 0, "comment": "该维度具体评价"},
    "logic":        {"score": 0, "comment": "该维度具体评价"},
    "analogy":      {"score": 0, "comment": "该维度具体评价"}
  },
  "card_points": [
    {
      "quote": "引用用户原文片段（必须来自原文，不得编造）",
      "issue": "哪里讲不通 / 为什么讲不通",
      "hint_direction": "改进方向，给方向不给答案（例：可以想想这个东西解决了什么麻烦）",
      "structure_hint": ["及格的重讲至少要覆盖的要点一", "要点二", "要点三（2-3 条，只说要覆盖什么，不写内容）"],
      "starter_line": "一句起头示范（只给第一句怎么开口，绝不展开成解释）"
    }
  ],
  "progress_note": "与上轮对比的进步点/退步点；首轮可给整体印象，并标注 prompt_version: fe-rubric@1.1",
  "boundary_recheck": false
}

# 分层揭示（三个层级的提示，严禁混淆）
为每个 card_point 再产出两个字段，逐级递进，但**任何一级都不得写出概念的正确答案**：
- structure_hint：2-3 条「骨架」。只说明一个及格的重讲必须覆盖哪几个角度，例如「先说清它解决什么麻烦」「再给一个日常场景」。
  禁止写出定义、机制、数据或结论——那是用户该自己组织的内容。
- starter_line：一句话起头示范。只帮用户把第一句说出口（如「它就像……」「你可以想象……」），
  长度不超过 40 字，**绝不能顺着写出第二句或完整解释**。

# 铁律（务必遵守）
1. 绝不给出概念的现成答案或标准解释。hint_direction / structure_hint / starter_line 三层都只能给「方向、骨架、起头」，
   绝不能写出正确定义、机制或完整阐述。保留用户的生成效应。
2. card_points 的 quote 必须引用用户原文片段，不得凭空编造。
3. 以「外行有没有听懂」为唯一标准。用户用了术语但没解释，简洁性/逻辑性减分。
4. 语气像教练：先肯定可取之处，再指出卡点，鼓励重讲。
5. 输出只有 JSON，不要任何额外文字。"""


def _grade_of(score):
    if score >= 85:
        return "优"
    if score >= 70:
        return "良"
    if score >= 50:
        return "中"
    return "差"


def _call_model(model, system_prompt, user_content, api_key, base_url, temperature=0.2):
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode("utf-8"))
    content = resp["choices"][0]["message"]["content"]
    start, end = content.find("{"), content.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("模型未返回 JSON")
    return json.loads(content[start:end])


def _call(model, user_content, api_key, base_url):
    return _call_model(model, SYSTEM_PROMPT, user_content, api_key, base_url)


def evaluate(topic, background, user_text, prev_grade=None, api_key=None, base_url=None):
    """返回评价 dict；失败抛异常由调用方处理。"""
    api_key = api_key or os.environ.get("DASHSCOPE_API_KEY", "")
    base_url = base_url or os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL)
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY")
    user_content = (
        f"课题：{topic}\n一句话背景：{background}\n"
        + (f"（上一轮等级：{prev_grade}，本轮请对比进步点）\n" if prev_grade else "")
        + f"\n用户的裸讲（请评价）：\n{user_text}"
    )
    d = _call(PRIMARY_MODEL, user_content, api_key, base_url)
    score = d.get("overall_score", 0)
    if isinstance(score, int) and 68 <= score <= 72:
        try:
            d2 = _call(RECHECK_MODEL, user_content, api_key, base_url)
            for k in d["dimensions"]:
                a = d["dimensions"][k]["score"]
                b = d2["dimensions"][k]["score"]
                d["dimensions"][k]["score"] = round((a + b) / 2)
            d["overall_score"] = sum(v["score"] for v in d["dimensions"].values())
            d["grade"] = _grade_of(d["overall_score"])
            d["boundary_recheck"] = True
            note = d.get("progress_note", "")
            d["progress_note"] = (note + " [边界分自动二次评价取中]").strip()
        except Exception:
            d["boundary_recheck"] = "recheck-failed"
    d["prompt_version"] = PROMPT_VERSION
    d["card_points"] = _normalize_card_points(d.get("card_points"))
    return d


def _normalize_card_points(cps):
    """保证每个卡点都带 structure_hint / starter_line 字段（模型漏给时降级为空）。"""
    if not isinstance(cps, list):
        return []
    out = []
    for c in cps:
        if not isinstance(c, dict):
            continue
        sh = c.get("structure_hint")
        if isinstance(sh, str):
            sh = [sh] if sh.strip() else []
        if not isinstance(sh, list):
            sh = []
        c = dict(c)
        c["structure_hint"] = [str(x).strip() for x in sh if str(x).strip()][:3]
        c["starter_line"] = str(c.get("starter_line") or "").strip()
        out.append(c)
    return out


# ---------- 结业后：标准示范（方案 A） ----------
# 仅在用户已拿到「良」及以上、自己讲通过之后才调用。
# 此时训练目的已达成，给示范用于对照提升，不再破坏生成效应。
DEMO_SYSTEM_PROMPT = """你是一名擅长把复杂概念讲给外行听的科普作者。用户已经用自己的话把这个概念讲通了，现在请你给出一份「标准示范」，供他对照参考。

# 要求
1. 讲给完全不懂的外行（假想听众是初中生）听，不用任何未解释的术语。
2. 结构：先用一句大白话说清「它是什么」→ 再用一个生活类比 → 再说「为什么/怎么起作用」→ 最后说「怎么用得上」。
3. 长度 250-350 字，段落短，句子短。
4. 必须包含一个原创、贴切的生活类比。
5. 结尾附一条「避坑提醒」：讲这个概念时最容易说错的一点。

# 输出（只输出 JSON）
{
  "title": "概念名",
  "one_liner": "一句话大白话定义（30 字内）",
  "analogy": "生活类比（一句话）",
  "demo_text": "标准示范正文，250-350 字，可含换行",
  "pitfall": "避坑提醒：讲这个概念最容易说错的一点"
}

只输出 JSON，不要任何额外文字。"""


def demonstrate(topic, background, user_text=None, api_key=None, base_url=None):
    """结业后生成标准示范；失败抛异常由调用方处理。"""
    api_key = api_key or os.environ.get("DASHSCOPE_API_KEY", "")
    base_url = base_url or os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL)
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY")
    content = (
        f"课题：{topic}\n一句话背景：{background}\n\n"
        f"用户自己的讲述（仅供你了解他关注的角度，不必评价）：\n{user_text or '（无）'}\n\n"
        "请给出这个课题的标准示范。"
    )
    d = _call_model(PRIMARY_MODEL, DEMO_SYSTEM_PROMPT, content, api_key, base_url, temperature=0.5)
    d["prompt_version"] = "fe-demo@1.0"
    return d


if __name__ == "__main__":
    import sys
    # 简单自检：python evaluator.py "课题" "背景" "裸讲"
    if len(sys.argv) >= 4:
        print(json.dumps(evaluate(sys.argv[1], sys.argv[2], sys.argv[3]),
                         ensure_ascii=False, indent=2))
