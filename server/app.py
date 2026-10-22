# -*- coding: utf-8 -*-
"""
费曼实验课 · 后端服务（零依赖，标准库 http.server）
路由：
  GET  /api/health
  GET  /api/topics/daily         -> 每日 10 条（6 底库 + 4 热榜占位）
  POST /api/topics/random         -> 随机 1 条
  POST /api/evaluate              -> 千问评价（服务端持 key）
  POST /api/export/markdown      -> 生成 300 字小科普的 Markdown 文本
  POST /api/demonstrate          -> 结业后标准示范（仅限良/优，服务端二次校验）
静态目录：../web/dist（生产构建后）；开发期由 Vite 单独托管
"""
import os
import sys
import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluator  # noqa: E402

PORT = int(os.environ.get("PORT", "8000"))

# 热榜占位（MVP 用静态占位，M2 接真实爬取）
HOT_PLACEHOLDER = [
    {"title": "AI  Agent 到底是什么", "background": "近期热词，指能自主调用工具完成任务的 AI 程序。",
     "difficulty": "进阶", "guide_questions": ["它和普通聊天机器人区别在哪？", "它能'自主'到什么程度？", "举例一个它帮人做事的场景"],
     "category": "hot", "category_label": "热榜", "tags": ["AI", "热点"], "source": "hot"},
    {"title": "为什么最近总说'新质生产力'", "background": "政策与财经热词，指以科技创新为核心的新生产力。",
     "difficulty": "进阶", "guide_questions": ["它和一般'生产力'差别在哪？", "哪些行业算新质生产力？", "为什么现在强调它？"],
     "category": "hot", "category_label": "热榜", "tags": ["经济", "热点"], "source": "hot"},
    {"title": "直播带货背后的算法逻辑", "background": "热门消费现象，平台用推荐算法决定你看到什么。",
     "difficulty": "入门", "guide_questions": ["为什么总刷到同类内容？", "算法靠什么决定推送？", "这对消费者是好是坏？"],
     "category": "hot", "category_label": "热榜", "tags": ["互联网", "热点"], "source": "hot"},
    {"title": "城市'十五分钟生活圈'是什么", "background": "近期民生热词，指步行 15 分钟可达基本服务。",
     "difficulty": "入门", "guide_questions": ["它解决什么生活痛点？", "哪些服务算在内？", "为什么突然被推广？"],
     "category": "hot", "category_label": "热榜", "tags": ["生活", "热点"], "source": "hot"},
]

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

# 生产构建产物目录（web/dist），由后端一并托管，实现单进程上线
DIST_DIR = os.path.abspath(os.path.join(HERE, "..", "web", "dist"))

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".txt": "text/plain; charset=utf-8",
}


def load_base():
    path = os.path.join(HERE, "topics_base.json")
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8")).get("topics", [])
        except Exception:
            return []
    return []


BASE_TOPICS = load_base()


def daily_topics():
    # 6 条底库（按日期取确定子集）+ 4 条热榜占位
    pool = list(BASE_TOPICS)
    random.seed(_today_seed())
    random.shuffle(pool)
    base_pick = pool[:6]
    return base_pick + HOT_PLACEHOLDER[:4]


def _today_seed():
    import datetime
    return datetime.date.today().isoformat()


def build_markdown(payload):
    topic = payload.get("topic", "")
    grade = payload.get("grade", "")
    dims = payload.get("dimensions", {})
    summary = payload.get("summary", "")
    text = payload.get("text", "")
    lines = []
    lines.append(f"# 费曼实验课 · 结业小科普：{topic}")
    lines.append("")
    lines.append(f"> 等级：**{grade}**　|　日期：{_today_seed()}")
    lines.append("")
    if summary:
        lines.append(f"**一句话总结**：{summary}")
        lines.append("")
    lines.append("## 我的理解（裸讲）")
    lines.append("")
    lines.append(text or "（此处为你的讲述内容）")
    lines.append("")
    lines.append("## 四维自评")
    lines.append("")
    for k, label in [("simplicity", "简洁性"), ("completeness", "完整性"),
                     ("logic", "逻辑性"), ("analogy", "比喻力")]:
        v = dims.get(k, {})
        lines.append(f"- **{label}** {v.get('score', 0)}/25：{v.get('comment', '')}")
    lines.append("")
    lines.append("---")
    lines.append("*由「费曼实验课」生成 · 讲不明白，就是没搞懂*")
    return "\n".join(lines)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj=None, body=None, ctype="application/json"):
        self.send_response(code)
        for k, v in CORS.items():
            self.send_header(k, v)
        if obj is not None:
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif body is not None:
            b = body.encode("utf-8")
            self.send_header("Content-Type", ctype + "; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        else:
            self.end_headers()

    def do_OPTIONS(self):
        self._send(204)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send(200, {"status": "ok", "topics": len(BASE_TOPICS)})
        elif path == "/api/topics/daily":
            self._send(200, {"date": _today_seed(), "topics": daily_topics()})
        elif path == "/api/topics/all":
            # 全量底库（题库页用），附带分类统计
            cats = {}
            for t in BASE_TOPICS:
                key = t.get("category", "base")
                cats[key] = cats.get(key, 0) + 1
            self._send(200, {
                "count": len(BASE_TOPICS),
                "categories": cats,
                "topics": BASE_TOPICS,
            })
        else:
            self._serve_static(path)

    def _send_raw(self, code, data, ctype):
        """直接下发字节流（静态文件，含图片/字体等二进制）"""
        self.send_response(code)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, path):
        """托管 web/dist：命中文件则下发，否则 SPA 回退 index.html"""
        rel = (path or "/").lstrip("/")
        target = os.path.normpath(os.path.join(DIST_DIR, rel)) if rel else DIST_DIR
        if not target.startswith(DIST_DIR):  # 防目录穿越
            self._send(404, {"error": "not found"})
            return
        if os.path.isdir(target) or not os.path.isfile(target):
            target = os.path.join(DIST_DIR, "index.html")  # SPA 回退
        if not os.path.isfile(target):
            self._send(200, None, "<h1>费曼实验课</h1><p>web/dist 尚未构建，请先在 web/ 目录执行 npm install &amp;&amp; npm run build</p>",
                       "text/html; charset=utf-8")
            return
        ext = os.path.splitext(target)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        try:
            with open(target, "rb") as f:
                self._send_raw(200, f.read(), ctype)
        except Exception:  # noqa
            self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            payload = {}
        if path == "/api/topics/random":
            pool = BASE_TOPICS + HOT_PLACEHOLDER
            self._send(200, random.choice(pool) if pool else {"error": "empty"})
        elif path == "/api/evaluate":
            try:
                result = evaluator.evaluate(
                    topic=payload.get("topic", ""),
                    background=payload.get("background", ""),
                    user_text=payload.get("text", ""),
                    prev_grade=payload.get("prev_grade"),
                )
                self._send(200, result)
            except Exception as e:  # noqa
                self._send(200, {"error": str(e), "summary": "评价服务繁忙，你的讲述已保存，请稍后重试"})
        elif path == "/api/export/markdown":
            self._send(200, None, build_markdown(payload), "text/markdown")
        elif path == "/api/demonstrate":
            # 结业后标准示范（方案 A）：仅当用户已拿到良/优，前端才允许调用
            try:
                grade = payload.get("grade", "")
                if grade not in ("优", "良"):
                    self._send(200, {"error": "forbidden",
                                     "summary": "标准示范仅在结业（良及以上）后开放 —— 先自己讲通，再来看别人怎么讲。"})
                else:
                    demo = evaluator.demonstrate(
                        topic=payload.get("topic", ""),
                        background=payload.get("background", ""),
                        user_text=payload.get("text", ""),
                    )
                    self._send(200, demo)
            except Exception as e:  # noqa
                self._send(200, {"error": str(e), "summary": "示范生成失败，请稍后重试"})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass


def main():
    dist_ok = os.path.isfile(os.path.join(DIST_DIR, "index.html"))
    print(f"费曼实验课后端启动：http://localhost:{PORT}  (底库 {len(BASE_TOPICS)} 条)")
    print(f"前端静态目录：{DIST_DIR}  " + ("（已构建，可直接访问）" if dist_ok else "（未构建，请先在 web/ 执行 npm run build）"))
    # 多线程：评价请求最长 40s，避免阻塞静态资源与其他 API
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
