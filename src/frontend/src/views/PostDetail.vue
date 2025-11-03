<template>
	<div class="page">
			<div class="top-actions">
				<PageActions>
					<template #left>
						<button @click="goBack">返回</button>
					</template>
					<template #right>
						<!-- right slot intentionally empty for details -->
					</template>
				</PageActions>

				<div class="title">帖子详情</div>
			</div>

		<div class="content-wrap">
			<div class="card">
				<div v-if="post" class="content">
					<h2>{{ post.title }}</h2>
					<p class="meta">发布者：{{ post.author }}</p>
					<div class="images">
						<img v-for="(img, idx) in post.images" :key="idx" :src="img" class="img" />
					</div>
					<div class="body">{{ post.content }}</div>
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const post = ref(null)

import PageActions from '../components/PageActions.vue'

function goBack() { router.push({ name: 'CommunityHome' }) }

function loadPost() {
	const id = route.params.id
	const raw = localStorage.getItem('community_posts')
	if (!raw) return
	try {
		const posts = JSON.parse(raw)
		post.value = posts.find(p => p.id === id) || null
	} catch (e) { post.value = null }
}

onMounted(loadPost)
</script>

<style scoped>
.page { background: #f5f7fb; padding: 20px 0 }
.top-actions { display:block; padding:12px 0; border-bottom:1px solid #eee; margin-bottom:12px }
.top-actions .title { font-size:18px; font-weight:600; max-width:1200px; margin:8px auto 0; padding:0 20px; text-align:left }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.card { width:720px; background:#fff; padding:18px; border-radius:8px; box-shadow:0 1px 4px rgba(16,24,40,0.06) }
.side-placeholder { width:260px }
.toolbar { display:flex; gap:8px }
.toolbar button { padding:8px 12px; border-radius:4px; border:none; background:#f5f5f5; cursor:pointer }
.img { width:320px; height:200px; object-fit:cover; margin-right:8px }
.meta { color:#888 }
.body { margin-top:12px; white-space:pre-wrap }

@media (max-width:900px) {
	.card { width:100%; padding:12px }
	.content-wrap { padding-left:12px }
	.side-placeholder { display:none }
}
</style>
