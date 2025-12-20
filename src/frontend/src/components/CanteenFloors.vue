<template>
  <div class="canteen-floors">
  <el-tabs v-model="activeFloor" tab-position="top" type="card">
      <el-tab-pane
    v-for="floor in floors"
        :key="floor.id"
        :label="floor.name"
    :name="String(floor.id)"
      >
        <div class="windows-list">
          <div class="windows-list-inner" :key="animationKey">
            <div
              v-for="(window, idx) in floor.windows"
              :key="window.id"
              class="window-block"
              :style="staggerStyle(idx)"
              ref="windowRefs"
            >
            <div class="window-title">{{ window.name }}</div>
            <div class="dish-card-list">
              <div v-for="dish in window.dishes" :key="dish.id" class="dish-card" @click="goToDish && goToDish(dish.id)">
                <AchievementImage
                  v-if="dish.image"
                  :dish-id="dish.id"
                  :src="getImageUrl(dish.image)"
                  :width="100"
                  :height="72"
                  :radius="6"
                  alt="菜品图片"
                  class="dish-card-img"
                />
                <div class="dish-card-info">
                  <div class="dish-card-name">{{ dish.name }}</div>
                  <div class="dish-card-price">￥{{ dish.price }}</div>
                </div>
              </div>
            </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import AchievementImage from '@/components/common/AchievementImage.vue'
function getImageUrl(image) {
  if (!image) return ''
  if (image.startsWith('http://') || image.startsWith('https://')) return image
  if (image.startsWith('/media/')) return image
  return '/media/' + image.replace(/^\/+/, '')
}


import { ref, watch, computed, onMounted, onBeforeUnmount, onUpdated, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getCanteenFloors } from '@/utils/api/listApi'
import { useRouter } from 'vue-router'

const props = defineProps({
  canteenId: {
    type: String,
    required: true
  }
})

const router = useRouter()

function goToDish(dishId) {
  const state = { from: router.currentRoute.value.name, scrollY: window.scrollY }
  router.push({ name: 'DishDetail', params: { id: dishId }, state })
}

const floors = ref([])
const emit = defineEmits(['floorsLoaded'])
const activeFloor = ref('')
// 切换楼层时通过更新 key 触发过渡重新进入
const animationTick = ref(0)
const animationKey = computed(() => `${activeFloor.value}-${animationTick.value}`)
const route = useRoute()

// IntersectionObserver: 仅当窗口块进入视口时触发浮现
const windowRefs = ref([])
let io = null

function setupObserver() {
  if (io) return
  if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
    io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const el = entry.target
      if (entry.isIntersecting) {
        el.classList.add('is-visible')
        io.unobserve(el)
      }
    })
    }, { root: null, threshold: 0.01 })
  } else {
    io = null
  }
}

function observeWindows() {
  if (!io) setupObserver()
  // 清理旧的可见标记，重新观察新节点
  const skipAnimation = sessionStorage.getItem('returningFromDetail') === '1'
  windowRefs.value.forEach((el) => {
    if (!el) return
    el.classList.remove('is-visible')
    if (skipAnimation) {
      // 返回详情时直接显示，不做浮现
      el.classList.add('is-visible')
    } else if (io) {
      io.observe(el)
    } else {
      // 回退：不支持 IO 时直接显示
      el.classList.add('is-visible')
    }
  })
  // 用一次后清除标记
  if (skipAnimation) sessionStorage.removeItem('returningFromDetail')
}

onMounted(() => {
  setupObserver()
  // 初次数据到位后，等待 DOM 更新再开始观察
  nextTick(() => {
    observeWindows()
  })
})

// DOM 更新后（例如列表刷新），重新观察新出现的窗口块
onUpdated(() => {
  nextTick(() => {
    observeWindows()
  })
})

onBeforeUnmount(() => {
  if (io) {
    windowRefs.value.forEach((el) => el && io.unobserve(el))
    io.disconnect()
    io = null
  }
})

// 阶梯延迟（ms）与持续时长配置
const baseDelay = 40
const maxDelay = 12 // 最多延迟阶梯数量，避免过长
const durationMs = 360

function staggerStyle(idx) {
  const safeIdx = Math.min(idx, maxDelay)
  const delay = safeIdx * baseDelay
  return {
    '--fade-up-delay': `${delay}ms`,
    '--fade-up-duration': `${durationMs}ms`
  }
}

const fetchFloors = async () => {
  try {
    const res = await getCanteenFloors(props.canteenId)
    if (res && Array.isArray(res.data)) {
      floors.value = res.data
      if (floors.value.length > 0) {
  // 优先恢复持久化的楼层
  const savedFloorKey = `activeFloor:${props.canteenId}`
  const saved = sessionStorage.getItem(savedFloorKey)
  const exists = saved && floors.value.some(f => String(f.id) === String(saved))
  activeFloor.value = exists ? String(saved) : String(floors.value[0].id)
  emit('floorsLoaded', true)
      }
    } else {
      floors.value = []
      emit('floorsLoaded', true)
    }
  } catch (e) {
    floors.value = []
    emit('floorsLoaded', true)
  }
}

watch(() => props.canteenId, fetchFloors, { immediate: true })

// 每次切换楼层，递增 tick，使 TransitionGroup 重新挂载触发 appear 过渡
watch(activeFloor, async () => {
  // 仅在非“返回详情”场景递增 animationTick，触发浮现动画
  if (sessionStorage.getItem('returningFromDetail') !== '1') {
    animationTick.value++
  }
  // 持久化当前食堂的楼层选择
  const savedFloorKey = `activeFloor:${props.canteenId}`
  sessionStorage.setItem(savedFloorKey, String(activeFloor.value))
  await nextTick()
  observeWindows()
})
</script>

<style scoped>
.canteen-floors {
  width: 100%;
  min-height: calc(100vh - 64px);
  background: transparent;
}
.windows-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 16px;
}
.windows-list-inner {
  display: contents; /* 保持原列布局 */
}
.window-block {
  background: #fff7ed;
  border: 1px solid #ffe0b2;
  border-radius: 8px;
  padding: 16px;
  min-width: 220px;
  flex: 1 1 220px;
  box-shadow: 0 2px 8px #f5c16c22;
  /* 初始隐藏并下移，待进入视口再浮现 */
  opacity: 0;
  transform: translateY(12px);
  transition: opacity var(--fade-up-duration, 360ms) ease-out,
              transform var(--fade-up-duration, 360ms) ease-out;
  transition-delay: var(--fade-up-delay, 0ms);
}
.no-animate .window-block {
  opacity: 1 !important;
  transform: none !important;
}
.window-block:hover {
  /* 悬浮时无任何放大和阴影变化 */
  box-shadow: 0 2px 8px #f5c16c22;
  transform: none;
}
.window-title {
  font-weight: bold;
  color: orange;
  margin-bottom: 8px;
}

.dish-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  margin-top: 8px;
}
.dish-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #f5c16c22;
  padding: 16px 12px 12px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: box-shadow 0.18s, transform 0.18s;
  border: 1px solid #ffe0b2;
}
.dish-card:hover {
  box-shadow: 0 8px 32px #ff980033;
  transform: translateY(-2px) scale(1.03);
}
.dish-card-img {
  width: 100px;
  height: 72px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 1px 4px #ff980033;
  margin-bottom: 10px;
}
.dish-card-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.dish-card-name {
  font-weight: 500;
  color: #333;
  font-size: 16px;
  margin-bottom: 4px;
  text-align: center;
}
.dish-card-price {
  color: #ff9800;
  font-weight: bold;
  font-size: 15px;
  text-align: center;
}
@media (min-width: 900px) {
  .dish-card-list {
    grid-template-columns: repeat(5, 1fr);
  }
}

/* 进入视口后浮现 */
.window-block.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* 无障碍：尊重减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .window-block {
    transition: none;
  }
}
</style>
