<template>
  <div class="ui-section-title">
    <slot />
  </div>
</template>
<script setup>
</script>
<style scoped>
.ui-section-title{ color: var(--color-accent); font-weight:600; font-size: var(--text-lg); display:flex; align-items:center; gap:8px }
</style>
