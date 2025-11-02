
<template>
  <div class="register-bg">
    <el-card class="register-card">
      <h2 class="register-title">Register</h2>
      <el-form :model="registerForm" @submit.prevent="onRegister">
        <el-form-item label="Username">
          <el-input v-model="registerForm.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="registerForm.password" type="password" autocomplete="new-password" />
        </el-form-item>
        <el-form-item label="Nickname">
          <el-input v-model="registerForm.nickname" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onRegister" class="register-btn">Register</el-button>
        </el-form-item>
        <el-form-item>
          <router-link to="/login">Already have an account? Login</router-link>
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
const registerForm = ref({ username: '', password: '', nickname: '' });

const onRegister = async () => {
  try {
    await axios.post('/api/v1/register', registerForm.value);
    alert('Register success! Please login.');
  router.push('/login');
  } catch (err) {
    alert(err.response?.data?.message || 'Register failed');
  }
};
</script>

<style scoped>
.register-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff9800 60%, #fff3e0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.register-card {
  width: 350px;
  padding: 32px 24px 18px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(255,152,0,0.15);
  background: #fffbe6;
}
.register-title {
  text-align: center;
  color: #ff9800;
  margin-bottom: 18px;
  font-weight: bold;
}
.register-btn {
  width: 100%;
  background: #ff9800;
  border: none;
}
.register-btn:hover {
  background: #fb8c00;
}
</style>
