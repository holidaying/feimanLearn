<template>
  <view class="wrap">
    <canvas
      canvas-id="radar"
      id="radar"
      class="canvas"
      :style="{ width: sizePx + 'px', height: sizePx + 'px' }"
    ></canvas>
  </view>
</template>

<script setup>
import { ref, watch, onMounted, getCurrentInstance } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{ label, score, max }]
  size: { type: Number, default: 240 },
})

const instance = getCurrentInstance()
const sizePx = ref(props.size)
const COLOR_FILL = 'rgba(15, 107, 96, 0.22)'
const COLOR_LINE = '#0F6B60'
const COLOR_GRID = '#DED5C2'
const COLOR_TEXT = '#4A443A'

function draw() {
  const ctx = uni.createCanvasContext('radar', instance.proxy)
  const S = sizePx.value
  const cx = S / 2
  const cy = S / 2
  const r = S * 0.32
  const N = props.data.length || 4
  const max = (props.data[0] && props.data[0].max) || 25
  const angle = (i) => -Math.PI / 2 + (i * 2 * Math.PI) / N

  ctx.clearRect(0, 0, S, S)

  // 网格
  ctx.setStrokeStyle(COLOR_GRID)
  ctx.setLineWidth(1)
  for (const frac of [0.25, 0.5, 0.75, 1]) {
    ctx.beginPath()
    for (let i = 0; i <= N; i++) {
      const a = angle(i % N)
      const x = cx + r * frac * Math.cos(a)
      const y = cy + r * frac * Math.sin(a)
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.stroke()
  }
  // 轴线
  for (let i = 0; i < N; i++) {
    const a = angle(i)
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + r * Math.cos(a), cy + r * Math.sin(a))
    ctx.stroke()
  }
  // 数据多边形
  ctx.beginPath()
  for (let i = 0; i <= N; i++) {
    const idx = i % N
    const a = angle(idx)
    const frac = Math.max(0, Math.min(1, (props.data[idx].score || 0) / max))
    const x = cx + r * frac * Math.cos(a)
    const y = cy + r * frac * Math.sin(a)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.closePath()
  ctx.setFillStyle(COLOR_FILL)
  ctx.fill()
  ctx.setStrokeStyle(COLOR_LINE)
  ctx.setLineWidth(2)
  ctx.stroke()

  // 标签
  ctx.setFillStyle(COLOR_TEXT)
  ctx.setFontSize(11)
  for (let i = 0; i < N; i++) {
    const a = angle(i)
    const lx = cx + (r + 24) * Math.cos(a)
    const ly = cy + (r + 24) * Math.sin(a)
    ctx.setTextAlign(
      Math.abs(Math.cos(a)) < 0.2 ? 'center' : Math.cos(a) > 0 ? 'left' : 'right'
    )
    ctx.setTextBaseline('middle')
    ctx.fillText(props.data[i].label, lx, ly)
  }
  ctx.draw()
}

onMounted(() => {
  // 按实际渲染宽度换算，保证不同机型不糊
  try {
    const q = uni.createSelectorQuery().in(instance.proxy)
    q.select('#radar').boundingClientRect((rect) => {
      if (rect && rect.width) sizePx.value = Math.round(rect.width)
      draw()
    }).exec()
  } catch (e) {
    draw()
  }
})

watch(() => props.data, draw, { deep: true })
</script>

<style scoped>
.wrap { display: flex; justify-content: center; }
.canvas { display: block; }
</style>
