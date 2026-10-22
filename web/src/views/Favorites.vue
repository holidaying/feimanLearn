<template>
  <section>
    <div class="head-row anim d1">
      <div class="eyebrow" style="flex:1;margin:0;">我的收藏</div>
      <button class="btn-ghost btn-sm" @click="goBack">← 返回实验台</button>
    </div>

    <h1 class="display-sm anim d2" style="margin-top: var(--s-4);">
      收藏的课题
      <span class="mono-lg" style="margin-left: var(--s-3); color: var(--ink-3);">{{ session.favorites.length }} 条</span>
    </h1>

    <p v-if="!session.favorites.length" class="pull muted anim d3" style="margin-top: var(--s-6);">
      还没有收藏。去<strong>题库</strong>点 ☆ 把想练的课题存到这里，方便随时开讲。
    </p>

    <ol v-else class="favs">
      <li
        v-for="(t, i) in session.favorites"
        :key="t.title + i"
        class="row anim"
        :style="{ animationDelay: Math.min(i, 14) * 40 + 'ms' }"
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
          <div class="marks">
            <span v-if="practicedOf(t.title)" class="mark done">
              ✓ 已实验 · {{ practicedOf(t.title).grade }} <b>{{ practicedOf(t.title).score }}</b>
            </span>
            <span v-else class="mark todo">尚未实验</span>
          </div>
        </div>

        <button class="star on" title="取消收藏" @click.stop="toggleFavorite(t)">★</button>
      </li>
    </ol>

    <div v-if="session.favorites.length" class="actions anim d4">
      <button class="btn-ghost" @click="openBank">去题库挑题 →</button>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import {
  session, enterTopic, toggleFavorite, practicedOf,
  loadAllTopics, resetSession, loadDaily,
} from '../store.js'

onMounted(loadAllTopics)

function goBack() { resetSession(); loadDaily() }
function openBank() { session.step = 'bank'; loadAllTopics() }
</script>

<style scoped>
.head-row { display: flex; align-items: center; justify-content: space-between; gap: var(--s-4); flex-wrap: wrap; }
.btn-sm { padding: 7px 14px; font-size: 13px; }

.favs { list-style: none; margin: var(--s-6) 0 0; padding: 0; }
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

.marks { display: flex; gap: var(--s-3); flex-wrap: wrap; }
.mark { font-size: 12px; padding: 2px 9px; border-radius: var(--r-sm); }
.mark.done { background: var(--teal-soft); color: var(--teal); }
.mark.done b { font-family: var(--font-mono); }
.mark.todo { background: var(--paper-sunken); color: var(--ink-3); }

.star {
  justify-self: end; background: none; border: 0; cursor: pointer;
  font-size: 20px; line-height: 1; padding: 4px; color: var(--accent);
  transition: transform var(--dur-2) var(--ease-out-quart), color var(--dur-2) var(--ease-out-quart);
}
.star:hover { transform: scale(1.15); color: var(--accent-ink); }

.actions { margin-top: var(--s-7); }
</style>
