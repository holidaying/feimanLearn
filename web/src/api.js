// 费曼实验课 · 前端 API 层
// 后端 server/app.py 已开启 CORS(*)，且 Vite 开发期对 /api 做反代，
// 生产期后端同源托管 web/dist，因此统一使用相对路径 /api。

const BASE = '/api'

async function req(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error('HTTP ' + res.status)
  return res
}

export async function getHealth() {
  const r = await req('/health')
  return r.json()
}

export async function getDailyTopics() {
  const r = await req('/topics/daily')
  const d = await r.json()
  return d.topics || []
}

// 全量底库（题库页）：{ count, categories, topics }
export async function getAllTopics() {
  const r = await req('/topics/all')
  return r.json()
}

export async function getRandomTopic() {
  const r = await req('/topics/random', { method: 'POST', body: '{}' })
  return r.json()
}

// payload: { topic, background, text, prev_grade }
export async function evaluate(payload) {
  const r = await req('/evaluate', {
    method: 'POST',
    body: JSON.stringify({
      topic: payload.topic,
      background: payload.background,
      text: payload.text,
      prev_grade: payload.prev_grade || null,
    }),
  })
  return r.json()
}

// 结业后标准示范（方案 A）：payload { topic, background, text, grade }
export async function getDemonstration(payload) {
  const r = await req('/demonstrate', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return r.json()
}

// payload: { topic, grade, dimensions, summary, text }
export async function exportMarkdown(payload) {
  const r = await req('/export/markdown', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return r.text()
}
