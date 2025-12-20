<template>
  <div class="post-item" @click="handleClick">
    <div class="post-content">
      <div class="post-title">{{ post.title || post.subject || '无标题' }}</div>
      <div class="post-meta">
        <span class="post-time">{{ formattedTime }}</span>
        <span v-if="showStats" class="post-stats">
          <span class="stat-item">
            <span class="icon">👍</span>
            {{ post.likes_count || 0 }}
          </span>
          <span class="stat-item">
            <span class="icon">💬</span>
            {{ post.comments_count || 0 }}
          </span>
        </span>
      </div>
    </div>
    <!-- 图片缩略图 -->
    <div v-if="post.images && post.images.length > 0" class="post-thumbnail">
      <img 
        :src="post.images[0]" 
        :alt="post.subject"
        class="thumbnail-image"
      />
      <div v-if="post.images.length > 1" class="image-count">
        +{{ post.images.length - 1 }}
      </div>
    </div>
  </div>
  
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import AchievementImage from '@/components/common/AchievementImage.vue'

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  showStats: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

const formattedTime = computed(() => {
  const timestamp = props.post.createdAt || props.post.created_at
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const handleClick = () => {
  if (props.post.id) {
    router.push(`/community/${props.post.id}`)
  }
}

// 菜品关联：post.dish 或 post.dish_id
const dishId = computed(() => props.post.dish?.id || props.post.dish_id || null)
const dishImage = computed(() => {
  const img = props.post.dish?.image || props.post.dish_image
  if (!img) return ''
  if (/^(https?:|data:|blob:)/.test(img)) return img
  if (String(img).startsWith('/media/')) return img
  return '/media/' + String(img).replace(/^\/+/, '')
})
</script>

<style scoped>
.post-item {
  padding: 12px 14px;
  margin: 8px 0;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.post-item:last-child {
  border-bottom: none;
  transition: border-color .12s ease, box-shadow .12s ease, transform .12s ease;
}
.post-item:hover { border-color: var(--color-accent); box-shadow: 0 4px 14px rgba(0,0,0,0.06); transform: translateY(-1px) }

.post-content {
  flex: 1;
  min-width: 0;
}
.post-item:hover { border-color: var(--color-accent); box-shadow: 0 4px 14px rgba(0,0,0,0.06); transform: translateY(-1px) }

.post-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: #333;
  margin-bottom: 6px;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.35;
}

.post-thumbnail {
  position: relative;
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-count {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #666;
}

.post-time { color: #999 }

.post-stats { display: flex; gap: 10px }
.stat-item { display:flex; align-items:center; gap: 4px; padding: 2px 6px; border-radius: 999px; background: #f4f6f8; color: #445 }
.icon { font-size: 0.9rem }
</style>
