<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <span>←</span>
          <span>返回</span>
        </button>
        <h2>我的帖子</h2>
      </div>
    </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadPosts">重试</el-button>
      </div>

      <div v-else-if="posts.length === 0" class="empty">
        <el-empty description="暂无发布的帖子">
          <el-button type="primary" @click="goToCreate">发布第一篇帖子</el-button>
        </el-empty>
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
          <el-button 
            :disabled="pagination.page <= 1"
            @click="goToPage(pagination.page - 1)"
          >上一页</el-button>
          <span class="page-info">
            第 {{ pagination.page }} / {{ pagination.total_pages }} 页
            (共 {{ pagination.total }} 篇)
          </span>
          <el-button 
            :disabled="pagination.page >= pagination.total_pages"
            @click="goToPage(pagination.page + 1)"
          >下一页</el-button>
        </div>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
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
/* PageContainer 已提供容器与背景，此处仅小范围调整 */

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
  color: #c00;
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

/* 分页按钮使用 Element Plus 默认样式 */

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
