<template>
  <div class="section-card">
    <div class="header">
      <h3 class="title">{{ title }}</h3>
      <div class="actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <div class="content">
      <slot name="content">
        <p class="empty">暂无内容</p>
      </slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' }
})
</script>

<style scoped>
.section-card {
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 8px;
  padding: 1rem;
  background: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.title { margin: 0; font-size: 1.05rem; }
.actions { font-size: 0.9rem; }
.content { min-height: 2.5rem; }
.empty { color: #999; }
</style>
