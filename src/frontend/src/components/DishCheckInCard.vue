<template>
  <div 
    class="dish-card" 
    :class="achievementClass"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
    @click="goToDishDetail"
  >
    <div class="dish-image">
      <img :src="imageUrl" :alt="dish.name" />
      <div class="check-count-badge">×{{ dish.check_in_count }}</div>
    </div>
    <div class="dish-name" :title="dish.name">{{ dish.name }}</div>
    
    <!-- 悬浮卡片 -->
    <transition name="tooltip-fade">
      <div v-if="showTooltip" class="dish-tooltip" @click.stop>
        <div class="tooltip-header">
          <h4>{{ dish.name }}</h4>
          <div class="badge" :class="achievementClass">
            {{ achievementLabel }}
          </div>
        </div>
        
        <div class="tooltip-content">
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
            <span class="label">打卡:</span>
            <span class="value">{{ dish.check_in_count }} 次</span>
          </div>
          
          <div class="info-row">
            <span class="label">消费:</span>
            <span class="value">¥{{ dish.total_consumption?.toFixed(2) }}</span>
          </div>
          
          <div v-if="dish.tags && dish.tags.length" class="tags">
            <el-tag 
              v-for="tag in dish.tags" 
              :key="tag.id" 
              size="small" 
              type="info"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
        
        <div class="tooltip-footer">
          <span class="hint">点击查看详情</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getAchievementByCount } from '@/utils/achievements'

const props = defineProps({
  dish: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const showTooltip = ref(false)

// 根据打卡次数获取成就等级
const achievement = computed(() => {
  return getAchievementByCount(props.dish.check_in_count || 0)
})

const achievementClass = computed(() => {
  return `achievement-${achievement.value.key}`
})

const achievementLabel = computed(() => {
  return achievement.value.name
})

const imageUrl = computed(() => {
  const img = props.dish.image
  if (!img) return '/favicon.ico'
  if (img.startsWith('http') || img.startsWith('data:') || img.startsWith('blob:')) {
    return img
  }
  return img.startsWith('/') ? img : `/media/${img}`
})

const goToDishDetail = () => {
  router.push(`/dish/${props.dish.id}`)
}
</script>

<style scoped>
.dish-card {
  position: relative;
  width: 100px;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 4px;
  border-radius: 8px;
  background: var(--color-surface);
}

.dish-card:hover {
  transform: translateY(-4px);
}

/* 成就边框 */
.achievement-bronze {
  border: 2px solid #CD7F32;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.2);
}

.achievement-silver {
  border: 2px solid #C0C0C0;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.3);
}

.achievement-gold {
  border: 2px solid #FFD700;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.achievement-rainbow {
  border: 2px solid transparent;
  background: linear-gradient(white, white) padding-box,
              linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff) border-box;
  box-shadow: 0 2px 12px rgba(255, 0, 255, 0.5);
}

.dish-image {
  position: relative;
  width: 92px;
  height: 92px;
  border-radius: 6px;
  overflow: hidden;
  background: #f5f5f5;
}

.dish-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.check-count-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.dish-name {
  margin-top: 4px;
  font-size: 12px;
  text-align: center;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 2px;
}

/* 悬浮卡片 */
.dish-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  width: 240px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  padding: 12px;
}

.dish-tooltip::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: white;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.tooltip-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--color-text);
  font-weight: 600;
}

.badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  color: white;
  font-weight: bold;
}

.badge.achievement-bronze {
  background: #CD7F32;
  border: none;
}

.badge.achievement-silver {
  background: #C0C0C0;
  border: none;
}

.badge.achievement-gold {
  background: #FFD700;
  color: #333;
  border: none;
}

.badge.achievement-rainbow {
  background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff);
  border: none;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
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

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.tooltip-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.tooltip-footer .hint {
  font-size: 11px;
  color: var(--color-muted);
  font-style: italic;
}

/* 动画 */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-4px);
}
</style>
