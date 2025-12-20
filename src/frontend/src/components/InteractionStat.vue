<template>
  <div class="interaction-stat" role="button" @click="onClick">
    <div class="num">{{ count }}</div>
    <div class="label">{{ name }}</div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue'
const props = defineProps({
  name: { type: String, required: true },
  count: { type: Number, default: 0 },
  to: { type: String, default: '' }
})
const emit = defineEmits(['navigate'])

const onClick = () => {
  // TODO: 路由跳转逻辑（如使用 vue-router）
  // emit 供父组件选择处理
  emit('navigate', props.to)
}
</script>

<style scoped>
.interaction-stat {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f4f6f8;
  border: 1px solid rgba(0,0,0,0.06);
  margin: 6px;
  min-width: 110px;
  cursor: pointer;
  transition: border-color .12s ease, box-shadow .12s ease, transform .12s ease;
}
.interaction-stat:hover { border-color: var(--color-accent); box-shadow: 0 4px 14px rgba(0,0,0,0.06); transform: translateY(-1px) }
.num { font-weight: 700; font-size: 1.1rem; color: #222 }
.label { font-size: 0.85rem; color: #555; margin-top: 2px }
</style>
