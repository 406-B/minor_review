<template>
	<div class="image-uploader">
		<div class="images-preview" v-if="imageUrls.length > 0">
			<div v-for="(url, index) in imageUrls" :key="index" class="image-item">
				<img :src="url" :alt="`图片${index + 1}`" class="preview-image" />
				<button @click="removeImage(index)" class="remove-btn" type="button" :disabled="uploading">
					<span class="remove-icon">×</span>
				</button>
			</div>
			<div v-if="imageUrls.length < maxImages && !uploading" class="upload-box" @click="triggerFileInput">
				<span class="upload-icon">+</span>
				<span class="upload-text">添加图片</span>
			</div>
			<div v-if="uploading" class="upload-box uploading-box">
				<span class="upload-icon">⏳</span>
				<span class="upload-text">{{ uploadedCount }}/{{ totalCount }}</span>
			</div>
		</div>
		<div v-else-if="!uploading" class="upload-box-empty" @click="triggerFileInput">
			<span class="upload-icon">+</span>
			<span class="upload-text">添加图片</span>
			<span class="upload-hint">最多{{ maxImages }}张</span>
		</div>
		<div v-else class="upload-box-empty uploading-box">
			<span class="upload-icon">⏳</span>
			<span class="upload-text">上传中 {{ uploadedCount }}/{{ totalCount }}</span>
			<span class="upload-hint">{{ uploadProgress }}%</span>
		</div>
		<input
			ref="fileInput"
			type="file"
			accept="image/*"
			multiple
			@change="handleFileSelect"
			style="display: none"
			:disabled="uploading"
		/>
	</div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch, computed } from 'vue'
import { uploadImage } from '@/api/community'

const props = defineProps({
	modelValue: {
		type: Array,
		default: () => []
	},
	maxImages: {
		type: Number,
		default: 9
	}
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const imageUrls = ref([...props.modelValue])
const uploading = ref(false)
const uploadedCount = ref(0)
const totalCount = ref(0)

// 计算上传进度百分比
const uploadProgress = computed(() => {
	if (totalCount.value === 0) return 0
	return Math.round((uploadedCount.value / totalCount.value) * 100)
})

// 监听props变化，同步更新imageUrls
watch(() => props.modelValue, (newValue) => {
	imageUrls.value = [...newValue]
})

function triggerFileInput() {
	if (imageUrls.value.length >= props.maxImages) {
		alert(`最多只能上传${props.maxImages}张图片`)
		return
	}
	if (uploading.value) {
		alert('正在上传中，请稍候...')
		return
	}
	fileInput.value.click()
}

/**
 * 压缩图片
 * @param {File} file - 原始图片文件
 * @param {number} maxWidth - 最大宽度
 * @param {number} maxHeight - 最大高度
 * @param {number} quality - 压缩质量 0-1
 * @returns {Promise<Blob>} 压缩后的图片Blob
 */
function compressImage(file, maxWidth = 1920, maxHeight = 1920, quality = 0.8) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader()
		reader.readAsDataURL(file)
		
		reader.onload = (e) => {
			const img = new Image()
			img.src = e.target.result
			
			img.onload = () => {
				let width = img.width
				let height = img.height
				
				// 计算缩放比例
				if (width > maxWidth || height > maxHeight) {
					const ratio = Math.min(maxWidth / width, maxHeight / height)
					width = width * ratio
					height = height * ratio
				}
				
				// 创建canvas进行压缩
				const canvas = document.createElement('canvas')
				canvas.width = width
				canvas.height = height
				
				const ctx = canvas.getContext('2d')
				ctx.drawImage(img, 0, 0, width, height)
				
				// 转换为Blob
				canvas.toBlob(
					(blob) => {
						if (blob) {
							resolve(blob)
						} else {
							reject(new Error('图片压缩失败'))
						}
					},
					file.type,
					quality
				)
			}
			
			img.onerror = () => reject(new Error('图片加载失败'))
		}
		
		reader.onerror = () => reject(new Error('文件读取失败'))
	})
}

async function handleFileSelect(event) {
	const files = Array.from(event.target.files)
	const remainingSlots = props.maxImages - imageUrls.value.length
	
	if (files.length > remainingSlots) {
		alert(`最多还能上传${remainingSlots}张图片`)
		event.target.value = ''
		return
	}
	
	uploading.value = true
	uploadedCount.value = 0
	totalCount.value = files.filter(f => f.type.startsWith('image/')).length
	
	try {
		// 并发上传所有图片
		const uploadPromises = files.map(async (file) => {
			if (!file.type.startsWith('image/')) {
				return null
			}
			
			try {
				// 先压缩图片（如果大于500KB）
				let fileToUpload = file
				if (file.size > 500 * 1024) {
					try {
						const compressedBlob = await compressImage(file)
						fileToUpload = new File([compressedBlob], file.name, { type: file.type })
					} catch (error) {
						console.warn('图片压缩失败，使用原图上传:', error)
					}
				}
				
				// 调用后端API上传图片
				const imageUrl = await uploadImage(fileToUpload)
				uploadedCount.value++
				return imageUrl
			} catch (error) {
				console.error('图片上传失败:', error)
				uploadedCount.value++
				alert(`图片 ${file.name} 上传失败: ${error.message || '未知错误'}`)
				return null
			}
		})
		
		// 等待所有上传完成
		const results = await Promise.all(uploadPromises)
		
		// 将成功上传的图片URL添加到列表
		results.forEach(url => {
			if (url) {
				imageUrls.value.push(url)
			}
		})
		
		// 更新父组件
		emit('update:modelValue', imageUrls.value)
	} finally {
		uploading.value = false
		uploadedCount.value = 0
		totalCount.value = 0
		// 清空input，允许重复选择相同文件
		event.target.value = ''
	}
}

function removeImage(index) {
	imageUrls.value.splice(index, 1)
	emit('update:modelValue', imageUrls.value)
}
</script>

<style scoped>
.image-uploader {
	width: 100%;
}

.images-preview {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
	gap: 12px;
}

.image-item {
	position: relative;
	width: 100%;
	padding-bottom: 100%;
	border-radius: 8px;
	overflow: hidden;
	background: #f5f5f5;
}

.preview-image {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.remove-btn {
	position: absolute;
	top: 4px;
	right: 4px;
	width: 24px;
	height: 24px;
	border: none;
	border-radius: 50%;
	background: rgba(0, 0, 0, 0.6);
	color: white;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.3s;
	padding: 0;
}

.remove-btn:hover {
	background: rgba(0, 0, 0, 0.8);
	transform: scale(1.1);
}

.remove-icon {
	font-size: 20px;
	line-height: 1;
}

.upload-box,
.upload-box-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	border: 2px dashed #dcdfe6;
	border-radius: 8px;
	background: #fafafa;
	cursor: pointer;
	transition: all 0.3s;
	min-height: 100px;
}

.upload-box {
	width: 100%;
	padding-bottom: 100%;
	position: relative;
}

.upload-box > * {
	position: absolute;
}

.upload-box .upload-icon {
	top: 35%;
	left: 50%;
	transform: translateX(-50%);
}

.upload-box .upload-text {
	top: 55%;
	left: 50%;
	transform: translateX(-50%);
}

.upload-box-empty {
	padding: 40px 20px;
}

.upload-box:hover,
.upload-box-empty:hover {
	border-color: var(--color-accent);
	background: var(--color-accent-weak);
}

.uploading-box {
	opacity: 0.6;
	cursor: not-allowed;
	pointer-events: none;
}

.uploading-box:hover {
	border-color: #dcdfe6;
	background: #fafafa;
}

.upload-icon {
	font-size: 32px;
	color: #8c939d;
	margin-bottom: 8px;
}

.upload-text {
	font-size: 14px;
	color: #606266;
}

.upload-hint {
	font-size: 12px;
	color: #909399;
	margin-top: 4px;
}

@media (max-width: 768px) {
	.images-preview {
		grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
		gap: 8px;
	}
}
</style>
