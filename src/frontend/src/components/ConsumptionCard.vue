<template>
  <SectionCard class="consumption-card" title="食堂消费记录">
    <template #actions>
      <button v-if="hasData" class="link" @click="viewDetails">查看详情</button>
    </template>
    <template #content>
      <!-- 未绑定状态 -->
      <div v-if="!hasData && !loading" class="empty-state">
        <div class="empty-icon">🍽️</div>
        <p class="empty-text">尚未绑定学号</p>
        <button class="bind-btn" @click="showBindDialog">立即绑定</button>
      </div>

      <!-- 加载中 -->
      <div v-else-if="loading" class="loading-state">
        <p>加载中...</p>
      </div>

      <!-- 已绑定，显示数据 -->
      <div v-else class="consumption-data">
        <div class="chart-container">
          <canvas ref="chartCanvas" width="200" height="200"></canvas>
          <div class="total-amount">
            <div class="amount-label">总消费</div>
            <div class="amount-value">¥{{ totalAmount }}</div>
          </div>
        </div>
        <div class="canteen-summary">
          <div class="summary-item">
            <span class="label">食堂数量</span>
            <span class="value">{{ canteenCount }}</span>
          </div>
          <div class="summary-item">
            <span class="label">最后更新</span>
            <span class="value">{{ lastUpdated }}</span>
          </div>
        </div>
      </div>
    </template>
  </SectionCard>

  <!-- 绑定弹窗 -->
  <div v-if="bindDialogVisible" class="dialog-overlay">
    <div class="dialog-content" @click.stop>
      <h3>绑定食堂消费</h3>
      
      <!-- 步骤1：输入学号密码 -->
      <div v-if="loginStep === 1">
        <div class="form-group">
          <label>学号</label>
          <input 
            v-model="loginForm.username" 
            type="text" 
            placeholder="请输入学号"
            :disabled="binding"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入INFO密码"
            :disabled="binding"
          />
        </div>
        <div class="dialog-tip">
          <p>🔒 安全说明：</p>
          <ul>
            <li>您的学号和密码将通过加密传输</li>
            <li>系统不会存储您的密码</li>
            <li>仅用于一次性登录获取消费数据</li>
          </ul>
        </div>
      </div>
      
      <!-- 步骤2：输入验证码 -->
      <div v-else-if="loginStep === 2">
        <div class="verification-tip">
          <div class="tip-icon">📱</div>
          <p class="tip-text">为了您的账号安全，我们已将验证码以短信形式发送至与您校园卡绑定的手机号上，请及时输入。</p>
        </div>
        <div class="form-group">
          <label>验证码</label>
          <input 
            v-model="loginForm.verificationCode" 
            type="text" 
            placeholder="请输入6位验证码"
            maxlength="6"
            :disabled="binding"
          />
        </div>
      </div>
      
      <!-- 步骤3：登录中 -->
      <div v-else-if="loginStep === 3" class="loading-step">
        <div class="loading-spinner"></div>
        <p>正在登录，请稍候...</p>
      </div>
      
      <div class="dialog-actions">
        <button class="cancel-btn" @click="closeBindDialog" :disabled="binding">取消</button>
        <button 
          v-if="loginStep === 1"
          class="confirm-btn" 
          @click="handleStartLogin" 
          :disabled="binding || !loginForm.username || !loginForm.password"
        >
          {{ binding ? '登录中...' : '确认' }}
        </button>
        <button 
          v-else-if="loginStep === 2"
          class="confirm-btn" 
          @click="handleSubmitCode" 
          :disabled="binding || !loginForm.verificationCode || loginForm.verificationCode.length !== 6"
        >
          {{ binding ? '验证中...' : '确认' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import SectionCard from './SectionCard.vue'
import { getConsumption, startAutoLogin, submitVerificationCode, checkLoginStatus } from '@/api/canteen'

const router = useRouter()
const chartCanvas = ref(null)
const loading = ref(false)
const consumptionData = ref(null)
const bindDialogVisible = ref(false)
const binding = ref(false)
const loginStep = ref(1) // 1: 输入学号密码, 2: 输入验证码, 3: 登录中
const loginForm = ref({
  username: '',
  password: '',
  verificationCode: '',
  sessionId: ''
})
let pollTimer = null

const hasData = computed(() => !!consumptionData.value)
const totalAmount = computed(() => consumptionData.value?.total_amount || '0.00')
const canteenCount = computed(() => consumptionData.value?.canteen_count || 0)
const lastUpdated = computed(() => {
  if (!consumptionData.value?.last_fetched) return '--'
  const date = new Date(consumptionData.value.last_fetched)
  return date.toLocaleDateString('zh-CN')
})

// 自动检测浏览器类型
const detectBrowser = () => {
  const userAgent = navigator.userAgent.toLowerCase()
  
  if (userAgent.includes('edg/')) {
    return 'edge'
  } else if (userAgent.includes('chrome') && !userAgent.includes('edg')) {
    return 'chrome'
  } else if (userAgent.includes('firefox')) {
    return 'firefox'
  } else if (userAgent.includes('safari') && !userAgent.includes('chrome')) {
    return 'safari'
  }
  
  // 默认使用 Chrome
  return 'chrome'
}

// 绘制环状图
const drawDonutChart = () => {
  if (!chartCanvas.value || !consumptionData.value?.canteen_data) return

  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  const centerX = 100
  const centerY = 100
  const radius = 80
  const innerRadius = 55

  // 清空画布
  ctx.clearRect(0, 0, 200, 200)

  const canteenData = consumptionData.value.canteen_data
  const entries = Object.entries(canteenData)
  const total = entries.reduce((sum, [, amount]) => sum + parseFloat(amount), 0)

  // 颜色方案：优先使用 CSS 主题色，回退到硬编码值
  const _css = getComputedStyle(document.documentElement)
  const cssAccent = (_css.getPropertyValue('--color-accent') || '').trim() || '#ffa000'
  const cssAccentWeak = (_css.getPropertyValue('--color-accent-weak') || '').trim() || '#ffecb3'
  const colors = [
    cssAccent, '#67C23A', '#E6A23C', '#F56C6C',
    '#909399', '#00D4AA', '#FF6B9D', '#C990C0'
  ]

  let startAngle = -Math.PI / 2 // 从顶部开始

  entries.forEach(([name, amount], index) => {
    const angle = (parseFloat(amount) / total) * 2 * Math.PI
    const endAngle = startAngle + angle

    // 绘制外圆弧
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, endAngle)
    ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true)
    ctx.closePath()
    ctx.fillStyle = colors[index % colors.length]
    ctx.fill()

    startAngle = endAngle
  })
}

// 加载消费数据
const loadConsumption = async () => {
  loading.value = true
  try {
    console.log('[ConsumptionCard] 开始加载消费数据...')
    const response = await getConsumption()
    
    if (response.code === 200 && response.data) {
      console.log('[ConsumptionCard] 消费数据加载成功:', response.data)
      consumptionData.value = response.data
      // 延迟绘制图表，确保 canvas 已渲染
      setTimeout(drawDonutChart, 100)
    } else if (response.code === 404) {
      console.log('[ConsumptionCard] 用户未绑定学号')
      // 未绑定
      consumptionData.value = null
    } else {
      console.warn('[ConsumptionCard] 获取消费数据返回异常状态:', response)
      window.$message?.warning?.(response.message || '获取消费数据失败')
    }
  } catch (err) {
    console.error('[ConsumptionCard] 加载消费数据失败:', {
      error: err,
      status: err?.response?.status,
      data: err?.response?.data,
      message: err?.message
    })
    
    if (err?.response?.status === 404) {
      // 404 是正常情况（未绑定），不显示错误
      console.log('[ConsumptionCard] 用户未绑定学号（404）')
    } else if (err?.response?.status === 401) {
      // 未登录时不弹窗，交由界面遮罩或导航处理
      console.log('[ConsumptionCard] 未登录，跳过提示')
    } else {
      const errorMsg = err?.response?.data?.message || '加载消费数据失败，请稍后重试'
      window.$message?.error?.(errorMsg)
    }
  } finally {
    loading.value = false
  }
}

// 处理登录成功后的绑定操作
const handleLoginSuccess = async (servicehall) => {
  try {
    console.log('[ConsumptionCard] 开始绑定，学号:', loginForm.value.username, 'servicehall:', servicehall)
    // 使用学号和 cookie 调用后端绑定接口
    const { fetchWithCookie } = await import('@/api/canteen')
    const result = await fetchWithCookie(loginForm.value.username, servicehall)
    
    console.log('[ConsumptionCard] 绑定接口返回:', result)
    
    if (result.code === 200) {
      window.$message?.success?.('绑定成功！')
      bindDialogVisible.value = false
      binding.value = false
      // 重新加载消费数据
      await loadConsumption()
    } else {
      console.error('[ConsumptionCard] 绑定失败，返回码:', result.code, '消息:', result.message)
      window.$message?.error?.(result.message || '绑定失败')
      bindDialogVisible.value = false
      binding.value = false
    }
  } catch (err) {
    console.error('[ConsumptionCard] 绑定异常:', err)
    console.error('[ConsumptionCard] 异常详情:', {
      message: err?.message,
      response: err?.response?.data,
      status: err?.response?.status
    })
    const errorMsg = err?.response?.data?.message || err?.message || '绑定失败，请重试'
    window.$message?.error?.(errorMsg)
    bindDialogVisible.value = false
    binding.value = false
  }
}

// 显示绑定弹窗
const showBindDialog = () => {
  bindDialogVisible.value = true
}

// 关闭绑定弹窗
const closeBindDialog = () => {
  if (binding.value) return
  bindDialogVisible.value = false
  // 恢复页面滚动
  try { document.body.style.overflow = '' } catch (e) {}
  loginStep.value = 1
  loginForm.value = {
    username: '',
    password: '',
    verificationCode: '',
    sessionId: ''
  }
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 启动登录流程
const handleStartLogin = async () => {
  if (binding.value) return
  
  binding.value = true
  console.log('[ConsumptionCard] 开始自动登录流程...')
  
  try {
    const browserType = detectBrowser()
    const response = await startAutoLogin(
      loginForm.value.username,
      loginForm.value.password,
      browserType,
      true
    )
    
    console.log('[ConsumptionCard] 登录响应:', response)
    const respPayload = response?.data ?? response
    
    if (respPayload.session_id) {
      loginForm.value.sessionId = respPayload.session_id
      
      if (respPayload.status === 'waiting_verification') {
        // 需要验证码
        loginStep.value = 2
        window.$message?.info?.('请输入验证码')
      } else if (respPayload.status === 'completed') {
        // 直接登录成功，使用返回的 cookie 进行绑定
        if (respPayload.servicehall) {
          await handleLoginSuccess(respPayload.servicehall)
        } else {
          window.$message?.error?.('登录成功但未获取到 cookie')
          bindDialogVisible.value = false
          binding.value = false
        }
      } else if (respPayload.status === 'failed') {
        // 登录失败
        window.$message?.error?.(respPayload.error || '登录失败')
        loginStep.value = 1
      }
    } else {
      window.$message?.error?.('登录失败，请重试')
    }
  } catch (err) {
    console.error('[ConsumptionCard] 绑定失败:', {
      error: err,
      status: err?.response?.status,
      data: err?.response?.data,
      message: err?.message
    })
    
    // 根据错误类型提供详细的用户提示
    const errorMsg = err?.response?.data?.message || ''
    
    if (errorMsg.includes('超时') || errorMsg.includes('timeout')) {
      window.$message?.error?.('登录超时，请确保在5分钟内完成登录')
    } else if (errorMsg.includes('浏览器') || errorMsg.includes('driver') || errorMsg.includes('Driver')) {
      window.$message?.error?.('浏览器驱动未安装或配置错误，请联系管理员')
    } else if (errorMsg.includes('cookie')) {
      window.$message?.error?.('无法获取登录凭证，请确保已成功登录一卡通系统')
    } else if (err?.response?.status === 401) {
      // 绑定流程中遇到 401，避免弹窗打断用户流程（页面上已有遮罩提示）
      console.log('[ConsumptionCard] 绑定时未登录，跳过提示')
    } else if (err?.response?.status === 500) {
      window.$message?.error?.(errorMsg || '服务器错误，请稍后重试')
    } else {
      window.$message?.error?.(errorMsg || '绑定失败，请重试')
    }
  } finally {
    binding.value = false
  }
}

// 提交验证码
const handleSubmitCode = async () => {
  if (binding.value) return
  
  binding.value = true
  console.log('[ConsumptionCard] 提交验证码...')
  
  try {
    await submitVerificationCode(
      loginForm.value.sessionId,
      loginForm.value.verificationCode
    )
    
    // 提交成功，开始轮询状态
    loginStep.value = 3
    startPolling()
  } catch (err) {
    console.error('[ConsumptionCard] 提交验证码失败:', err)
    const errorMsg = err?.response?.data?.error || err?.response?.data?.message || '验证码提交失败'
    window.$message?.error?.(errorMsg)
    binding.value = false
  }
}

// 开始轮询登录状态
const startPolling = () => {
  let pollCount = 0
  let servicehallWaits = 0
  const maxPolls = 60 // 最多轮询60次（2秒一次，共120秒）
  
  pollTimer = setInterval(async () => {
    pollCount++
    
    if (pollCount > maxPolls) {
      clearInterval(pollTimer)
      pollTimer = null
      binding.value = false
      loginStep.value = 1
      window.$message?.error?.('登录超时，请重试')
      return
    }
    
    try {
      const response = await checkLoginStatus(loginForm.value.sessionId)
      console.log('[ConsumptionCard] 轮询状态:', response)
      const respPayload = response?.data ?? response
      
      if (respPayload.status === 'completed') {
        // 登录成功，优先等待 servicehall 出现再绑定（可能存在短暂延迟）
        if (respPayload.servicehall) {
          clearInterval(pollTimer)
          pollTimer = null
          await handleLoginSuccess(respPayload.servicehall)
        } else {
          servicehallWaits++
          console.log('[ConsumptionCard] 登录已完成但无 servicehall，等待中 count=', servicehallWaits)
          // 等待最多3次额外轮询（约6秒）再放弃
          if (servicehallWaits > 3) {
            clearInterval(pollTimer)
            pollTimer = null
            window.$message?.error?.('登录成功但未获取到 cookie，请重试')
            bindDialogVisible.value = false
            binding.value = false
          }
          // 否则继续轮询
        }
      } else if (respPayload.status === 'failed') {
        // 登录失败
        clearInterval(pollTimer)
        pollTimer = null
        binding.value = false
        loginStep.value = 2
        window.$message?.error?.(respPayload.error || '登录失败，请重试')
      }
      // 其他状态继续轮询
    } catch (err) {
      console.error('[ConsumptionCard] 轮询状态失败:', err)
      // 会话不存在或其他错误
      if (err?.response?.status === 404) {
        clearInterval(pollTimer)
        pollTimer = null
        binding.value = false
        loginStep.value = 1
        window.$message?.error?.('登录会话已过期，请重新登录')
      }
    }
  }, 2000) // 每2秒轮询一次
}

// 查看详情
const viewDetails = () => {
  router.push('/canteen-consumption')
}

// 监听数据变化，重绘图表
watch(() => consumptionData.value, () => {
  if (consumptionData.value) {
    setTimeout(drawDonutChart, 100)
  }
})

// 当弹窗打开时锁定页面滚动，关闭时恢复
watch(() => bindDialogVisible.value, (val) => {
  try {
    document.body.style.overflow = val ? 'hidden' : ''
  } catch (e) {}
})

onUnmounted(() => {
  // 清理轮询定时器并恢复滚动
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  try { document.body.style.overflow = '' } catch (e) {}
})

onMounted(() => {
  loadConsumption()
})

// 暴露刷新方法供外部调用
defineExpose({
  refresh: loadConsumption
})
</script>

<style scoped>
.consumption-card {
  min-height: 280px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  color: #909399;
  margin-bottom: 16px;
  font-size: 14px;
}

.bind-btn {
  padding: 8px 24px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.bind-btn:hover {
  background: var(--brand-700);
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

/* 数据展示 */
.consumption-data {
  padding: 20px;
}

.chart-container {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
}

.total-amount {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.amount-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.amount-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.canteen-summary {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.summary-item .label {
  font-size: 12px;
  color: #909399;
}

.summary-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 绑定弹窗 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog-content h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #303133;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-accent);
}

.field-hint {
  margin: 6px 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.dialog-tip {
  background: var(--color-accent-weak);
  border-left: 3px solid var(--color-accent);
  padding: 12px;
  margin: 16px 0;
  font-size: 13px;
  color: #606266;
}

.dialog-tip p {
  margin: 0 0 8px;
  font-weight: 600;
}

.dialog-tip ul {
  margin: 0;
  padding-left: 20px;
}

.dialog-tip li {
  margin-bottom: 4px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.cancel-btn,
.confirm-btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background: #F5F7FA;
  color: #606266;
}

.cancel-btn:hover:not(:disabled) {
  background: #E4E7ED;
}

.confirm-btn {
  background: var(--color-accent);
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: var(--color-accent-weak);
}

.cancel-btn:disabled,
.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.link {
  color: var(--color-accent);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.link:hover {
  color: var(--color-accent-weak);
}

/* 验证码提示 */
.verification-tip {
  background: #FFF7E6;
  border-left: 3px solid #E6A23C;
  padding: 16px;
  margin: 16px 0;
  border-radius: 4px;
}

.tip-icon {
  font-size: 32px;
  text-align: center;
  margin-bottom: 8px;
}

.tip-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
  text-align: center;
}

/* 加载步骤 */
.loading-step {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409EFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-step p {
  color: #606266;
  font-size: 14px;
  margin: 0;
}
</style>
