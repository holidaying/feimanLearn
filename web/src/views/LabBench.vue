<template>
  <section>
    <!-- 英雄区：非对称，左对齐，CTA 是唯一焦点 -->
    <div class="hero">
      <div class="eyebrow anim d1">实验台 · {{ today }}</div>
      <h1 class="display anim d2">
        今天，<br />
        讲明白一件事。
      </h1>
      <p class="lede anim d3">
        每天 10 个课题，随机抽一个。<strong>不查资料</strong>先裸讲一遍，
        让千问扮演那个「听不懂的外行」给你打分 —— 讲错不是失败，是拿到了实验数据。
      </p>
      <button
        class="btn-primary btn-xl anim d4"
        :disabled="session.loading || !session.dailyTopics.length"
        @click="startRandom"
      >
        <span v-if="session.loading">抽取中…</span>
        <span v-else>开始随机实验 →</span>
      </button>
      <div class="hero-note mono anim d5">
        10 条 / 日 · 6 底库 + 4 热榜 · 建议 ≥ 80 字
      </div>
    </div>

    <hr class="rule" style="margin: var(--s-8) 0 var(--s-6);" />

    <!-- 课题索引：记录本式编号列表 -->
    <div class="eyebrow anim d5">今日课题 · {{ session.dailyTopics.length }} 条</div>

    <div v-if="session.loading && !session.dailyTopics.length" class="muted">
      正在准备今日课题…
    </div>
    <div v-else-if="!session.dailyTopics.length" class="pull muted">
      暂无课题。请确认后端已启动（<code>python server/app.py</code>）。
    </div>

    <ol v-else class="index">
      <li
        v-for="(t, i) in session.dailyTopics"
        :key="i"
        class="row anim"
        :style="{ animationDelay: 260 + i * 55 + 'ms' }"
        @click="enterTopic(t)"
      >
        <span class="num mono-lg">{{ String(i + 1).padStart(2, '0') }}</span>
        <div class="body">
          <div class="title-row">
            <h3 class="title">{{ t.title }}</h3>
            <span class="tag" :class="t.category === 'hot' ? 'tag-hot' : 'tag-base'">
              {{ t.category_label || (t.category === 'hot' ? '热榜' : '底库') }}
            </span>
          </div>
          <p class="bg muted">{{ t.background }}</p>
          <div class="meta">
            <span class="tag">{{ t.difficulty || '入门' }}</span>
            <span v-if="(t.guide_questions || [])[0]" class="q muted-2">
              ↳ {{ t.guide_questions[0] }}
            </span>
          </div>
        </div>
        <span class="go">→</span>
      </li>
    </ol>
  </section>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { session, loadDaily, startRandom, enterTopic } from '../store.js'

const today = computed(() => new Date().toISOString().slice(0, 10))

onMounted(() => {
  if (!session.dailyTopics.length) loadDaily()
})
</script>

<style scoped>
.hero { max-width: 720px; }
.hero h1 { margin: 0 0 var(--s-5); }
.lede {
  font-size: 17px; line-height: 1.85; color: var(--ink-2);
  margin: 0 0 var(--s-6); max-width: 62ch;
}
.lede strong { color: var(--ink); border-bottom: 2px solid var(--accent); padding-bottom: 1px; }
.btn-xl { min-width: 300px; }
.hero-note { margin-top: var(--s-4); }

/* 索引列表 */
.index { list-style: none; margin: 0; padding: 0; }
.row {
  position: relative;
  display: grid;
  grid-template-columns: 52px 1fr 32px;
  gap: var(--s-4);
  align-items: start;
  padding: var(--s-5) var(--s-4) var(--s-5) var(--s-3);
  border-top: 1px solid var(--rule);
  cursor: pointer;
  transition: background var(--dur-2) var(--ease-out-quart),
              transform var(--dur-2) var(--ease-out-quart);
}
.row:last-child { border-bottom: 1px solid var(--rule); }
.row::before { /* hover 时左侧琥珀规线 */
  content: "";
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; background: var(--accent);
  transform: scaleY(0); transform-origin: top;
  transition: transform var(--dur-3) var(--ease-out-expo);
}
.row:hover { background: var(--paper-raised); transform: translateX(3px); }
.row:hover::before { transform: scaleY(1); }

.num { color: var(--ink-3); padding-top: 3px; }
.row:hover .num { color: var(--accent); }

.title-row { display: flex; align-items: center; gap: var(--s-3); flex-wrap: wrap; }
.title {
  font-family: var(--font-display);
  font-size: 22px; font-weight: 700; letter-spacing: -0.01em;
}
.bg { margin: 4px 0 var(--s-3); font-size: 14px; line-height: 1.65; max-width: 68ch; }
.meta { display: flex; align-items: center; gap: var(--s-3); flex-wrap: wrap; }
.q { font-size: 13px; font-style: italic; }

.go {
  justify-self: end; padding-top: 4px;
  color: var(--ink-3); font-size: 18px;
  opacity: 0; transform: translateX(-6px);
  transition: all var(--dur-2) var(--ease-out-quart);
}
.row:hover .go { opacity: 1; transform: none; color: var(--accent); }

code { font-family: var(--font-mono); font-size: 13px; background: var(--paper-sunken); padding: 1px 6px; border-radius: var(--r-sm); }
</style>
