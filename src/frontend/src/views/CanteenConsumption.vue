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
        <h3>绑定学号</h3>
        <div class="form-group">
          <label>学号</label>
          <input 
            v-model="idserial" 
            type="text" 
            placeholder="请输入清华学号"
            :disabled="binding"
          />
        </div>
        <div class="form-group">
          <label>浏览器类型</label>
          <select v-model="browserType" :disabled="binding">
            <option value="chrome">Chrome</option>
            <option value="firefox">Firefox</option>
            <option value="edge">Edge</option>
            <option value="safari">Safari</option>
          </select>
        </div>
        <div class="dialog-tip">
          <p>📝 绑定说明：</p>
          <ul>
            <li>系统将自动打开浏览器</li>
            <li>请在浏览器中登录清华一卡通系统</li>
            <li>登录成功后，系统会自动获取数据</li>
            <li>请耐心等待，此过程可能需要几分钟</li>
          </ul>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="closeBindDialog" :disabled="binding">取消</button>
          <button class="confirm-btn" @click="handleBind" :disabled="binding || !idserial">
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
const idserial = ref('')
const browserType = ref('chrome')
const binding = ref(false)

const hasData = computed(() => !!consumptionData.value)

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
    const response = await getConsumption()
    if (response.code === 200 && response.data) {
      consumptionData.value = response.data
      setTimeout(drawDonutChart, 100)
    } else if (response.code === 404) {
      consumptionData.value = null
    }
  } catch (err) {
    console.error('加载消费数据失败:', err)
    if (err?.response?.status !== 404) {
      window.$message?.error?.('加载失败')
    }
  } finally {
    loading.value = false
  }
}

// 刷新数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    const response = await refreshConsumption(null, browserType.value)
    if (response.code === 200 && response.data) {
      consumptionData.value = response.data
      window.$message?.success?.('刷新成功')
      setTimeout(drawDonutChart, 100)
    } else {
      window.$message?.error?.(response.message || '刷新失败')
    }
  } catch (err) {
    console.error('刷新失败:', err)
    window.$message?.error?.(err?.response?.data?.message || '刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 解绑
const handleUnbind = async () => {
  if (!confirm('确定要解绑学号吗？解绑后将清除所有消费数据。')) return
  
  try {
    const response = await unbindAccount()
    if (response.code === 200) {
      window.$message?.success?.('解绑成功')
      consumptionData.value = null
    } else {
      window.$message?.error?.(response.message || '解绑失败')
    }
  } catch (err) {
    console.error('解绑失败:', err)
    window.$message?.error?.('解绑失败')
  }
}

// 显示绑定弹窗
const showBindDialog = () => {
  bindDialogVisible.value = true
  idserial.value = ''
  browserType.value = 'chrome'
}

// 关闭绑定弹窗
const closeBindDialog = () => {
  if (binding.value) return
  bindDialogVisible.value = false
}

// 处理绑定
const handleBind = async () => {
  if (!idserial.value || binding.value) return
  
  binding.value = true
  try {
    const response = await bindAccount(idserial.value, browserType.value)
    if (response.code === 200) {
      window.$message?.success?.('绑定成功！')
      consumptionData.value = response.data
      bindDialogVisible.value = false
      setTimeout(drawDonutChart, 100)
    } else {
      window.$message?.error?.(response.message || '绑定失败')
    }
  } catch (err) {
    console.error('绑定失败:', err)
    window.$message?.error?.(err?.response?.data?.message || '绑定失败，请重试')
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
