<template>
  <view class="page" v-if="result">
    <text class="eyebrow anim d1">实验报告 · 第 {{ roundNo }} 轮</text>

    <!-- 分数 -->
    <view class="score-hero anim d2">
      <view class="score-main">
        <text class="score-num">{{ shownScore }}</text>
        <text class="score-max mono">/ 100</text>
      </view>
      <view class="score-side">
        <GradeBadge :grade="result.grade" />
        <text class="mono" style="display:block;margin-top:12rpx;">{{ GRADE_LABEL[result.grade] }}</text>
        <text v-if="result.boundary_recheck === true" class="mono muted-2" style="display:block;margin-top:6rpx;">
          边界分 · 二次评价取中
        </text>
      </view>
    </view>

    <view class="bar anim d3"><view class="bar-in" :style="{ width: pct + '%' }"></view></view>

    <text class="pull anim d4">{{ result.summary }}</text>

    <!-- 四维 -->
    <text class="eyebrow sec">四维评分 · 各 25 分</text>
    <view class="panel radar-card anim d5">
      <RadarChart :data="radarData" :size="260" />
      <view class="dim-list">
        <view v-for="(d, i) in dims" :key="d.key" class="dim" :style="{ animationDelay: 520 + i * 70 + 'ms' }">
          <text class="dim-label">{{ d.label }}</text>
          <text class="dim-score mono-lg">{{ d.score }}</text>
          <text class="dim-max">/25</text>
        </view>
      </view>
    </view>

    <!-- 卡点 -->
    <text class="eyebrow sec">卡点清单 · 外行听不懂的地方</text>
    <view v-if="!cardPoints.length" class="panel muted">
      <text>暂未标出明显卡点，继续保持。</text>
    </view>
    <view v-else class="cps">
      <view
        v-for="(c, i) in cardPoints"
        :key="i"
        class="cp anim"
        :style="{ animationDelay: 480 + i * 90 + 'ms' }"
      >
        <text class="cp-idx mono">卡点 {{ pad(i + 1) }}</text>
        <text class="quote">{{ c.quote }}</text>
        <view class="cp-line"><text class="k mono">哪里讲不通</text><text class="v">{{ c.issue }}</text></view>
        <view class="cp-line"><text class="k mono">改进方向</text><text class="v hint">{{ c.hint_direction }}</text></view>

        <!-- L2 结构提示 -->
        <view v-if="c.structure_hint && c.structure_hint.length" class="skel">
          <text class="skel-title mono">及格改法 · 至少说清这 {{ c.structure_hint.length }} 点</text>
          <view v-for="(s, j) in c.structure_hint" :key="j" class="skel-item">
            <text class="sk-n mono">{{ j + 1 }}</text>
            <text class="sk-t">{{ s }}</text>
          </view>
        </view>

        <!-- L3 一句起头（第 3 轮起解锁） -->
        <view v-if="starterUnlocked && c.starter_line" class="starter">
          <text v-if="!revealed[i]" class="starter-btn mono" @click="reveal(i)">
            还是开不了口？看一句起头 →
          </text>
          <view v-else class="starter-body anim">
            <text class="mono muted-2">起头示范 · 只有一句</text>
            <text class="starter-line">{{ c.starter_line }}</text>
            <text class="mono muted-2">后面的话，得你自己说。</text>
          </view>
        </view>
      </view>
    </view>

    <view v-if="result.progress_note" class="panel note anim d6">
      <text class="mono" style="display:block;margin-bottom:10rpx;">与上轮对比</text>
      <text>{{ result.progress_note }}</text>
    </view>

    <!-- 历轮 -->
    <template v-if="session.rounds.length > 1">
      <text class="eyebrow sec">实验记录本 · 历轮</text>
      <view class="history anim d6">
        <view v-for="(r, i) in session.rounds" :key="i" class="chip">
          <text class="mono">R{{ i + 1 }}</text>
          <GradeBadge :grade="r.result.grade" />
          <text class="mono-lg">{{ r.result.overall_score }}</text>
        </view>
      </view>
    </template>

    <view class="actions anim d6">
      <button class="btn-primary btn-xl" @click="revise">修正重讲 · 第 {{ roundNo + 1 }} 轮 →</button>
      <button class="btn-ghost btn-xl" @click="goHome">← 返回实验台</button>
    </view>
    <text class="mono muted-2 tip">中 / 差不代表失败 —— 对着卡点补一课再讲，越讲越透。</text>
  </view>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { session, reviseRound, resetSession, loadDaily, GRADE_LABEL } from '../../store.js'
import RadarChart from '../../components/RadarChart.vue'
import GradeBadge from '../../components/GradeBadge.vue'

const result = computed(() => session.rounds[session.rounds.length - 1].result)
const roundNo = computed(() => session.rounds.length)
const cardPoints = computed(() => result.value.card_points || [])
const pct = computed(() => Math.max(0, Math.min(100, result.value.overall_score || 0)))

const dims = computed(() => {
  const d = result.value.dimensions
  return [
    { key: 'simplicity', label: '简洁性', score: d.simplicity.score },
    { key: 'completeness', label: '完整性', score: d.completeness.score },
    { key: 'logic', label: '逻辑性', score: d.logic.score },
    { key: 'analogy', label: '比喻力', score: d.analogy.score },
  ]
})
const radarData = computed(() => dims.value.map((d) => ({ label: d.label, score: d.score, max: 25 })))

/* L3：第 3 轮报告起才解锁一句起头 */
const starterUnlocked = computed(() => roundNo.value >= 3)
const revealed = ref([])
function reveal(i) { revealed.value[i] = true }

/* 分数滚动 */
const shownScore = ref(0)
function animateTo(target) {
  if (typeof requestAnimationFrame === 'undefined') { shownScore.value = target; return }
  const start = shownScore.value
  const dur = 900
  const t0 = Date.now()
  function frame() {
    const p = Math.min(1, (Date.now() - t0) / dur)
    const e = 1 - Math.pow(2, -10 * p)
    shownScore.value = Math.round(start + (target - start) * e)
    if (p < 1) requestAnimationFrame(frame)
  }
  requestAnimationFrame(frame)
}
onMounted(() => animateTo(result.value.overall_score || 0))

function pad(n) { return String(n).padStart(2, '0') }

function revise() {
  reviseRound()
  uni.redirectTo({ url: '/pages/narration/narration' })
}
function goHome() {
  resetSession()
  loadDaily()
  uni.reLaunch({ url: '/pages/bench/bench' })
}
</script>

<style scoped>
.score-hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 24rpx; margin: 8rpx 0 24rpx; }
.score-main { display: flex; align-items: baseline; gap: 12rpx; }
.score-num {
  font-family: var(--font-display);
  font-size: 120rpx;
  font-weight: 700;
  line-height: 0.9;
  color: var(--ink);
}
.score-max { font-size: 24rpx; }
.score-side { text-align: right; padding-bottom: 10rpx; }

.bar { height: 8rpx; background: var(--paper-sunken); border-radius: 999rpx; overflow: hidden; margin-bottom: 32rpx; }
.bar-in { height: 100%; background: var(--accent); border-radius: 999rpx; }

.sec { margin-top: 56rpx; }

.radar-card { padding: 32rpx 24rpx; }
.dim-list { display: flex; justify-content: space-around; margin-top: 24rpx; padding-top: 24rpx; border-top: 1rpx dashed var(--rule-2); }
.dim { display: flex; align-items: baseline; gap: 8rpx; }
.dim-label { font-size: 24rpx; color: var(--ink-2); }
.dim-score { color: var(--teal); }
.dim-max { font-size: 20rpx; color: var(--ink-3); }

.cps { display: flex; flex-direction: column; gap: 28rpx; }
.cp {
  background: var(--paper-raised);
  border: 1rpx solid var(--rule);
  border-left: 5rpx solid var(--accent);
  border-radius: var(--r-md);
  padding: 28rpx;
}
.cp-idx { display: block; margin-bottom: 10rpx; }
.quote {
  display: block;
  font-family: var(--font-display);
  font-size: 30rpx;
  line-height: 1.6;
  color: var(--ink);
  margin-bottom: 20rpx;
}
.cp-line { display: flex; margin-bottom: 8rpx; }
.k { display: inline-block; width: 150rpx; flex-shrink: 0; color: var(--ink-3); }
.v { flex: 1; font-size: 25rpx; line-height: 1.75; color: var(--ink-2); }
.v.hint { color: var(--teal); }

.skel {
  margin-top: 24rpx;
  padding: 22rpx;
  background: var(--paper-sunken);
  border: 1rpx dashed var(--rule-2);
  border-radius: var(--r-sm);
}
.skel-title { display: block; margin-bottom: 14rpx; }
.skel-item { display: flex; gap: 14rpx; margin-bottom: 8rpx; }
.sk-n { color: var(--accent); flex-shrink: 0; }
.sk-t { flex: 1; font-size: 25rpx; line-height: 1.75; color: var(--ink-2); }

.starter { margin-top: 24rpx; }
.starter-btn { color: var(--accent); border-bottom: 1rpx dashed var(--accent); display: inline-block; padding-bottom: 4rpx; }
.starter-body {
  padding: 22rpx 24rpx;
  background: var(--accent-soft);
  border-left: 4rpx solid var(--accent);
  border-radius: var(--r-sm);
}
.starter-line {
  display: block;
  font-family: var(--font-display);
  font-size: 30rpx;
  line-height: 1.7;
  color: var(--ink);
  margin: 10rpx 0;
}

.note { margin-top: 40rpx; font-size: 26rpx; line-height: 1.85; color: var(--ink-2); }

.history { display: flex; flex-wrap: wrap; gap: 16rpx; }
.chip {
  display: flex;
  align-items: center;
  gap: 14rpx;
  background: var(--paper-sunken);
  border: 1rpx solid var(--rule);
  border-radius: 999rpx;
  padding: 8rpx 22rpx;
}

.actions { margin-top: 56rpx; display: flex; flex-direction: column; gap: 20rpx; }
.tip { display: block; margin-top: 24rpx; }
</style>
