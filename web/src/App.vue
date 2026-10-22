<template>
  <div class="shell">
    <!-- 左侧导航轨 -->
    <nav class="rail">
      <button
        class="brand-mark"
        :title="session.step === 'bench' ? '' : '返回实验台'"
        @click="goHome"
      >
        <span class="glyph">🧪</span>
        <div>
          <div class="brand-name">费曼实验课</div>
          <div class="brand-tag">讲不明白，就是没搞懂</div>
        </div>
      </button>

      <div>
        <div class="eyebrow">实验流程</div>
        <div class="steps">
          <div
            v-for="(s, i) in STEPS"
            :key="s.key"
            class="step"
            :class="{ active: i === current, done: i < current }"
          >
            <span class="step-num">{{ i < current ? '✓' : i + 1 }}</span>
            <span class="step-label">
              <b>{{ s.label }}</b>
              <span>{{ s.hint }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- 题库导航 -->
      <div>
        <div class="eyebrow">题库</div>
        <div class="nav-list">
          <button
            class="nav-item"
            :class="{ on: session.step === 'bank' }"
            @click="open('bank')"
          >
            <span class="ni-ico">📚</span>
            <span class="ni-label">全部课题</span>
            <b class="mono-lg">{{ allCount }}</b>
          </button>
          <button
            class="nav-item"
            :class="{ on: session.step === 'favorites' }"
            @click="open('favorites')"
          >
            <span class="ni-ico">★</span>
            <span class="ni-label">我的收藏</span>
            <b class="mono-lg">{{ session.favorites.length }}</b>
          </button>
        </div>
      </div>

      <div class="rail-foot">
        <button class="stat stat-btn" @click="open('bank')" title="打开题库">
          <span>底库</span><b class="mono-lg">{{ baseCount ?? '—' }}</b>
        </button>
        <div class="stat"><span>今日课题</span><b class="mono-lg">{{ session.dailyTopics.length || '—' }}</b></div>
        <div class="stat"><span>{{ today }}</span></div>
      </div>
    </nav>

    <!-- 主区 -->
    <main class="main" :key="session.step">
      <div v-if="session.error" class="panel anim d1" style="border-color:var(--accent);background:var(--accent-soft);margin-bottom:var(--s-6);">
        <b style="color:var(--accent-ink)">实验中断</b>
        <div class="muted" style="font-size:14px;">{{ session.error }}</div>
      </div>

      <LabBench v-if="session.step === 'bench'" />
      <Narration v-else-if="session.step === 'narration'" />
      <Report v-else-if="session.step === 'report'" />
      <Graduation v-else-if="session.step === 'graduation'" />
      <TopicBank v-else-if="session.step === 'bank'" />
      <Favorites v-else-if="session.step === 'favorites'" />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { session, loadDaily, resetSession, loadAllTopics } from './store.js'
import * as api from './api.js'
import LabBench from './views/LabBench.vue'
import Narration from './views/Narration.vue'
import Report from './views/Report.vue'
import Graduation from './views/Graduation.vue'
import TopicBank from './views/TopicBank.vue'
import Favorites from './views/Favorites.vue'

const STEPS = [
  { key: 'bench',      label: '今日课题', hint: '选一个要讲的概念' },
  { key: 'narration',  label: '裸讲',     hint: '不查资料，先讲一遍' },
  { key: 'report',     label: '实验报告', hint: '外行视角的四维评价' },
  { key: 'graduation', label: '结业产出', hint: '文字 / MD / 图片卡' },
]

const ORDER = ['bench', 'narration', 'report', 'graduation']
const current = computed(() => ORDER.indexOf(session.step))

const baseCount = ref(null)
const allCount = computed(() => session.allTopics.length || baseCount.value || 0)
const today = computed(() => new Date().toISOString().slice(0, 10))

function goHome() {
  resetSession()
  loadDaily()
}

function open(step) {
  session.error = ''
  session.step = step
  loadAllTopics()
}

onMounted(async () => {
  loadDaily()
  try {
    const h = await api.getHealth()
    baseCount.value = h.topics
  } catch (e) { /* 后端未启动时静默 */ }
})
</script>

<style scoped>
/* 品牌区：可点击返回实验台 */
.brand-mark {
  font: inherit;
  background: none;
  border: 0;
  padding: 0;
  text-align: left;
  cursor: pointer;
  transition: opacity var(--dur-2) var(--ease-out-quart);
}
.brand-mark:hover { opacity: 0.7; }
.brand-mark:active { opacity: 0.5; }

/* 题库导航 */
.nav-list { display: flex; flex-direction: column; gap: 2px; }
.nav-item {
  display: flex; align-items: center; gap: var(--s-3);
  font: inherit; text-align: left;
  background: none; border: 1px solid transparent; border-radius: var(--r-md);
  padding: 9px var(--s-3); cursor: pointer; color: var(--ink-2);
  transition: all var(--dur-2) var(--ease-out-quart);
}
.nav-item:hover { background: var(--paper-raised); border-color: var(--rule); }
.nav-item.on {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent-ink);
  font-weight: 600;
}
.ni-ico { font-size: 15px; }
.ni-label { flex: 1; font-size: 14px; }
.nav-item b { font-size: 13px; color: var(--ink-3); }
.nav-item.on b { color: var(--accent-ink); }

/* 底库可点 */
.stat-btn {
  font: inherit; width: 100%;
  background: none; border: 0; padding: 3px 0;
  cursor: pointer; color: var(--ink-3);
  transition: color var(--dur-2) var(--ease-out-quart);
}
.stat-btn:hover { color: var(--accent); }
</style>
