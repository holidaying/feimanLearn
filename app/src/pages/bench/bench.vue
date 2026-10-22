<template>
  <view class="page">
    <!-- 品牌 -->
    <view class="brand anim d1">
      <text class="glyph">🧪</text>
      <view>
        <text class="brand-name">费曼实验课</text>
        <text class="brand-tag">讲不明白，就是没搞懂</text>
      </view>
    </view>

    <!-- 英雄区 -->
    <view class="hero anim d2">
      <text class="display">今天，\n讲明白一件事。</text>
      <text class="lead">不查资料，先讲一遍。讲不明白的地方，就是你没真懂的地方。</text>
      <button class="btn-primary btn-xl" :disabled="session.loading" @click="onStart">
        {{ session.loading ? '正在抽取…' : '开始随机实验 →' }}
      </button>
    </view>

    <!-- 快捷入口 -->
    <view class="quick anim d3">
      <view class="q" @click="goBank">
        <text class="q-ico">📚</text>
        <text class="q-label">全部课题</text>
        <text class="q-num">{{ session.allTopics.length || '—' }}</text>
      </view>
      <view class="q" @click="goFav">
        <text class="q-ico">★</text>
        <text class="q-label">我的收藏</text>
        <text class="q-num">{{ session.favorites.length }}</text>
      </view>
    </view>

    <view v-if="session.error" class="panel err">
      <text class="err-t">实验中断</text>
      <text class="err-d">{{ session.error }}</text>
    </view>

    <!-- 今日课题 -->
    <text class="eyebrow sec">今日课题 · {{ session.dailyTopics.length }} 条</text>
    <view v-if="!session.dailyTopics.length" class="panel muted">
      <text>{{ session.loading ? '正在加载课题…' : '暂无课题，请检查后端服务' }}</text>
    </view>
    <view v-else class="list">
      <view
        v-for="(t, i) in session.dailyTopics"
        :key="t.title"
        class="row anim"
        :style="{ animationDelay: 320 + i * 60 + 'ms' }"
        @click="enter(t)"
      >
        <text class="idx">{{ pad(i) }}</text>
        <view class="row-main">
          <text class="title">{{ t.title }}</text>
          <text class="bg" numberOfLines="2">{{ t.background }}</text>
          <view class="row-tags">
            <text class="tag" :class="t.source === 'hot' ? 'tag-hot' : 'tag-base'">
              {{ t.category_label || t.category }}
            </text>
            <text class="tag">{{ t.difficulty }}</text>
          </view>
        </view>
        <text class="arrow">›</text>
      </view>
    </view>

    <text class="foot mono muted-2">讲不明白，就是没搞懂</text>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { session, startRandom, enterTopic, loadDaily, loadAllTopics } from '../../store.js'

function pad(i) { return String(i).padStart(2, '0') }

function enter(t) {
  enterTopic(t)
  uni.navigateTo({ url: '/pages/narration/narration' })
}

async function onStart() {
  await startRandom()
  if (session.topic) uni.navigateTo({ url: '/pages/narration/narration' })
}

function goBank() {
  loadAllTopics()
  uni.navigateTo({ url: '/pages/bank/bank' })
}
function goFav() {
  uni.navigateTo({ url: '/pages/favorites/favorites' })
}

onShow(() => {
  if (!session.dailyTopics.length) loadDaily()
})
</script>

<style scoped>
.brand { display: flex; align-items: center; gap: 16rpx; margin-bottom: 48rpx; }
.glyph { font-size: 44rpx; }
.brand-name { display: block; font-family: var(--font-display); font-size: 30rpx; font-weight: 700; }
.brand-tag { display: block; font-size: 20rpx; color: var(--ink-3); }

.hero { margin-bottom: 48rpx; }
.display { display: block; margin-bottom: 24rpx; }
.lead { display: block; font-size: 27rpx; line-height: 1.8; color: var(--ink-2); margin-bottom: 36rpx; }

.quick { display: flex; gap: 20rpx; margin-bottom: 48rpx; }
.q {
  flex: 1;
  background: var(--paper-raised);
  border: 1rpx solid var(--rule);
  border-radius: var(--r-md);
  padding: 24rpx;
}
.q-ico { display: block; font-size: 32rpx; margin-bottom: 8rpx; }
.q-label { display: block; font-size: 25rpx; color: var(--ink-2); }
.q-num { display: block; font-family: var(--font-mono); font-size: 30rpx; font-weight: 700; color: var(--accent); }

.sec { margin-top: 16rpx; }

.list { display: flex; flex-direction: column; }
.row {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  padding: 26rpx 0;
  border-top: 1rpx solid var(--rule);
  border-left: 4rpx solid transparent;
  padding-left: 16rpx;
}
.row:active { background: var(--paper-raised); border-left-color: var(--accent); }
.idx {
  font-family: var(--font-mono);
  font-size: 22rpx;
  color: var(--ink-3);
  padding-top: 8rpx;
}
.row-main { flex: 1; min-width: 0; }
.title {
  display: block;
  font-family: var(--font-display);
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.5;
  margin-bottom: 8rpx;
}
.bg { display: block; font-size: 23rpx; line-height: 1.65; color: var(--ink-2); }
.row-tags { display: flex; gap: 10rpx; margin-top: 12rpx; }
.arrow { font-size: 40rpx; color: var(--rule-2); line-height: 1; padding-top: 6rpx; }

.err { border-color: var(--accent); background: var(--accent-soft); margin-bottom: 32rpx; }
.err-t { display: block; font-weight: 700; color: var(--accent-ink); margin-bottom: 6rpx; }
.err-d { display: block; font-size: 24rpx; color: var(--ink-2); }

.foot { display: block; text-align: center; margin-top: 64rpx; }
</style>
