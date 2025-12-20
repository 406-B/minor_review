<template>
  <div class="cards">
    <el-skeleton v-if="loading" :rows="3" animated />
    <div v-else class="grid">
      <el-card v-for="d in dishes" :key="d.id" class="dish" @click="$router.push('/dish/' + d.id)">
        <div class="thumb">
          <AchievementImage
            :dish-id="d.id"
            :src="imageUrl(d.image)"
            :width="'100%'"
            :height="'100%'"
            :radius="6"
          >
            <template #placeholder>
              <div class="thumb placeholder">{{ d.name?.[0] || '图' }}</div>
            </template>
          </AchievementImage>
        </div>
        <div class="row between">
          <div class="name">{{ d.name }}</div>
            <div class="score">★ {{ formatRating(d.rating) }}</div>
        </div>
        <div class="meta">{{ d.canteen_name || '未知食堂' }} · {{ (d.tags || []).map(t=>t.name).join('、') }}</div>
      </el-card>
    </div>
  </div>
  
</template>

<script setup>
import AchievementImage from '@/components/common/AchievementImage.vue'
defineProps({
  dishes: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})
const formatRating = (val) => {
  const n = Number(val)
  return Number.isFinite(n) ? n.toFixed(1) : '0.0'
}
const imageUrl = (src) => {
  if (!src) return '/favicon.ico'
  if (/^(https?:|data:|blob:)/.test(src)) return src
  // ensure media prefix
  if (src.startsWith('/media/')) return src
  return src.startsWith('/') ? src : '/media/' + src
}
</script>

<style scoped>
.row { display:flex; align-items:center; gap:8px; margin: 8px 0 }
.row.between { justify-content: space-between }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-top: 12px }
.dish { cursor: pointer; overflow: hidden }
.dish .name { font-weight: 600 }
.dish .meta { color: var(--color-muted); margin-top: 4px; font-size: 12px }
.thumb { width: 100%; height: 140px; border-radius: 6px; overflow: hidden; background: #f4f6f8 }
.thumb :deep(img), .thumb :deep(.el-image__inner) { width: 100%; height: 100%; object-fit: cover }
.thumb.placeholder { display:flex; align-items:center; justify-content:center; color:#999; font-weight:600; font-size: 22px }
</style>
