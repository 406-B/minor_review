<template>
  <div class="control-panel">
    <button class="btn logout" @click="onLogout">登出账号</button>
    <!-- 未来可在此添加更多控制按钮 -->
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import request from '@/api/request'

const router = useRouter()
const emit = defineEmits(['logged-out'])

const onLogout = async () => {
  try {
    // 调用后端登出接口
    await request.post('/login/logout')
  } catch (error) {
    console.error('登出接口调用失败:', error)
    // 即使后端调用失败，也继续清理本地状态
  }
  
  // 清理本地 token / 用户信息
  try { localStorage.removeItem('jwt') } catch (e) { /* ignore */ }
  try { localStorage.removeItem('user') } catch (e) { /* ignore */ }
  try { localStorage.removeItem('userInfo') } catch (e) { /* ignore */ }
  console.log('✅ 已清除本地用户信息')

  // 通知父组件已登出
  emit('logged-out')

  // 跳转到登录页
  router.push('/login')
}
</script>

<style scoped>
.control-panel { display: flex; gap: 0.75rem; margin-top: 1rem; }
.btn { padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.08); background: #fff; cursor: pointer }
.logout { color: #c00 }
</style>
