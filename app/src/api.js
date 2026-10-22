// 费曼实验课 · 移动端 API 层
// 与 Web 端同构：统一走 uni.request，后端已开启 CORS(*)
import { API_BASE } from './config.js'

function request(path, { method = 'GET', data = null } = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: API_BASE + path,
      method,
      data: data || undefined,
      header: { 'Content-Type': 'application/json' },
      timeout: 120000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data)
        else reject(new Error('HTTP ' + res.statusCode))
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败')),
    })
  })
}

export function getHealth() {
  return request('/health')
}

export function getDailyTopics() {
  return request('/topics/daily').then((d) => d.topics || [])
}

export function getAllTopics() {
  return request('/topics/all')
}

export function getRandomTopic() {
  return request('/topics/random', { method: 'POST', data: {} })
}

export function evaluate(payload) {
  return request('/evaluate', {
    method: 'POST',
    data: {
      topic: payload.topic,
      background: payload.background,
      text: payload.text,
      prev_grade: payload.prev_grade || null,
    },
  })
}

// 结业后标准示范（方案 A）
export function getDemonstration(payload) {
  return request('/demonstrate', {
    method: 'POST',
    data: {
      topic: payload.topic,
      background: payload.background,
      text: payload.text,
      grade: payload.grade,
    },
  })
}

export function exportMarkdown(payload) {
  return request('/export/markdown', { method: 'POST', data: payload })
}
