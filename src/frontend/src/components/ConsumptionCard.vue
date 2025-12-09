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
  <div v-if="bindDialogVisible" class="dialog-overlay" @click="closeBindDialog">
    <div class="dialog-content" @click.stop>
      <h3>绑定食堂消费</h3>
      <div class="dialog-tip">
        <p>📝 绑定说明：</p>
        <ul>
          <li>系统将自动打开浏览器</li>
          <li>请在浏览器中登录清华一卡通系统</li>
          <li>登录成功后，系统会自动提取学号并获取近3个月的食堂消费数据</li>
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
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import SectionCard from './SectionCard.vue'
import { getConsumption, bindAccount } from '@/api/canteen'

const router = useRouter()
const chartCanvas = ref(null)
const loading = ref(false)
const consumptionData = ref(null)
const bindDialogVisible = ref(false)
const binding = ref(false)

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

  // 颜色方案
  const colors = [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C',
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
      window.$message?.error?.('请先登录')
    } else {
      const errorMsg = err?.response?.data?.message || '加载消费数据失败，请稍后重试'
      window.$message?.error?.(errorMsg)
    }
  } finally {
    loading.value = false
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
  console.log('[ConsumptionCard] 开始绑定,浏览器类型:', browserType)
  
  // 提示用户等待浏览器打开
  window.$message?.info?.('正在打开浏览器，请在浏览器中完成登录...')
  
  try {
    // 系统自动提取学号
    const response = await bindAccount(null, browserType)
    
    if (response.code === 200) {
      console.log('[ConsumptionCard] 绑定成功:', response.data)
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
      console.warn('[ConsumptionCard] 绑定失败，返回状态:', response)
      window.$message?.error?.(response.message || '绑定失败')
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
      window.$message?.error?.('请先登录系统')
    } else if (err?.response?.status === 500) {
      window.$message?.error?.(errorMsg || '服务器错误，请稍后重试')
    } else {
      window.$message?.error?.(errorMsg || '绑定失败，请重试')
    }
  } finally {
    binding.value = false
  }
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
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.bind-btn:hover {
  background: #66B1FF;
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

.link {
  color: #409EFF;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.link:hover {
  color: #66B1FF;
}
</style>
