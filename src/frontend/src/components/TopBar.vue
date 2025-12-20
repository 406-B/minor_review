<template>
  <div class="top-bar">
    <div class="app-title">小众点评</div>
    <div class="nav-options">
      <span class="nav-item" @click="$router.push('/canteen')">食堂浏览</span>
      <span class="nav-item" @click="$router.push('/community')">美食论坛</span>
    </div>
    <div class="user-profile-text" @click="$router.push('/profile')">个人主页</div>
  </div>
</template>

<script setup>
// 仅样式和跳转，无需逻辑
</script>

<style scoped>
.top-bar {
  width: 100%;
  height: 60px;
  background: #fffbe6;
  border-bottom: 2px solid #ff9800;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 36px 0 32px;
  box-sizing: border-box;
  position: sticky;
  top: 0;
  z-index: 10;
}
.app-title {
  font-size: 2rem;
  color: #ff9800;
  font-weight: bold;
  letter-spacing: 6px;
  user-select: none;
}
.nav-options {
  display: flex;
  gap: 32px;
  margin-left: 40px;
}
.nav-item {
  font-size: 1.1rem;
  color: #666;
  cursor: pointer;
  padding: 6px 18px;
  border-radius: 18px;
  transition: background 0.18s, color 0.18s;
  user-select: none;
}
.nav-item.active,
.nav-item:hover {
  background: #ffecb3;
  color: #ff9800;
}
.user-profile-text {
  margin-left: auto;
  font-size: 1.1rem;
  color: #ff9800;
  font-weight: bold;
  padding: 6px 18px;
  border-radius: 18px;
  background: #fffbe6;
  user-select: none;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.user-profile-text:hover {
  background: #ffecb3;
  color: #fb8c00;
}
</style>
