<template>
  <view class="page" v-if="passed">
    <text class="eyebrow anim d1">结业 · 实验通过</text>

    <view class="hero anim d2">
      <text class="display">讲明白了。</text>
      <view class="grade-row">
        <GradeBadge :grade="grade" />
        <text class="score mono-lg">{{ passed.result.overall_score }} / 100</text>
      </view>
    </view>

    <!-- 我的理解 -->
    <text class="eyebrow sec">实验产出 · 我的理解</text>
    <view class="panel preview anim d3">
      <view class="line"><text class="k mono">一句话总结</text><text class="v">{{ summary }}</text></view>
      <scroll-view class="body-text" scroll-y :style="{ maxHeight: '480rpx' }">
        <text>{{ finalText }}</text>
      </scroll-view>
      <view class="tags">
        <text class="tag tag-base">#{{ session.topic }}</text>
        <text class="tag">{{ today }}</text>
      </view>
    </view>

    <!-- 导出 -->
    <text class="eyebrow sec">导出与分享</text>
    <view class="exports anim d4">
      <view class="exp" @click="copyText">
        <text class="exp-k mono">01</text>
        <text class="exp-b">复制文字</text>
        <text class="exp-d">科普正文到剪贴板</text>
      </view>
      <view class="exp" @click="copyMd">
        <text class="exp-k mono">02</text>
        <text class="exp-b">复制 Markdown</text>
        <text class="exp-d">含四维得分与等级</text>
      </view>
      <view class="exp" @click="makeCard">
        <text class="exp-k mono">03</text>
        <text class="exp-b">图片卡片</text>
        <text class="exp-d">1080 × 1440 分享卡</text>
      </view>
      <view class="exp accent" @click="share">
        <text class="exp-k mono">04</text>
        <text class="exp-b">系统分享</text>
        <text class="exp-d">调起原生分享面板</text>
      </view>
    </view>
    <text class="mono muted-2 tip">分享内容仅含科普正文与等级，不含原始裸讲稿</text>

    <!-- L4 标准示范 -->
    <text class="eyebrow sec">标准示范 · 讲给外行听</text>
    <view class="panel demo anim d5">
      <view v-if="!demo && !demoBusy">
        <text class="demo-lead">你已经自己讲通了。现在可以看看 AI 会怎么讲同一个课题 —— 对照差距，下次讲得更透。</text>
        <button class="btn-primary" @click="loadDemo">看看 AI 会怎么讲 →</button>
      </view>
      <text v-else-if="demoBusy" class="mono muted-2">正在生成标准示范…</text>
      <text v-else-if="demo.error" class="demo-err">{{ demo.summary || demo.error }}</text>
      <view v-else class="anim">
        <view v-if="demo.one_liner" class="demo-oneliner">
          <text class="mono muted-2">一句话</text>
          <text class="oneliner">{{ demo.one_liner }}</text>
        </view>
        <view v-if="demo.analogy" class="demo-line">
          <text class="k mono">生活类比</text><text class="v">{{ demo.analogy }}</text>
        </view>
        <view class="demo-text"><text>{{ demo.demo_text }}</text></view>
        <view v-if="demo.pitfall" class="demo-pit">
          <text class="k mono">避坑提醒</text><text class="v">{{ demo.pitfall }}</text>
        </view>
        <view class="demo-foot">
          <button class="btn-ghost btn-sm" @click="copyDemo">复制标准示范</button>
        </view>
      </view>
    </view>

    <view class="actions anim d6">
      <button class="btn-primary btn-xl" @click="another">再做一个实验 →</button>
      <button class="btn-ghost btn-xl" @click="goHome">回到实验台</button>
    </view>

    <!-- 离屏画布：生成分享卡 -->
    <canvas canvas-id="card" id="card" class="offscreen" :style="{ width: cardW + 'px', height: cardH + 'px' }"></canvas>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import { session, exportPayload, resetSession, loadDaily } from '../../store.js'
import * as api from '../../api.js'
import GradeBadge from '../../components/GradeBadge.vue'

const instance = getCurrentInstance()
const passed = computed(() => session.rounds[session.passedRound])
const finalText = computed(() => passed.value.text)
const grade = computed(() => passed.value.result.grade)
const summary = computed(() => passed.value.result.summary)
const today = computed(() => new Date().toISOString().slice(0, 10))

const mdText = ref('')
const demo = ref(null)
const demoBusy = ref(false)
const cardW = ref(540)
const cardH = ref(720)

onMounted(async () => {
  try { mdText.value = await api.exportMarkdown(exportPayload()) } catch (e) {}
})

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

function copy(text, okMsg) {
  uni.setClipboardData({ data: text, success: () => uni.showToast({ title: okMsg, icon: 'none' }) })
}
function copyText() { copy(finalText.value, '已复制到剪贴板') }
function copyMd() {
  if (!mdText.value) { uni.showToast({ title: 'Markdown 尚未生成', icon: 'none' }); return }
  copy(mdText.value, 'Markdown 已复制')
}
function copyDemo() { copy(demo.value.demo_text || '', '标准示范已复制') }

/* ---------- 分享卡（离屏 canvas） ---------- */
function wrapText(ctx, text, x, y, maxWidth, lh) {
  let line = ''
  let yy = y
  for (const ch of String(text)) {
    const t = line + ch
    if (ctx.measureText(t).width > maxWidth && line) {
      ctx.fillText(line, x, yy)
      line = ch
      yy += lh
    } else line = t
  }
  if (line) ctx.fillText(line, x, yy)
  return yy
}

function drawCard() {
  const W = cardW.value, H = cardH.value
  const ctx = uni.createCanvasContext('card', instance.proxy)
  const g = ctx.createLinearGradient(0, 0, 0, H)
  g.addColorStop(0, '#7C2D12')
  g.addColorStop(1, '#191712')
  ctx.setFillStyle(g)
  ctx.fillRect(0, 0, W, H)

  ctx.setStrokeStyle('rgba(255,255,255,0.05)')
  ctx.setLineWidth(1)
  for (let x = 0; x <= W; x += 18) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke() }
  for (let y = 0; y <= H; y += 18) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke() }

  ctx.setTextAlign('center')
  ctx.setFillStyle('#FFF6EC')
  ctx.setFontSize(26)
  ctx.fillText('费曼实验课', W / 2, 52)
  ctx.setFillStyle('rgba(255,246,236,0.72)')
  ctx.setFontSize(13)
  ctx.fillText('讲不明白，就是没搞懂', W / 2, 74)

  ctx.setFillStyle('#FFF6EC')
  ctx.setFontSize(23)
  let endY = wrapText(ctx, session.topic || '', W / 2, 118, W - 70, 30)

  // 等级圈
  const cx = W / 2, cy = endY + 78, r = 49
  ctx.beginPath()
  ctx.arc(cx, cy, r, 0, Math.PI * 2)
  ctx.setFillStyle('#F7E7D8')
  ctx.fill()
  ctx.setFillStyle(grade.value === '优' ? '#2F6B3A' : '#1E5FA8')
  ctx.setFontSize(22)
  ctx.fillText(grade.value, cx, cy - 3)
  ctx.setFontSize(12)
  ctx.fillText(passed.value.result.overall_score + ' 分', cx, cy + 22)

  // 卡片文案
  ctx.setFillStyle('rgba(255,246,236,0.9)')
  ctx.setFontSize(12)
  ctx.setTextAlign('left')
  wrapText(ctx, summary.value || '', 34, cy + r + 46, W - 68, 20)

  ctx.setFillStyle('rgba(255,246,236,0.66)')
  ctx.setFontSize(11)
  ctx.setTextAlign('right')
  ctx.fillText('费曼实验课 · ' + today.value, W - 24, H - 22)

  ctx.draw(false, () => {
    uni.canvasToTempFilePath({
      canvasId: 'card',
      x: 0, y: 0, width: W, height: H,
      destWidth: W * 2,
      destHeight: H * 2,
      success: (res) => {
        uni.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => uni.showToast({ title: '分享卡已存到相册', icon: 'none' }),
          fail: () => uni.showToast({ title: '保存失败，可用系统分享', icon: 'none' }),
        })
      },
      fail: () => uni.showToast({ title: '图片生成失败', icon: 'none' }),
    }, instance.proxy)
  })
}

function makeCard() {
  // canvas 需先布局完成，延迟一帧再画
  setTimeout(drawCard, 60)
}

function share() {
  const content = `我的理解：${session.topic}（${grade.value} ${passed.value.result.overall_score}分）\n\n${finalText.value}\n\n—— 费曼实验课`
  uni.shareWithSystem({
    type: 'text',
    summary: content,
    success: () => {},
    fail: () => copy(content, '已复制，可手动粘贴分享'),
  })
}

function another() { resetSession(); loadDaily(); uni.reLaunch({ url: '/pages/bench/bench' }) }
function goHome() { another() }
</script>

<style scoped>
.display { display: block; margin-bottom: 24rpx; }
.grade-row { display: flex; align-items: center; gap: 20rpx; }
.score { color: var(--teal); }

.sec { margin-top: 56rpx; }

.preview { padding: 32rpx; }
.line { display: flex; margin-bottom: 20rpx; }
.k { display: inline-block; width: 150rpx; flex-shrink: 0; color: var(--ink-3); }
.v { flex: 1; font-size: 26rpx; line-height: 1.75; color: var(--ink-2); }
.body-text {
  background: var(--paper-sunken);
  border-left: 5rpx solid var(--accent);
  border-radius: var(--r-md);
  padding: 26rpx;
  font-size: 26rpx;
  line-height: 1.9;
  color: var(--ink);
}
.tags { display: flex; gap: 12rpx; margin-top: 20rpx; flex-wrap: wrap; }

.exports { display: flex; flex-wrap: wrap; gap: 20rpx; }
.exp {
  width: calc(50% - 10rpx);
  box-sizing: border-box;
  background: var(--paper-raised);
  border: 1rpx solid var(--rule);
  border-radius: var(--r-md);
  padding: 26rpx;
}
.exp:active { border-color: var(--accent); background: var(--accent-soft); }
.exp-k { display: block; margin-bottom: 6rpx; }
.exp-b { display: block; font-size: 28rpx; font-weight: 700; margin-bottom: 4rpx; }
.exp-d { display: block; font-size: 21rpx; color: var(--ink-3); }
.exp.accent .exp-b { color: var(--accent); }
.tip { display: block; margin-top: 20rpx; }

.demo-lead { display: block; font-size: 26rpx; line-height: 1.8; color: var(--ink-2); margin-bottom: 26rpx; }
.demo-err { color: var(--accent-ink); font-size: 25rpx; }
.demo-oneliner { padding-bottom: 20rpx; border-bottom: 1rpx dashed var(--rule-2); margin-bottom: 20rpx; }
.oneliner { display: block; font-family: var(--font-display); font-size: 32rpx; line-height: 1.6; margin-top: 8rpx; }
.demo-line { display: flex; margin-bottom: 20rpx; }
.demo-text {
  background: var(--paper-sunken);
  border-left: 5rpx solid var(--teal);
  border-radius: var(--r-md);
  padding: 26rpx;
  font-size: 26rpx;
  line-height: 1.95;
  color: var(--ink);
}
.demo-pit {
  display: flex;
  margin-top: 20rpx;
  background: var(--accent-soft);
  border-radius: var(--r-sm);
  padding: 20rpx;
}
.demo-foot { margin-top: 26rpx; }

.actions { margin-top: 56rpx; display: flex; flex-direction: column; gap: 20rpx; }

.offscreen { position: fixed; left: -99999rpx; top: 0; }
</style>
