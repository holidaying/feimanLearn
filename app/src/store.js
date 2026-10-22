// 费曼实验课 · 会话状态（与 Web 端同构，仅把 localStorage 换成 uni storage）
import { reactive } from 'vue'
import * as api from './api.js'

export const session = reactive({
  step: 'bench',
  loading: false,
  error: '',
  dailyTopics: [],
  allTopics: [],
  practiced: {},
  favorites: [],
  topic: null,
  background: '',
  guideQuestions: [],
  rounds: [],
  passed: false,
  passedRound: null,
})

/* ---------- 本地持久化 ---------- */
const LS_PRACTICED = 'feynman.practiced.v1'
const LS_FAVS = 'feynman.favorites.v1'

function loadLS(key, fallback) {
  try {
    const v = uni.getStorageSync(key)
    return v ? v : fallback
  } catch (e) {
    return fallback
  }
}
function saveLS(key, val) {
  try {
    uni.setStorageSync(key, val)
  } catch (e) {}
}

session.practiced = loadLS(LS_PRACTICED, {})
session.favorites = loadLS(LS_FAVS, [])

function pickTopicFields(t) {
  return {
    title: t.title,
    background: t.background || '',
    category: t.category || 'base',
    category_label: t.category_label || '',
    difficulty: t.difficulty || '',
    guide_questions: t.guide_questions || [],
    tags: t.tags || [],
  }
}

export function isFavorite(title) {
  return session.favorites.some((x) => x.title === title)
}

export function toggleFavorite(t) {
  if (!t || !t.title) return
  const i = session.favorites.findIndex((x) => x.title === t.title)
  if (i >= 0) session.favorites.splice(i, 1)
  else session.favorites.push(pickTopicFields(t))
  saveLS(LS_FAVS, JSON.parse(JSON.stringify(session.favorites)))
}

export function practicedOf(title) {
  return session.practiced[title] || null
}

export function markPracticed(title, grade, score) {
  if (!title) return
  const prev = session.practiced[title]
  const best = prev && prev.score > score ? { grade: prev.grade, score: prev.score } : { grade, score }
  session.practiced[title] = {
    ...best,
    date: new Date().toISOString().slice(0, 10),
    rounds: (prev && prev.rounds ? prev.rounds : 0) + 1,
  }
  saveLS(LS_PRACTICED, JSON.parse(JSON.stringify(session.practiced)))
}

export async function loadAllTopics() {
  if (session.allTopics.length) return
  session.loading = true
  try {
    const d = await api.getAllTopics()
    session.allTopics = d.topics || []
  } catch (e) {
    session.error = '题库加载失败：' + e.message
  } finally {
    session.loading = false
  }
}

export function resetSession() {
  session.step = 'bench'
  session.topic = null
  session.background = ''
  session.guideQuestions = []
  session.rounds = []
  session.passed = false
  session.passedRound = null
  session.error = ''
}

export async function loadDaily() {
  session.loading = true
  session.error = ''
  try {
    session.dailyTopics = await api.getDailyTopics()
  } catch (e) {
    session.error = '无法连接后端服务：' + e.message
  } finally {
    session.loading = false
  }
}

export async function startRandom() {
  if (!session.dailyTopics.length) await loadDaily()
  const pool = session.dailyTopics
  if (!pool.length) return
  enterTopic(pool[Math.floor(Math.random() * pool.length)])
}

export function enterTopic(t) {
  session.topic = t.title
  session.background = t.background || ''
  session.guideQuestions = t.guide_questions || []
  session.rounds = []
  session.passed = false
  session.passedRound = null
  session.error = ''
  session.step = 'narration'
}

export async function submitRound(text, voiceText) {
  session.loading = true
  session.error = ''
  try {
    const prev = session.rounds.length
      ? session.rounds[session.rounds.length - 1].result.grade
      : null
    const result = await api.evaluate({
      topic: session.topic,
      background: session.background,
      text,
      prev_grade: prev,
    })
    if (result && result.error) {
      session.error = result.error + '：' + (result.summary || '请稍后重试')
      return null
    }
    session.rounds.push({ text, voiceText: voiceText || '', result })
    markPracticed(session.topic, result.grade, result.overall_score)
    const g = result.grade
    const passed = g === '优' || g === '良'
    if (passed) {
      session.passed = true
      session.passedRound = session.rounds.length - 1
      session.step = 'graduation'
    } else {
      session.step = 'report'
    }
    return result
  } catch (e) {
    session.error = '评价请求失败：' + e.message
    return null
  } finally {
    session.loading = false
  }
}

export function reviseRound() {
  session.step = 'narration'
}

export function exportPayload() {
  const r = session.rounds[session.passedRound]
  return {
    topic: session.topic,
    grade: r.result.grade,
    dimensions: r.result.dimensions,
    summary: r.result.summary,
    text: r.text,
  }
}

export const GRADE_COLOR = {
  优: '#2F6B3A',
  良: '#1E5FA8',
  中: '#B4451A',
  差: '#8E2A2A',
}

export const GRADE_LABEL = {
  优: '优 · 直接结业',
  良: '良 · 及格',
  中: '中 · 继续修正',
  差: '差 · 建议补课',
}
