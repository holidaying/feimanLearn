# -*- coding: utf-8 -*-
"""端到端冒烟测试：打本地后端若干个路由，结果写 UTF-8 文件。"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000"


def post(path, payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=body,
                                 headers={"Content-Type": "application/json"})
    for _ in range(15):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.URLError:
            time.sleep(1)
    raise RuntimeError("无法连接后端")


def main():
    out = []
    # 1) 健康
    try:
        h = post("/api/health", {})
        out.append("HEALTH: " + json.dumps(h, ensure_ascii=False))
    except Exception as e:
        out.append("HEALTH_ERR: " + repr(e))
    # 2) 每日课题
    try:
        d = post("/api/topics/daily", {})
        out.append("DAILY count=" + str(len(d.get("topics", []))))
        out.append("DAILY sample=" + d["topics"][0]["title"])
    except Exception as e:
        out.append("DAILY_ERR: " + repr(e))
    # 3) 评价（真实调用千问）
    try:
        e = post("/api/evaluate", {
            "topic": "通货膨胀",
            "background": "经济学概念，指整体物价水平持续上涨、货币购买力下降。",
            "text": "简单说钱变不值钱了。去年100块买10个包子，今年要12块。钱多了但东西没多，价格就上去了。",
        })
        out.append("EVALUATE score=" + str(e.get("overall_score")) + " grade=" + str(e.get("grade")))
        out.append("EVALUATE dims=" + json.dumps(e.get("dimensions", {}), ensure_ascii=False))
        out.append("EVALUATE summary=" + str(e.get("summary")))
    except Exception as e:
        out.append("EVALUATE_ERR: " + repr(e))
    # 4) 导出 MD
    try:
        md = post("/api/export/markdown", {
            "topic": "通货膨胀", "grade": "良",
            "summary": "用包子例子讲清了钱不值钱", "text": "钱变不值钱了……",
            "dimensions": {"simplicity": {"score": 20, "comment": "通俗"},
                           "completeness": {"score": 25, "comment": "三要素齐"},
                           "logic": {"score": 25, "comment": "因果清"},
                           "analogy": {"score": 25, "comment": "比喻好"}},
        })
        out.append("MARKDOWN head=" + md.get("text", md)[:40] if isinstance(md, dict) else str(md)[:40])
    except Exception as e:
        out.append("MARKDOWN_ERR: " + repr(e))
    open("D:/AI小项目/费曼学习法/server/_test_out.txt", "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    main()
