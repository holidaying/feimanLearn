#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
费曼实验课 · 评价 Prompt 试跑脚本（Prompt v1.0）
真实调用通义千问 qwen-plus 验证评分准不准、稳不稳。

用法：
  set DASHSCOPE_API_KEY=你的key
  python evaluate.py            # 跑 3 个内置测试用例（预期 优/中/差 梯度）
  python evaluate.py --debug     # 额外打印原始返回内容

说明：
- 走 DashScope OpenAI 兼容端点，仅用标准库 urllib，零依赖。
- temperature=0.2；若总分落在 68-72 边界，自动二次评价（qwen-max）取中。
"""
import os
import sys
import json
import urllib.request
import urllib.error

# 兼容 OpenAI 的 chat/completions 端点；可用环境变量 DASHSCOPE_BASE_URL 覆盖
DEFAULT_BASE_URL = "https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1"
URL = os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/chat/completions"
PRIMARY_MODEL = "qwen3.7-plus"
RECHECK_MODEL = "qwen3.7-max"
PROMPT_VERSION = "fe-rubric@1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEM_PROMPT = open(os.path.join(HERE, "system_prompt.md"), encoding="utf-8").read()


def grade_of(score):
    if score >= 85:
        return "优"
    if score >= 70:
        return "良"
    if score >= 50:
        return "中"
    return "差"


def _call(model, user_content):
    body = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode("utf-8"))
    content = resp["choices"][0]["message"]["content"]
    start, end = content.find("{"), content.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("模型未返回 JSON：" + content[:200])
    return json.loads(content[start:end])


def evaluate(topic, background, user_text, debug=False):
    user_content = f"课题：{topic}\n一句话背景：{background}\n\n用户的裸讲（请评价）：\n{user_text}"
    try:
        d = _call(PRIMARY_MODEL, user_content)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode("utf-8")[:600]}
    except Exception as e:  # noqa
        return {"error": str(e)}

    if debug:
        d["_raw"] = user_content
    # 边界二次评价取中
    score = d.get("overall_score", 0)
    if isinstance(score, int) and 68 <= score <= 72:
        try:
            d2 = _call(RECHECK_MODEL, user_content)
            for k in d["dimensions"]:
                a = d["dimensions"][k]["score"]
                b = d2["dimensions"][k]["score"]
                d["dimensions"][k]["score"] = round((a + b) / 2)
            d["overall_score"] = sum(v["score"] for v in d["dimensions"].values())
            d["grade"] = grade_of(d["overall_score"])
            d["boundary_recheck"] = True
            note = d.get("progress_note", "")
            d["progress_note"] = (note + " [边界分自动二次评价取中]").strip()
        except Exception:
            d["boundary_recheck"] = "recheck-failed"
    return d


def pretty(d):
    if "error" in d:
        return "  [ERR] " + d["error"]
    lines = []
    lines.append(f"  总分 {d.get('overall_score')} · 等级 {d.get('grade')} · 边界复评={d.get('boundary_recheck')}")
    lines.append(f"  外行总评：{d.get('summary')}")
    for k, label in [("simplicity", "简洁性"), ("completeness", "完整性"),
                     ("logic", "逻辑性"), ("analogy", "比喻力")]:
        v = d["dimensions"][k]
        lines.append(f"   · {label} {v['score']:>2}/25 — {v['comment']}")
    cps = d.get("card_points", [])
    lines.append(f"  卡点 {len(cps)} 处：")
    for cp in cps:
        lines.append(f"     - 原文「{cp['quote']}」→ {cp['issue']}")
        lines.append(f"       方向：{cp['hint_direction']}")
    lines.append(f"  备注：{d.get('progress_note')}")
    return "\n".join(lines)


CASES = [
    {
        "tag": "预期 优",
        "topic": "通货膨胀",
        "background": "经济学概念，指整体物价水平持续上涨、货币购买力下降。",
        "text": (
            "通货膨胀简单说就是钱变得不值钱了。比如去年 100 块能买 10 个包子，今年同样的包子要 12 块，"
            "那就是物价涨了、钱毛了。它为什么发生？最常见的原因是市场上的钱变多了——比如央行多印钞、"
            "或者大家贷款更容易，钱多了但东西没变多，每个东西对应的价格自然就上去了。怎么用这个知识？"
            "新闻说 CPI 涨了，你就知道手里的现金在悄悄缩水，长期全放活期其实是在亏。打个比方，"
            "通货膨胀就像往一锅粥里不断加水，粥的总量看着多了，但每一勺里的米反而稀了，你舀到的粮食变少——"
            "钱也是，数量多了，购买力这勺'米'就淡了。"
        ),
    },
    {
        "tag": "预期 良",
        "topic": "闭包 closure",
        "background": "编程概念，函数与其词法作用域的组合，能记住定义时所处环境的变量。",
        "text": (
            "闭包可以这样理解：一个函数不只会执行代码，它还会随身带着它被创造时所在环境的'背包'。"
            "比如在外面定义了一个变量 count，里面返回一个函数每次让 count 加一，那么每次调用这个返回的函数，"
            "count 都还在、不会被清掉——这就是闭包在'记住'当时的环境。它常用来做私有数据，"
            "比如一个模块只给你'增加'和'读取'两个入口，但真正的数字藏在闭包里，外面改不了。"
            "打个不精确的比方，就像公司前台只给你两个办事窗口，但内部的账本你碰不到。"
        ),
    },
    {
        "tag": "预期 中",
        "topic": "闭包 closure",
        "background": "编程概念，函数与其词法作用域的组合，能记住定义时所处环境的变量。",
        "text": (
            "闭包就是说，一个函数能记住自己出生那个地方（定义时的周围环境）里的变量，"
            "即使后来被拿到别处去用，那些变量还跟着它。比如我做一个计数器，每次调用就加一，"
            "靠的就是闭包记住了那个计数的数字。不过它底层到底怎么实现的我讲不太清，"
            "反正就是函数把所在环境'打包'一起带走了，所以数据不会丢。"
        ),
    },
    {
        "tag": "预期 差",
        "topic": "区块链",
        "background": "一种按时间顺序将数据区块链式相连、去中心化存储的分布式账本技术。",
        "text": (
            "区块链就是比特币啊，去中心化的，很安全，未来会改变世界。"
            "具体原理我不太清楚，反正很牛的技术。"
        ),
    },
]


def main():
    global API_KEY
    API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
    out = []
    out.append(f"=== 费曼实验课 评价 Prompt 试跑（{PROMPT_VERSION}）===\n")
    if not API_KEY:
        out.append("ERROR: 未设置环境变量 DASHSCOPE_API_KEY，无法调用千问。")
        out.append("请在运行前执行：  set DASHSCOPE_API_KEY=你的key")
        text = "\n".join(out)
        print(text)
        sys.exit(2)
    debug = "--debug" in sys.argv
    for i, c in enumerate(CASES, 1):
        out.append(f"【用例 {i} · {c['tag']}】课题：{c['topic']}")
        try:
            d = evaluate(c["topic"], c["background"], c["text"], debug=debug)
            out.append(pretty(d))
        except Exception as e:  # noqa
            import traceback
            out.append("[RUN_ERR] " + traceback.format_exc().replace("\n", " | "))
        out.append("-" * 60)
    text = "\n".join(out)
    try:
        print(text)
    except Exception:
        pass
    report_path = os.path.join(HERE, "_run_report.txt")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as we:  # noqa
        out.append("REPORT_WRITE_ERR: " + str(we))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        with open(os.path.join(HERE, "_fatal.txt"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
