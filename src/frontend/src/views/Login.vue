
<template>
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
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '@/api/listApi';

const router = useRouter();
const loginForm = ref({ username: '', password: '' });

const onLogin = async () => {
  try {
  const res = await login(loginForm.value);
    localStorage.setItem('token', res.data.jwt);
  router.push('/home');
  } catch (err) {
  alert(err.response?.data?.message || '登录失败');
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
