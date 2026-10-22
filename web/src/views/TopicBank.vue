<template>
  <section>
    <div class="head-row anim d1">
      <div class="eyebrow" style="flex:1;margin:0;">题库 · 全部课题</div>
      <button class="btn-ghost btn-sm" @click="goBack">← 返回实验台</button>
    </div>

    <h1 class="display-sm anim d2" style="margin-top: var(--s-4);">
      历史题库
      <span class="mono-lg" style="margin-left: var(--s-3); color: var(--ink-3);">{{ topics.length }} 条</span>
    </h1>

    <!-- 类型分类 -->
    <div class="filters anim d3">
      <div class="eyebrow" style="margin-bottom: var(--s-3);">按类型</div>
      <div class="chips">
        <button
          v-for="c in categories"
          :key="c.key"
          class="chip-btn"
          :class="{ on: cat === c.key }"
          @click="cat = c.key"
        >
          {{ c.label }}
          <b>{{ c.n }}</b>
        </button>
      </div>

      <div class="eyebrow" style="margin: var(--s-5) 0 var(--s-3);">按状态</div>
      <div class="chips">
        <button
          v-for="s in STATUS"
          :key="s.key"
          class="chip-btn"
          :class="{ on: status === s.key }"
          @click="status = s.key"
        >{{ s.label }}</button>
      </div>
    </div>

    <!-- 列表 -->
    <div v-if="session.loading && !topics.length" class="muted">正在装填题库…</div>
    <div v-else-if="!topics.length" class="pull muted">
      当前筛选下没有课题。换个类型或状态看看。
    </div>

    <ol v-else class="bank">
      <li
        v-for="(t, i) in topics"
        :key="t.title + i"
        class="row anim"
        :style="{ animationDelay: Math.min(i, 14) * 35 + 'ms' }"
        @click="enterTopic(t)"
      >
        <span class="num mono-lg">{{ String(i + 1).padStart(2, '0') }}</span>

        <div class="body">
          <div class="title-row">
            <h3 class="title">{{ t.title }}</h3>
            <span class="tag" :class="t.category === 'hot' ? 'tag-hot' : 'tag-base'">
              {{ t.category_label || (t.category === 'hot' ? '热榜' : '底库') }}
            </span>
            <span class="tag">{{ t.difficulty || '入门' }}</span>
          </div>
          <p class="bg muted">{{ t.background }}</p>

          <!-- 标记：已实验 / 已收藏 -->
          <div class="marks">
            <span v-if="practicedOf(t.title)" class="mark done">
              ✓ 已实验 · {{ practicedOf(t.title).grade }}
              <b>{{ practicedOf(t.title).score }}</b>
              <span class="mono muted-2">· {{ practicedOf(t.title).rounds }} 轮</span>
            </span>
            <span v-if="isFavorite(t.title)" class="mark fav">★ 已收藏</span>
          </div>
        </div>

        <button
          class="star"
          :class="{ on: isFavorite(t.title) }"
          :title="isFavorite(t.title) ? '取消收藏' : '收藏此题'"
          @click.stop="toggleFavorite(t)"
        >{{ isFavorite(t.title) ? '★' : '☆' }}</button>
      </li>
    </ol>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  session, loadAllTopics, enterTopic,
  isFavorite, toggleFavorite, practicedOf, resetSession, loadDaily,
} from '../store.js'

const cat = ref('all')
const status = ref('all')

const STATUS = [
  { key: 'all', label: '全部' },
  { key: 'done', label: '已实验' },
  { key: 'undone', label: '未实验' },
  { key: 'fav', label: '已收藏' },
]

onMounted(loadAllTopics)

const categories = computed(() => {
  const map = new Map()
  for (const t of session.allTopics) {
    const key = t.category || 'base'
    const label = t.category_label || (key === 'hot' ? '热榜' : '底库')
    if (!map.has(key)) map.set(key, { key, label, n: 0 })
    map.get(key).n++
  }
  const list = [...map.values()].sort((a, b) => b.n - a.n)
  return [{ key: 'all', label: '全部', n: session.allTopics.length }, ...list]
})

const topics = computed(() => {
  let list = session.allTopics
  if (cat.value !== 'all') list = list.filter((t) => (t.category || 'base') === cat.value)
  if (status.value === 'done') list = list.filter((t) => practicedOf(t.title))
  else if (status.value === 'undone') list = list.filter((t) => !practicedOf(t.title))
  else if (status.value === 'fav') list = list.filter((t) => isFavorite(t.title))
  return list
})

function goBack() { resetSession(); loadDaily() }
</script>

<style scoped>
.head-row { display: flex; align-items: center; justify-content: space-between; gap: var(--s-4); flex-wrap: wrap; }
.btn-sm { padding: 7px 14px; font-size: 13px; }

.filters { margin: var(--s-6) 0 var(--s-6); }
.chips { display: flex; gap: var(--s-2); flex-wrap: wrap; }
.chip-btn {
  font: inherit; font-size: 13px; font-weight: 600;
  background: var(--paper-raised);
  border: 1px solid var(--rule); border-radius: 999px;
  padding: 6px 14px; cursor: pointer; color: var(--ink-2);
  transition: all var(--dur-2) var(--ease-out-quart);
}
.chip-btn b { font-family: var(--font-mono); font-size: 11px; margin-left: 5px; color: var(--ink-3); }
.chip-btn:hover { border-color: var(--accent); color: var(--accent); }
.chip-btn.on {
  background: var(--accent); border-color: var(--accent); color: #FFF8F0;
}
.chip-btn.on b { color: rgba(255, 248, 240, 0.75); }

.bank { list-style: none; margin: 0; padding: 0; }
.row {
  position: relative;
  display: grid; grid-template-columns: 48px 1fr 40px;
  gap: var(--s-4); align-items: start;
  padding: var(--s-4) var(--s-3);
  border-top: 1px solid var(--rule);
  cursor: pointer;
  transition: background var(--dur-2) var(--ease-out-quart), transform var(--dur-2) var(--ease-out-quart);
}
.row:last-child { border-bottom: 1px solid var(--rule); }
.row::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; background: var(--accent);
  transform: scaleY(0); transform-origin: top;
  transition: transform var(--dur-3) var(--ease-out-expo);
}
.row:hover { background: var(--paper-raised); transform: translateX(3px); }
.row:hover::before { transform: scaleY(1); }

.num { color: var(--ink-3); padding-top: 4px; }
.row:hover .num { color: var(--accent); }

.title-row { display: flex; align-items: center; gap: var(--s-3); flex-wrap: wrap; }
.title { font-family: var(--font-display); font-size: 19px; font-weight: 700; letter-spacing: -0.01em; }
.bg { margin: 5px 0 var(--s-2); font-size: 13px; line-height: 1.6; max-width: 74ch; }

.marks { display: flex; gap: var(--s-3); flex-wrap: wrap; margin-top: 2px; }
.mark { font-size: 12px; padding: 2px 9px; border-radius: var(--r-sm); }
.mark.done { background: var(--teal-soft); color: var(--teal); }
.mark.done b { font-family: var(--font-mono); }
.mark.fav { background: var(--accent-soft); color: var(--accent-ink); }

.star {
  justify-self: end;
  background: none; border: 0; cursor: pointer;
  font-size: 20px; line-height: 1; padding: 4px;
  color: var(--rule-2);
  transition: color var(--dur-2) var(--ease-out-quart), transform var(--dur-2) var(--ease-out-quart);
}
.star:hover { color: var(--accent); transform: scale(1.15); }
.star.on { color: var(--accent); }
</style>
