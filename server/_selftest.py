# -*- coding: utf-8 -*-
"""单进程自测：同进程起 HTTPServer 线程，再打各路由，结果写 UTF-8 文件。"""
import json
import threading
import time
import urllib.request
import app as appmod

PORT = 8011
server = None


def run():
    global server
    srv = appmod.HTTPServer(("127.0.0.1", PORT), appmod.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    out = []
    base = f"http://127.0.0.1:{PORT}"

    def call(path, payload=None):
        if payload is None:
            req = urllib.request.Request(base + path)
        else:
            req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))

    try:
        h = call("/api/health")
        out.append("HEALTH: " + json.dumps(h, ensure_ascii=False))
    except Exception as e:
        out.append("HEALTH_ERR: " + repr(e))
    try:
        d = call("/api/topics/daily")
        out.append("DAILY count=" + str(len(d.get("topics", []))) + " sample=" + d["topics"][0]["title"])
    except Exception as e:
        out.append("DAILY_ERR: " + repr(e))
    try:
        e = call("/api/evaluate", {
            "topic": "通货膨胀",
            "background": "经济学概念，指整体物价水平持续上涨、货币购买力下降。",
            "text": "简单说钱变不值钱了。去年100块买10个包子，今年要12块。钱多了但东西没多，价格就上去了。",
        })
        out.append("EVALUATE score=" + str(e.get("overall_score")) + " grade=" + str(e.get("grade")))
        out.append("EVALUATE dims=" + json.dumps(e.get("dimensions", {}), ensure_ascii=False))
        out.append("EVALUATE summary=" + str(e.get("summary")))
    except Exception as e:
        out.append("EVALUATE_ERR: " + repr(e))
    try:
        md = call("/api/export/markdown", {
            "topic": "通货膨胀", "grade": "良",
            "summary": "用包子例子讲清了钱不值钱", "text": "钱变不值钱了……",
            "dimensions": {"simplicity": {"score": 20, "comment": "通俗"},
                           "completeness": {"score": 25, "comment": "三要素齐"},
                           "logic": {"score": 25, "comment": "因果清"},
                           "analogy": {"score": 25, "comment": "比喻好"}},
        })
        if isinstance(md, dict):
            out.append("MARKDOWN head=" + md.get("text", "")[:50])
        else:
            out.append("MARKDOWN raw=" + str(md)[:50])
    except Exception as e:
        out.append("MARKDOWN_ERR: " + repr(e))
    srv.shutdown()
    open("D:/AI小项目/费曼学习法/server/_test_out.txt", "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    run()
