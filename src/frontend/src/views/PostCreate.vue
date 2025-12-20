<template>
	<PageContainer>
		<template #header>
			<AppTopBar />
		</template>
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

					<!-- 图片上传区域 -->
					<div class="images-section">
						<div class="section-label">添加图片（可选，最多9张）</div>
						<ImageUploader v-model="imageUrls" :max-images="9" />
					</div>

					<!-- 菜品选择区域 -->
					<div class="dish-section">
						<div class="section-label">关联菜品（可选）</div>
						
						<!-- 已选菜品显示 -->
						<div v-if="selectedDish" class="selected-dish-card">
							<img :src="selectedDish.image || '/default-dish.png'" class="dish-image" @error="handleImageError" />
							<div class="dish-info">
								<div class="dish-name">{{ selectedDish.name }}</div>
								<div class="dish-meta">
									<span class="dish-price">¥{{ selectedDish.price }}</span>
									<span class="dish-canteen">{{ selectedDish.canteen_name }}</span>
								</div>
							</div>
							<!-- 悬停显示的删除按钮 -->
							<button @click="removeDish" class="remove-dish-btn" type="button">×</button>
						</div>

						<!-- 添加菜品按钮 -->
						<button v-else @click="showDishModal = true" class="add-dish-btn" type="button">
							<span class="plus-icon">+</span>
							<span>添加菜品</span>
						</button>
					</div>
				</div>
			</div>
			<div class="side-placeholder"></div>
		</div>
		</div>
	</PageContainer>
	
	<!-- 菜品选择悬浮窗 -->
	<div v-if="showDishModal" class="dish-modal-overlay" @click.self="closeDishModal">
		<div class="dish-modal">
			<!-- 顶部操作栏 -->
			<div class="modal-header">
				<button class="cancel-btn" @click="closeDishModal" type="button">取消</button>
				<h3>选择菜品</h3>
				<button 
					class="confirm-btn"
					:class="{ active: tempSelectedDish }"
					:disabled="!tempSelectedDish"
					@click="confirmDishSelection"
					type="button"
				>
					确认选择
				</button>
			</div>
			
			<!-- 搜索框 -->
			<div class="modal-search">
				<input 
					v-model="dishSearchKeyword"
					@input="handleDishSearch"
					type="text"
					placeholder="搜索菜品名称..."
				/>
			</div>
			
			<!-- 搜索结果列表 -->
			<div class="modal-results">
				<div v-if="searchingDishes" class="searching">搜索中...</div>
				<div v-else-if="dishSearchKeyword && dishResults.length === 0" class="no-results">
					未找到相关菜品
				</div>
				<div v-else-if="!dishSearchKeyword" class="empty-hint">
					请输入菜品名称进行搜索
				</div>
				<div 
					v-for="dish in dishResults" 
					:key="dish.id"
					class="dish-card"
					:class="{ selected: tempSelectedDish?.id === dish.id }"
					@click="toggleDishSelection(dish)"
				>
					<img 
						:src="dish.image || '/default-dish.png'" 
						:alt="dish.name"
						@error="handleImageError"
					/>
					<div class="dish-info">
						<h4>{{ dish.name }}</h4>
						<p class="price">¥{{ dish.price }}</p>
						<p class="canteen">{{ dish.canteen_name }}</p>
					</div>
					<!-- 勾选框 -->
					<div class="checkbox" :class="{ checked: tempSelectedDish?.id === dish.id }">
						<span v-if="tempSelectedDish?.id === dish.id">✓</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPost, searchDishes } from '@/api/community'
import PageActions from '../components/PageActions.vue'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import ImageUploader from '../components/ImageUploader.vue'

const router = useRouter()
const subject = ref('')
const content = ref('')
const imageUrls = ref([])
const publishing = ref(false)

// 菜品相关
const selectedDish = ref(null)
const dishSearchKeyword = ref('')
const dishResults = ref([])
const searchingDishes = ref(false)
const showDishModal = ref(false)
const tempSelectedDish = ref(null) // 悬浮窗中临时选择的菜品
let searchTimeout = null

function goBack() {
	router.push({ name: 'CommunityHome' })
}

// 关闭菜品选择悬浮窗
function closeDishModal() {
	showDishModal.value = false
	dishSearchKeyword.value = ''
	dishResults.value = []
	tempSelectedDish.value = null
}

// 确认选择菜品
function confirmDishSelection() {
	if (tempSelectedDish.value) {
		selectedDish.value = tempSelectedDish.value
		closeDishModal()
	}
}

// 切换菜品选择状态
function toggleDishSelection(dish) {
	if (tempSelectedDish.value?.id === dish.id) {
		tempSelectedDish.value = null
	} else {
		tempSelectedDish.value = dish
	}
}

// 搜索菜品
async function handleDishSearch() {
	// 清除之前的搜索延时
	if (searchTimeout) {
		clearTimeout(searchTimeout)
	}
	
	// 如果搜索关键词为空，清空结果
	if (!dishSearchKeyword.value.trim()) {
		dishResults.value = []
		return
	}
	
	// 延时搜索，避免频繁请求
	searchTimeout = setTimeout(async () => {
		searchingDishes.value = true
		try {
			console.log('🔍 开始搜索菜品，关键词:', dishSearchKeyword.value)
			const response = await searchDishes(dishSearchKeyword.value.trim(), 1, 20)
			console.log('🔍 搜索菜品响应:', response)
			console.log('📊 响应代码:', response?.code)
			console.log('📦 响应数据类型:', typeof response?.data)
			console.log('📦 响应数据:', response?.data)
			
			if (response.code === 200 && response.data) {
				// 后端直接返回菜品数组在 data 字段中
				dishResults.value = Array.isArray(response.data) ? response.data : []
				console.log('✅ 搜索到菜品数量:', dishResults.value.length)
				console.log('✅ 菜品列表:', dishResults.value)
			} else {
				console.warn('⚠️ 响应格式异常')
				dishResults.value = []
			}
		} catch (err) {
			console.error('❌ 搜索菜品失败:', err)
			console.error('❌ 错误详情:', err.response?.data || err.message)
			dishResults.value = []
		} finally {
			searchingDishes.value = false
		}
	}, 300) // 300ms 延时
}

// 移除已选菜品
function removeDish() {
	selectedDish.value = null
}

// 处理图片加载错误
function handleImageError(e) {
	e.target.src = '/default-dish.png'
}

async function publish() {
	if (!localStorage.getItem('jwt')) {
		window.$message?.warning?.('您需要先登录')
		return router.push('/login')
	}
	// 验证标题
	if (!subject.value.trim()) {
		window.$message?.warning?.('请填写标题')
		return
	}
	
	if (subject.value.length > 200) {
		window.$message?.warning?.('标题长度不能超过 200 字符')
		return
	}
	
	// 验证内容
	if (!content.value.trim()) {
		window.$message?.warning?.('请填写内容')
		return
	}
	
	if (content.value.length > 5000) {
		window.$message?.warning?.('内容长度不能超过 5000 字符')
		return
	}
	
	publishing.value = true
	
	// 显示审核中的提示
	const auditingMessage = window.$message?.loading?.('正在进行内容审核，请稍候...')
	
	try {
		const response = await createPost(
			subject.value.trim(), 
			content.value.trim(),
			imageUrls.value,  // 传递图片URL数组
			selectedDish.value?.id || null  // 传递菜品ID
		)
		
		// 关闭审核中提示
		if (auditingMessage && typeof auditingMessage.close === 'function') {
			auditingMessage.close()
		}
		
		// 处理审核结果
		if (response.code === 200 && response.data) {
			window.$message?.success?.('✅ 审核通过，发布成功！')
			// 跳转到帖子详情页
			setTimeout(() => {
				router.push({ name: 'PostDetail', params: { id: response.data.id } })
			}, 500)
		} else if (response.code === 400) {
			// 审核失败，显示详细原因
			const errorMsg = response.message || '发布失败'
			window.$message?.error?.(`❌ ${errorMsg}`)
		} else {
			window.$message?.error?.(response.message || '发布失败')
		}
	} catch (err) {
		console.error('发布帖子失败:', err)
		
		// 关闭审核中提示
		if (auditingMessage && typeof auditingMessage.close === 'function') {
			auditingMessage.close()
		}
		
		// 根据错误类型显示不同的提示
		if (err.response?.status === 401) {
			window.$message?.warning?.('请先登录')
			router.push('/login')
		} else if (err.response?.status === 400) {
			// 处理400错误（包括审核失败）
			const errorMsg = err.response?.data?.message || '数据验证失败，请检查标题和内容'
			window.$message?.error?.(`❌ ${errorMsg}`)
		} else {
			window.$message?.error?.('发布失败，请检查网络连接或稍后重试')
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

.images-section {
	margin-top: 24px;
	padding-top: 24px;
	border-top: 1px solid #f0f0f0;
}

.section-label {
	font-size: 14px;
	font-weight: 600;
	color: #333;
	margin-bottom: 12px;
}

/* ========== 菜品选择相关样式 ========== */

/* 已选择的菜品卡片 */
.selected-dish-card {
	position: relative;
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px;
	background: #f8f9fa;
	border: 1px solid #e4e7ed;
	border-radius: 8px;
	transition: all 0.3s ease;
}

.selected-dish-card:hover {
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.selected-dish-card .dish-image {
	width: 60px;
	height: 60px;
	border-radius: 6px;
	object-fit: cover;
	flex-shrink: 0;
}

.selected-dish-card .dish-info {
	flex: 1;
	min-width: 0;
}

.selected-dish-card .dish-name {
	font-size: 15px;
	font-weight: 600;
	color: #303133;
	margin-bottom: 4px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.selected-dish-card .dish-meta {
	display: flex;
	align-items: center;
	gap: 12px;
	margin-top: 4px;
}

.selected-dish-card .dish-price {
	font-size: 16px;
	font-weight: 700;
	color: #f56c6c;
}

.selected-dish-card .dish-canteen {
	font-size: 13px;
	color: #909399;
}

/* 删除按钮 - 悬停时显示 */
.remove-dish-btn {
	position: absolute;
	top: -8px;
	right: -8px;
	width: 26px;
	height: 26px;
	border-radius: 50%;
	background: rgba(0, 0, 0, 0.6);
	color: white;
	border: 2px solid white;
	font-size: 20px;
	line-height: 1;
	cursor: pointer;
	opacity: 0;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.selected-dish-card:hover .remove-dish-btn {
	opacity: 1;
}

.remove-dish-btn:hover {
	background: rgba(245, 108, 108, 0.9);
	transform: scale(1.15);
}

/* 添加菜品按钮 */
.add-dish-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	width: 100%;
	padding: 20px;
	background: white;
	border: 2px dashed #67c23a;
	border-radius: 8px;
	color: #67c23a;
	font-size: 15px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
}

.add-dish-btn:hover {
	background: #f0f9ff;
	border-color: #409eff;
	color: #409eff;
}

.add-dish-btn .plus-icon {
	font-size: 28px;
	font-weight: bold;
	line-height: 1;
}

/* 悬浮窗遮罩 */
.dish-modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 2000;
	padding: 20px;
	animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
	from { opacity: 0; }
	to { opacity: 1; }
}

/* 悬浮窗主体 */
.dish-modal {
	background: white;
	border-radius: 12px;
	width: 100%;
	max-width: 600px;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
	animation: slideUp 0.3s ease;
}

@keyframes slideUp {
	from {
		transform: translateY(20px);
		opacity: 0;
	}
	to {
		transform: translateY(0);
		opacity: 1;
	}
}

/* 悬浮窗头部 */
.modal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16px 20px;
	border-bottom: 1px solid #ebeef5;
	flex-shrink: 0;
}

.modal-header h3 {
	margin: 0;
	font-size: 18px;
	font-weight: 600;
	color: #303133;
}

.modal-header .cancel-btn,
.modal-header .confirm-btn {
	padding: 8px 16px;
	border-radius: 6px;
	font-size: 14px;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.3s ease;
	border: none;
}

.modal-header .cancel-btn {
	background: transparent;
	color: #606266;
}

.modal-header .cancel-btn:hover {
	background: #f5f7fa;
	color: #303133;
}

.modal-header .confirm-btn {
	background: #dcdfe6;
	color: #a8abb2;
	cursor: not-allowed;
}

.modal-header .confirm-btn.active {
	background: #409eff;
	color: white;
	cursor: pointer;
}

.modal-header .confirm-btn.active:hover {
	background: #66b1ff;
}

/* 搜索框 */
.modal-search {
	padding: 16px 20px;
	border-bottom: 1px solid #ebeef5;
	flex-shrink: 0;
}

.modal-search input {
	width: 100%;
	padding: 12px 16px;
	border: 1px solid #dcdfe6;
	border-radius: 8px;
	font-size: 15px;
	transition: border-color 0.3s ease;
}

.modal-search input:focus {
	outline: none;
	border-color: #409eff;
}

.modal-search input::placeholder {
	color: #c0c4cc;
}

/* 结果列表 */
.modal-results {
	flex: 1;
	overflow-y: auto;
	padding: 16px 20px;
}

.modal-results::-webkit-scrollbar {
	width: 8px;
}

.modal-results::-webkit-scrollbar-thumb {
	background: #dcdfe6;
	border-radius: 4px;
}

.modal-results::-webkit-scrollbar-thumb:hover {
	background: #c0c4cc;
}

.modal-results .searching,
.modal-results .no-results,
.modal-results .empty-hint {
	text-align: center;
	padding: 60px 20px;
	color: #909399;
	font-size: 14px;
}

/* 菜品卡片 */
.dish-card {
	position: relative;
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px;
	margin-bottom: 12px;
	background: #f8f9fa;
	border: 2px solid transparent;
	border-radius: 8px;
	cursor: pointer;
	transition: all 0.3s ease;
}

.dish-card:hover {
	background: #ecf5ff;
	border-color: #d9ecff;
	box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.dish-card.selected {
	border-color: #409eff;
	background: #ecf5ff;
}

.dish-card img {
	width: 60px;
	height: 60px;
	border-radius: 6px;
	object-fit: cover;
	flex-shrink: 0;
}

.dish-card .dish-info {
	flex: 1;
	min-width: 0;
}

.dish-card .dish-info h4 {
	font-size: 15px;
	font-weight: 600;
	margin: 0 0 4px 0;
	color: #303133;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.dish-card .dish-info .price {
	font-size: 16px;
	font-weight: 700;
	color: #f56c6c;
	margin: 4px 0;
}

.dish-card .dish-info .canteen {
	font-size: 13px;
	color: #909399;
	margin: 0;
}

/* 勾选框 */
.checkbox {
	width: 24px;
	height: 24px;
	border: 2px solid #dcdfe6;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	transition: all 0.3s ease;
	background: white;
}

.dish-card:hover .checkbox {
	border-color: #409eff;
}

.checkbox.checked {
	background: #409eff;
	border-color: #409eff;
	color: white;
	font-size: 16px;
	font-weight: bold;
}

@media (max-width:900px) {
	.card { width:100%; padding:12px }
	.content-wrap { padding-left:12px }
	.side-placeholder { display:none }
	
	.dish-modal {
		max-width: calc(100vw - 40px);
		max-height: calc(100vh - 40px);
	}
}
</style>
