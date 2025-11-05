<template>
	<div class="page">
			<div class="top-actions">
				<PageActions>
					<template #left>
						<button @click="goBack" class="back">返回</button>
					</template>
					<template #right>
						<button @click="publish" class="publish" :disabled="publishing">
							{{ publishing ? '发布中...' : '发布' }}
						</button>
					</template>
				</PageActions>

				<div class="title">发帖</div>
			</div>

		<div class="content-wrap">
			<div class="card">
				<div class="form">
					<input 
						v-model="subject" 
						placeholder="请输入标题（最多200字符）"
						class="subject-input"
						:disabled="publishing"
						maxlength="200"
					/>
					
					<div class="tips subject-tips">
						<span class="char-count" :class="{ warning: subject.length > 180 }">
							{{ subject.length }} / 200
						</span>
					</div>
					
					<textarea 
						v-model="content" 
						placeholder="分享你的想法..."
						class="content-input"
						:disabled="publishing"
					></textarea>
					
					<div class="tips">
						<span class="char-count" :class="{ warning: content.length > 4500 }">
							{{ content.length }} / 5000
						</span>
						<span class="hint">支持最多 5000 字符</span>
					</div>

					<!-- TODO：暂时隐藏图片上传功能，因为后端 API 文档中未提供图片上传接口 -->
					<!-- <div class="upload">
						<input type="file" accept="image/*" @change="onFileChange" />
						<div v-if="preview" class="preview-wrap">
							<img :src="preview" class="preview" />
						</div>
					</div> -->
				</div>
			</div>
			<div class="side-placeholder"></div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPost } from '@/api/community'
import PageActions from '../components/PageActions.vue'

const router = useRouter()
const subject = ref('')
const content = ref('')
const publishing = ref(false)
// const preview = ref(null)
// const imageFile = ref(null)

function goBack() {
	router.push({ name: 'CommunityHome' })
}

// function onFileChange(e) {
// 	const file = e.target.files && e.target.files[0]
// 	if (!file) return
// 	imageFile.value = file
// 	const reader = new FileReader()
// 	reader.onload = (ev) => { preview.value = ev.target.result }
// 	reader.readAsDataURL(file)
// }

async function publish() {
	// 验证标题
	if (!subject.value.trim()) {
		alert('请填写标题')
		return
	}
	
	if (subject.value.length > 200) {
		alert('标题长度不能超过 200 字符')
		return
	}
	
	// 验证内容
	if (!content.value.trim()) {
		alert('请填写内容')
		return
	}
	
	if (content.value.length > 5000) {
		alert('内容长度不能超过 5000 字符')
		return
	}
	
	publishing.value = true
	
	try {
		const response = await createPost(subject.value.trim(), content.value.trim())
		
		if (response.code === 200 && response.data) {
			alert('发布成功！')
			// 跳转到帖子详情页
			router.push({ name: 'PostDetail', params: { id: response.data.id } })
		} else {
			alert(response.message || '发布失败')
		}
	} catch (err) {
		console.error('发布帖子失败:', err)
		
		// 根据错误类型显示不同的提示
		if (err.response?.status === 401) {
			alert('请先登录')
		} else if (err.response?.status === 400) {
			alert(err.response?.data?.message || '数据验证失败，请检查标题和内容')
		} else {
			alert('发布失败，请检查网络连接或稍后重试')
		}
	} finally {
		publishing.value = false
	}
}
</script>

<style scoped>
.page { background: #f5f7fb; padding: 20px 0; min-height: 100vh }
.top-actions { display:block; padding:12px 0; border-bottom:1px solid #eee; margin-bottom:12px }
.top-actions .title { font-size:18px; font-weight:600; max-width:1200px; margin:8px auto 0; padding:0 20px; text-align:left }
.content-wrap { display:flex; justify-content:flex-start; gap:20px; padding-left:20px }
.card { width:720px; background:#fff; padding:18px; border-radius:8px; box-shadow:0 1px 4px rgba(16,24,40,0.06) }
.side-placeholder { width:260px }
.toolbar { display:flex; gap:8px }
.back, .publish { padding:8px 12px; border-radius:4px; border:none; cursor:pointer; transition: all 0.3s }
.back { background:#f5f5f5 }
.back:hover { background:#e8e8e8 }
.publish { background:#409eff; color:#fff }
.publish:hover:not(:disabled) { background:#66b1ff }
.publish:disabled { background:#ccc; cursor:not-allowed }

.form { display: flex; flex-direction: column; gap: 16px }

.subject-input {
	width: 100%;
	padding: 14px 16px;
	border: 1px solid #dcdfe6;
	border-radius: 8px;
	font-size: 18px;
	font-weight: 600;
	font-family: inherit;
}
.subject-input:focus {
	outline: none;
	border-color: #409eff;
}
.subject-input:disabled {
	background: #f5f5f5;
	cursor: not-allowed;
}

.subject-tips {
	margin-top: -8px;
	justify-content: flex-end;
}

.content-input { 
	width: 100%; 
	min-height: 320px; 
	padding: 16px; 
	border: 1px solid #dcdfe6; 
	border-radius: 8px; 
	font-size: 15px; 
	resize: vertical;
	line-height: 1.8;
	font-family: inherit;
}
.content-input:focus { 
	outline: none; 
	border-color: #409eff 
}
.content-input:disabled { 
	background: #f5f5f5; 
	cursor: not-allowed 
}

.tips { 
	display: flex; 
	justify-content: space-between; 
	align-items: center; 
	padding: 0 4px;
	font-size: 13px;
}
.char-count { 
	color: #909399;
	font-weight: 500;
}
.char-count.warning { 
	color: #f56c6c 
}
.hint { 
	color: #c0c4cc 
}

.upload { margin-top:12px }
.preview { width:240px; height:160px; object-fit:cover; margin-top:8px; border-radius: 8px }

@media (max-width:900px) {
	.card { width:100%; padding:12px }
	.content-wrap { padding-left:12px }
	.side-placeholder { display:none }
}
</style>
