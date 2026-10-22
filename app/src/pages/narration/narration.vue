<template>
  <view class="page">
    <!-- 课题 -->
    <view class="anim d1">
      <text class="eyebrow">第 {{ roundNo }} 轮讲述 · 不查资料</text>
      <text class="display-sm">{{ session.topic }}</text>
      <text class="bg">{{ session.background }}</text>
    </view>

    <!-- 引导问题 -->
    <view v-if="session.guideQuestions.length" class="panel guides anim d2">
      <text class="eyebrow">可以顺着这几个方向讲</text>
      <text v-for="(q, i) in session.guideQuestions" :key="i" class="gq">· {{ q }}</text>
    </view>

    <!-- 输入 -->
    <view class="anim d3">
      <textarea
        class="input"
        v-model="text"
        placeholder="把它讲给一个完全不懂的人听。用大白话，别用术语。"
        placeholder-class="ph"
        :maxlength="2000"
        auto-height
      />
      <view class="meta">
        <text class="mono muted-2">{{ text.length }} 字</text>
        <text class="mono muted-2">建议 150–400 字</text>
      </view>
    </view>

    <!-- 语音 -->
    <view v-if="speechOk" class="voice anim d4" :class="{ rec: listening }" @click="toggleVoice">
      <text class="dot" :class="{ on: listening }"></text>
      <text class="v-txt">{{ listening ? '正在听… 点击停止' : '🎙 语音讲述' }}</text>
    </view>

    <view v-if="session.error" class="panel err anim d4">
      <text class="err-d">{{ session.error }}</text>
    </view>

    <!-- 操作 -->
    <view class="actions anim d5">
      <button class="btn-primary btn-xl" :disabled="!canSubmit || session.loading" @click="submit">
        {{ session.loading ? '外行正在听…' : '提交 · 交给外行打分' }}
      </button>
      <button class="btn-ghost btn-xl" @click="goBack">← 返回实验台</button>
    </view>

    <text class="tip mono muted-2">先讲完再查资料。讲错不是失败，是拿到了实验数据。</text>
  </view>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { onBackPress } from '@dcloudio/uni-app'
import { session, submitRound, resetSession, loadDaily } from '../../store.js'
import * as speech from '../../utils/speech.js'

const text = ref('')
const listening = ref(false)
const speechOk = ref(speech.isSupported())

const roundNo = computed(() => session.rounds.length + 1)
const canSubmit = computed(() => text.value.trim().length >= 10)

function toggleVoice() {
  if (listening.value) {
    listening.value = false
    speech.stop()
    return
  }
  listening.value = true
  speech.start({
    onPartial: (t) => { text.value = t },
    onFinal: (t) => { text.value = (text.value ? text.value : '') + t },
    onEnd: () => { listening.value = false },
    onError: (m) => {
      listening.value = false
      uni.showToast({ title: m, icon: 'none' })
    },
  })
}

async function submit() {
  if (!canSubmit.value || session.loading) return
  if (listening.value) { listening.value = false; speech.stop() }
  const r = await submitRound(text.value.trim(), '')
  if (!r) return
  if (session.step === 'graduation') uni.redirectTo({ url: '/pages/graduation/graduation' })
  else uni.redirectTo({ url: '/pages/report/report' })
}

function goBack() {
  if (text.value.trim().length > 0) {
    uni.showModal({
      title: '放弃这一轮？',
      content: '当前讲述还没有提交，返回实验台会丢失。',
      confirmText: '放弃',
      cancelText: '继续讲',
      success: (res) => { if (res.confirm) doBack() },
    })
  } else doBack()
}

function doBack() {
  if (listening.value) { listening.value = false; speech.stop() }
  resetSession()
  loadDaily()
  uni.reLaunch({ url: '/pages/bench/bench' })
}

onBackPress(() => {
  if (session.topic) { goBack(); return true }
  return false
})

onUnmounted(() => { speech.stop() })
</script>

<style scoped>
.display-sm { display: block; margin: 8rpx 0 20rpx; }
.bg { display: block; font-size: 25rpx; line-height: 1.7; color: var(--ink-2); }

.guides { margin: 40rpx 0; }
.gq { display: block; font-size: 25rpx; line-height: 2; color: var(--ink-2); }

.input {
  width: 100%;
  min-height: 420rpx;
  box-sizing: border-box;
  background: var(--paper-raised);
  border: 1rpx solid var(--rule);
  border-radius: var(--r-md);
  padding: 28rpx;
  font-size: 28rpx;
  line-height: 1.85;
  color: var(--ink);
}
.ph { color: var(--ink-3); }
.meta { display: flex; justify-content: space-between; margin-top: 12rpx; }

.voice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14rpx;
  margin-top: 28rpx;
  border: 1rpx solid var(--rule-2);
  border-radius: var(--r-md);
  padding: 22rpx;
}
.voice.rec { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.dot { width: 14rpx; height: 14rpx; border-radius: 999rpx; background: var(--rule-2); }
.dot.on { background: var(--accent); }
.v-txt { font-size: 27rpx; }

.err { border-color: var(--accent); background: var(--accent-soft); margin-top: 28rpx; }
.err-d { font-size: 24rpx; color: var(--accent-ink); }

.actions { margin-top: 44rpx; display: flex; flex-direction: column; gap: 20rpx; }
.tip { display: block; margin-top: 32rpx; }
</style>
