<template>
	<PageContainer>
		<template #header>
			<AppTopBar />
		</template>
			<div class="top-actions">
				<PageActions>
					<template #left>
						<button class="toolbar-btn" @click="goBack">返回</button>
					</template>
					<template #right>
						<button v-if="canDelete" @click="handleDelete" class="delete-btn">删除</button>
					</template>
				</PageActions>

				<SectionTitle>帖子详情</SectionTitle>
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
					
					<!-- 帖子图片 -->
					<div v-if="post.images && post.images.length > 0" class="post-images">
						<img 
							v-for="(image, index) in post.images" 
							:key="index"
							:src="image"
							class="post-image"
							@click="previewImage(image)"
							:alt="`图片${index + 1}`"
						/>
					</div>
					
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
							<ImageUploader 
								v-model="commentImages" 
								:max-count="9"
								class="comment-image-uploader"
							/>
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
											@click="toggleReplyForm(comment.id)"
											class="comment-reply-btn"
										>
											回复
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
								
								<!-- 评论图片 -->
								<div v-if="comment.images && comment.images.length > 0" class="comment-images">
									<img 
										v-for="(image, index) in comment.images" 
										:key="index"
										:src="image"
										class="comment-image"
										@click="previewImage(image)"
									/>
								</div>
								
								<!-- 回复表单 -->
								<div v-if="replyingTo === comment.id" class="reply-form">
									<textarea 
										v-model="replyContent" 
										:placeholder="`回复 ${comment.author?.nickname || comment.author?.username || '匿名用户'}...`"
										class="reply-input"
										:disabled="replying"
									></textarea>
									<ImageUploader 
										v-model="replyImages" 
										:max-count="9"
										class="reply-image-uploader"
									/>
									<div class="reply-actions">
										<button 
											@click="handleReply(comment.id)" 
											class="reply-submit-btn"
											:disabled="replying || !replyContent.trim()"
										>
											{{ replying ? '发送中...' : '发送' }}
										</button>
										<button 
											@click="cancelReply" 
											class="reply-cancel-btn"
											:disabled="replying"
										>
											取消
										</button>
									</div>
								</div>
								
								<!-- 回复列表 -->
								<div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
									<div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
										<div class="reply-header">
											<img 
												:src="reply.author?.avatar || '/default-avatar.png'" 
												class="reply-avatar"
												@error="handleAvatarError"
											/>
											<div class="reply-author-info">
												<div class="reply-author-name">{{ reply.author?.nickname || reply.author?.username || '匿名用户' }}</div>
												<div class="reply-time">{{ formatTime(reply.created_at) }}</div>
											</div>
											<div class="reply-actions">
												<button 
													@click="handleReplyLike(reply, comment)" 
													:class="['reply-like-btn', { liked: reply.is_liked }]"
												>
													{{ reply.is_liked ? '❤️' : '🤍' }} {{ reply.likes_count || 0 }}
												</button>
												<button 
													@click="replyToReply(comment.id, reply)"
													class="reply-reply-btn"
												>
													回复
												</button>
												<button 
													v-if="canDeleteComment(reply)" 
													@click="handleDeleteReply(reply.id, comment)"
													class="reply-delete-btn"
												>
													删除
												</button>
											</div>
										</div>
										<div class="reply-content">{{ reply.content }}</div>
										
										<!-- 回复图片 -->
										<div v-if="reply.images && reply.images.length > 0" class="reply-images">
											<img 
												v-for="(image, index) in reply.images" 
												:key="index"
												:src="image"
												class="reply-image"
												@click="previewImage(image)"
											/>
										</div>
									</div>
								</div>
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
	</PageContainer>
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
const commentImages = ref([]) // 评论图片
const replyingTo = ref(null)
const replyContent = ref('')
const replyImages = ref([]) // 回复图片
const replying = ref(false)
const replyTargetUser = ref(null) // 记录要@的用户

import PageActions from '../components/PageActions.vue'
import PageContainer from '@/components/ui/PageContainer.vue'
import SectionTitle from '@/components/ui/SectionTitle.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import ImageUploader from '@/components/ImageUploader.vue'

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
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	if (!confirm('确定要删除这条帖子吗？')) return
	
	try {
		const response = await deletePost(post.value.id)
		
		if (response.code === 200) {
			window.$message?.success?.('删除成功')
			router.push({ name: 'CommunityHome' })
		} else {
			window.$message?.error?.(response.message || '删除失败')
		}
	} catch (err) {
		console.error('删除帖子失败:', err)
		if (err?.response?.status === 401) {
			window.$message?.warning?.('您需要先登录')
			return router.push('/login')
		}
		window.$message?.error?.('删除失败，请重试')
	}
}

async function handleLike() {
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
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
		if (err?.response?.status === 401) {
			window.$message?.warning?.('您需要先登录')
			router.push('/login')
		} else {
			window.$message?.error?.('操作失败，请重试')
		}
	} finally {
		liking.value = false
	}
}

async function handleComment() {
	if (!newComment.value.trim() || commenting.value) return
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	commenting.value = true
	
	try {
		const response = await createComment(post.value.id, newComment.value, commentImages.value)
		
		if (response.code === 200 && response.data) {
			// 将新评论添加到列表顶部
			comments.value.unshift(response.data)
			// 更新评论数
			post.value.comments_count = (post.value.comments_count || 0) + 1
			// 清空输入框和图片
			newComment.value = ''
			commentImages.value = []
			window.$message?.success?.('评论成功')
		} else {
			window.$message?.error?.(response.message || '评论失败')
		}
	} catch (err) {
		console.error('发表评论失败:', err)
		if (err?.response?.status === 401) {
			window.$message?.warning?.('您需要先登录')
			router.push('/login')
		} else {
			window.$message?.error?.('评论失败，请重试')
		}
	} finally {
		commenting.value = false
	}
}

async function handleCommentLike(comment) {
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
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
		if (err?.response?.status === 401) {
			window.$message?.warning?.('您需要先登录')
			router.push('/login')
		} else {
			window.$message?.error?.('操作失败，请重试')
		}
	}
}

async function handleDeleteComment(commentId) {
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	if (!confirm('确定要删除这条评论吗？')) return
	
	try {
		const response = await deleteComment(commentId)
		
		if (response.code === 200) {
			// 从列表中移除评论
			comments.value = comments.value.filter(c => c.id !== commentId)
			// 更新评论数
			post.value.comments_count = Math.max(0, (post.value.comments_count || 0) - 1)
		} else {
			window.$message?.error?.(response.message || '删除失败')
		}
	} catch (err) {
		console.error('删除评论失败:', err)
		if (err?.response?.status === 401) {
			window.$message?.warning?.('您需要先登录')
			router.push('/login')
		} else {
			window.$message?.error?.('删除失败，请重试')
		}
	}
}

// 切换回复表单
function toggleReplyForm(commentId) {
	if (replyingTo.value === commentId) {
		replyingTo.value = null
		replyContent.value = ''
		replyImages.value = []
		replyTargetUser.value = null
	} else {
		replyingTo.value = commentId
		replyContent.value = ''
		replyImages.value = []
		replyTargetUser.value = null
	}
}

// 回复其他回复（实际是回复顶级评论，但@提及被回复的用户）
function replyToReply(topCommentId, replyData) {
	replyingTo.value = topCommentId
	replyTargetUser.value = replyData.author
	// 自动在输入框中添加@用户名
	const mentionText = `@${replyData.author?.nickname || replyData.author?.username || '用户'} `
	replyContent.value = mentionText
}

// 取消回复
function cancelReply() {
	replyingTo.value = null
	replyContent.value = ''
	replyTargetUser.value = null
}

// 处理回复
async function handleReply(parentCommentId) {
	if (!replyContent.value.trim() || replying.value) return
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	replying.value = true
	
	try {
		const response = await createComment(post.value.id, replyContent.value, replyImages.value, parentCommentId)
		
		if (response.code === 200 && response.data) {
			// 找到父评论并添加回复
			const parentComment = comments.value.find(c => c.id === parentCommentId)
			if (parentComment) {
				if (!parentComment.replies) {
					parentComment.replies = []
				}
				parentComment.replies.push(response.data)
			}
			// 更新评论总数
			post.value.comments_count = (post.value.comments_count || 0) + 1
			// 清空输入、图片并关闭表单
			replyContent.value = ''
			replyImages.value = []
			replyingTo.value = null
			window.$message?.success?.('回复成功')
		} else {
			window.$message?.error?.(response.message || '回复失败')
		}
	} catch (err) {
		console.error('回复评论失败:', err)
		if (err?.response?.status === 401) {
			window.$message?.warning?.('您需要先登录')
			router.push('/login')
		} else {
			window.$message?.error?.('回复失败，请重试')
		}
	} finally {
		replying.value = false
	}
}

// 处理回复点赞
async function handleReplyLike(reply, parentComment) {
	try {
		const response = await toggleCommentLike(reply.id)
		
		if (response.code === 200 && response.data) {
			reply.is_liked = response.data.is_liked
			// 更新点赞数
			if (response.data.is_liked) {
				reply.likes_count = (reply.likes_count || 0) + 1
			} else {
				reply.likes_count = Math.max(0, (reply.likes_count || 0) - 1)
			}
		}
	} catch (err) {
		console.error('回复点赞操作失败:', err)
		alert('操作失败，请重试')
	}
}

// 删除回复
async function handleDeleteReply(replyId, parentComment) {
	if (!confirm('确定要删除这条回复吗？')) return
	
	try {
		const response = await deleteComment(replyId)
		
		if (response.code === 200) {
			// 从父评论的回复列表中移除
			if (parentComment.replies) {
				parentComment.replies = parentComment.replies.filter(r => r.id !== replyId)
			}
			// 更新评论总数
			post.value.comments_count = Math.max(0, (post.value.comments_count || 0) - 1)
		} else {
			alert(response.message || '删除失败')
		}
	} catch (err) {
		console.error('删除回复失败:', err)
		alert('删除失败，请重试')
	}
}

// 预览图片
function previewImage(imageUrl) {
	// 简单实现：在新窗口打开图片
	window.open(imageUrl, '_blank')
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
.page { background: var(--color-bg); padding: 20px 0; min-height: 100vh }
.top-actions { display:block; padding:12px 0; border-bottom:1px solid #eee; margin-bottom:12px }
.top-actions .title { font-size:18px; font-weight:600; max-width:1200px; margin:8px auto 0; padding:0 20px; text-align:left }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.card { width:720px; background:var(--color-surface); padding:18px; border-radius:var(--radius-sm); box-shadow:var(--shadow-sm); border:1px solid var(--color-border) }
.side-placeholder { width:260px }
.toolbar { display:flex; gap:8px }
.toolbar-btn { padding:8px 12px; border-radius:var(--radius-xs); border:1px solid var(--color-border); background:var(--color-surface); cursor:pointer }
.delete-btn { padding:8px 12px; border-radius:var(--radius-xs); border:none; background:#f56c6c; color:#fff; cursor:pointer; transition: all 0.3s }
.delete-btn:hover { background:#f45454 }

.loading, .error { text-align: center; padding: 40px 20px; color: var(--color-muted); font-size: 14px }
.error { color: #f56c6c }

.post-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0 }
.author-info { display: flex; align-items: center; gap: 12px }
.avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover }
.author-details { display: flex; flex-direction: column }
.author-name { font-weight: 600; font-size: 14px; color: var(--color-text) }
.post-time { font-size: 12px; color: var(--color-muted); margin-top: 4px }
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
	border-color: var(--color-accent); 
	color: var(--color-accent) 
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
	color: var(--color-text);
	margin: 20px 0 16px 0;
	line-height: 1.4;
}

.body { 
	margin-top: 12px; 
	white-space: pre-wrap; 
	line-height: 1.8; 
	font-size: 15px; 
	color: var(--color-text);
	margin-bottom: 32px;
}

/* 帖子图片样式 */
.post-images {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
	gap: 12px;
	margin: 20px 0;
}

.post-image {
	width: 100%;
	height: 200px;
	object-fit: cover;
	border-radius: 8px;
	cursor: pointer;
	transition: all 0.3s;
}

.post-image:hover {
	transform: scale(1.02);
	box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 评论区样式 */
.comments-section { 
	margin-top: 32px; 
	padding-top: 24px; 
	border-top: 2px solid #f0f0f0 
}
.comments-header h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--color-text) }

.comment-form { margin-bottom: 24px; background: var(--color-surface); padding: 16px; border-radius: var(--radius-sm); border:1px solid var(--color-border) }
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
.comment-input:focus { outline: none; border-color: var(--color-accent) }
.comment-btn { padding: 8px 20px; background: var(--color-accent); color: #fff; border: none; border-radius: var(--radius-xs); cursor: pointer; font-size: 14px; transition: all 0.3s; }
.comment-btn:hover:not(:disabled) { background: var(--brand-700) }
.comment-btn:disabled { 
	background: #ccc; 
	cursor: not-allowed 
}

.no-comments { text-align: center; padding: 40px 20px; color: var(--color-muted); font-size: 14px }

.comments-list { display: flex; flex-direction: column; gap: 16px }
.comment-item { padding: 16px; background: var(--color-surface); border:1px solid var(--color-border); border-radius: var(--radius-sm); transition: all 0.3s; }
.comment-item:hover { box-shadow: var(--shadow-sm) }
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
.comment-author-name { font-weight: 600; font-size: 13px; color: var(--color-text) }
.comment-time { font-size: 11px; color: var(--color-muted); margin-top: 2px }
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
.comment-like-btn:hover { border-color: var(--color-accent); color: var(--color-accent) }
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
.comment-delete-btn:hover { background: #fef0f0; border-color: #f56c6c }
.comment-content { 
	white-space: pre-wrap; 
	line-height: 1.6; 
	font-size: 14px; 
	color: #555 
}

/* 评论图片样式 */
.comment-images {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	margin-top: 12px;
}
.comment-image {
	width: 100px;
	height: 100px;
	object-fit: cover;
	border-radius: 4px;
	cursor: pointer;
	transition: all 0.3s;
}
.comment-image:hover {
	transform: scale(1.05);
	box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* 回复按钮样式 */
.comment-reply-btn {
	padding: 4px 10px;
	border: 1px solid #dcdfe6;
	background: #fff;
	border-radius: 4px;
	cursor: pointer;
	font-size: 12px;
	color: #409eff;
	transition: all 0.3s;
}
.comment-reply-btn:hover {
	background: #ecf5ff;
	border-color: #409eff;
}

/* 回复表单样式 */
.reply-form {
	margin-top: 12px;
	padding: 12px;
	background: #f0f2f5;
	border-radius: 6px;
}
.reply-input {
	width: 100%;
	min-height: 60px;
	padding: 10px;
	border: 1px solid #dcdfe6;
	border-radius: 4px;
	font-size: 13px;
	resize: vertical;
	margin-bottom: 8px;
	font-family: inherit;
}
.reply-input:focus {
	outline: none;
	border-color: #409eff;
}
.reply-actions {
	display: flex;
	gap: 8px;
	justify-content: flex-end;
}
.reply-submit-btn {
	padding: 6px 16px;
	background: #409eff;
	color: #fff;
	border: none;
	border-radius: 4px;
	cursor: pointer;
	font-size: 13px;
	transition: all 0.3s;
}
.reply-submit-btn:hover:not(:disabled) {
	background: #66b1ff;
}
.reply-submit-btn:disabled {
	background: #ccc;
	cursor: not-allowed;
}
.reply-cancel-btn {
	padding: 6px 16px;
	background: #fff;
	color: #606266;
	border: 1px solid #dcdfe6;
	border-radius: 4px;
	cursor: pointer;
	font-size: 13px;
	transition: all 0.3s;
}
.reply-cancel-btn:hover:not(:disabled) {
	border-color: #409eff;
	color: #409eff;
}
.reply-cancel-btn:disabled {
	cursor: not-allowed;
	opacity: 0.6;
}

/* 回复列表样式 */
.replies-list {
	margin-top: 16px;
	padding-left: 24px;
	border-left: 2px solid #e4e7ed;
}
.reply-item {
	padding: 12px;
	margin-bottom: 12px;
	background: #fff;
	border-radius: 6px;
	transition: all 0.3s;
}
.reply-item:hover {
	background: #fafbfc;
}
.reply-item:last-child {
	margin-bottom: 0;
}
.reply-header {
	display: flex;
	align-items: center;
	margin-bottom: 10px;
}
.reply-avatar {
	width: 30px;
	height: 30px;
	border-radius: 50%;
	object-fit: cover;
	margin-right: 10px;
}
.reply-author-info {
	flex: 1;
}
.reply-author-name {
	font-weight: 600;
	font-size: 12px;
	color: #333;
}
.reply-time {
	font-size: 11px;
	color: #999;
	margin-top: 2px;
}
.reply-actions {
	display: flex;
	gap: 6px;
}
.reply-like-btn {
	padding: 3px 8px;
	border: 1px solid #dcdfe6;
	background: #fff;
	border-radius: 3px;
	cursor: pointer;
	font-size: 11px;
	transition: all 0.3s;
}
.reply-like-btn:hover {
	border-color: #409eff;
	color: #409eff;
}
.reply-like-btn.liked {
	border-color: #f56c6c;
	color: #f56c6c;
	background: #fef0f0;
}
.reply-reply-btn {
	padding: 3px 8px;
	border: 1px solid #dcdfe6;
	background: #fff;
	border-radius: 3px;
	cursor: pointer;
	font-size: 11px;
	color: #409eff;
	transition: all 0.3s;
}
.reply-reply-btn:hover {
	background: #ecf5ff;
	border-color: #409eff;
}
.reply-delete-btn {
	padding: 3px 8px;
	border: 1px solid #dcdfe6;
	background: #fff;
	border-radius: 3px;
	cursor: pointer;
	font-size: 11px;
	color: #f56c6c;
	transition: all 0.3s;
}
.reply-delete-btn:hover {
	background: #fef0f0;
	border-color: #f56c6c;
}
.reply-content {
	white-space: pre-wrap;
	line-height: 1.5;
	font-size: 13px;
	color: #555;
}

/* 评论和回复的图片上传器样式 */
.comment-image-uploader,
.reply-image-uploader {
	margin: 12px 0;
}

.comment-image-uploader :deep(.upload-container),
.reply-image-uploader :deep(.upload-container) {
	gap: 8px;
}

.comment-image-uploader :deep(.image-preview),
.reply-image-uploader :deep(.image-preview) {
	width: 80px;
	height: 80px;
}

.comment-image-uploader :deep(.upload-trigger),
.reply-image-uploader :deep(.upload-trigger) {
	width: 80px;
	height: 80px;
	font-size: 12px;
}

/* 回复图片样式 */
.reply-images {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
	margin-top: 10px;
}
.reply-image {
	width: 80px;
	height: 80px;
	object-fit: cover;
	border-radius: 4px;
	cursor: pointer;
	transition: all 0.3s;
}
.reply-image:hover {
	transform: scale(1.05);
	box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

@media (max-width:900px) {
	.card { width:100%; padding:12px }
	.content-wrap { padding-left:12px }
	.side-placeholder { display:none }
}
</style>
