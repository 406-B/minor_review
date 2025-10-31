<template>
  <div class="profile-info">
    <div class="avatar-area">
      <img class="avatar" src="@/assets/logo.svg" alt="avatar" />
    </div>
    <div class="meta">
      <h2 class="name">Example User</h2>
      <p class="bio">这是一个示例个人简介（TODO: 从后端加载真实用户信息）</p>

      <ul class="meta-list">
        <li><strong>邮箱：</strong>example@example.com <!-- TODO: 替换为真实数据 --></li>
        <li><strong>注册时间：</strong>2025-01-01 <!-- TODO: 后端数据 --></li>
      </ul>

      <div class="placeholders">
        <!-- 预留空间用于未来功能 -->
        <p class="todo">TODO: 显示用户角色 / 等级 / 个人签名等</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// 本组件目前仅用于展示静态示例信息，后续应从后端获取真实用户数据
</script>

<style scoped>
.profile-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  border: 1px solid rgba(0,0,0,0.06);
  padding: 1rem;
  border-radius: 8px;
  background: #fff;
}
.avatar { width: 72px; height: 72px; border-radius: 8px; object-fit: cover; }
.meta-list { margin: 0.5rem 0 0; padding-left: 1rem; }
.todo { color: #999; margin-top: 0.5rem; }
.name { margin: 0; }
.bio { margin: 0.25rem 0; color: #555 }
</style>
