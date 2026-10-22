<template>
  <span class="badge" :style="style">{{ grade }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { GRADE_COLOR } from '../store.js'

const props = defineProps({
  grade: { type: String, required: true },
  size: { type: String, default: 'md' }, // sm | md | lg
})

const style = computed(() => {
  const c = GRADE_COLOR[props.grade] || '#6b7280'
  const pad = props.size === 'lg' ? '10px 22px' : props.size === 'sm' ? '2px 10px' : '6px 16px'
  const fs = props.size === 'lg' ? '26px' : props.size === 'sm' ? '13px' : '18px'
  return {
    color: c,
    borderColor: c,
    background: c + '14',
    padding: pad,
    fontSize: fs,
    fontWeight: 700,
  }
})
</script>

<style scoped>
.badge {
  display: inline-block;
  border: 2px solid;
  border-radius: 999px;
  line-height: 1.2;
}
</style>
