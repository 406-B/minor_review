<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>

    <div class="consumption-page">
      <PageActions>
        <template #left>
          <button class="toolbar-btn" @click="goBack">返回</button>
        </template>
        <template #right>
          <button v-if="hasData" class="toolbar-btn refresh-btn" @click="handleRefresh" :disabled="refreshing">
            {{ refreshing ? '刷新中...' : '刷新数据' }}
          </button>
          <button v-if="hasData" class="toolbar-btn danger-btn" @click="handleUnbind">解绑学号</button>
        </template>
      </PageActions>

      <div class="page-header">
        <h1>食堂消费记录</h1>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-container">
        <p>加载中...</p>
      </div>

      <!-- 未绑定状态 -->
      <div v-else-if="!hasData" class="empty-container">
        <div class="empty-icon">🍽️</div>
        <p class="empty-text">尚未绑定学号</p>
        <p class="empty-hint">绑定学号后，可查看食堂消费数据</p>
        <button class="bind-btn" @click="showBindDialog">立即绑定</button>
      </div>

      <!-- 数据展示 -->
      <div v-else class="content-container">
        <!-- 概览卡片 -->
        <div class="overview-card card">
          <div class="card-header">
            <h2>消费概览</h2>
          </div>
          <div class="card-body">
            <div class="overview-grid">
              <div class="overview-item">
                <div class="item-label">学号</div>
                <div class="item-value">{{ consumptionData.idserial }}</div>
              </div>
              <div class="overview-item highlight">
                <div class="item-label">总消费</div>
                <div class="item-value primary">¥{{ consumptionData.total_amount }}</div>
              </div>
              <div class="overview-item">
                <div class="item-label">消费食堂</div>
                <div class="item-value">{{ consumptionData.canteen_count }} 个</div>
              </div>
              <div class="overview-item">
                <div class="item-label">最后更新</div>
                <div class="item-value">{{ formatDate(consumptionData.last_fetched) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 图表卡片 -->
        <div class="chart-card card">
          <div class="card-header">
            <h2>消费分布</h2>
          </div>
          <div class="card-body">
            <div class="chart-wrapper">
              <canvas ref="chartCanvas" width="300" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- 食堂列表 -->
        <div class="canteen-list-card card">
          <div class="card-header">
            <h2>各食堂消费明细</h2>
          </div>
          <div class="card-body">
            <div class="canteen-list">
              <div 
                v-for="(item, index) in canteenList" 
                :key="index"
                class="canteen-item"
              >
                <div class="canteen-info">
                  <div class="canteen-icon" :style="{ backgroundColor: item.color }">
                    {{ item.name[0] }}
                  </div>
                  <div class="canteen-name">{{ item.name }}</div>
                </div>
                <div class="canteen-stats">
                  <div class="amount">¥{{ item.amount }}</div>
                  <div class="percentage">{{ item.percentage }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

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
  </PageContainer>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PageActions from '@/components/PageActions.vue'
import { getConsumption, refreshConsumption, unbindAccount, startAutoLogin, submitVerificationCode, checkLoginStatus } from '@/api/canteen'

const router = useRouter()
const chartCanvas = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const consumptionData = ref(null)
const hasData = computed(() => !!consumptionData.value)
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

// 颜色方案
const colors = [
  '#409EFF', '#67C23A', '#E6A23C', '#F56C6C',
  '#909399', '#00D4AA', '#FF6B9D', '#C990C0'
]

// 食堂列表（带百分比）
const canteenList = computed(() => {
  if (!consumptionData.value?.canteen_data) return []
  
  const data = consumptionData.value.canteen_data
  const total = parseFloat(consumptionData.value.total_amount)
  
  return Object.entries(data)
    .map(([name, amount], index) => ({
      name,
      amount: parseFloat(amount).toFixed(2),
      percentage: ((parseFloat(amount) / total) * 100).toFixed(1),
      color: colors[index % colors.length]
    }))
    .sort((a, b) => parseFloat(b.amount) - parseFloat(a.amount))
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '--'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 绘制环状图
const drawDonutChart = () => {
  if (!chartCanvas.value || !canteenList.value.length) return

  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  const centerX = 150
  const centerY = 150
  const radius = 120
  const innerRadius = 75

  // 清空画布
  ctx.clearRect(0, 0, 300, 300)

  const total = canteenList.value.reduce((sum, item) => sum + parseFloat(item.amount), 0)
  let startAngle = -Math.PI / 2

  canteenList.value.forEach((item) => {
    const angle = (parseFloat(item.amount) / total) * 2 * Math.PI
    const endAngle = startAngle + angle

    // 绘制扇形
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, endAngle)
    ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true)
    ctx.closePath()
    ctx.fillStyle = item.color
    ctx.fill()

    // 绘制边框
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 2
    ctx.stroke()

    startAngle = endAngle
  })

  // 绘制中心文字
  ctx.fillStyle = '#303133'
  ctx.font = 'bold 16px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('总消费', centerX, centerY - 12)
  
  ctx.font = 'bold 24px sans-serif'
  ctx.fillStyle = '#409EFF'
  ctx.fillText(`¥${consumptionData.value.total_amount}`, centerX, centerY + 12)
}

// 加载消费数据
const loadConsumption = async () => {
  loading.value = true
  try {
    console.log('[CanteenConsumption] 开始加载消费数据...')
    const response = await getConsumption()
    
    if (response.code === 200 && response.data) {
      console.log('[CanteenConsumption] 消费数据加载成功:', response.data)
      consumptionData.value = response.data
      setTimeout(drawDonutChart, 100)
    } else if (response.code === 404) {
      console.log('[CanteenConsumption] 用户未绑定学号')
      consumptionData.value = null
    } else {
      console.warn('[CanteenConsumption] 获取消费数据返回异常状态:', response)
      window.$message?.warning?.(response.message || '获取消费数据失败')
    }
  } catch (err) {
    console.error('[CanteenConsumption] 加载消费数据失败:', {
      error: err,
      status: err?.response?.status,
      data: err?.response?.data,
      message: err?.message
    })
    
    if (err?.response?.status === 404) {
      console.log('[CanteenConsumption] 用户未绑定学号（404）')
    } else if (err?.response?.status === 401) {
      window.$message?.error?.('登录已过期，请重新登录')
      setTimeout(() => router.push('/login'), 1500)
    } else {
      const errorMsg = err?.response?.data?.message || '加载消费数据失败，请刷新页面重试'
      window.$message?.error?.(errorMsg)
    }
  } finally {
    loading.value = false
  }
}

// 刷新数据
const handleRefresh = async () => {
  refreshing.value = true
  console.log('[CanteenConsumption] 开始刷新消费数据...')
  
  // 自动检测浏览器类型
  const browserType = detectBrowser()
  
  try {
    const response = await refreshConsumption(null, browserType)
    
    if (response.code === 200 && response.data) {
      console.log('[CanteenConsumption] 刷新成功:', response.data)
      window.$message?.success?.('刷新成功！正在获取完整数据...')
      
      // 刷新成功后，重新获取完整的序列化数据
      await loadConsumption()
    } else {
      console.warn('[CanteenConsumption] 刷新失败，返回状态:', response)
      window.$message?.error?.(response.message || '刷新失败')
    }
  } catch (err) {
    console.error('[CanteenConsumption] 刷新失败:', {
      error: err,
      status: err?.response?.status,
      data: err?.response?.data,
      message: err?.message
    })
    
    const errorMsg = err?.response?.data?.message || ''
    
    if (errorMsg.includes('未绑定')) {
      window.$message?.error?.('未绑定学号，请先绑定')
    } else if (errorMsg.includes('cookie') || errorMsg.includes('失效')) {
      window.$message?.error?.('登录凭证已失效，系统将自动重新获取，请稍候...')
    } else if (err?.response?.status === 401) {
      window.$message?.error?.('登录已过期，请重新登录')
      setTimeout(() => router.push('/login'), 1500)
    } else if (err?.response?.status === 500) {
      window.$message?.error?.(errorMsg || '服务器错误，请稍后重试')
    } else {
      window.$message?.error?.(errorMsg || '刷新失败，请稍后重试')
    }
  } finally {
    refreshing.value = false
  }
}

// 解绑
const handleUnbind = async () => {
  if (!confirm('确定要解绑学号吗？解绑后将清除所有消费数据。')) return
  
  console.log('[CanteenConsumption] 开始解绑学号...')
  
  try {
    const response = await unbindAccount()
    
    if (response.code === 200) {
      console.log('[CanteenConsumption] 解绑成功')
      window.$message?.success?.('解绑成功')
      consumptionData.value = null
    } else {
      console.warn('[CanteenConsumption] 解绑失败，返回状态:', response)
      window.$message?.error?.(response.message || '解绑失败')
    }
  } catch (err) {
    console.error('[CanteenConsumption] 解绑失败:', {
      error: err,
      status: err?.response?.status,
      data: err?.response?.data,
      message: err?.message
    })
    
    const errorMsg = err?.response?.data?.message || ''
    
    if (errorMsg.includes('未绑定')) {
      window.$message?.warning?.('尚未绑定学号')
      consumptionData.value = null
    } else if (err?.response?.status === 401) {
      window.$message?.error?.('登录已过期，请重新登录')
      setTimeout(() => router.push('/login'), 1500)
    } else {
      window.$message?.error?.(errorMsg || '解绑失败，请稍后重试')
    }
  }
}

// 处理登录成功后的绑定操作
const handleLoginSuccess = async (servicehall) => {
  try {
    console.log('[CanteenConsumption] 开始绑定，学号:', loginForm.value.username, 'servicehall:', servicehall)
    // 使用学号和 cookie 调用后端绑定接口
    const { fetchWithCookie } = await import('@/api/canteen')
    const result = await fetchWithCookie(loginForm.value.username, servicehall)
    
    console.log('[CanteenConsumption] 绑定接口返回:', result)
    
    if (result.code === 200) {
      window.$message?.success?.('绑定成功！')
      bindDialogVisible.value = false
      binding.value = false
      // 重新加载消费数据
      await loadConsumption()
    } else {
      console.error('[CanteenConsumption] 绑定失败，返回码:', result.code, '消息:', result.message)
      window.$message?.error?.(result.message || '绑定失败')
      bindDialogVisible.value = false
      binding.value = false
    }
  } catch (err) {
    console.error('[CanteenConsumption] 绑定异常:', err)
    console.error('[CanteenConsumption] 异常详情:', {
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
  console.log('[CanteenConsumption] 开始自动登录流程...')
  
  try {
    const browserType = detectBrowser()
    const response = await startAutoLogin(
      loginForm.value.username,
      loginForm.value.password,
      browserType,
      true
    )
    
    console.log('[CanteenConsumption] 登录响应:', response)
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
    console.error('[CanteenConsumption] 启动登录失败:', err)
    const errorMsg = err?.response?.data?.error || err?.response?.data?.message || err?.message || '登录失败'
    window.$message?.error?.(errorMsg)
  } finally {
    binding.value = false
  }
}

// 提交验证码
const handleSubmitCode = async () => {
  if (binding.value) return
  
  binding.value = true
  console.log('[CanteenConsumption] 提交验证码...')
  
  try {
    await submitVerificationCode(
      loginForm.value.sessionId,
      loginForm.value.verificationCode
    )
    
    // 提交成功，开始轮询状态
    loginStep.value = 3
    startPolling()
  } catch (err) {
    console.error('[CanteenConsumption] 提交验证码失败:', err)
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
      console.log('[CanteenConsumption] 轮询状态:', response)
      const respPayload = response?.data ?? response
      
      if (respPayload.status === 'completed') {
        // 登录成功，优先等待 servicehall 出现再绑定（可能存在短暂延迟）
        if (respPayload.servicehall) {
          clearInterval(pollTimer)
          pollTimer = null
          await handleLoginSuccess(respPayload.servicehall)
        } else {
          servicehallWaits++
          console.log('[CanteenConsumption] 登录已完成但无 servicehall，等待中 count=', servicehallWaits)
          if (servicehallWaits > 3) {
            clearInterval(pollTimer)
            pollTimer = null
            window.$message?.error?.('登录成功但未获取到 cookie，请重试')
            bindDialogVisible.value = false
            binding.value = false
          }
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
      console.error('[CanteenConsumption] 轮询状态失败:', err)
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

// 返回
const goBack = () => {
  router.back()
}

// 当弹窗打开时锁定页面滚动，关闭时恢复
watch(() => bindDialogVisible.value, (val) => {
  try { document.body.style.overflow = val ? 'hidden' : '' } catch (e) {}
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  try { document.body.style.overflow = '' } catch (e) {}
})

onMounted(() => {
  loadConsumption()
})
</script>

<style scoped>
.consumption-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0;
}

.toolbar-btn {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.toolbar-btn:hover:not(:disabled) {
  background: #F5F7FA;
  border-color: #409EFF;
  color: #409EFF;
}

.toolbar-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn {
  background: #409EFF;
  color: white;
  border-color: #409EFF;
}

.refresh-btn:hover:not(:disabled) {
  background: #66B1FF;
}

.danger-btn {
  color: #F56C6C;
  border-color: #F56C6C;
}

.danger-btn:hover {
  background: #FEF0F0;
}

/* 加载和空状态 */
.loading-container,
.empty-container {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: #303133;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

.bind-btn {
  padding: 12px 32px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.bind-btn:hover {
  background: #66B1FF;
}

/* 内容区域 */
.content-container {
  display: grid;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #E4E7ED;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.card-body {
  padding: 20px;
}

/* 概览卡片 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.overview-item {
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
  text-align: center;
}

.overview-item.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.overview-item.highlight .item-label,
.overview-item.highlight .item-value {
  color: white;
}

.item-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.item-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.item-value.primary {
  color: white;
  font-size: 28px;
}

/* 图表卡片 */
.chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

/* 食堂列表 */
.canteen-list {
  display: grid;
  gap: 12px;
}

.canteen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
  transition: all 0.3s;
}

.canteen-item:hover {
  background: #E4E7ED;
  transform: translateX(4px);
}

.canteen-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.canteen-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.canteen-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.canteen-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.amount {
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
}

.percentage {
  font-size: 14px;
  color: #909399;
  min-width: 50px;
  text-align: right;
}

/* 绑定弹窗（复用 ConsumptionCard 的样式）*/
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
  border-color: #409EFF;
}

.field-hint {
  margin: 6px 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.dialog-tip {
  background: #F0F9FF;
  border-left: 3px solid #409EFF;
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
  background: #409EFF;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #66B1FF;
}

.cancel-btn:disabled,
.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .canteen-stats {
    flex-direction: column;
    gap: 4px;
    align-items: flex-end;
  }
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
