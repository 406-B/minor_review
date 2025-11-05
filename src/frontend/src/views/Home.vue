<template>
  <div class="user-bg">
    <el-card class="user-card user-center-card">
      <div class="main-title">小众点评</div>
  <el-button type="primary" @click="onStart" class="logout-btn">开始使用</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const onStart = () => {
  router.push('/canteen');
};
</script>

<style scoped>
.user-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff9800 60%, #fff3e0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.user-card {
  width: 400px;
  padding: 48px 24px 32px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(255,152,0,0.15);
  background: #fffbe6;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.user-center-card {
  justify-content: center;
}
.main-title {
  font-size: 2.8rem;
  color: #ff9800;
  font-weight: bold;
  margin-bottom: 40px;
  letter-spacing: 8px;
  text-align: center;
}
.logout-btn {
  width: 100%;
  background: #ff9800;
  border: none;
  font-size: 1.1rem;
  margin-top: 10px;
  color: #fff;
}
.logout-btn:hover {
  background: #fb8c00;
}
</style>
