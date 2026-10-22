<template>
  <view class="badge" :style="{ background: color + '14', borderColor: color + '40', color: color }">
    <text class="g">{{ grade }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { GRADE_COLOR } from '../store.js'

const props = defineProps({
  grade: { type: String, default: '中' },
  size: { type: String, default: 'md' }, // sm | md | lg
})

const color = computed(() => GRADE_COLOR[props.grade] || '#B4451A')
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid;
  border-radius: 999rpx;
  padding: 8rpx 26rpx;
}
.g {
  font-family: var(--font-display);
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.2;
}
</style>
