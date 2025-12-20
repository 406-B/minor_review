<template>
  <div class="food-calendar">
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <el-button size="small" @click="loadData">重试</el-button>
    </div>
    
    <div v-else class="calendar-content">
      <div v-for="dayData in checkIns" :key="dayData.date" class="day-column">
        <div class="date-label">
          <div class="date">{{ formatDateLabel(dayData.date) }}</div>
          <div class="weekday">{{ getWeekday(dayData.date) }}</div>
        </div>
        
        <div class="dishes-container">
          <!-- 翻页按钮 - 左 -->
          <button 
            v-if="getMergedDishes(dayData).length > 3"
            class="page-btn page-left"
            @click="prevPage(dayData.date)"
            aria-label="上一页"
          >
            ◀
          </button>
          
          <div class="dishes-wrapper">
            <template v-if="getMergedDishes(dayData).length > 0">
              <!-- 显示当前页的菜品 -->
              <DishCheckInCard 
                v-for="dish in getCurrentPageDishes(dayData)" 
                :key="dish.id + '-' + dayData.date"
                :dish="dish"
              />
            </template>
            <div v-else class="no-check-in">
              <span>未打卡</span>
            </div>
          </div>
          
          <!-- 翻页按钮 - 右 -->
          <button 
            v-if="getMergedDishes(dayData).length > 3"
            class="page-btn page-right"
            @click="nextPage(dayData.date)"
            aria-label="下一页"
          >
            ▶
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecentCheckIns } from '@/api/foodCalendar'
import DishCheckInCard from './DishCheckInCard.vue'

const props = defineProps({
  days: {
    type: Number,
    default: 7
  }
})

const loading = ref(false)
const error = ref(null)
const checkIns = ref([])
// 记录每一天的当前页码
const pageIndexes = ref({})

const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await getRecentCheckIns(props.days)
    
    if (response.code === 200 && response.data) {
      checkIns.value = response.data.check_ins || []
      // 初始化每天的页码为0
      checkIns.value.forEach(day => {
        pageIndexes.value[day.date] = 0
      })
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

// 合并相同菜品，统计每个菜品在当天的打卡次数
const getMergedDishes = (dayData) => {
  if (!dayData.dishes || dayData.dishes.length === 0) {
    return []
  }
  
  const dishMap = new Map()
  
  dayData.dishes.forEach(dish => {
    if (dishMap.has(dish.id)) {
      // 相同菜品，累加当天打卡次数
      const existing = dishMap.get(dish.id)
      existing.daily_check_count = (existing.daily_check_count || 1) + 1
    } else {
      // 新菜品，初始化当天打卡次数为1
      dishMap.set(dish.id, {
        ...dish,
        daily_check_count: 1
      })
    }
  })
  
  return Array.from(dishMap.values())
}

// 获取当前页应该显示的菜品
const getCurrentPageDishes = (dayData) => {
  const mergedDishes = getMergedDishes(dayData)
  const currentPage = pageIndexes.value[dayData.date] || 0
  const pageSize = 3
  
  if (mergedDishes.length <= pageSize) {
    return mergedDishes
  }
  
  const startIndex = currentPage * pageSize
  return mergedDishes.slice(startIndex, startIndex + pageSize)
}

// 上一页
const prevPage = (date) => {
  const mergedDishes = getMergedDishes(checkIns.value.find(d => d.date === date))
  const totalPages = Math.ceil(mergedDishes.length / 3)
  const currentPage = pageIndexes.value[date] || 0
  
  // 循环翻页：如果在第一页，跳到最后一页
  pageIndexes.value[date] = currentPage === 0 ? totalPages - 1 : currentPage - 1
}

// 下一页
const nextPage = (date) => {
  const mergedDishes = getMergedDishes(checkIns.value.find(d => d.date === date))
  const totalPages = Math.ceil(mergedDishes.length / 3)
  const currentPage = pageIndexes.value[date] || 0
  
  // 循环翻页：如果在最后一页，跳到第一页
  pageIndexes.value[date] = (currentPage + 1) % totalPages
}

const formatDateLabel = (dateStr) => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (dateStr === formatDate(today)) {
    return '今天'
  } else if (dateStr === formatDate(yesterday)) {
    return '昨天'
  } else {
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}/${day}`
  }
}

const getWeekday = (dateStr) => {
  const date = new Date(dateStr)
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weekdays[date.getDay()]
}

const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.food-calendar {
  width: 100%;
}

.loading,
.error {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-muted);
}

.error {
  color: #f56c6c;
}

.calendar-content {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
}

.day-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: var(--color-surface);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  transition: all 0.2s;
  height: 450px;
}

.day-column:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--brand-200);
}

.date-label {
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.date {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 2px;
}

.weekday {
  font-size: 11px;
  color: var(--color-muted);
}

.dishes-container {
  position: relative;
  display: flex;
  flex-direction: row;
  gap: 6px;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 0;
  padding: 8px 0;
}

.dishes-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
  flex: 1;
  min-height: 0;
}

.page-btn {
  width: 20px;
  height: 48px;
  border: 1px solid var(--color-border);
  background: white;
  color: var(--color-text);
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-btn.page-left {
  margin-right: 2px;
}

.page-btn.page-right {
  margin-left: 2px;
}

.page-btn:hover {
  background: var(--brand-50);
  border-color: var(--brand-200);
  color: var(--brand-600);
}

.page-btn:active {
  transform: scale(0.95);
}

.no-check-in {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  flex: 1;
  min-height: 100px;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  color: var(--color-muted);
  font-size: 12px;
}

@media (max-width: 1200px) {
  .calendar-content {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .day-column {
    height: 420px;
  }
}

@media (max-width: 768px) {
  .calendar-content {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .day-column {
    height: 380px;
  }
}
</style>
