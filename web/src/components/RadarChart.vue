<template>
  <svg :viewBox="`0 0 ${size} ${size}`" :width="size" :height="size" class="radar">
    <!-- 网格环 -->
    <polygon
      v-for="(ring, i) in rings"
      :key="'r' + i"
      :points="ring"
      fill="none"
      stroke="#DED7C6"
      stroke-width="1"
    />
    <!-- 轴线 -->
    <line
      v-for="(ax, i) in axes"
      :key="'a' + i"
      :x1="cx"
      :y1="cy"
      :x2="ax.x"
      :y2="ax.y"
      stroke="#C6BCA4"
      stroke-width="1"
    />

    <!-- 数据：整体绘制入场 -->
    <g class="data">
      <polygon
        :points="dataPoints"
        fill="rgba(15,107,96,0.18)"
        stroke="#0F6B60"
        stroke-width="2"
      />
      <circle
        v-for="(p, i) in dataVertices"
        :key="'p' + i"
        :cx="p.x"
        :cy="p.y"
        r="3.5"
        fill="#0F6B60"
      />
    </g>

    <!-- 标签 -->
    <text
      v-for="(l, i) in labels"
      :key="'l' + i"
      :x="labelPos[i].x"
      :y="labelPos[i].y"
      text-anchor="middle"
      font-size="13"
      fill="#4E4739"
    >{{ l.label }}</text>
    <text
      v-for="(l, i) in labels"
      :key="'v' + i"
      :x="labelPos[i].x"
      :y="labelPos[i].y + 17"
      text-anchor="middle"
      font-size="12"
      font-weight="700"
      fill="#0F6B60"
    >{{ l.score }}</text>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, required: true }, // [{label, score, max}]
  size: { type: Number, default: 240 },
})

const cx = computed(() => props.size / 2)
const cy = computed(() => props.size / 2)
const radius = computed(() => props.size / 2 - 46)
const N = computed(() => props.data.length)

const angle = (i) => -Math.PI / 2 + (i * 2 * Math.PI) / N.value
const pointAt = (i, frac) => ({
  x: cx.value + radius.value * frac * Math.cos(angle(i)),
  y: cy.value + radius.value * frac * Math.sin(angle(i)),
})

const rings = computed(() =>
  [0.25, 0.5, 0.75, 1].map((frac) =>
    props.data.map((_, i) => {
      const p = pointAt(i, frac)
      return `${p.x},${p.y}`
    }).join(' ')
  )
)
const axes = computed(() => props.data.map((_, i) => pointAt(i, 1)))
const dataVertices = computed(() =>
  props.data.map((d, i) => {
    const frac = Math.max(0, Math.min(1, (d.score || 0) / (d.max || 25)))
    return pointAt(i, frac)
  })
)
const dataPoints = computed(() => dataVertices.value.map((p) => `${p.x},${p.y}`).join(' '))
const labels = computed(() => props.data)
const labelPos = computed(() => props.data.map((_, i) => pointAt(i, 1.2)))
</script>

<style scoped>
.radar { display: block; margin: 0 auto; overflow: visible; }

.data {
  transform-box: fill-box;
  transform-origin: center;
  animation: radar-in 900ms cubic-bezier(0.16, 1, 0.3, 1) 200ms both;
}
@keyframes radar-in {
  from { opacity: 0; transform: scale(0.2); }
  to   { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .data { animation: none; }
}
</style>
