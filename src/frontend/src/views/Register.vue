
<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="register-bg">
      <el-card class="register-card">
  <h2 class="register-title">注册</h2>
      <el-form :model="registerForm" @submit.prevent="onRegister" label-width="80px" label-position="right">
        <el-form-item label="用户名">
          <el-input v-model="registerForm.username" autocomplete="username" style="width: 100%;" />
          <div class="help">5-12位，仅包含字母与数字，字母在前，数字在后</div>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="registerForm.password" type="password" autocomplete="new-password" style="width: 100%;" />
          <div class="help">8-15位，需同时包含大小写字母、数字，以及符号 - _ * ^ 中至少一个</div>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="registerForm.nickname" style="width: 100%;" />
          <div class="help">2-20个字符，支持中英文、数字与常用符号</div>
        </el-form-item>
        <el-form-item class="center-btn-item">
          <el-button type="primary" @click="onRegister" class="register-btn">注册</el-button>
        </el-form-item>
        <el-form-item class="center-btn-item">
          <router-link to="/login">已有账号？去登录</router-link>
        </el-form-item>
      </el-form>
      </el-card>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register, login } from '@/api/listApi';
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import { ElMessageBox } from 'element-plus'

const router = useRouter();
const registerForm = ref({ username: '', password: '', nickname: '' });

function validateUsername(name) {
  if (!name) return '请输入用户名'
  if (name.length < 5 || name.length > 12) return '用户名长度需为 5-12 位'
  const pattern = /^[A-Za-z]+[0-9]+$/
  if (!pattern.test(name)) return '用户名需以字母开头且包含数字，仅字母与数字'
  return ''
}

function validatePassword(pwd) {
  if (!pwd) return '请输入密码'
  if (pwd.length < 8 || pwd.length > 15) return '密码长度需为 8-15 位'
  const hasLower = /[a-z]/.test(pwd)
  const hasUpper = /[A-Z]/.test(pwd)
  const hasDigit = /\d/.test(pwd)
  const hasSpec = /[-_*^]/.test(pwd)
  if (!(hasLower && hasUpper && hasDigit && hasSpec)) return '需包含大小写字母、数字及 - _ * ^ 中至少一个符号'
  return ''
}

function validateNickname(nick) {
  if (!nick || !nick.trim()) return '请输入昵称'
  const n = nick.trim()
  if (n.length < 2 || n.length > 20) return '昵称长度建议 2-20 个字符'
  return ''
}

const onRegister = async () => {
  // 前端校验
  const userErr = validateUsername(registerForm.value.username)
  const pwdErr = validatePassword(registerForm.value.password)
  const nickErr = validateNickname(registerForm.value.nickname)
  const errs = [
    userErr && `用户名：${userErr}`,
    pwdErr && `密码：${pwdErr}`,
    nickErr && `昵称：${nickErr}`,
  ].filter(Boolean)
  if (errs.length) {
    try { await ElMessageBox.alert(errs.join('\n'), '请修正后再提交', { type: 'warning' }) } catch (_) {}
    return
  }
  try {
    await register(registerForm.value);
    // 注册成功后自动登录，节省一步
    const loginRes = await login({ username: registerForm.value.username, password: registerForm.value.password })
    const jwt = loginRes?.jwt || loginRes?.data?.jwt
    if (jwt) {
      localStorage.setItem('jwt', jwt)
    }
    window.$message?.success?.('注册成功，已为你登录')
    router.push('/onboarding/tags');
  } catch (err) {
    // 提取后端错误
    const data = err?.response?.data || {}
    const msg = data.message || '注册失败'
  const serverErrors = data.errors || {}
  // 统一用弹窗呈现服务端失败原因（不在页面内堆叠错误）
    const lines = []
    if (serverErrors && typeof serverErrors === 'object') {
      for (const key of Object.keys(serverErrors)) {
        const val = serverErrors[key]
        const text = Array.isArray(val) ? val.join('; ') : String(val)
        lines.push(`${key}: ${text}`)
      }
    }
    const content = [msg, ...lines].filter(Boolean).join('\n')
  try { await ElMessageBox.alert(content, '注册失败', { type: 'error' }) } catch (_) {}
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
.register-btn {
  width: 100%;
  background: #ff9800;
  border: none;
}
.register-btn:hover {
  background: #fb8c00;
}
.help { margin-top: 6px; font-size: 12px; color: var(--color-muted); line-height: 1.4 }
</style>
