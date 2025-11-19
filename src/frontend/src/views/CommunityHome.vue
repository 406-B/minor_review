<template>
	<TopBar />
	<div class="community-page">
			<div class="top-actions">
				<div class="title">点评社区</div>
				<div class="actions">
					<button class="publish-btn" @click="goCreate">我要发帖</button>
				</div>
			</div>

			<div class="content-wrap">
				<div class="list-wrap">
					<div v-if="loading" class="loading">加载中...</div>
					<div v-else-if="error" class="error">{{ error }}</div>
					<div v-else-if="posts.length === 0" class="empty">暂无帖子</div>
					<div v-else v-for="post in posts" :key="post.id" class="post-card">
						<div class="post-left" @click="goDetail(post.id)">
							<h3 class="post-title">{{ post.subject || '无标题' }}</h3>
							<div class="post-content-preview" v-if="post.content_preview">
								{{ post.content_preview }}
							</div>
							<div class="post-info">
								<span class="post-author">{{ post.author?.nickname || post.author?.username || '匿名用户' }}</span>
								<span class="post-stats">
									<span class="stat-item">❤️ {{ post.likes_count || 0 }}</span>
									<span class="stat-item">💬 {{ post.comments_count || 0 }}</span>
								</span>
							</div>
						</div>
					</div>
					
					<!-- 分页控制 -->
					<div v-if="pagination.total_pages > 1" class="pagination">
						<button 
							:disabled="pagination.page <= 1" 
							@click="loadPage(pagination.page - 1)"
						>上一页</button>
						<span>第 {{ pagination.page }} / {{ pagination.total_pages }} 页</span>
						<button 
							:disabled="pagination.page >= pagination.total_pages" 
							@click="loadPage(pagination.page + 1)"
						>下一页</button>
					</div>
				</div>
			</div>
		</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/components/TopBar.vue'
import { getPostList } from '@/api/community'

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const error = ref(null)
const pagination = ref({
	page: 1,
	page_size: 20,
	total: 0,
	total_pages: 0
})

async function loadPosts(page = 1) {
	loading.value = true
	error.value = null
	try {
		const response = await getPostList(page, pagination.value.page_size)
		
		if (response.code === 200 && response.data) {
			posts.value = response.data.posts || []
			pagination.value = {
				...pagination.value,
				...response.data.pagination
			}
		} else {
			error.value = response.message || '获取帖子列表失败'
		}
	} catch (err) {
		console.error('加载帖子列表失败:', err)
		error.value = '加载失败，请检查网络连接'
		// 开发环境下显示详细错误
		if (import.meta.env.DEV) {
			console.error('详细错误:', err)
		}
	} finally {
		loading.value = false
	}
}

function loadPage(page) {
	loadPosts(page)
}

function goCreate() {
	router.push({ name: 'PostCreate' })
}

function goDetail(id) {
	router.push({ name: 'PostDetail', params: { id } })
}

onMounted(() => loadPosts())
</script>

<style scoped>
.community-page { display:block; background: #f5f7fb; padding: 20px 0; min-height: 100vh }
.top-actions { display:flex; justify-content:space-between; align-items:center; padding:12px 20px; border-bottom:1px solid #eee; margin-bottom:16px }
.top-actions .title { font-size:18px; font-weight:600 }
.top-actions .actions { }
.publish-btn { padding:8px 14px; background:#67c23a; color:#fff; border:none; border-radius:6px; cursor:pointer; transition: all 0.3s }
.publish-btn:hover { background:#5daf34 }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.list-wrap { width:720px; background:#fff; padding:16px; border-radius:8px; box-shadow:0 1px 4px rgba(16,24,40,0.06) }
.post-card { display:flex; justify-content:space-between; align-items:center; padding:14px; border:1px solid #f0f0f0; margin-bottom:12px; border-radius:8px; background:#fff; transition: all 0.3s }
.post-card:hover { box-shadow: 0 2px 8px rgba(16,24,40,0.1); border-color: #409eff }
.post-left { cursor:pointer; flex:1 }
.post-title { font-size: 16px; font-weight: 600; color: #333; margin: 0 0 8px 0; line-height: 1.4 }
.post-content-preview { font-size: 13px; color: #666; margin-bottom: 8px; line-height: 1.5 }
.post-content { font-size: 14px; color: #333; margin-bottom: 8px; line-height: 1.6 }
.post-info { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #666 }
.post-author { color: #409eff }
.post-stats { display: flex; gap: 12px }
.stat-item { display: inline-flex; align-items: center; gap: 4px }

.loading, .error, .empty { 
	text-align: center; 
	padding: 40px 20px; 
	color: #666; 
	font-size: 14px 
}
.error { color: #f56c6c }

.pagination { 
	display: flex; 
	justify-content: center; 
	align-items: center; 
	gap: 16px; 
	padding: 20px 0; 
	margin-top: 20px 
}
.pagination button { 
	padding: 6px 12px; 
	background: #409eff; 
	color: #fff; 
	border: none; 
	border-radius: 4px; 
	cursor: pointer;
	transition: all 0.3s;
}
.pagination button:hover:not(:disabled) { 
	background: #66b1ff 
}
.pagination button:disabled { 
	background: #ccc; 
	cursor: not-allowed 
}
.pagination span { 
	font-size: 14px; 
	color: #666 
}

/* Optional right column placeholder styling (kept minimal) */
.side-placeholder { width:260px }

@media (max-width: 900px) {
	.content-wrap { padding-left:12px }
	.list-wrap { width:100%; max-width:720px }
}
</style>
