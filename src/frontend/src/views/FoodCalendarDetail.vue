<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    
    <div class="calendar-detail">
      <div class="header">
        <h2>美食日历</h2>
        <div class="month-selector">
          <button class="nav-btn" @click="prevMonth" :disabled="loading">
            <span>‹</span>
          </button>
          <span class="month-label">{{ currentYear }}年 {{ currentMonth }}月</span>
          <button class="nav-btn" @click="nextMonth" :disabled="loading || isCurrentMonth">
            <span>›</span>
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <el-button @click="loadData">重试</el-button>
      </div>
      
      <div v-else class="calendar-grid">
        <!-- 星期标题 -->
        <div class="weekday-header">
          <div v-for="day in weekDays" :key="day" class="weekday-label">
            {{ day }}
          </div>
        </div>
        
        <!-- 日历格子 -->
        <div class="calendar-days">
          <!-- 填充空格 -->
          <div 
            v-for="i in firstDayOfMonth" 
            :key="'empty-' + i" 
            class="calendar-cell empty"
          ></div>
          
          <!-- 日期格子 -->
          <div 
            v-for="day in daysInMonth" 
            :key="day"
            class="calendar-cell"
            :class="{
              'has-check-in': hasCheckIn(day),
              'is-today': isToday(day)
            }"
          >
            <div class="day-number">{{ day }}</div>
            <div v-if="hasCheckIn(day)" class="dishes-preview">
              <div class="dish-dots">
                <span 
                  v-for="(dish, idx) in getDayDishes(day).slice(0, 3)" 
                  :key="idx"
                  class="dish-dot"
                  :class="`achievement-${getAchievementKey(dish)}`"
                ></span>
                <span v-if="getDayDishes(day).length > 3" class="more-count">
                  +{{ getDayDishes(day).length - 3 }}
                </span>
              </div>
            </div>
            
            <!-- 点击展开详情 -->
            <transition name="expand">
              <div v-if="expandedDay === day" class="day-detail">
                <div class="detail-header">
                  <h4>{{ currentMonth }}/{{ day }} 的打卡</h4>
                  <button class="close-btn" @click="expandedDay = null">×</button>
                </div>
                <div class="detail-dishes">
                  <DishCheckInCard 
                    v-for="dish in getDayDishes(day)" 
                    :key="dish.id"
                    :dish="dish"
                  />
                </div>
              </div>
            </transition>
            
            <!-- 点击按钮 -->
            <button 
              v-if="hasCheckIn(day)" 
              class="expand-btn"
              @click="toggleExpand(day)"
            >
              {{ expandedDay === day ? '收起' : '查看' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 统计摘要 -->
      <div v-if="summary && !loading" class="summary">
        <h3>本月统计</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <div class="label">总打卡次数</div>
            <div class="value">{{ summary.total_check_ins }}</div>
          </div>
          <div class="summary-item">
            <div class="label">不同菜品</div>
            <div class="value">{{ summary.total_dishes }}</div>
          </div>
          <div class="summary-item">
            <div class="label">总消费</div>
            <div class="value price">¥{{ summary.total_consumption?.toFixed(2) }}</div>
          </div>
          <div v-if="summary.most_frequent_dish" class="summary-item">
            <div class="label">最爱菜品</div>
            <div class="value">{{ summary.most_frequent_dish.name }}</div>
          </div>
        </div>
      </div>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCheckInHistory } from '@/api/foodCalendar'
import { getAchievementByCount } from '@/utils/achievements'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import DishCheckInCard from '@/components/DishCheckInCard.vue'

const loading = ref(false)
const error = ref(null)
const checkIns = ref([])
const summary = ref(null)
const expandedDay = ref(null)

const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth() + 1)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

// 计算当月天数
const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 0).getDate()
})

// 计算当月第一天是星期几 (0-6)
const firstDayOfMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value - 1, 1).getDay()
})

// 是否是当前月份
const isCurrentMonth = computed(() => {
  const now = new Date()
  return currentYear.value === now.getFullYear() && currentMonth.value === now.getMonth() + 1
})

const loadData = async () => {
  loading.value = true
  error.value = null
  expandedDay.value = null
  
  try {
    const response = await getCheckInHistory({
      year: currentYear.value,
      month: currentMonth.value
    })
    
    if (response.code === 200 && response.data) {
      checkIns.value = response.data.check_ins || []
      summary.value = response.data.summary || null
    } else {
      error.value = response.message || '获取打卡历史失败'
    }
  } catch (err) {
    console.error('加载打卡历史失败:', err)
    error.value = err?.response?.data?.message || err?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  loadData()
}

const nextMonth = () => {
  if (isCurrentMonth.value) return
  
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  loadData()
}

const hasCheckIn = (day) => {
  const dateStr = formatDate(day)
  return checkIns.value.some(item => item.date === dateStr && item.dishes?.length > 0)
}

const getDayDishes = (day) => {
  const dateStr = formatDate(day)
  const dayData = checkIns.value.find(item => item.date === dateStr)
  return dayData?.dishes || []
}

const isToday = (day) => {
  const now = new Date()
  return currentYear.value === now.getFullYear() &&
         currentMonth.value === now.getMonth() + 1 &&
         day === now.getDate()
}

const formatDate = (day) => {
  const month = String(currentMonth.value).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  return `${currentYear.value}-${month}-${dayStr}`
}

const toggleExpand = (day) => {
  expandedDay.value = expandedDay.value === day ? null : day
}

const getAchievementKey = (dish) => {
  return getAchievementByCount(dish.check_in_count || 0).key
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.calendar-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--color-text);
}

.month-selector {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 6px;
  cursor: pointer;
  font-size: 20px;
  color: var(--color-text);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn:hover:not(:disabled) {
  background: var(--brand-50);
  border-color: var(--brand-200);
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.month-label {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
  min-width: 140px;
  text-align: center;
}

.loading,
.error {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-muted);
}

.error {
  color: #f56c6c;
}

.calendar-grid {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.weekday-label {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-muted);
  padding: 8px;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-cell {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 8px;
  background: white;
  transition: all 0.2s;
}

.calendar-cell.empty {
  background: transparent;
  border: none;
}

.calendar-cell.has-check-in {
  cursor: pointer;
  border-color: var(--brand-200);
}

.calendar-cell.has-check-in:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--brand-400);
}

.calendar-cell.is-today {
  background: var(--brand-50);
  border-color: var(--brand-400);
  border-width: 2px;
}

.day-number {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.dishes-preview {
  margin-top: 8px;
}

.dish-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.dish-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dish-dot.achievement-bronze {
  background: #CD7F32;
}

.dish-dot.achievement-silver {
  background: #C0C0C0;
}

.dish-dot.achievement-gold {
  background: #FFD700;
}

.dish-dot.achievement-rainbow {
  background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff);
}

.more-count {
  font-size: 10px;
  color: var(--color-muted);
}

.expand-btn {
  position: absolute;
  bottom: 4px;
  right: 4px;
  font-size: 10px;
  padding: 2px 6px;
  background: var(--brand-500);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: var(--brand-600);
}

.day-detail {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  padding: 12px;
  min-width: 280px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.detail-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--color-text);
}

.close-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  color: var(--color-muted);
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e0e0e0;
  color: var(--color-text);
}

.detail-dishes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.summary {
  margin-top: 32px;
  background: var(--color-surface);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.summary h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: var(--color-text);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.summary-item .label {
  font-size: 13px;
  color: var(--color-muted);
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
}

.summary-item .value.price {
  color: #f56c6c;
}

/* 动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .month-selector {
    justify-content: center;
  }
  
  .calendar-days {
    gap: 4px;
  }
  
  .calendar-cell {
    padding: 4px;
  }
  
  .day-number {
    font-size: 12px;
  }
  
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
