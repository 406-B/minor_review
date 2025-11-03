<template>
		<div class="community-page">
			<div class="top-actions">
				<div class="title">点评社区</div>
				<div class="actions">
					<button class="publish-btn" @click="goCreate">我要发帖</button>
				</div>
			</div>

			<div class="content-wrap">
				<div class="list-wrap">
					<div v-for="post in posts" :key="post.id" class="post-card">
						<div class="post-left" @click="goDetail(post.id)">
							<h3 class="post-title">{{ post.title }}</h3>
							<p class="post-author">发布者：{{ post.author }}</p>
						</div>
						<div class="post-right">
							<img v-if="post.images && post.images.length" :src="post.images[0]" class="thumb" />
						</div>
					</div>
				</div>
			</div>
		</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const posts = ref([])

function loadPosts() {
	const raw = localStorage.getItem('community_posts')
	if (raw) {
		try { posts.value = JSON.parse(raw) } catch (e) { posts.value = [] }
	} else {
		// 初始示例帖子
		posts.value = [
			{
				id: '1',
				title: '示例帖子：第一次点评',
				author: '示例用户',
				content: '这是一个示例帖子，用来展示社区首页。',
				images: []
			}
		]
		localStorage.setItem('community_posts', JSON.stringify(posts.value))
	}
}

function goCreate() {
	router.push({ name: 'PostCreate' })
}

function goDetail(id) {
	router.push({ name: 'PostDetail', params: { id } })
}

onMounted(loadPosts)
</script>

<style scoped>
.community-page { display:block; background: #f5f7fb; padding: 20px 0 }
.top-actions { display:flex; justify-content:space-between; align-items:center; padding:12px 20px; border-bottom:1px solid #eee; margin-bottom:16px }
.top-actions .title { font-size:18px; font-weight:600 }
.top-actions .actions { }
.publish-btn { padding:8px 14px; background:#67c23a; color:#fff; border:none; border-radius:6px; cursor:pointer }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.list-wrap { width:720px; background:#fff; padding:16px; border-radius:8px; box-shadow:0 1px 4px rgba(16,24,40,0.06) }
.post-card { display:flex; justify-content:space-between; align-items:center; padding:14px; border:1px solid #f0f0f0; margin-bottom:12px; border-radius:8px; background:#fff }
.post-left { cursor:pointer; flex:1 }
.post-title { margin:0 0 6px }
.thumb { width:160px; height:110px; object-fit:cover; border-radius:6px; margin-left:12px }

/* Optional right column placeholder styling (kept minimal) */
.side-placeholder { width:260px }

@media (max-width: 900px) {
	.content-wrap { padding-left:12px }
	.list-wrap { width:100%; max-width:720px }
}
</style>
