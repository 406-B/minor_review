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
          <template v-if="dayData.dishes && dayData.dishes.length > 0">
            <DishCheckInCard 
              v-for="dish in dayData.dishes" 
              :key="dish.id + '-' + dayData.date"
              :dish="dish"
            />
          </template>
          <div v-else class="no-check-in">
            <span>未打卡</span>
          </div>
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

const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await getRecentCheckIns(props.days)
    
    if (response.code === 200 && response.data) {
      checkIns.value = response.data.check_ins || []
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
  min-height: 200px;
}

.day-column:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--brand-200);
}

.date-label {
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
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
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
  flex: 1;
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
}

@media (max-width: 768px) {
  .calendar-content {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .day-column {
    min-height: 150px;
  }
}
</style>
