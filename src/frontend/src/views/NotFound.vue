<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div style="text-align:center;padding:2em;">
      <h1>404 页面未找到</h1>
      <p>您访问的页面不存在。</p>
    </div>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
</script>

<style scoped>
h1 {
  color: #e74c3c;
}
p {
  color: #888;
}
</style>
