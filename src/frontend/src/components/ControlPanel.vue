<template>
  <div class="control-panel">
    <button class="btn logout" @click="onLogout">登出账号 (TODO)</button>
    <!-- 未来可在此添加更多控制按钮 -->
  </div>
</template>

<script setup>
const emit = defineEmits(['logged-out'])

const onLogout = () => {
  // 清理本地 token / 用户信息
  try { localStorage.removeItem('jwt') } catch (e) { /* ignore */ }
  try { localStorage.removeItem('user') } catch (e) { /* ignore */ }

  // 通知父组件或应用已登出，父组件可根据需要刷新状态或跳转。
  emit('logged-out')

  // TODO: 前端登录页尚未实现，跳转功能暂不需要实现。
  // 将来可以在此处调用 router.push('/login') 或者调用后端登出接口再跳转。
  console.log('logout processed (token cleared, TODO: navigate to login)')
}
</script>

<style scoped>
.control-panel { display: flex; gap: 0.75rem; margin-top: 1rem; }
.btn { padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.08); background: #fff; cursor: pointer }
.logout { color: #c00 }
</style>
