<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="nf-wrap">
      <h1 class="nf-title">404 页面未找到</h1>
      <p class="nf-desc">您访问的页面不存在。</p>
      <div class="nf-actions">
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
        <el-button @click="$router.push('/login')">去登录</el-button>
      </div>
    </div>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
</script>

<style scoped>
.nf-wrap{ text-align:center; padding: 2em }
.nf-title{ color: var(--color-accent); }
.nf-desc{ color: var(--color-muted); margin: 8px 0 12px }
.nf-actions{ display:flex; gap:12px; justify-content:center }
</style>
