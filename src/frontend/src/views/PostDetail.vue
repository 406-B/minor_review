<template>
	<div class="page">
			<div class="top-actions">
				<PageActions>
					<template #left>
						<button @click="goBack">返回</button>
					</template>
					<template #right>
						<button v-if="canDelete" @click="handleDelete" class="delete-btn">删除</button>
					</template>
				</PageActions>

				<div class="title">帖子详情</div>
			</div>

		<div class="content-wrap">
			<div class="card">
				<div v-if="loading" class="loading">加载中...</div>
				<div v-else-if="error" class="error">{{ error }}</div>
				<div v-else-if="post" class="content">
					<div class="post-header">
						<div class="author-info">
							<img 
								:src="post.author?.avatar || '/default-avatar.png'" 
								class="avatar"
								@error="handleAvatarError"
							/>
							<div class="author-details">
								<div class="author-name">{{ post.author?.nickname || post.author?.username || '匿名用户' }}</div>
								<div class="post-time">{{ formatTime(post.created_at) }}</div>
							</div>
						</div>
						<div class="post-actions">
							<button 
								@click="handleLike" 
								:class="['like-btn', { liked: post.is_liked }]"
								:disabled="liking"
							>
								{{ post.is_liked ? '❤️' : '🤍' }} {{ post.likes_count || 0 }}
							</button>
						</div>
					</div>
					
					<h2 class="post-subject">{{ post.subject || '无标题' }}</h2>
					<div class="body">{{ post.content }}</div>
					
					<!-- 评论区 -->
					<div class="comments-section">
						<div class="comments-header">
							<h3>评论 ({{ post.comments_count || 0 }})</h3>
						</div>
						
						<!-- 发表评论 -->
						<div class="comment-form">
							<textarea 
								v-model="newComment" 
								placeholder="写下你的评论..."
								class="comment-input"
								:disabled="commenting"
							></textarea>
							<button 
								@click="handleComment" 
								class="comment-btn"
								:disabled="commenting || !newComment.trim()"
							>
								{{ commenting ? '发布中...' : '发表评论' }}
							</button>
						</div>
						
						<!-- 评论列表 -->
						<div v-if="loadingComments" class="loading">加载评论中...</div>
						<div v-else-if="comments.length === 0" class="no-comments">暂无评论</div>
						<div v-else class="comments-list">
							<div v-for="comment in comments" :key="comment.id" class="comment-item">
								<div class="comment-header">
									<img 
										:src="comment.author?.avatar || '/default-avatar.png'" 
										class="comment-avatar"
										@error="handleAvatarError"
									/>
									<div class="comment-author-info">
										<div class="comment-author-name">{{ comment.author?.nickname || comment.author?.username || '匿名用户' }}</div>
										<div class="comment-time">{{ formatTime(comment.created_at) }}</div>
									</div>
									<div class="comment-actions">
										<button 
											@click="handleCommentLike(comment)" 
											:class="['comment-like-btn', { liked: comment.is_liked }]"
										>
											{{ comment.is_liked ? '❤️' : '🤍' }} {{ comment.likes_count || 0 }}
										</button>
										<button 
											v-if="canDeleteComment(comment)" 
											@click="handleDeleteComment(comment.id)"
											class="comment-delete-btn"
										>
											删除
										</button>
									</div>
								</div>
								<div class="comment-content">{{ comment.content }}</div>
							</div>
						</div>
					</div>
				</div>
				<div v-else>
					未找到该帖子
				</div>
			</div>
			<div class="side-placeholder"></div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
	getPostDetail, 
	deletePost, 
	togglePostLike,
	createComment,
	deleteComment,
	toggleCommentLike
} from '@/api/community'

const router = useRouter()
const route = useRoute()
const post = ref(null)
const comments = ref([])
const loading = ref(false)
const loadingComments = ref(false)
const error = ref(null)
const liking = ref(false)
const commenting = ref(false)
const newComment = ref('')

import PageActions from '../components/PageActions.vue'

// 计算当前用户ID（从 localStorage 或其他地方获取）
const currentUserId = computed(() => {
	// 这里需要根据实际情况获取当前用户ID
	// 可以从 localStorage、Vuex 或其他状态管理中获取
	const userInfo = localStorage.getItem('userInfo')
	if (userInfo) {
		try {
			const user = JSON.parse(userInfo)
			return user.id
		} catch (e) {
			return null
		}
	}
	return null
})

// 是否可以删除帖子
const canDelete = computed(() => {
	return post.value && currentUserId.value && post.value.author?.id === currentUserId.value
})

// 是否可以删除评论
const canDeleteComment = (comment) => {
	return currentUserId.value && comment.author?.id === currentUserId.value
}

function goBack() { 
	router.push({ name: 'CommunityHome' }) 
}

async function loadPost() {
	const id = route.params.id
	loading.value = true
	error.value = null
	
	try {
		const response = await getPostDetail(id)
		
		if (response.code === 200 && response.data) {
			post.value = response.data
			// 如果响应中包含评论，直接使用
			if (response.data.comments) {
				comments.value = response.data.comments
			}
		} else {
			error.value = response.message || '获取帖子详情失败'
		}
	} catch (err) {
		console.error('加载帖子详情失败:', err)
		error.value = '加载失败，请检查网络连接'
	} finally {
		loading.value = false
	}
}

async function handleDelete() {
	if (!confirm('确定要删除这条帖子吗？')) return
	
	try {
		const response = await deletePost(post.value.id)
		
		if (response.code === 200) {
			alert('删除成功')
			router.push({ name: 'CommunityHome' })
		} else {
			alert(response.message || '删除失败')
		}
	} catch (err) {
		console.error('删除帖子失败:', err)
		alert('删除失败，请重试')
	}
}

async function handleLike() {
	if (liking.value) return
	liking.value = true
	
	try {
		const response = await togglePostLike(post.value.id)
		
		if (response.code === 200 && response.data) {
			post.value.is_liked = response.data.is_liked
			// 更新点赞数
			if (response.data.is_liked) {
				post.value.likes_count = (post.value.likes_count || 0) + 1
			} else {
				post.value.likes_count = Math.max(0, (post.value.likes_count || 0) - 1)
			}
		}
	} catch (err) {
		console.error('点赞操作失败:', err)
		alert('操作失败，请重试')
	} finally {
		liking.value = false
	}
}

async function handleComment() {
	if (!newComment.value.trim() || commenting.value) return
	commenting.value = true
	
	try {
		const response = await createComment(post.value.id, newComment.value)
		
		if (response.code === 200 && response.data) {
			// 将新评论添加到列表顶部
			comments.value.unshift(response.data)
			// 更新评论数
			post.value.comments_count = (post.value.comments_count || 0) + 1
			// 清空输入框
			newComment.value = ''
		} else {
			alert(response.message || '评论失败')
		}
	} catch (err) {
		console.error('发表评论失败:', err)
		alert('评论失败，请重试')
	} finally {
		commenting.value = false
	}
}

async function handleCommentLike(comment) {
	try {
		const response = await toggleCommentLike(comment.id)
		
		if (response.code === 200 && response.data) {
			comment.is_liked = response.data.is_liked
			// 更新点赞数
			if (response.data.is_liked) {
				comment.likes_count = (comment.likes_count || 0) + 1
			} else {
				comment.likes_count = Math.max(0, (comment.likes_count || 0) - 1)
			}
		}
	} catch (err) {
		console.error('评论点赞操作失败:', err)
		alert('操作失败，请重试')
	}
}

async function handleDeleteComment(commentId) {
	if (!confirm('确定要删除这条评论吗？')) return
	
	try {
		const response = await deleteComment(commentId)
		
		if (response.code === 200) {
			// 从列表中移除评论
			comments.value = comments.value.filter(c => c.id !== commentId)
			// 更新评论数
			post.value.comments_count = Math.max(0, (post.value.comments_count || 0) - 1)
		} else {
			alert(response.message || '删除失败')
		}
	} catch (err) {
		console.error('删除评论失败:', err)
		alert('删除失败，请重试')
	}
}

function formatTime(timestamp) {
	if (!timestamp) return ''
	const date = new Date(timestamp)
	const now = new Date()
	const diff = now - date
	
	// 小于1分钟
	if (diff < 60000) return '刚刚'
	// 小于1小时
	if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
	// 小于24小时
	if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
	// 小于7天
	if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
	
	// 超过7天，显示具体日期
	return date.toLocaleDateString('zh-CN')
}

function handleAvatarError(e) {
	e.target.src = '/default-avatar.png'
}

onMounted(loadPost)
</script>

<style scoped>
.page { background: #f5f7fb; padding: 20px 0; min-height: 100vh }
.top-actions { display:block; padding:12px 0; border-bottom:1px solid #eee; margin-bottom:12px }
.top-actions .title { font-size:18px; font-weight:600; max-width:1200px; margin:8px auto 0; padding:0 20px; text-align:left }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.card { width:720px; background:#fff; padding:18px; border-radius:8px; box-shadow:0 1px 4px rgba(16,24,40,0.06) }
.side-placeholder { width:260px }
.toolbar { display:flex; gap:8px }
.toolbar button { padding:8px 12px; border-radius:4px; border:none; background:#f5f5f5; cursor:pointer }
.delete-btn { padding:8px 12px; border-radius:4px; border:none; background:#f56c6c; color:#fff; cursor:pointer; transition: all 0.3s }
.delete-btn:hover { background:#f45454 }

.loading, .error { text-align: center; padding: 40px 20px; color: #666; font-size: 14px }
.error { color: #f56c6c }

.post-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0 }
.author-info { display: flex; align-items: center; gap: 12px }
.avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover }
.author-details { display: flex; flex-direction: column }
.author-name { font-weight: 600; font-size: 14px; color: #333 }
.post-time { font-size: 12px; color: #999; margin-top: 4px }
.post-actions { display: flex; gap: 8px }
.like-btn { 
	padding: 6px 14px; 
	border: 1px solid #dcdfe6; 
	background: #fff; 
	border-radius: 4px; 
	cursor: pointer; 
	font-size: 14px;
	transition: all 0.3s;
}
.like-btn:hover:not(:disabled) { 
	border-color: #409eff; 
	color: #409eff 
}
.like-btn.liked { 
	border-color: #f56c6c; 
	color: #f56c6c; 
	background: #fef0f0 
}
.like-btn:disabled { 
	cursor: not-allowed; 
	opacity: 0.6 
}

.post-subject {
	font-size: 24px;
	font-weight: 700;
	color: #1a1a1a;
	margin: 20px 0 16px 0;
	line-height: 1.4;
}

.body { 
	margin-top: 12px; 
	white-space: pre-wrap; 
	line-height: 1.8; 
	font-size: 15px; 
	color: #333;
	margin-bottom: 32px;
}

/* 评论区样式 */
.comments-section { 
	margin-top: 32px; 
	padding-top: 24px; 
	border-top: 2px solid #f0f0f0 
}
.comments-header h3 { 
	font-size: 16px; 
	font-weight: 600; 
	margin-bottom: 16px; 
	color: #333 
}

.comment-form { 
	margin-bottom: 24px; 
	background: #f9fafb; 
	padding: 16px; 
	border-radius: 8px 
}
.comment-input { 
	width: 100%; 
	min-height: 80px; 
	padding: 12px; 
	border: 1px solid #dcdfe6; 
	border-radius: 4px; 
	font-size: 14px; 
	resize: vertical;
	margin-bottom: 12px;
	font-family: inherit;
}
.comment-input:focus { 
	outline: none; 
	border-color: #409eff 
}
.comment-btn { 
	padding: 8px 20px; 
	background: #409eff; 
	color: #fff; 
	border: none; 
	border-radius: 4px; 
	cursor: pointer; 
	font-size: 14px;
	transition: all 0.3s;
}
.comment-btn:hover:not(:disabled) { 
	background: #66b1ff 
}
.comment-btn:disabled { 
	background: #ccc; 
	cursor: not-allowed 
}

.no-comments { 
	text-align: center; 
	padding: 40px 20px; 
	color: #999; 
	font-size: 14px 
}

.comments-list { display: flex; flex-direction: column; gap: 16px }
.comment-item { 
	padding: 16px; 
	background: #f9fafb; 
	border-radius: 8px;
	transition: all 0.3s;
}
.comment-item:hover { 
	background: #f5f7fa 
}
.comment-header { 
	display: flex; 
	align-items: center; 
	margin-bottom: 12px 
}
.comment-avatar { 
	width: 36px; 
	height: 36px; 
	border-radius: 50%; 
	object-fit: cover; 
	margin-right: 12px 
}
.comment-author-info { 
	flex: 1 
}
.comment-author-name { 
	font-weight: 600; 
	font-size: 13px; 
	color: #333 
}
.comment-time { 
	font-size: 11px; 
	color: #999; 
	margin-top: 2px 
}
.comment-actions { 
	display: flex; 
	gap: 8px 
}
.comment-like-btn { 
	padding: 4px 10px; 
	border: 1px solid #dcdfe6; 
	background: #fff; 
	border-radius: 4px; 
	cursor: pointer; 
	font-size: 12px;
	transition: all 0.3s;
}
.comment-like-btn:hover { 
	border-color: #409eff; 
	color: #409eff 
}
.comment-like-btn.liked { 
	border-color: #f56c6c; 
	color: #f56c6c; 
	background: #fef0f0 
}
.comment-delete-btn { 
	padding: 4px 10px; 
	border: 1px solid #dcdfe6; 
	background: #fff; 
	border-radius: 4px; 
	cursor: pointer; 
	font-size: 12px; 
	color: #f56c6c;
	transition: all 0.3s;
}
.comment-delete-btn:hover { 
	background: #fef0f0; 
	border-color: #f56c6c 
}
.comment-content { 
	white-space: pre-wrap; 
	line-height: 1.6; 
	font-size: 14px; 
	color: #555 
}

@media (max-width:900px) {
	.card { width:100%; padding:12px }
	.content-wrap { padding-left:12px }
	.side-placeholder { display:none }
}
</style>
