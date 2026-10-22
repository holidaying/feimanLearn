# -*- coding: utf-8 -*-
"""
费曼实验课 · 话题底库生成器
用千问批量产出 6 大类话题种子，落地为 topics_base.json。
每类约 20 条，结构支持后续扩到 1000 条（再跑几轮即可）。
字段：title / background / difficulty / guide_questions / category / tags
"""
import os
import json
import urllib.request
import urllib.error

CATEGORIES = [
    ("科学常识", "science", "物理、化学、生物、天文、医学等可被外行理解的基础科学现象"),
    ("经济金融", "economy", "通胀、利率、税、复利、市场等日常会接触的经济金融概念"),
    ("技术概念", "tech", "编程、AI、互联网、工程等领域的通俗可讲的技术概念"),
    ("人文社科", "humanities", "历史、心理、社会、哲学、语言等人文学科的可讲概念"),
    ("生活经验", "life", "健康、饮食、消费、人际、习惯等生活场景中的可讲经验"),
    ("职场方法", "career", "沟通、管理、效率、决策等职场中可讲的方法论"),
]

def build_prompt(n, scope):
    return (
        "你是费曼学习法话题库的编辑。请生成 " + str(n) + " 个适合普通人练习『用自己的话讲清楚』的热门话题，"
        "主题范围：" + scope + "。\n"
        "要求：话题具体、有现实感、非纯学术黑话；难度混合（入门/进阶/硬核）；"
        "每条给出一句话背景简介（外行也能看懂）和 3 个引导问题（帮助用户热身，但不要给答案）。\n"
        "只输出如下 JSON，不要任何额外文字：\n"
        '{"topics":[{"title":"话题名","background":"一句话背景","difficulty":"入门|进阶|硬核",'
        '"guide_questions":["q1","q2","q3"],"tags":["标签1","标签2"]}]}'
    )

BASE_URL = os.environ.get(
    "DASHSCOPE_BASE_URL", "https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1"
)
MODEL = "qwen3.7-plus"


def _call(prompt, api_key):
    url = BASE_URL.rstrip("/") + "/chat/completions"
    body = {
        "model": MODEL,
        "temperature": 0.8,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read().decode("utf-8"))
    content = resp["choices"][0]["message"]["content"]
    s, e = content.find("{"), content.rfind("}") + 1
    return json.loads(content[s:e])


def main():
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    here = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(here, "_gen_log.txt")
    path = os.path.join(here, "topics_base.json")
    # 增量：加载已有底库，跳过已生成的类目
    existing = []
    if os.path.exists(path):
        try:
            existing = json.load(open(path, encoding="utf-8")).get("topics", [])
        except Exception:
            existing = []
    done_cats = {t.get("category") for t in existing}
    log = []
    if not api_key:
        open(log_path, "w", encoding="utf-8").write("ERROR: 缺少 DASHSCOPE_API_KEY")
        return
    out = list(existing)
    per_cat = int(os.environ.get("PER_CAT", "20"))
    for label, key, scope in CATEGORIES:
        if key in done_cats:
            log.append(f"[{label}] 已存在，跳过")
            continue
        try:
            data = _call(build_prompt(per_cat, scope), api_key)
            for t in data.get("topics", []):
                out.append({
                    "title": t.get("title", "").strip(),
                    "background": t.get("background", "").strip(),
                    "difficulty": t.get("difficulty", "入门"),
                    "guide_questions": t.get("guide_questions", [])[:3],
                    "category": key,
                    "category_label": label,
                    "tags": t.get("tags", [])[:4],
                    "source": "base",
                })
            log.append(f"[{label}] +{len(data.get('topics', []))} 条")
        except Exception as e:  # noqa
            log.append(f"[{label}] 失败: {repr(e)}")
        # 每类生成完立即落盘，避免超时丢失进度
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "generated_by": "qwen3.7-plus",
                       "count": len(out), "topics": out}, f, ensure_ascii=False, indent=2)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log[-1] + "\n")
    log.append(f"累计 {len(out)} 条，已写入 {path}")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log[-1] + "\n")


if __name__ == "__main__":
    main()
