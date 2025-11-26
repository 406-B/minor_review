<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <div class="modal-header">
        <h3>上传头像</h3>
        <button class="close-btn" @click="handleCancel">×</button>
      </div>
      
      <div class="modal-body">
        <!-- 未选择图片时显示上传区域 -->
        <div
          v-if="!imageFile"
          class="upload-area"
          :class="{ 'drag-over': isDragging }"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
        >
          <div class="upload-icon">📁</div>
          <p class="upload-text">拖拽图片到这里</p>
          <p class="upload-hint">或</p>
          <button class="browse-btn" @click="triggerFileInput">浏览本地文件</button>
          <p class="file-hint">支持 JPG、PNG、GIF 格式</p>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,image/gif"
            style="display: none"
            @change="handleFileSelect"
          />
        </div>

        <!-- 选择图片后显示裁剪区域 -->
        <div v-else class="crop-area">
          <div class="crop-container">
            <canvas ref="canvas" class="crop-canvas"></canvas>
          </div>
          
          <div class="crop-controls">
            <button class="control-btn" @click="resetImage">重新选择</button>
            <button class="control-btn primary" @click="handleCrop">确认裁剪</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'cropped'])

const isDragging = ref(false)
const imageFile = ref(null)
const fileInput = ref(null)
const canvas = ref(null)
const image = ref(null)
const cropSize = ref(300) // 裁剪框大小

// 拖拽处理
const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    validateAndLoadFile(files[0])
  }
}

// 文件选择处理
const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    validateAndLoadFile(files[0])
  }
}

// 验证并加载文件
const validateAndLoadFile = (file) => {
  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!validTypes.includes(file.type)) {
    alert('请上传 JPG、PNG 或 GIF 格式的图片')
    return
  }

  // 验证文件大小（限制 5MB）
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }

  imageFile.value = file
  loadImage(file)
}

// 加载图片
const loadImage = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const img = new Image()
    img.onload = () => {
      image.value = img
      nextTick(() => {
        drawImage()
      })
    }
    img.src = e.target.result
  }
  reader.readAsDataURL(file)
}

// 绘制图片到 canvas
const drawImage = () => {
  if (!canvas.value || !image.value) return

  const ctx = canvas.value.getContext('2d')
  const img = image.value

  // 设置 canvas 尺寸
  canvas.value.width = cropSize.value
  canvas.value.height = cropSize.value

  // 计算居中裁剪
  const scale = Math.max(cropSize.value / img.width, cropSize.value / img.height)
  const scaledWidth = img.width * scale
  const scaledHeight = img.height * scale
  const x = (cropSize.value - scaledWidth) / 2
  const y = (cropSize.value - scaledHeight) / 2

  // 绘制图片
  ctx.drawImage(img, x, y, scaledWidth, scaledHeight)
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 重置图片
const resetImage = () => {
  imageFile.value = null
  image.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 裁剪图片
const handleCrop = () => {
  if (!canvas.value) return

  canvas.value.toBlob((blob) => {
    if (blob) {
      const croppedFile = new File([blob], imageFile.value.name, {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
      emit('cropped', croppedFile)
      handleCancel()
    }
  }, 'image/jpeg', 0.9)
}

// 取消
const handleCancel = () => {
  resetImage()
  emit('update:visible', false)
}

// 监听 visible 变化，关闭时重置
watch(() => props.visible, (newVal) => {
  if (!newVal) {
    resetImage()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
}

.upload-area.drag-over {
  border-color: #2b8aef;
  background-color: rgba(43, 138, 239, 0.05);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  color: #666;
  margin: 0.5rem 0;
}

.upload-hint {
  color: #999;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.browse-btn {
  padding: 0.6rem 1.5rem;
  background-color: #2b8aef;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
  margin: 0.5rem 0;
}

.browse-btn:hover {
  background-color: #1a73d9;
}

.file-hint {
  font-size: 0.85rem;
  color: #999;
  margin-top: 1rem;
}

.crop-area {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.crop-container {
  margin-bottom: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.crop-canvas {
  display: block;
  max-width: 100%;
  height: auto;
}

.crop-controls {
  display: flex;
  gap: 1rem;
}

.control-btn {
  padding: 0.6rem 1.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #666;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.control-btn:hover {
  border-color: #999;
  background-color: #f5f5f5;
}

.control-btn.primary {
  background-color: #2b8aef;
  color: white;
  border-color: #2b8aef;
}

.control-btn.primary:hover {
  background-color: #1a73d9;
  border-color: #1a73d9;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
  }

  .upload-area {
    padding: 2rem 1rem;
  }
}
</style>
