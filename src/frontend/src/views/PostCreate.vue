<template>
	<div class="page">
			<div class="top-actions">
				<PageActions>
					<template #left>
						<button @click="goBack" class="back">返回</button>
					</template>
					<template #right>
						<button @click="publish" class="publish">发布</button>
					</template>
				</PageActions>

				<div class="title">发帖</div>
			</div>

		<div class="content-wrap">
			<div class="card">
				<div class="form">
					<input v-model="title" placeholder="标题" class="title-input" />
					<textarea v-model="content" placeholder="输入帖子内容..." class="content-input"></textarea>

					<div class="upload">
						<input type="file" accept="image/*" @change="onFileChange" />
						<div v-if="preview" class="preview-wrap">
							<img :src="preview" class="preview" />
						</div>
					</div>
				</div>
			</div>
			<div class="side-placeholder"></div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PageActions from '../components/PageActions.vue'

const router = useRouter()
const title = ref('')
const content = ref('')
const preview = ref(null)
const imageFile = ref(null)

function goBack() {
	router.push({ name: 'CommunityHome' })
}

function onFileChange(e) {
	const file = e.target.files && e.target.files[0]
	if (!file) return
	imageFile.value = file
	const reader = new FileReader()
	reader.onload = (ev) => { preview.value = ev.target.result }
	reader.readAsDataURL(file)
}

function publish() {
	if (!title.value.trim()) {
		alert('请填写标题')
		return
	}

	// 模拟后端校验/上传
	const raw = localStorage.getItem('community_posts')
	const posts = raw ? JSON.parse(raw) : []
	const id = Date.now().toString()
	const newPost = {
		id,
		title: title.value,
		author: '当前用户',
		content: content.value,
		images: preview.value ? [preview.value] : []
	}
	posts.unshift(newPost)
	localStorage.setItem('community_posts', JSON.stringify(posts))

	// 跳转到详情页
	router.push({ name: 'PostDetail', params: { id } })
}
</script>

<style scoped>
.page { background: #f5f7fb; padding: 20px 0 }
.top-actions { display:block; padding:12px 0; border-bottom:1px solid #eee; margin-bottom:12px }
.top-actions .title { font-size:18px; font-weight:600; max-width:1200px; margin:8px auto 0; padding:0 20px; text-align:left }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.card { width:720px; background:#fff; padding:18px; border-radius:8px; box-shadow:0 1px 4px rgba(16,24,40,0.06) }
.side-placeholder { width:260px }
.toolbar { display:flex; gap:8px }
.back, .publish { padding:8px 12px; border-radius:4px; border:none; cursor:pointer }
.back { background:#f5f5f5 }
.publish { background:#409eff; color:#fff }
.title-input { width:100%; padding:8px; font-size:16px; margin-bottom:8px }
.content-input { width:100%; min-height:160px; padding:8px }
.upload { margin-top:12px }
.preview { width:240px; height:160px; object-fit:cover; margin-top:8px }

@media (max-width:900px) {
	.card { width:100%; padding:12px }
	.content-wrap { padding-left:12px }
	.side-placeholder { display:none }
}
</style>
