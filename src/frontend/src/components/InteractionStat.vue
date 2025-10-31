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
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  background: #f7f9fc;
  margin: 0.25rem;
  min-width: 90px;
  cursor: pointer;
}
.num { font-weight: 600; font-size: 1.1rem; }
.label { font-size: 0.85rem; color: #555 }
</style>
