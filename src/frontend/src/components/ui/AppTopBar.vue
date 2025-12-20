<template>
  <div class="app-top-bar">
    <div class="title" @click="safeGo('/')">小众点评</div>
    <nav class="nav" aria-label="主导航">
  <span class="item" :class="{ active: isActive('/profile') }" @click="safeGo('/profile')">个人主页</span>
      <span class="item" :class="{ active: isActive('/canteen') }" @click="safeGo('/canteen')">食堂浏览</span>
      <span class="item" :class="{ active: isActive('/community') }" @click="safeGo('/community')">美食论坛</span>
    </nav>
    <template v-if="!isAuthed">
      <div class="unauth-wrap">
        <span class="unauth-hint">未登录：登录后可体验论坛与个人主页等更多功能</span>
        <div class="auth-actions">
          <button class="login-btn" @click="go('/login')">登录</button>
          <button class="register-btn" @click="go('/register')">注册</button>
        </div>
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
  // 允许未登录用户访问页面（页面内自行决定是否遮罩或限制交互）
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
.item:hover { background: var(--brand-100); color: var(--brand-800, #8A4B00); }
.item.active { background: var(--brand-100); color: var(--brand-800, #8A4B00); font-weight: 600; }
/* 个人主页已放入 .nav 作为 .item，无需单独 .profile 样式 */
.unauth-wrap { margin-left: auto; display: flex; align-items: center; gap: 12px }
.unauth-hint { color: var(--color-muted); font-size: .85rem; white-space: nowrap }
.auth-actions { display:flex; gap:12px }
.login-btn, .register-btn {
  padding:6px 16px; border-radius:18px; cursor:pointer; background:var(--brand-50); border:1px solid transparent; font-size:.9rem; color:var(--color-accent); transition:background .18s,color .18s;
}
.login-btn:hover, .register-btn:hover,
.login-btn:focus-visible, .register-btn:focus-visible {
  background: var(--brand-100);
  color: var(--brand-800, #8A4B00);
}
.register-btn { font-weight:600 }
</style>
