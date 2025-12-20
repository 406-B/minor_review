<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    
    <div class="calendar-detail">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <span>←</span>
            <span>返回</span>
          </button>
          <h2>美食日历</h2>
        </div>
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
              <div 
                v-for="(dish, idx) in getMergedDayDishes(day).slice(0, 4)" 
                :key="idx"
                class="dish-item"
                :class="`achievement-${getAchievementKey(dish)}`"
                @mouseenter="hoverDish = { day, dishId: dish.id }"
                @mouseleave="hoverDish = null"
              >
                <span class="dish-name-text">{{ dish.name }}</span>
                <span class="dish-count">×{{ dish.daily_check_count }}</span>
                
                <!-- 悬浮卡片 -->
                <transition name="tooltip-fade">
                  <div 
                    v-if="hoverDish?.day === day && hoverDish?.dishId === dish.id" 
                    class="dish-hover-card"
                  >
                    <div class="hover-header">
                      <h4>{{ dish.name }}</h4>
                      <div class="badge" :class="`achievement-${getAchievementKey(dish)}`">
                        {{ getAchievementLabel(dish) }}
                      </div>
                    </div>
                    
                    <div class="hover-content">
                      <div class="info-row">
                        <span class="label">所属:</span>
                        <span class="value">{{ dish.canteen_name }} - {{ dish.window_name }}</span>
                      </div>
                      <div class="info-row">
                        <span class="label">价格:</span>
                        <span class="value price">¥{{ dish.price?.toFixed(2) }}</span>
                      </div>
                      <div class="info-row">
                        <span class="label">评分:</span>
                        <span class="value rating">⭐ {{ dish.rating?.toFixed(1) }}</span>
                      </div>
                      <div class="info-row">
                        <span class="label">当天打卡:</span>
                        <span class="value">{{ dish.daily_check_count }} 次</span>
                      </div>
                      <div class="info-row">
                        <span class="label">总打卡:</span>
                        <span class="value">{{ dish.check_in_count }} 次</span>
                      </div>
                    </div>
                  </div>
                </transition>
              </div>
              <div v-if="getMergedDayDishes(day).length > 4" class="more-indicator">
                …
              </div>
            </div>
            
            <!-- 点击展开详情 -->
            <transition name="expand">
              <div v-if="expandedDay === day" class="day-detail">
                <div class="detail-header">
                  <h4>{{ currentMonth }}/{{ day }} 的打卡</h4>
                  <button class="close-btn" @click="expandedDay = null">×</button>
                </div>
                <div class="detail-dishes-container">
                  <!-- 左翻页按钮 -->
                  <button 
                    v-if="getMergedDayDishes(day).length > 6"
                    class="detail-page-btn page-left"
                    @click="prevDetailPage(day)"
                    aria-label="上一页"
                  >
                    ◀
                  </button>
                  
                  <div class="detail-dishes">
                    <DishCheckInCard 
                      v-for="dish in getCurrentDetailPageDishes(day)" 
                      :key="dish.id"
                      :dish="dish"
                    />
                  </div>
                  
                  <!-- 右翻页按钮 -->
                  <button 
                    v-if="getMergedDayDishes(day).length > 6"
                    class="detail-page-btn page-right"
                    @click="nextDetailPage(day)"
                    aria-label="下一页"
                  >
                    ▶
                  </button>
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
const hoverDish = ref(null)
const detailPageIndexes = ref({})

const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth() + 1)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

// 合并同一天的相同菜品
const getMergedDayDishes = (day) => {
  const dishes = getDayDishes(day)
  const dishMap = new Map()
  
  dishes.forEach(dish => {
    if (dishMap.has(dish.id)) {
      const existing = dishMap.get(dish.id)
      existing.daily_check_count = (existing.daily_check_count || 1) + 1
    } else {
      dishMap.set(dish.id, {
        ...dish,
        daily_check_count: 1
      })
    }
  })
  
  return Array.from(dishMap.values())
}

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
  if (expandedDay.value === day) {
    expandedDay.value = null
  } else {
    expandedDay.value = day
    // 初始化该天的页码
    if (!detailPageIndexes.value[day]) {
      detailPageIndexes.value[day] = 0
    }
  }
}

// 获取展开详情当前页应该显示的菜品
const getCurrentDetailPageDishes = (day) => {
  const mergedDishes = getMergedDayDishes(day)
  const currentPage = detailPageIndexes.value[day] || 0
  const pageSize = 6
  
  if (mergedDishes.length <= pageSize) {
    return mergedDishes
  }
  
  const startIndex = currentPage * pageSize
  return mergedDishes.slice(startIndex, startIndex + pageSize)
}

// 展开详情上一页
const prevDetailPage = (day) => {
  const mergedDishes = getMergedDayDishes(day)
  const totalPages = Math.ceil(mergedDishes.length / 6)
  const currentPage = detailPageIndexes.value[day] || 0
  
  detailPageIndexes.value[day] = currentPage === 0 ? totalPages - 1 : currentPage - 1
}

// 展开详情下一页
const nextDetailPage = (day) => {
  const mergedDishes = getMergedDayDishes(day)
  const totalPages = Math.ceil(mergedDishes.length / 6)
  const currentPage = detailPageIndexes.value[day] || 0
  
  detailPageIndexes.value[day] = (currentPage + 1) % totalPages
}

const getAchievementKey = (dish) => {
  return getAchievementByCount(dish.check_in_count || 0).key
}

const getAchievementLabel = (dish) => {
  return getAchievementByCount(dish.check_in_count || 0).name
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text);
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--brand-50);
  border-color: var(--brand-200);
  color: var(--brand-600);
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
  margin-bottom: 8px;
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
  min-height: 120px;
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
  z-index: 10;
}

.calendar-cell:has(.dish-hover-card) {
  z-index: 100;
}

.calendar-cell:has(.day-detail) {
  z-index: 200;
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
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 11px;
}

.dish-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  padding: 3px 6px;
  border-radius: 4px;
  border-left: 3px solid transparent;
  background: var(--color-surface);
  transition: all 0.2s;
  cursor: pointer;
}

.dish-item:hover {
  background: var(--brand-50);
  transform: translateX(2px);
}

.dish-item.achievement-bronze {
  border-left-color: #CD7F32;
}

.dish-item.achievement-silver {
  border-left-color: #C0C0C0;
}

.dish-item.achievement-gold {
  border-left-color: #FFD700;
}

.dish-item.achievement-rainbow {
  border-left: 3px solid;
  border-image: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff) 1;
}

.dish-name-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 10px;
  color: var(--color-text);
}

.dish-count {
  font-size: 9px;
  color: var(--color-muted);
  font-weight: 600;
  flex-shrink: 0;
}

.more-indicator {
  text-align: center;
  font-size: 14px;
  color: var(--color-muted);
  padding: 4px 0;
  font-weight: bold;
}

/* 悬浮卡片 */
.dish-hover-card {
  position: absolute;
  left: 100%;
  top: 0;
  margin-left: 8px;
  width: 220px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  padding: 10px;
}

.dish-hover-card::before {
  content: '';
  position: absolute;
  right: 100%;
  top: 8px;
  border: 5px solid transparent;
  border-right-color: white;
}

.hover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

.hover-header h4 {
  margin: 0;
  font-size: 13px;
  color: var(--color-text);
  font-weight: 600;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
  margin-left: 4px;
}

.badge.achievement-bronze {
  background: #CD7F32;
}

.badge.achievement-silver {
  background: #C0C0C0;
}

.badge.achievement-gold {
  background: #FFD700;
  color: #333;
}

.badge.achievement-rainbow {
  background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff);
}

.hover-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.info-row .label {
  color: var(--color-muted);
  font-weight: 500;
}

.info-row .value {
  color: var(--color-text);
  font-weight: 600;
}

.value.price {
  color: #f56c6c;
}

.value.rating {
  color: #ff9800;
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-4px);
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
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1002;
  padding: 0;
  min-width: 480px;
  width: max-content;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
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

.detail-dishes-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  min-height: 300px;
  min-width: 450px;
}

.detail-page-btn {
  width: 28px;
  height: 110px;
  border: 1px solid var(--color-border);
  background: white;
  color: var(--color-text);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.detail-page-btn:hover {
  background: var(--brand-50);
  border-color: var(--brand-200);
  color: var(--brand-600);
}

.detail-page-btn:active {
  transform: scale(0.95);
}

.detail-dishes {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 12px;
  flex: 1;
  min-height: 270px;
  max-height: 270px;
}

.detail-dishes :deep(.dish-card) {
  width: 100%;
  height: 100%;
  min-width: 0;
  max-width: 110px;
  margin: 0 auto;
  overflow: visible;
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
