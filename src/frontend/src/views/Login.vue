<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="login-bg">
      <el-card class="login-card">
      <h2 class="login-title">登录</h2>
      <el-form :model="loginForm" @submit.prevent="onLogin" label-width="80px" label-position="right">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" autocomplete="username" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" autocomplete="current-password" style="width: 100%;" />
        </el-form-item>
        <el-form-item class="center-btn-item">
          <el-button type="primary" @click="onLogin" class="login-btn">登录</el-button>
        </el-form-item>
        <el-form-item class="center-btn-item">
          <router-link to="/register">没有账号？去注册</router-link>
        </el-form-item>
      </el-form>
      </el-card>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '@/api/listApi';
import { getProfileSections } from '@/api/profile';
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'

const router = useRouter();
const loginForm = ref({ username: '', password: '' });

const onLogin = async () => {
  console.log('onLogin called', loginForm.value); // 调试：事件触发与数据
  try {
    const res = await login(loginForm.value);
    console.log('login response', res); // 调试：接口响应
    
    // 保存 JWT token
    localStorage.setItem('jwt', res.jwt);
    
    // 保存用户信息（重要！用于权限判断）
    const userInfo = {
      id: res.userId,
      username: res.username,
      nickname: res.nickname
    };
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
    console.log('✅ 用户信息已保存到 localStorage:', userInfo);
    
    try {
      const prof = await getProfileSections();
      const tags = prof?.user?.preference_tags || [];
      if (Array.isArray(tags) && tags.length === 0) {
        return router.push('/onboarding/tags');
      }
    } catch (_) { /* 忽略拉取资料失败，继续进入个人主页 */ }
    router.push('/profile');
  } catch (err) {
    console.error('login error', err); // 调试：错误信息
    const msg = err.response?.data?.message;
    if (msg === 'Invalid credentials') {
      alert('用户名或密码错误');
    } else if (msg === 'User not found') {
      alert('用户不存在');
    } else {
      alert(msg || '登录失败');
    }
  }
};
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff9800 60%, #fff3e0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card {
  width: 350px;
  padding: 32px 24px 18px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(255,152,0,0.15);
  background: #fffbe6;
}
.login-title {
  text-align: center;
  color: #ff9800;
  margin-bottom: 18px;
  font-weight: bold;
}
.center-btn-item {
  justify-content: center !important;
  display: flex !important;
}
/* 让 el-form label 靠右对齐，输入框左侧对齐 */
.el-form {
  width: 100%;
}
.el-form-item__label {
  text-align: right;
  width: 80px;
  min-width: 80px;
  padding-right: 8px;
}
.el-form-item {
  margin-bottom: 18px;
}
.el-input {
  width: 100%;
}
.login-btn {
  width: 100%;
  background: #ff9800;
  border: none;
}
.login-btn:hover {
  background: #fb8c00;
}
</style>
