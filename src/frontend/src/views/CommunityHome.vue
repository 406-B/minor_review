<template>
	<PageContainer>
		<template #header>
			<AppTopBar />
		</template>
			<div class="top-actions">
				<SectionTitle>点评社区</SectionTitle>
				<div class="actions">
					<button class="publish-btn" @click="goCreate">我要发帖</button>
				</div>
			</div>

			<div class="content-wrap">
				<div class="list-wrap">
					<div v-if="loading" class="loading">加载中...</div>
					<!-- 错误通过弹窗提示，不再在页面显示 -->
					<EmptyState v-else-if="posts.length === 0" text="暂无帖子" />
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
		</PageContainer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PageContainer from '@/components/ui/PageContainer.vue'
import SectionTitle from '@/components/ui/SectionTitle.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
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
			// 使用弹窗提示具体原因
			ElMessageBox.alert(
				error.value,
				'出错了',
				{ type: 'error' }
			)
			// 可选：清空列表，避免页面误解为空态
			posts.value = []
		}
	} catch (err) {
		console.error('加载帖子列表失败:', err)
		// 优先采用后端返回的 message，其次采用异常消息
		const detail = err?.response?.data?.message || err?.message || '加载失败，请检查网络连接'
		error.value = detail
		ElMessageBox.alert(detail, '出错了', { type: 'error' })
	} finally {
		loading.value = false
	}
}

function loadPage(page) {
	loadPosts(page)
}

function goCreate() {
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	router.push({ name: 'PostCreate' })
}

function goDetail(id) {
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	router.push({ name: 'PostDetail', params: { id } })
}

onMounted(() => loadPosts())
</script>

<style scoped>
.community-page { display:block; background: var(--color-bg); padding: 20px 0; min-height: 100vh }
.top-actions { display:flex; justify-content:space-between; align-items:center; padding:12px 20px; border-bottom:1px solid #eee; margin-bottom:16px }
.top-actions .title { font-size:18px; font-weight:600 }
.publish-btn { padding:8px 14px; background:var(--color-accent); color:#fff; border:none; border-radius:var(--radius-xs); cursor:pointer; transition: all 0.3s }
.publish-btn:hover { background:var(--brand-700) }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.list-wrap { width:720px; background:var(--color-surface); padding:16px; border-radius:var(--radius-sm); box-shadow:var(--shadow-sm); border:1px solid var(--color-border) }
.post-card { display:flex; justify-content:space-between; align-items:center; padding:14px; border:1px solid var(--color-border); margin-bottom:12px; border-radius:var(--radius-sm); background:var(--color-surface); transition: all 0.3s }
.post-card:hover { box-shadow: var(--shadow-md); border-color: var(--brand-200) }
.post-left { cursor:pointer; flex:1 }
.post-title { font-size: 16px; font-weight: 600; color: var(--color-text); margin: 0 0 8px 0; line-height: 1.4 }
.post-content-preview { font-size: 13px; color: var(--color-muted); margin-bottom: 8px; line-height: 1.5 }
.post-content { font-size: 14px; color: var(--color-text); margin-bottom: 8px; line-height: 1.6 }
.post-info { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--color-muted) }
.post-author { color: var(--color-accent) }
.post-stats { display: flex; gap: 12px }
.stat-item { display: inline-flex; align-items: center; gap: 4px }

.loading, .error, .empty { 
	text-align: center; 
	padding: 40px 20px; 
	color: var(--color-muted); 
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
	background: var(--color-accent); 
	color: #fff; 
	border: none; 
	border-radius: var(--radius-xs); 
	cursor: pointer;
	transition: all 0.3s;
}
.pagination button:hover:not(:disabled) { 
	background: var(--brand-700) 
}

.pagination button:disabled { 
	background: #ccc; 
	cursor: not-allowed 
}
.pagination span { 
	font-size: 14px; 
	color: var(--color-muted) 
}

/* Optional right column placeholder styling (kept minimal) */
.side-placeholder { width:260px }

@media (max-width: 900px) {
	.content-wrap { padding-left:12px }
	.list-wrap { width:100%; max-width:720px }
}
</style>
