<template>
  <div class="ui-page-container">
    <header v-if="$slots.header" class="ui-page-header">
      <slot name="header" />
    </header>
    <main class="ui-page-main">
      <slot />
    </main>
  </div>
</template>

<script setup>
// dumb layout container
</script>

<style scoped>
.ui-page-container{ max-width: var(--container-max); margin:0 auto; padding: 24px; }
.ui-page-header{ margin-bottom: 16px; display:flex; align-items:center; justify-content:space-between }
.ui-page-main{ background: var(--color-surface); border:1px solid var(--color-border); border-radius: var(--radius-sm); padding: 16px; box-shadow: var(--shadow-sm); }
</style>
