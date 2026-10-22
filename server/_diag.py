# -*- coding: utf-8 -*-
import os, json, urllib.request, traceback
BASE_URL = "https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1"
MODEL = "qwen3.7-plus"
api_key = os.environ["DASHSCOPE_API_KEY"]
prompt = ('你是话题库编辑，生成2个适合费曼练习的话题。只输出JSON：'
          '{"topics":[{"title":"x","background":"y","difficulty":"入门",'
          '"guide_questions":["a","b","c"],"tags":["t1"]}]}')
url = BASE_URL + "/chat/completions"
body = {"model": MODEL, "temperature": 0.8, "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}]}
req = urllib.request.Request(url, data=json.dumps(body).encode(),
                             headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"})
lines = []
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read().decode())
    content = resp["choices"][0]["message"]["content"]
    lines.append("RAW=" + content[:500])
    s, e = content.find("{"), content.rfind("}") + 1
    parsed = json.loads(content[s:e])
    lines.append("PARSED_OK topics=" + str(len(parsed.get("topics", []))))
except Exception:
    lines.append("ERR=" + traceback.format_exc())
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_diag.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
