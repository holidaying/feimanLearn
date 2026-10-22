<template>
  <section>
    <!-- 顶部：返回出口 -->
    <div class="head-row anim d1">
      <div class="eyebrow" style="flex:1;margin:0;">
        {{ roundNo > 1 ? `第 ${roundNo} 轮讲述 · 修正重讲` : '第一次讲述' }}
      </div>
      <button class="btn-ghost btn-sm" @click="goBack">← 返回实验台</button>
    </div>

    <h1 class="display-sm anim d2" style="margin-top: var(--s-5);">{{ session.topic }}</h1>

    <div class="pull anim d3" style="margin: var(--s-5) 0 var(--s-7);">
      <p class="bg">{{ session.background }}</p>
      <div v-if="session.guideQuestions.length" class="guide">
        <div class="mono" style="margin-bottom: 6px;">热身引导 · 不查资料，凭直觉答</div>
        <ul>
          <li v-for="(q, i) in session.guideQuestions" :key="i">{{ q }}</li>
        </ul>
      </div>
    </div>

    <!-- 讲述输入：页面唯一焦点 -->
    <div class="field anim d4">
      <div class="field-head">
        <label class="mono">你的裸讲</label>
        <button class="voice" :class="{ rec: listening }" @click="toggleVoice">
          <span v-if="listening" class="ring"></span>
          <span class="dot" :class="{ on: listening }"></span>
          {{ listening ? '停止录音' : srSupported ? '语音输入' : '浏览器不支持' }}
        </button>
      </div>

      <textarea
        v-model="draft"
        rows="12"
        placeholder="用自己的话把这个概念讲清楚。&#10;&#10;可以打比方、举例子，也可以先随便讲 —— 首轮「先胡说」是被鼓励的。&#10;讲透三点更容易拿高分：是什么 / 为什么 / 怎么用，再加一个生活里的类比。"
      ></textarea>

      <div v-if="listening && interim" class="interim">…{{ interim }}</div>

      <div class="field-foot">
        <span class="mono">
          字数 {{ count }} <span v-if="count < 80" class="warn">· 建议 ≥ 80</span>
          <span v-if="voiceAccum" class="ok"> · 语音 {{ voiceAccum.length }} 字</span>
        </span>
        <button class="btn-primary" :disabled="session.loading || count === 0" @click="onSubmit">
          {{ session.loading ? '实验中…' : roundNo > 1 ? '提交修正版 →' : '提交实验 →' }}
        </button>
      </div>
    </div>

    <p v-if="!srSupported" class="mono muted-2" style="margin-top: var(--s-4);">
      当前浏览器不支持 Web Speech API，可直接打字；Chrome / Edge 支持边说边出字。
    </p>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { session, submitRound, resetSession, loadDaily } from '../store.js'

const roundNo = computed(() => session.rounds.length + 1)
const draft = ref('')
const interim = ref('')
const voiceAccum = ref('')
const listening = ref(false)
const srSupported = ref(false)

let recog = null
let shouldListen = false   // 用户是否「意图录音」——与 listening 分离，解决连续模式自动结束
let watchdog = null

const count = computed(() => (draft.value || '').trim().length)

onMounted(() => {
  if (session.rounds.length > 0) {
    draft.value = session.rounds[session.rounds.length - 1].text
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  srSupported.value = !!SR
})

/* ---------- 语音：可靠启停 ---------- */
function startVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) return

  // 每次都新建实例，避免复用已 abort 的实例进入 InvalidStateError
  if (recog) { try { recog.onend = null; recog.abort() } catch (e) {} }

  recog = new SR()
  recog.lang = 'zh-CN'
  recog.interimResults = true
  recog.continuous = true

  recog.onresult = (e) => {
    let finalText = '', interimText = ''
    for (let i = 0; i < e.results.length; i++) {
      const t = e.results[i][0].transcript
      if (e.results[i].isFinal) finalText += t
      else interimText += t
    }
    if (finalText) {
      draft.value = (draft.value ? draft.value + ' ' : '') + finalText
      voiceAccum.value += finalText
    }
    interim.value = interimText
  }

  recog.onerror = (e) => {
    console.warn('[speech]', e && e.error)
    shouldListen = false
    listening.value = false
  }

  recog.onend = () => {
    // Chrome 在 continuous 模式下会因静音自动结束；只要用户没主动停止就续接
    if (shouldListen) {
      try { recog.start() } catch (e) { shouldListen = false; listening.value = false }
    } else {
      listening.value = false
      interim.value = ''
    }
  }

  shouldListen = true
  try {
    recog.start()
    listening.value = true
  } catch (e) {
    shouldListen = false
    listening.value = false
  }
}

function stopVoice() {
  shouldListen = false
  listening.value = false      // 立即复位 UI，不等事件回调
  interim.value = ''
  clearTimeout(watchdog)
  if (recog) {
    try { recog.onend = null } catch (e) {}
    try { recog.abort() } catch (e) {}   // abort 立刻终止，不等最终结果
  }
  // 兜底：400ms 后再确认一次，防止极端情况下状态残留
  watchdog = setTimeout(() => {
    listening.value = false
    if (recog) { try { recog.abort() } catch (e) {} }
  }, 400)
}

function toggleVoice() {
  if (!srSupported.value) return
  if (listening.value || shouldListen) stopVoice()
  else startVoice()
}

/* ---------- 返回 ---------- */
function goBack() {
  if (draft.value.trim() && !window.confirm('当前讲述尚未提交，确定放弃并返回实验台？')) return
  stopVoice()
  resetSession()
  loadDaily()
}

async function onSubmit() {
  if (!draft.value.trim()) return
  stopVoice()
  await submitRound(draft.value.trim(), voiceAccum.value)
  if (!session.error) {
    draft.value = ''
    interim.value = ''
    voiceAccum.value = ''
  }
}

onBeforeUnmount(() => {
  shouldListen = false
  clearTimeout(watchdog)
  if (recog) {
    try { recog.onend = null; recog.abort() } catch (e) {}
  }
})
</script>

<style scoped>
.head-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--s-4); flex-wrap: wrap;
}
.btn-sm { padding: 7px 14px; font-size: 13px; }

.bg { margin: 0 0 var(--s-4); color: var(--ink-2); font-size: 15px; line-height: 1.75; max-width: 68ch; }
.guide ul { margin: 0; padding-left: 18px; }
.guide li { font-size: 14px; line-height: 1.8; color: var(--ink-2); }

.field {
  background: var(--paper-raised);
  border: 1px solid var(--rule);
  border-radius: var(--r-lg);
  padding: var(--s-5);
  transition: border-color var(--dur-2) var(--ease-out-quart),
              box-shadow var(--dur-3) var(--ease-out-quart);
}
.field:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft);
}
.field-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--s-4); margin-bottom: var(--s-4);
}
.field label { margin: 0; }

textarea {
  width: 100%;
  font: inherit; font-size: 16px; line-height: 1.9;
  color: var(--ink);
  background: transparent;
  border: 0; outline: none; resize: vertical;
  padding: 0;
}
textarea::placeholder { color: var(--ink-3); }

.interim {
  font-style: italic; color: var(--accent);
  font-size: 14px; margin-top: var(--s-3);
  animation: fade var(--dur-2) var(--ease-out-quart);
}

.field-foot {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--s-4); flex-wrap: wrap;
  margin-top: var(--s-4); padding-top: var(--s-4);
  border-top: 1px dashed var(--rule-2);
}
.warn { color: var(--accent); }
.ok { color: var(--teal); }

.voice {
  position: relative;
  display: inline-flex; align-items: center; gap: var(--s-2);
  font: inherit; font-size: 13px; font-weight: 600;
  background: transparent; color: var(--ink-2);
  border: 1.5px solid var(--rule-2); border-radius: 999px;
  padding: 7px 14px; cursor: pointer;
  transition: all var(--dur-2) var(--ease-out-quart);
}
.voice:hover { border-color: var(--accent); color: var(--accent); }
.voice.rec { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.dot { width: 7px; height: 7px; border-radius: 999px; background: var(--rule-2); }
.dot.on { background: var(--accent); }
.ring {
  position: absolute; left: 12px;
  width: 7px; height: 7px; border-radius: 999px;
  background: var(--accent);
  animation: pulse-ring 1.5s var(--ease-out-quart) infinite;
}
</style>
