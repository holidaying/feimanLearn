<template>
  <section v-if="passed">
    <div class="eyebrow anim d1">结业 · 实验通过</div>

    <div class="hero anim d2">
      <h1 class="display">讲明白了。</h1>
      <div class="grade-row">
        <GradeBadge :grade="grade" size="lg" />
        <span class="score mono-lg">{{ passed.result.overall_score }} / 100</span>
      </div>
    </div>

    <hr class="rule" style="margin: var(--s-7) 0;" />

    <!-- 产出预览 -->
    <div class="eyebrow anim d3">实验产出 · 我的理解</div>
    <div class="panel preview anim d4">
      <div class="line"><b class="mono">一句话总结</b>{{ summary }}</div>
      <div class="body-text">{{ finalText }}</div>
      <div class="tags">
        <span class="tag tag-base">#{{ session.topic }}</span>
        <span class="tag">{{ today }}</span>
      </div>
    </div>

    <!-- 方案 A：结业后标准示范（主动点开，默认不展示） -->
    <div class="eyebrow" style="margin-top: var(--s-8);">标准示范 · 讲给外行听</div>
    <div class="panel demo anim d5">
      <div v-if="!demo && !demoBusy" class="demo-gate">
        <p class="demo-lead">
          你已经自己讲通了。现在可以看看 AI 会怎么讲同一个课题 —— 对照差距，下次讲得更透。
        </p>
        <button class="btn-primary" @click="loadDemo">看看 AI 会怎么讲 →</button>
      </div>

      <div v-else-if="demoBusy" class="demo-loading mono muted-2">
        正在生成标准示范…
      </div>

      <div v-else-if="demo.error" class="demo-err">
        {{ demo.summary || demo.error }}
      </div>

      <div v-else class="demo-body anim fade">
        <div v-if="demo.one_liner" class="demo-oneliner">
          <span class="mono muted-2">一句话</span>
          <p>{{ demo.one_liner }}</p>
        </div>
        <div v-if="demo.analogy" class="demo-line">
          <b class="mono">生活类比</b>{{ demo.analogy }}
        </div>
        <div class="demo-text">{{ demo.demo_text }}</div>
        <div v-if="demo.pitfall" class="demo-pit">
          <b class="mono">避坑提醒</b>{{ demo.pitfall }}
        </div>
        <div class="demo-foot">
          <button class="btn-ghost btn-sm" @click="copyDemo">复制标准示范</button>
          <span class="mono muted-2">对照完，想想你哪一句可以换成他的说法</span>
        </div>
      </div>
    </div>

    <!-- 导出 -->
    <div class="eyebrow" style="margin-top: var(--s-8);">导出与分享</div>
    <div class="exports anim d5">
      <button class="exp" :disabled="busy" @click="copyText">
        <span class="exp-k mono">01</span>
        <b>复制文字</b>
        <span class="muted-2" style="font-size:13px;">科普正文到剪贴板</span>
      </button>
      <button class="exp" :disabled="busy" @click="downloadMd">
        <span class="exp-k mono">02</span>
        <b>下载 Markdown</b>
        <span class="muted-2" style="font-size:13px;">含四维得分与等级</span>
      </button>
      <button class="exp" :disabled="busy" @click="downloadImage">
        <span class="exp-k mono">03</span>
        <b>图片卡片</b>
        <span class="muted-2" style="font-size:13px;">1080 × 1440 分享卡</span>
      </button>
      <button class="exp accent" :disabled="busy" @click="share">
        <span class="exp-k mono">04</span>
        <b>系统分享</b>
        <span class="muted-2" style="font-size:13px;">调起原生分享面板</span>
      </button>
    </div>
    <p class="mono muted-2" style="margin-top: var(--s-4);">
      分享内容仅含科普正文与等级，不含原始裸讲稿
    </p>

    <div v-if="toast" class="toast">{{ toast }}</div>

    <div class="actions anim d6">
      <button class="btn-primary" @click="another">再做一个实验 →</button>
      <button class="btn-ghost" @click="goHome">回到实验台</button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { session, exportPayload, resetSession, loadDaily } from '../store.js'
import * as api from '../api.js'
import GradeBadge from '../components/GradeBadge.vue'

const passed = computed(() => session.rounds[session.passedRound])
const finalText = computed(() => passed.value.text)
const grade = computed(() => passed.value.result.grade)
const summary = computed(() => passed.value.result.summary)
const today = computed(() => new Date().toISOString().slice(0, 10))

const mdText = ref('')
const busy = ref(false)
const toast = ref('')
let toastTimer = null

/* 方案 A：标准示范（结业后按需加载） */
const demo = ref(null)
const demoBusy = ref(false)

async function loadDemo() {
  if (demo.value || demoBusy.value) return
  demoBusy.value = true
  try {
    demo.value = await api.getDemonstration({
      topic: session.topic,
      background: session.background,
      text: finalText.value,
      grade: grade.value,
    })
  } catch (e) {
    demo.value = { error: e.message, summary: '标准示范生成失败：' + e.message }
  } finally {
    demoBusy.value = false
  }
}

async function copyDemo() {
  try {
    await navigator.clipboard.writeText(demo.value?.demo_text || '')
    showToast('标准示范已复制')
  } catch (e) {
    showToast('复制失败，请手动选择文字')
  }
}

function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 2600)
}

onMounted(async () => {
  busy.value = true
  try {
    mdText.value = await api.exportMarkdown(exportPayload())
  } catch (e) {
    showToast('Markdown 生成失败：' + e.message)
  } finally {
    busy.value = false
  }
})

function downloadBlob(blob, name) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

async function copyText() {
  try {
    await navigator.clipboard.writeText(finalText.value)
    showToast('已复制到剪贴板')
  } catch (e) {
    showToast('复制失败，请手动选择文字')
  }
}

function downloadMd() {
  if (!mdText.value) { showToast('Markdown 尚未生成'); return }
  downloadBlob(new Blob([mdText.value], { type: 'text/markdown;charset=utf-8' }),
    `费曼实验课-${session.topic}.md`)
  showToast('Markdown 已下载')
}

/* ============ 分享卡片（1080×1440） ============ */
function buildCardCanvas() {
  const W = 1080, H = 1440
  const canvas = document.createElement('canvas')
  canvas.width = W; canvas.height = H
  const ctx = canvas.getContext('2d')

  // 深琥珀 → 墨黑渐变（品牌色，不用紫蓝）
  const g = ctx.createLinearGradient(0, 0, 0, H)
  g.addColorStop(0, '#7C2D12'); g.addColorStop(1, '#191712')
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H)

  // 细网格（与网页底纹呼应）
  ctx.strokeStyle = 'rgba(255,255,255,0.045)'; ctx.lineWidth = 1
  for (let x = 0; x <= W; x += 36) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke() }
  for (let y = 0; y <= H; y += 36) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke() }

  ctx.textAlign = 'center'
  ctx.fillStyle = '#FFF6EC'
  ctx.font = 'bold 52px "Songti SC","SimSun",serif'
  ctx.fillText('费曼实验课', W / 2, 104)
  ctx.fillStyle = 'rgba(255,246,236,0.72)'; ctx.font = '26px sans-serif'
  ctx.fillText('讲不明白，就是没搞懂', W / 2, 148)

  ctx.fillStyle = '#FFF6EC'; ctx.font = 'bold 46px "Songti SC","SimSun",serif'
  const endY = wrapText(ctx, session.topic || '', W / 2, 232, W - 140, 60)

  drawGradeCircle(ctx, W / 2, endY + 158, 98, grade.value, passed.value.result.overall_score)

  const d = passed.value.result.dimensions
  drawRadar(ctx, W / 2, endY + 486, 148, [
    { label: '简洁性', score: d.simplicity.score },
    { label: '完整性', score: d.completeness.score },
    { label: '逻辑性', score: d.logic.score },
    { label: '比喻力', score: d.analogy.score },
  ])

  ctx.fillStyle = 'rgba(255,246,236,0.66)'; ctx.font = '24px sans-serif'; ctx.textAlign = 'right'
  ctx.fillText('费曼实验课 · ' + today.value, W - 40, H - 40)
  return canvas
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  let line = '', yy = y
  for (const ch of String(text)) {
    const test = line + ch
    if (ctx.measureText(test).width > maxWidth && line) {
      ctx.fillText(line, x, yy); line = ch; yy += lineHeight
    } else line = test
  }
  if (line) ctx.fillText(line, x, yy)
  return yy
}

function drawGradeCircle(ctx, cx, cy, r, grade, score) {
  const colors = { 优: '#F7E7D8', 良: '#F7E7D8', 中: '#F7E7D8', 差: '#F7E7D8' }
  const ink = { 优: '#2F6B3A', 良: '#1E5FA8', 中: '#B4451A', 差: '#8E2A2A' }
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2)
  ctx.fillStyle = colors[grade] || '#F7E7D8'; ctx.fill()
  ctx.fillStyle = ink[grade] || '#7C2D12'; ctx.textAlign = 'center'
  ctx.font = 'bold 44px "Songti SC","SimSun",serif'
  ctx.fillText(grade, cx, cy - 4)
  ctx.font = '24px sans-serif'
  ctx.fillText(score + ' 分', cx, cy + 38)
}

function drawRadar(ctx, cx, cy, r, data) {
  const N = data.length
  const angle = (i) => -Math.PI / 2 + (i * 2 * Math.PI) / N
  ctx.strokeStyle = 'rgba(255,246,236,0.22)'
  for (const frac of [0.25, 0.5, 0.75, 1]) {
    ctx.beginPath()
    for (let i = 0; i <= N; i++) {
      const a = angle(i % N)
      const x = cx + r * frac * Math.cos(a), y = cy + r * frac * Math.sin(a)
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.stroke()
  }
  for (let i = 0; i < N; i++) {
    const a = angle(i)
    ctx.beginPath(); ctx.moveTo(cx, cy)
    ctx.lineTo(cx + r * Math.cos(a), cy + r * Math.sin(a)); ctx.stroke()
  }
  ctx.beginPath()
  for (let i = 0; i <= N; i++) {
    const idx = i % N, a = angle(idx)
    const frac = Math.max(0, Math.min(1, (data[idx].score || 0) / 25))
    const x = cx + r * frac * Math.cos(a), y = cy + r * frac * Math.sin(a)
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  }
  ctx.closePath()
  ctx.fillStyle = 'rgba(242,201,160,0.42)'; ctx.fill()
  ctx.strokeStyle = '#F2C9A0'; ctx.stroke()
  ctx.fillStyle = '#FFF6EC'; ctx.font = '23px sans-serif'; ctx.textAlign = 'center'
  for (let i = 0; i < N; i++) {
    const a = angle(i)
    ctx.fillText(data[i].label, cx + (r + 34) * Math.cos(a), cy + (r + 34) * Math.sin(a) + 8)
  }
}

function downloadImage() {
  busy.value = true
  try {
    buildCardCanvas().toBlob((b) => {
      if (b) { downloadBlob(b, `费曼实验课-${session.topic}.png`); showToast('图片卡已下载') }
      busy.value = false
    }, 'image/png')
  } catch (e) {
    showToast('图片生成失败：' + e.message); busy.value = false
  }
}

async function share() {
  try {
    const blob = await new Promise((res) => buildCardCanvas().toBlob(res, 'image/png'))
    const file = new File([blob], `费曼实验课-${session.topic}.png`, { type: 'image/png' })
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({ files: [file], title: '费曼实验课', text: `我的理解：${session.topic}（${grade.value}）` })
    } else if (navigator.share) {
      await navigator.share({ title: '费曼实验课', text: `我的理解：${session.topic}（${grade.value}）` })
    } else {
      downloadImage()
      showToast('当前环境不支持系统分享，已为你下载图片')
    }
  } catch (e) { /* 用户取消 */ }
}

function another() { resetSession(); loadDaily() }
function goHome() { resetSession(); loadDaily() }
</script>

<style scoped>
.hero h1 { margin: 0 0 var(--s-5); }
.grade-row { display: flex; align-items: center; gap: var(--s-4); flex-wrap: wrap; }
.score { font-size: 20px; font-weight: 700; color: var(--teal); }

.preview { padding: var(--s-6); }
.line { font-size: 15px; line-height: 1.75; color: var(--ink-2); margin-bottom: var(--s-4); }
.line b { display: inline-block; min-width: 96px; margin-right: var(--s-3); color: var(--ink-3); }
.body-text {
  font-size: 15px; line-height: 1.9; color: var(--ink);
  white-space: pre-wrap;
  background: var(--paper-sunken);
  border-left: 3px solid var(--accent);
  border-radius: var(--r-md);
  padding: var(--s-5);
  max-height: 340px; overflow: auto;
}
.tags { margin-top: var(--s-4); display: flex; gap: var(--s-2); flex-wrap: wrap; }

/* 导出：编号卡片网格 */
.exports {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--s-4);
}
.exp {
  display: flex; flex-direction: column; align-items: flex-start; gap: 2px;
  font: inherit; text-align: left;
  background: var(--paper-raised);
  border: 1px solid var(--rule); border-radius: var(--r-md);
  padding: var(--s-5); cursor: pointer;
  transition: all var(--dur-2) var(--ease-out-quart);
}
.exp:hover:not(:disabled) {
  border-color: var(--accent); background: var(--accent-soft);
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(180, 69, 26, 0.14);
}
.exp:disabled { opacity: 0.5; cursor: not-allowed; }
.exp-k { margin-bottom: 4px; }
.exp.accent b { color: var(--accent); }

/* 方案 A · 标准示范 */
.demo { padding: var(--s-6); }
.demo-lead {
  font-size: 15px; line-height: 1.8; color: var(--ink-2);
  margin: 0 0 var(--s-5); max-width: 58ch;
}
.demo-loading { font-size: 13px; }
.demo-err { font-size: 14px; color: var(--accent-ink); }
.demo-oneliner {
  margin-bottom: var(--s-4);
  padding-bottom: var(--s-4);
  border-bottom: 1px dashed var(--rule-2);
}
.demo-oneliner p {
  font-family: var(--font-display);
  font-size: 22px; line-height: 1.6; color: var(--ink);
  margin: 4px 0 0;
}
.demo-line { font-size: 14px; line-height: 1.75; color: var(--teal); margin-bottom: var(--s-4); }
.demo-line b { display: inline-block; min-width: 72px; margin-right: var(--s-3); color: var(--ink-3); }
.demo-text {
  font-size: 15px; line-height: 1.95; color: var(--ink);
  white-space: pre-wrap;
  background: var(--paper-sunken);
  border-left: 3px solid var(--teal);
  border-radius: var(--r-md);
  padding: var(--s-5);
}
.demo-pit {
  margin-top: var(--s-4);
  font-size: 14px; line-height: 1.7; color: var(--accent-ink);
  background: var(--accent-soft);
  border-radius: var(--r-sm);
  padding: var(--s-4);
}
.demo-pit b { display: inline-block; min-width: 72px; margin-right: var(--s-3); }
.demo-foot {
  display: flex; align-items: center; gap: var(--s-4);
  flex-wrap: wrap; margin-top: var(--s-5);
}
.demo-foot .mono { font-size: 12px; }

.toast {
  margin-top: var(--s-5);
  background: var(--accent-soft); color: var(--accent-ink);
  border-left: 3px solid var(--accent);
  padding: 10px 14px; border-radius: var(--r-md); font-size: 14px;
  animation: rise var(--dur-3) var(--ease-out-expo);
}

.actions { display: flex; gap: var(--s-4); flex-wrap: wrap; margin-top: var(--s-8); }

@media (max-width: 640px) {
  .exports { grid-template-columns: 1fr; }
}
</style>
