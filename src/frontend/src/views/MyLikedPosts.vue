<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    
    <div class="liked-posts-page">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <span>←</span>
            <span>返回</span>
          </button>
          <h2>我点赞的帖子</h2>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadPosts">重试</el-button>
      </div>

      <div v-else-if="posts.length === 0" class="empty">
        <el-empty description="暂无点赞的帖子">
          <el-button type="primary" @click="$router.push('/community')">去社区看看</el-button>
        </el-empty>
      </div>

      <div v-else class="posts-container">
        <PostItem
          v-for="post in posts"
          :key="post.id"
          :post="post"
          @click="goToPostDetail(post.id)"
        />
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
import { getLikedPosts } from '@/api/community'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PostItem from '@/components/PostItem.vue'

const router = useRouter()
const posts = ref([])
const loading = ref(true)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 20

async function loadPosts() {
  loading.value = true
  error.value = null
  try {
    const response = await getLikedPosts(currentPage.value, pageSize)
    if (response.code === 200 && response.data) {
      posts.value = response.data.posts || []
      if (response.data.pagination) {
        totalPages.value = response.data.pagination.total_pages || 1
      }
    } else {
      error.value = response.message || '加载失败'
    }
  } catch (err) {
    console.error('加载点赞帖子失败:', err)
    error.value = '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  currentPage.value = page
  loadPosts()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPostDetail(postId) {
  router.push(`/community/${postId}`)
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.liked-posts-page {
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

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  .liked-posts-page {
    padding: 16px;
  }

  .header h2 {
    font-size: 20px;
  }
}
</style>
