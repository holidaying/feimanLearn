<template>
  <section v-if="result">
    <div class="head-row anim d1">
      <div class="eyebrow" style="flex:1;margin:0;">实验报告 · 第 {{ roundNo }} 轮</div>
      <button class="btn-ghost btn-sm" @click="changeTopic">← 返回实验台</button>
    </div>

    <!-- 焦点：分数 -->
    <div class="score-hero anim d2">
      <div class="score-main">
        <span class="score-num">{{ shownScore }}</span>
        <span class="score-max mono">/ 100</span>
      </div>
      <div class="score-side">
        <GradeBadge :grade="result.grade" size="lg" />
        <div class="mono" style="margin-top: 8px;">
          {{ GRADE_LABEL[result.grade] }}
        </div>
        <div v-if="result.boundary_recheck === true" class="mono muted-2" style="margin-top: 4px;">
          边界分 · 二次评价取中
        </div>
      </div>
    </div>

    <!-- 分数条：擦除动画 -->
    <div class="bar anim d3"><span :style="{ width: pct + '%' }"></span></div>

    <p class="summary pull anim d4">{{ result.summary }}</p>

    <!-- 四维雷达 -->
    <div class="eyebrow" style="margin-top: var(--s-8);">四维评分 · 各 25 分</div>
    <div class="panel radar-card anim d5">
      <RadarChart :data="radarData" :size="280" />
      <div class="dim-list">
        <div v-for="(d, i) in dims" :key="d.key" class="dim anim" :style="{ animationDelay: 520 + i * 70 + 'ms' }">
          <span class="dim-label">{{ d.label }}</span>
          <span class="dim-score mono-lg">{{ d.score }}</span>
          <span class="dim-max">/25</span>
        </div>
      </div>
    </div>

    <!-- 卡点清单 -->
    <div class="eyebrow" style="margin-top: var(--s-8);">卡点清单 · 外行听不懂的地方</div>
    <div v-if="!cardPoints.length" class="pull muted">
      暂未标出明显卡点，继续保持。
    </div>
    <div v-else class="cps">
      <div
        v-for="(c, i) in cardPoints"
        :key="i"
        class="cp anim"
        :style="{ animationDelay: 480 + i * 90 + 'ms' }"
      >
        <div class="cp-idx mono">卡点 {{ String(i + 1).padStart(2, '0') }}</div>
        <blockquote class="quote">{{ c.quote }}</blockquote>
        <div class="cp-line"><b class="mono">哪里讲不通</b>{{ c.issue }}</div>
        <div class="cp-line hint"><b class="mono">改进方向</b>{{ c.hint_direction }}</div>

        <!-- 方案 B：结构提示（只给骨架，不给内容） -->
        <div v-if="c.structure_hint && c.structure_hint.length" class="skel">
          <div class="skel-title mono">及格改法 · 至少说清这 {{ c.structure_hint.length }} 点</div>
          <ol class="skel-list">
            <li v-for="(s, j) in c.structure_hint" :key="j">{{ s }}</li>
          </ol>
        </div>

        <!-- 方案 C：多轮仍卡住，才给一句起头 -->
        <div v-if="starterUnlocked && c.starter_line" class="starter">
          <button v-if="!revealed.has(i)" class="starter-btn mono" @click="reveal(i)">
            还是开不了口？看一句起头 →
          </button>
          <div v-else class="starter-body anim fade">
            <span class="mono muted-2">起头示范 · 只有一句</span>
            <p class="starter-line">{{ c.starter_line }}</p>
            <span class="mono muted-2">后面的话，得你自己说。</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="result.progress_note" class="panel note anim d6">
      <div class="mono" style="margin-bottom: 6px;">与上轮对比</div>
      {{ result.progress_note }}
    </div>

    <div v-if="session.rounds.length > 1" class="eyebrow" style="margin-top: var(--s-8);">实验记录本 · 历轮</div>
    <div v-if="session.rounds.length > 1" class="history anim d6">
      <span v-for="(r, i) in session.rounds" :key="i" class="chip">
        <span class="mono">R{{ i + 1 }}</span>
        <GradeBadge :grade="r.result.grade" size="sm" />
        <b class="mono-lg">{{ r.result.overall_score }}</b>
      </span>
    </div>

    <div class="actions anim d6">
      <button class="btn-primary btn-xl" @click="revise">
        修正重讲 · 第 {{ roundNo + 1 }} 轮 →
      </button>
    </div>
    <p class="mono muted-2" style="margin-top: var(--s-4);">
      中 / 差不代表失败 —— 对着卡点补一课再讲，越讲越透。
    </p>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { session, reviseRound, resetSession, loadDaily, GRADE_LABEL } from '../store.js'
import RadarChart from '../components/RadarChart.vue'
import GradeBadge from '../components/GradeBadge.vue'

const result = computed(() => session.rounds[session.rounds.length - 1].result)
const roundNo = computed(() => session.rounds.length)
const cardPoints = computed(() => result.value.card_points || [])
const pct = computed(() => Math.max(0, Math.min(100, result.value.overall_score || 0)))

/* 方案 C：同一卡点连改两轮还卡着（第 3 轮报告）才解锁「一句起头」 */
const starterUnlocked = computed(() => roundNo.value >= 3)
const revealed = ref(new Set())
function reveal(i) {
  const s = new Set(revealed.value)
  s.add(i)
  revealed.value = s
}

const dims = computed(() => {
  const d = result.value.dimensions
  return [
    { key: 'simplicity',   label: '简洁性', score: d.simplicity.score },
    { key: 'completeness', label: '完整性', score: d.completeness.score },
    { key: 'logic',        label: '逻辑性', score: d.logic.score },
    { key: 'analogy',      label: '比喻力', score: d.analogy.score },
  ]
})
const radarData = computed(() => dims.value.map((d) => ({ label: d.label, score: d.score, max: 25 })))

/* 分数滚动 */
const shownScore = ref(0)
const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

function animateTo(target) {
  if (reduce) { shownScore.value = target; return }
  const start = shownScore.value
  const dur = 900
  const t0 = performance.now()
  function frame(now) {
    const p = Math.min(1, (now - t0) / dur)
    const e = 1 - Math.pow(2, -10 * p) // ease-out-expo
    shownScore.value = Math.round(start + (target - start) * e)
    if (p < 1) requestAnimationFrame(frame)
  }
  requestAnimationFrame(frame)
}
watch(() => result.value.overall_score, (v) => animateTo(v || 0), { immediate: true })
watch(roundNo, () => { revealed.value = new Set() })

function revise() { reviseRound() }
function changeTopic() { resetSession(); loadDaily() }
</script>

<style scoped>
/* 顶部返回行 */
.head-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--s-4); flex-wrap: wrap;
}
.btn-sm { padding: 7px 14px; font-size: 13px; }

/* 分数英雄区 */
.score-hero {
  display: flex; align-items: flex-end; gap: var(--s-6);
  flex-wrap: wrap; margin: var(--s-4) 0 var(--s-4);
}
.score-main { display: flex; align-items: baseline; gap: var(--s-3); }
.score-num {
  font-family: var(--font-display);
  font-size: clamp(72px, 11vw, 132px);
  font-weight: 700; line-height: 0.9;
  letter-spacing: -0.04em;
  color: var(--ink);
}
.score-max { font-size: 18px; }
.score-side { padding-bottom: 10px; }

/* 分数条 */
.bar {
  height: 6px; background: var(--paper-sunken);
  border-radius: 999px; overflow: hidden;
  max-width: 560px; margin-bottom: var(--s-6);
}
.bar span {
  display: block; height: 100%;
  background: var(--accent);
  transform-origin: left;
  animation: wipe var(--dur-5) var(--ease-out-expo) 240ms both;
}

.summary {
  font-size: 17px; line-height: 1.8; color: var(--ink-2);
  max-width: 66ch; margin: 0;
}

/* 雷达 */
.radar-card { padding: var(--s-6); }
.dim-list {
  display: flex; justify-content: center; gap: var(--s-6);
  flex-wrap: wrap; margin-top: var(--s-4);
  padding-top: var(--s-4); border-top: 1px dashed var(--rule-2);
}
.dim { display: flex; align-items: baseline; gap: 6px; }
.dim-label { font-size: 14px; color: var(--ink-2); }
.dim-score { font-weight: 700; color: var(--teal); }
.dim-max { font-size: 12px; color: var(--ink-3); }

/* 卡点 */
.cps { display: flex; flex-direction: column; gap: var(--s-5); }
.cp {
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  border-left: 3px solid var(--accent);
  border-radius: var(--r-md);
  padding: var(--s-5);
}
.cp-idx { margin-bottom: var(--s-2); }
.quote {
  margin: 0 0 var(--s-4);
  font-family: var(--font-display);
  font-size: 19px; line-height: 1.6; color: var(--ink);
}
.cp-line { font-size: 14px; line-height: 1.7; color: var(--ink-2); margin-bottom: 4px; }
.cp-line b {
  display: inline-block; min-width: 92px; margin-right: var(--s-3);
  font-weight: 700; color: var(--ink-3);
}
.cp-line.hint { color: var(--teal); }

/* 方案 B · 结构提示 */
.skel {
  margin-top: var(--s-4); padding: var(--s-4) var(--s-4) var(--s-4) var(--s-5);
  background: var(--paper-sunken);
  border: 1px dashed var(--rule-2);
  border-radius: var(--r-sm);
}
.skel-title { font-size: 12px; color: var(--ink-3); letter-spacing: .06em; margin-bottom: var(--s-3); }
.skel-list { margin: 0; padding-left: 1.4em; }
.skel-list li {
  font-size: 14px; line-height: 1.8; color: var(--ink-2);
  margin-bottom: 2px;
}
.skel-list li::marker { color: var(--accent); font-family: var(--font-mono); font-size: 12px; }

/* 方案 C · 一句起头（折叠） */
.starter { margin-top: var(--s-4); }
.starter-btn {
  background: none; border: none; padding: 0;
  font-size: 12px; letter-spacing: .05em; color: var(--accent);
  cursor: pointer; border-bottom: 1px dashed var(--accent);
  transition: opacity var(--dur-2) var(--ease-out);
}
.starter-btn:hover { opacity: .65; }
.starter-body {
  padding: var(--s-4) var(--s-5);
  background: color-mix(in srgb, var(--accent) 6%, var(--paper-raised));
  border-left: 2px solid var(--accent);
  border-radius: var(--r-sm);
}
.starter-line {
  font-family: var(--font-display);
  font-size: 18px; line-height: 1.7; color: var(--ink);
  margin: 6px 0;
}

.note { padding: var(--s-5); font-size: 15px; line-height: 1.8; color: var(--ink-2); }

.history { display: flex; gap: var(--s-3); flex-wrap: wrap; }
.chip {
  display: inline-flex; align-items: center; gap: var(--s-3);
  background: var(--paper-sunken); border: 1px solid var(--rule);
  border-radius: 999px; padding: 5px 14px;
}

.actions {
  display: flex; align-items: center; gap: var(--s-4);
  flex-wrap: wrap; margin-top: var(--s-8);
}
</style>
