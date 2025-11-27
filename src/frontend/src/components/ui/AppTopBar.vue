<template>
  <div class="app-top-bar">
    <div class="title" @click="safeGo('/')">小众点评</div>
    <nav class="nav" aria-label="主导航">
      <span class="item" :class="{ active: isActive('/canteen') }" @click="safeGo('/canteen')">食堂浏览</span>
      <span class="item" :class="{ active: isActive('/community') }" @click="safeGo('/community')">美食论坛</span>
    </nav>
    <template v-if="isAuthed">
      <button class="profile" @click="safeGo('/profile')" aria-label="个人主页">个人主页</button>
    </template>
    <template v-else>
      <div class="auth-actions">
        <button class="login-btn" @click="go('/login')">登录</button>
        <button class="register-btn" @click="go('/register')">注册</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { isProtectedPath } from '@/constants/permissions.js'
const route = useRoute()
const router = useRouter()
const go = (to) => router.push(to)
const isActive = (path) => route.path.startsWith(path)
const isAuthed = computed(() => !!localStorage.getItem('jwt'))

function safeGo(path) {
  if (!isAuthed.value && isProtectedPath(path)) {
    // 未登录跳 profile 或社区 → 去 login
    window.$message?.warning?.('请先登录')
    return go('/login')
  }
  go(path)
}
</script>

<style scoped>
.app-top-bar {
  height: 60px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  padding: 0 28px;
  gap: 40px;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 10;
}
.title {
  font-size: 1.6rem;
  color: var(--color-accent);
  font-weight: 600;
  letter-spacing: 4px;
  user-select: none;
  cursor: pointer;
}
.nav { display: flex; gap: 20px; }
.item {
  font-size: .95rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px 16px;
  border-radius: 18px;
  transition: background .18s,color .18s;
  user-select: none;
}
.item.active, .item:hover { background: var(--brand-100); color: var(--color-accent); }
.profile {
  margin-left: auto;
  font-size: .95rem;
  color: var(--color-accent);
  font-weight: 600;
  padding: 6px 16px;
  border-radius: 18px;
  background: var(--brand-50);
  user-select: none;
  cursor: pointer;
  transition: background .18s,color .18s;
  border: 1px solid transparent;
}
.profile:hover { background: var(--brand-100); color: var(--brand-700); }
.auth-actions { margin-left:auto; display:flex; gap:12px }
.login-btn, .register-btn {
  padding:6px 16px; border-radius:18px; cursor:pointer; background:var(--brand-50); border:1px solid transparent; font-size:.9rem; color:var(--color-accent); transition:background .18s,color .18s;
}
.login-btn:hover, .register-btn:hover { background: var(--brand-100); color: var(--brand-700); }
.register-btn { font-weight:600 }
</style>
