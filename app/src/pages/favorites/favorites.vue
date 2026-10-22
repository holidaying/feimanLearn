<template>
  <view class="page">
    <text class="eyebrow anim d1">我的收藏 · {{ session.favorites.length }} 条</text>

    <view v-if="!session.favorites.length" class="panel empty anim d2">
      <text class="empty-t">还没有收藏</text>
      <text class="empty-d">在「全部课题」里点右侧的 ☆，把想练的课题攒到这里。</text>
      <button class="btn-primary" style="margin-top:28rpx;" @click="goBank">去题库挑几个 →</button>
    </view>

    <view v-else class="list">
      <view v-for="(t, i) in session.favorites" :key="t.title" class="row" @click="enter(t)">
        <view class="row-main">
          <text class="title">{{ t.title }}</text>
          <text class="bg" numberOfLines="2">{{ t.background }}</text>
          <view class="row-tags">
            <text class="tag tag-base">{{ t.category_label || t.category }}</text>
            <text class="tag">{{ t.difficulty }}</text>
            <text v-if="practicedOf(t.title)" class="tag tag-done">✓ {{ practicedOf(t.title).grade }} {{ practicedOf(t.title).score }} · {{ practicedOf(t.title).rounds }}轮</text>
            <text v-else class="tag">未实验</text>
          </view>
        </view>
        <text class="star on" @click.stop="toggle(t)">★</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { session, enterTopic, toggleFavorite, practicedOf } from '../../store.js'

function toggle(t) { toggleFavorite(t) }
function enter(t) {
  enterTopic(t)
  uni.navigateTo({ url: '/pages/narration/narration' })
}
function goBank() { uni.navigateTo({ url: '/pages/bank/bank' }) }
</script>

<style scoped>
.empty { padding: 40rpx 32rpx; text-align: left; }
.empty-t { display: block; font-family: var(--font-display); font-size: 34rpx; font-weight: 700; margin-bottom: 12rpx; }
.empty-d { display: block; font-size: 25rpx; line-height: 1.8; color: var(--ink-2); }

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
.title { display: block; font-family: var(--font-display); font-size: 30rpx; font-weight: 700; line-height: 1.5; margin-bottom: 8rpx; }
.bg { display: block; font-size: 23rpx; line-height: 1.65; color: var(--ink-2); }
.row-tags { display: flex; flex-wrap: wrap; gap: 10rpx; margin-top: 12rpx; }
.tag-done { background: var(--teal-soft); color: var(--teal); }
.star { font-size: 36rpx; color: var(--accent); padding: 0 6rpx; }
</style>
