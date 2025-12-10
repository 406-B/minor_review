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
    <div v-if="bindDialogVisible" class="dialog-overlay" @click="closeBindDialog">
      <div class="dialog-content" @click.stop>
        <h3>绑定食堂消费</h3>
        <div class="dialog-tip">
          <p>📝 绑定说明:</p>
          <ul>
            <li>系统将自动打开浏览器</li>
            <li>请在浏览器中登录清华一卡通系统</li>
            <li>登录成功后,系统会自动提取学号并获取近3个月的食堂消费数据</li>
            <li>请耐心等待,此过程可能需要几分钟</li>
          </ul>
        </div>
        <div class="dialog-actions">
        <button class="cancel-btn" @click="closeBindDialog" :disabled="binding">取消</button>
        <button class="confirm-btn" @click="handleBind" :disabled="binding">
          {{ binding ? '绑定中...' : '确认绑定' }}
        </button>
        </div>
      </div>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PageActions from '@/components/PageActions.vue'
import { getConsumption, bindAccount, refreshConsumption, unbindAccount } from '@/api/canteen'

const router = useRouter()
const chartCanvas = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const consumptionData = ref(null)
const bindDialogVisible = ref(false)
const binding = ref(false)

const hasData = computed(() => !!consumptionData.value)

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

// 显示绑定弹窗
const showBindDialog = () => {
  bindDialogVisible.value = true
}

// 关闭绑定弹窗
const closeBindDialog = () => {
  if (binding.value) return
  bindDialogVisible.value = false
}

// 处理绑定
const handleBind = async () => {
  if (binding.value) return
  
  // 自动检测浏览器类型
  const browserType = detectBrowser()
  
  binding.value = true
  console.log('[CanteenConsumption] 开始绑定,浏览器类型:', browserType)
  
  // 提示用户等待浏览器打开
  window.$message?.info?.('正在打开浏览器，请在浏览器中完成登录（最多等待5分钟）...')
  
  try {
    // 系统自动提取学号
    const response = await bindAccount(null, browserType)
    
    if (response.code === 200) {
      console.log('[CanteenConsumption] 绑定成功:', response.data)
      const extractedId = response.data?.idserial
      if (extractedId) {
        window.$message?.success?.(`绑定成功！已自动识别学号: ${extractedId}`)
      } else {
        window.$message?.success?.('绑定成功！正在获取完整数据...')
      }
      bindDialogVisible.value = false
      
      // 绑定成功后，重新获取完整的序列化数据
      await loadConsumption()
    } else {
      console.warn('[CanteenConsumption] 绑定失败，返回状态:', response)
      window.$message?.error?.(response.message || '绑定失败')
    }
  } catch (err) {
    console.error('[CanteenConsumption] 绑定失败:', {
      error: err,
      status: err?.response?.status,
      data: err?.response?.data,
      message: err?.message
    })
    
    // 根据错误类型提供详细的用户提示
    const errorMsg = err?.response?.data?.message || ''
    
    if (errorMsg.includes('超时') || errorMsg.includes('timeout')) {
      window.$message?.error?.('登录超时，请确保在5分钟内完成登录并重试')
    } else if (errorMsg.includes('浏览器') || errorMsg.includes('driver') || errorMsg.includes('Driver')) {
      window.$message?.error?.('浏览器驱动未安装或配置错误，请检查系统配置或联系管理员')
    } else if (errorMsg.includes('cookie')) {
      window.$message?.error?.('无法获取登录凭证，请确保已成功登录一卡通系统')
    } else if (errorMsg.includes('已绑定')) {
      window.$message?.warning?.('该学号已被其他用户绑定')
    } else if (err?.response?.status === 401) {
      window.$message?.error?.('登录已过期，请重新登录')
      setTimeout(() => router.push('/login'), 1500)
    } else if (err?.response?.status === 400) {
      window.$message?.error?.(errorMsg || '参数错误，请检查学号格式')
    } else if (err?.response?.status === 500) {
      window.$message?.error?.(errorMsg || '服务器错误，请稍后重试')
    } else {
      window.$message?.error?.(errorMsg || '绑定失败，请重试')
    }
  } finally {
    binding.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

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
</style>
