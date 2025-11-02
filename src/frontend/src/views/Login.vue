
<template>
  <div class="login-bg">
    <el-card class="login-card">
      <h2 class="login-title">Login</h2>
      <el-form :model="loginForm" @submit.prevent="onLogin">
        <el-form-item label="Username">
          <el-input v-model="loginForm.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="loginForm.password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onLogin" class="login-btn">Login</el-button>
        </el-form-item>
        <el-form-item>
          <router-link to="/register">No account? Register</router-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const loginForm = ref({ username: '', password: '' });

const onLogin = async () => {
  try {
    const res = await axios.patch('/api/v1/login', loginForm.value);
    localStorage.setItem('token', res.data.jwt);
  router.push('/home');
  } catch (err) {
    alert(err.response?.data?.message || 'Login failed');
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
.login-btn {
  width: 100%;
  background: #ff9800;
  border: none;
}
.login-btn:hover {
  background: #fb8c00;
}
</style>
