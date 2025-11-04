<template>
  <div class="control-panel">
    <button class="btn logout" @click="onLogout">登出账号 (TODO)</button>
    <!-- 未来可在此添加更多控制按钮 -->
  </div>
</template>

<script setup>
const onLogout = () => {
  // TODO: 调用登出 API 并清理本地状态 / 跳转登录页
  console.log('logout clicked (TODO)')
}
</script>

<style scoped>
.control-panel { display: flex; gap: 0.75rem; margin-top: 1rem; }
.btn { padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.08); background: #fff; cursor: pointer }
.logout { color: #c00 }
</style>
