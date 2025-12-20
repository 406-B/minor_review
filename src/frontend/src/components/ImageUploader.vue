<template>
	<div class="image-uploader">
		<div class="images-preview" v-if="imageUrls.length > 0">
			<div v-for="(url, index) in imageUrls" :key="index" class="image-item">
				<img :src="url" :alt="`图片${index + 1}`" class="preview-image" />
				<button @click="removeImage(index)" class="remove-btn" type="button">
					<span class="remove-icon">×</span>
				</button>
			</div>
			<div v-if="imageUrls.length < maxImages" class="upload-box" @click="triggerFileInput">
				<span class="upload-icon">+</span>
				<span class="upload-text">添加图片</span>
			</div>
		</div>
		<div v-else class="upload-box-empty" @click="triggerFileInput">
			<span class="upload-icon">+</span>
			<span class="upload-text">添加图片</span>
			<span class="upload-hint">最多{{ maxImages }}张</span>
		</div>
		<input
			ref="fileInput"
			type="file"
			accept="image/*"
			multiple
			@change="handleFileSelect"
			style="display: none"
		/>
	</div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'

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

function triggerFileInput() {
	if (imageUrls.value.length >= props.maxImages) {
		alert(`最多只能上传${props.maxImages}张图片`)
		return
	}
	fileInput.value.click()
}

async function handleFileSelect(event) {
	const files = Array.from(event.target.files)
	const remainingSlots = props.maxImages - imageUrls.value.length
	
	if (files.length > remainingSlots) {
		alert(`最多还能上传${remainingSlots}张图片`)
		return
	}
	
	// 模拟上传并生成URL（实际项目中应该调用图床API）
	for (const file of files) {
		if (file.type.startsWith('image/')) {
			// 这里使用本地预览URL，实际应该上传到服务器获取真实URL
			const url = URL.createObjectURL(file)
			imageUrls.value.push(url)
		}
	}
	
	// 更新父组件
	emit('update:modelValue', imageUrls.value)
	
	// 清空input，允许重复选择相同文件
	event.target.value = ''
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
