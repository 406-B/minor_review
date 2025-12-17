<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    
    <div class="received-comments-page">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <span>←</span>
            <span>返回</span>
          </button>
          <h2>我收到的评论</h2>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadComments">重试</el-button>
      </div>

      <div v-else-if="receivedComments.length === 0" class="empty">
        <el-empty description="暂无收到的评论">
          <el-button type="primary" @click="$router.push('/community/create')">发布帖子</el-button>
        </el-empty>
      </div>

      <div v-else class="comments-container">
        <div
          v-for="item in receivedComments"
          :key="item.id"
          class="comment-card"
          @click="goToPost(item.post_id)"
        >
          <div class="comment-header">
            <img
              :src="item.author_avatar || '/default-avatar.png'"
              class="comment-avatar"
              @error="handleAvatarError"
            />
            <div class="author-info">
              <div class="author-name">{{ item.author_name || '匿名用户' }}</div>
              <div class="comment-time">{{ formatTime(item.created_at) }}</div>
            </div>
          </div>
          <div class="comment-content">{{ item.content }}</div>
          <div class="comment-meta">
            <span class="post-link">来自您的帖子：{{ item.post_subject || '无标题' }}</span>
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
import { getMyPosts } from '@/api/community'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'

const router = useRouter()
const receivedComments = ref([])
const loading = ref(true)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10 // 每页显示较少帖子，因为需要展开评论

async function loadComments() {
  loading.value = true
  error.value = null
  try {
    // 获取我的帖子，然后提取所有评论
    const response = await getMyPosts(currentPage.value, pageSize)
    if (response.code === 200 && response.data) {
      const posts = response.data.posts || []
      
      // 收集所有帖子的评论
      const allComments = []
      for (const post of posts) {
        if (post.comments && post.comments.length > 0) {
          // 为每个评论添加帖子信息
          post.comments.forEach(comment => {
            allComments.push({
              ...comment,
              post_id: post.id,
              post_subject: post.subject,
              author_name: comment.author?.nickname || comment.author?.username,
              author_avatar: comment.author?.avatar
            })
          })
        }
      }
      
      // 按时间排序（最新的在前）
      allComments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      
      receivedComments.value = allComments
      
      if (response.data.pagination) {
        totalPages.value = response.data.pagination.total_pages || 1
      }
    } else {
      error.value = response.message || '加载失败'
    }
  } catch (err) {
    console.error('加载收到的评论失败:', err)
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

function handleAvatarError(e) {
  e.target.src = '/default-avatar.png'
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.received-comments-page {
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

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border);
}

.author-info {
  flex: 1;
}

.author-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 2px;
}

.comment-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.comment-content {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text);
  margin-bottom: 0.75rem;
  padding-left: 52px; /* 对齐头像 */
}

.comment-meta {
  padding-left: 52px;
  font-size: 13px;
}

.post-link {
  color: var(--brand-600);
  font-weight: 500;
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
  .received-comments-page {
    padding: 16px;
  }

  .header h2 {
    font-size: 20px;
  }

  .comment-content,
  .comment-meta {
    padding-left: 0;
  }
}
</style>
