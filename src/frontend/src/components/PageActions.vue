<template>
  <div class="page-actions">
    <div class="left"><slot name="left" /></div>
    <div class="right"><slot name="right" /></div>
  </div>
</template>

<script setup>
// simple presentational component using slots for left/right actions
</script>

<style scoped>
.page-actions { display:flex; justify-content:space-between; align-items:center; padding:8px 20px; max-width:1200px; margin:0 auto 8px }
.page-actions .left, .page-actions .right { display:flex; align-items:center; gap:8px }
</style>
