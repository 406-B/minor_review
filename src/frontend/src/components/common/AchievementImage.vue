<template>
  <div class="achi-wrap" :style="wrapStyle">
    <img
      v-if="src && imageOk"
      :src="src"
      :alt="alt"
      class="achi-img"
      :class="borderClass"
      @error="onError"
      @load="onLoad"
    />
    <template v-if="!(src && imageOk)">
      <slot name="placeholder">
        <div class="achi-placeholder">图</div>
      </slot>
    </template>
    <div v-if="count > 0" class="achi-badge" :class="badgeClass">{{ badgeText }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ensureAchievementsLoaded, getDishCheckinCount, getAchievementByCount, onAchievementsUpdated, offAchievementsUpdated } from '@/utils/achievements'

const props = defineProps({
  dishId: { type: [String, Number], required: true },
  src: { type: String, default: '' },
  alt: { type: String, default: '菜品图片' },
  width: { type: [String, Number], default: '100%' },
  height: { type: [String, Number], default: '100%' },
  radius: { type: [String, Number], default: '8px' },
})

const countRef = ref(0)
const count = computed(() => countRef.value)
let handler = null
const imageOk = ref(true)

const wrapStyle = computed(() => ({
  width: typeof props.width === 'number' ? props.width + 'px' : props.width,
  height: typeof props.height === 'number' ? props.height + 'px' : props.height,
  borderRadius: typeof props.radius === 'number' ? props.radius + 'px' : props.radius,
}))

const borderClass = computed(() => {
  const ach = getAchievementByCount(count.value)
  return ach.key ? `achieve-border-${ach.key}` : ''
})
const badgeClass = computed(() => {
  const ach = getAchievementByCount(count.value)
  return ach.key ? `badge-${ach.key}` : ''
})
const badgeText = computed(() => getAchievementByCount(count.value).label)

function refresh() {
  countRef.value = getDishCheckinCount(props.dishId)
}

function onError() { imageOk.value = false }
function onLoad() { imageOk.value = true }

onMounted(async () => {
  await ensureAchievementsLoaded()
  refresh()
  handler = (e) => {
    if (!e?.detail) return
    if (Number(e.detail.dishId) === Number(props.dishId)) refresh()
  }
  onAchievementsUpdated(handler)
})

onBeforeUnmount(() => {
  if (handler) offAchievementsUpdated(handler)
})
</script>

<style scoped>
.achi-wrap { position: relative; overflow: hidden; }
.achi-img { width: 100%; height: 100%; object-fit: cover; border-radius: inherit; display: block; }
.achi-placeholder { width: 100%; height: 100%; display:flex; align-items:center; justify-content:center; color:#999; background:#f4f6f8; border-radius: inherit; font-weight:600 }
.achi-badge {
  position: absolute;
  right: 6px;
  bottom: 6px;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
/* 成就边框样式（与 DishDetail 统一） */
.achieve-border-bronze { border: 5px solid #cd7f32; }
.achieve-border-silver { border: 5px solid #c0c0c0; }
.achieve-border-gold { border: 5px solid #ffd700; }
.achieve-border-rainbow {
  border: 5px solid transparent;
  background-image: linear-gradient(white, white),
    linear-gradient(90deg, #ff0000, #ffa500, #ffff00, #00ff00, #00ffff, #0000ff, #8b00ff);
  background-origin: border-box;
  background-clip: content-box, border-box;
}
/* 成就徽章样式 */
.badge-bronze { background: #cd7f32; color: #fff; }
.badge-silver { background: #c0c0c0; color: #333; }
.badge-gold { background: #ffd700; color: #7a5f00; }
.badge-rainbow {
  background: linear-gradient(90deg, #ff0000, #ffa500, #ffff00, #00ff00, #00ffff, #0000ff, #8b00ff);
  color: #fff;
}
</style>
