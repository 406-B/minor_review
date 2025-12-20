<template>
  <div class="ui-empty">
    <img v-if="icon" :src="icon" alt="" />
    <p>{{ text }}</p>
    <slot />
  </div>
</template>
<script setup>
const props = defineProps({ text: { type:String, default:'暂无数据' }, icon: { type:String, default:'' }})
</script>
<style scoped>
.ui-empty{ color:var(--color-muted); text-align:center; padding: 40px 0 }
.ui-empty img{ width: 120px; opacity:.75; margin-bottom:12px }
</style>
