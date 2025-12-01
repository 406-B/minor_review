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
</script>

<style scoped>
.post-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.post-item:hover {
  background-color: rgba(43, 138, 239, 0.05);
}

.post-item:last-child {
  border-bottom: none;
}

.post-content {
  flex: 1;
  min-width: 0;
}

.post-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: #333;
  margin-bottom: 0.4rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #666;
}

.post-time {
  color: #999;
}

.post-stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.icon {
  font-size: 0.9rem;
}
</style>
