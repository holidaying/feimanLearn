<template>
  <view class="page">
    <text class="eyebrow anim d1">全部课题 · {{ count }} 条</text>

    <!-- 类型筛选 -->
    <scroll-view class="chips anim d2" scroll-x>
      <view class="chips-in">
        <text
          v-for="c in cats"
          :key="c.key"
          class="chip"
          :class="{ on: catFilter === c.key }"
          @click="catFilter = c.key"
        >{{ c.label }}</text>
      </view>
    </scroll-view>

    <!-- 状态筛选 -->
    <scroll-view class="chips anim d3" scroll-x>
      <view class="chips-in">
        <text
          v-for="s in STATUSES"
          :key="s.key"
          class="chip"
          :class="{ on: statusFilter === s.key }"
          @click="statusFilter = s.key"
        >{{ s.label }}</text>
      </view>
    </scroll-view>

    <text class="mono muted-2" style="display:block;margin:8rpx 0 24rpx;">
      命中 {{ list.length }} 条
    </text>

    <view v-if="!list.length" class="panel muted">
      <text>没有符合条件的课题，换个筛选试试。</text>
    </view>

    <view v-else class="list">
      <view v-for="(t, i) in list" :key="t.title" class="row" @click="enter(t)">
        <view class="row-main">
          <text class="title">{{ t.title }}</text>
          <text class="bg" numberOfLines="2">{{ t.background }}</text>
          <view class="row-tags">
            <text class="tag tag-base">{{ t.category_label || t.category }}</text>
            <text class="tag">{{ t.difficulty }}</text>
            <text v-if="practicedOf(t.title)" class="tag tag-done">✓ 已实验 · {{ practicedOf(t.title).grade }} {{ practicedOf(t.title).score }} · {{ practicedOf(t.title).rounds }}轮</text>
            <text v-if="isFavorite(t.title)" class="tag tag-fav">★ 已收藏</text>
          </view>
        </view>
        <text class="star" :class="{ on: isFavorite(t.title) }" @click.stop="toggle(t)">
          {{ isFavorite(t.title) ? '★' : '☆' }}
        </text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { session, loadAllTopics, enterTopic, isFavorite, toggleFavorite, practicedOf } from '../../store.js'

const CATS = [
  { key: 'all', label: '全部' },
  { key: 'science', label: '科学常识' },
  { key: 'economy', label: '经济金融' },
  { key: 'tech', label: '技术概念' },
  { key: 'humanities', label: '人文社科' },
  { key: 'life', label: '生活经验' },
  { key: 'career', label: '职场方法' },
]
const STATUSES = [
  { key: 'all', label: '全部' },
  { key: 'done', label: '已实验' },
  { key: 'todo', label: '未实验' },
  { key: 'fav', label: '已收藏' },
]

const catFilter = ref('all')
const statusFilter = ref('all')
const cats = CATS

const count = computed(() => session.allTopics.length)

const list = computed(() => {
  return session.allTopics.filter((t) => {
    if (catFilter.value !== 'all' && t.category !== catFilter.value) return false
    if (statusFilter.value === 'done' && !practicedOf(t.title)) return false
    if (statusFilter.value === 'todo' && practicedOf(t.title)) return false
    if (statusFilter.value === 'fav' && !isFavorite(t.title)) return false
    return true
  })
})

function toggle(t) { toggleFavorite(t) }

function enter(t) {
  enterTopic(t)
  uni.navigateTo({ url: '/pages/narration/narration' })
}

onMounted(() => { loadAllTopics() })
</script>

<style scoped>
.chips { white-space: nowrap; margin-bottom: 16rpx; }
.chips-in { display: flex; flex-direction: row; gap: 14rpx; padding: 4rpx 0; }
.chip {
  display: inline-block;
  flex-shrink: 0;
  font-size: 25rpx;
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  background: var(--paper-sunken);
  color: var(--ink-2);
  border: 1rpx solid transparent;
}
.chip.on { background: var(--accent-soft); color: var(--accent-ink); border-color: var(--accent); }

.list { display: flex; flex-direction: column; }
.row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 26rpx 0;
  border-top: 1rpx solid var(--rule);
  border-left: 4rpx solid transparent;
  padding-left: 14rpx;
}
.row:active { background: var(--paper-raised); border-left-color: var(--accent); }
.row-main { flex: 1; min-width: 0; }
.title {
  display: block;
  font-family: var(--font-display);
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.5;
  margin-bottom: 8rpx;
}
.bg { display: block; font-size: 23rpx; line-height: 1.65; color: var(--ink-2); }
.row-tags { display: flex; flex-wrap: wrap; gap: 10rpx; margin-top: 12rpx; }
.tag-done { background: var(--teal-soft); color: var(--teal); }
.tag-fav { background: var(--accent-soft); color: var(--accent-ink); }
.star { font-size: 36rpx; color: var(--rule-2); padding: 0 6rpx; }
.star.on { color: var(--accent); }
</style>
