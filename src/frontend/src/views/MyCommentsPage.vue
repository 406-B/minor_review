<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    
    <div class="my-comments-page">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <span>←</span>
            <span>返回</span>
          </button>
          <h2>我发布的评论</h2>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadComments">重试</el-button>
      </div>

      <div v-else-if="comments.length === 0" class="empty">
        <el-empty description="暂无发布的评论">
          <el-button type="primary" @click="$router.push('/community')">去社区看看</el-button>
        </el-empty>
      </div>

      <div v-else class="comments-container">
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="comment-card"
          @click="goToPost(comment.post_id)"
        >
          <div class="comment-content">{{ comment.content }}</div>
          <div class="comment-meta">
            <span class="post-link">来自帖子：{{ comment.post_subject || '无标题' }}</span>
            <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <el-button
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </el-button>
        <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
        <el-button
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </el-button>
      </div>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMyComments } from '@/api/community'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'

const router = useRouter()
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 20

async function loadComments() {
  loading.value = true
  error.value = null
  try {
    const response = await getMyComments(currentPage.value, pageSize)
    if (response.code === 200 && response.data) {
      comments.value = response.data.comments || []
      if (response.data.pagination) {
        totalPages.value = response.data.pagination.total_pages || 1
      }
    } else {
      error.value = response.message || '加载失败'
    }
  } catch (err) {
    console.error('加载我的评论失败:', err)
    error.value = '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  currentPage.value = page
  loadComments()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPost(postId) {
  router.push(`/community/${postId}`)
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.my-comments-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
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

.loading,
.error,
.empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
}

.error {
  color: #d32f2f;
}

.comments-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-card {
  padding: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.comment-card:hover {
  border-color: var(--brand-200);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.comment-content {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text);
  margin-bottom: 0.75rem;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.post-link {
  color: var(--brand-600);
  font-weight: 500;
}

.comment-time {
  color: var(--color-text-tertiary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
}

.page-info {
  font-size: 14px;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .my-comments-page {
    padding: 16px;
  }

  .header h2 {
    font-size: 20px;
  }

  .comment-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
