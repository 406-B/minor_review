<template>
  <div class="my-posts">
    <TopBar />
    
    <div class="container">
      <div class="header">
        <h1 class="page-title">我的帖子</h1>
        <button class="back-btn" @click="goBack">返回</button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="loadPosts" class="retry-btn">重试</button>
      </div>

      <div v-else-if="posts.length === 0" class="empty">
        <p>暂无发布的帖子</p>
        <button @click="goToCreate" class="create-btn">发布第一篇帖子</button>
      </div>

      <div v-else class="posts-container">
        <PostItem
          v-for="post in posts"
          :key="post.id"
          :post="post"
          :showStats="true"
        />

        <!-- 分页控件 -->
        <div v-if="pagination.total_pages > 1" class="pagination">
          <button 
            class="page-btn" 
            :disabled="pagination.page <= 1"
            @click="goToPage(pagination.page - 1)"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ pagination.page }} / {{ pagination.total_pages }} 页
            (共 {{ pagination.total }} 篇)
          </span>
          <button 
            class="page-btn"
            :disabled="pagination.page >= pagination.total_pages"
            @click="goToPage(pagination.page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import PostItem from '@/components/PostItem.vue'
import { getMyPosts } from '@/api/community'

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const error = ref('')
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0
})

const loadPosts = async (page = 1) => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await getMyPosts(page, pagination.value.page_size)
    
    if (response.code === 200 && response.data) {
      posts.value = response.data.posts || []
      pagination.value = response.data.pagination || pagination.value
    } else {
      error.value = '获取帖子列表失败'
    }
  } catch (err) {
    console.error('加载我的帖子失败:', err)
    error.value = err.message || '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    loadPosts(page)
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const goBack = () => {
  router.back()
}

const goToCreate = () => {
  router.push('/community/create')
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.my-posts {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.back-btn {
  padding: 0.5rem 1rem;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #666;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #f5f5f5;
  border-color: #999;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
}

.error {
  color: #c00;
}

.retry-btn,
.create-btn {
  margin-top: 1rem;
  padding: 0.6rem 1.5rem;
  background-color: #2b8aef;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background-color 0.2s;
}

.retry-btn:hover,
.create-btn:hover {
  background-color: #1a73d9;
}

.posts-container {
  background-color: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.page-btn {
  padding: 0.5rem 1rem;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #666;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #2b8aef;
  color: white;
  border-color: #2b8aef;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #666;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.4rem;
  }

  .pagination {
    flex-direction: column;
    gap: 0.75rem;
  }

  .page-info {
    order: -1;
  }
}
</style>
