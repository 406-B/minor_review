<template>
  <div v-if="visible" class="dialog-overlay" @click="handleCancel">
    <div class="dialog-content" @click.stop>
      <h3>举报内容</h3>
      
      <div class="report-form">
        <div class="form-group">
          <label>举报原因（可多选）</label>
          <div class="checkbox-group">
            <label class="checkbox-item">
              <input type="checkbox" v-model="selectedReasons" value="political">
              <span>政治敏感话题</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="selectedReasons" value="obscene">
              <span>淫秽信息</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="selectedReasons" value="advertisement">
              <span>恶意广告</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="selectedReasons" value="attack">
              <span>人身攻击</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="selectedReasons" value="other">
              <span>其他</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>
            补充说明
            <span v-if="isOtherSelected" class="required-mark">*必填</span>
          </label>
          <textarea 
            v-model="description" 
            :placeholder="isOtherSelected ? '请详细说明举报原因' : '可选填补充说明'"
            :class="{ 'is-required': isOtherSelected }"
            rows="4"
          ></textarea>
          <div v-if="showError" class="error-tip">
            选择"其他"时，必须填写补充说明
          </div>
        </div>
      </div>

      <div class="dialog-actions">
        <button class="cancel-btn" @click="handleCancel" :disabled="submitting">取消</button>
        <button class="confirm-btn" @click="handleSubmit" :disabled="submitting || !canSubmit">
          {{ submitting ? '提交中...' : '举报' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { reportContent } from '@/api/report'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  contentId: {
    type: [String, Number],
    required: true
  },
  contentType: {
    type: String,
    required: true,
    validator: (value) => ['post', 'comment', 'review'].includes(value)
  }
})

const emit = defineEmits(['update:visible', 'success'])

const selectedReasons = ref([])
const description = ref('')
const submitting = ref(false)
const showError = ref(false)

const isOtherSelected = computed(() => selectedReasons.value.includes('other'))

const canSubmit = computed(() => {
  // 必须至少选择一个原因
  if (selectedReasons.value.length === 0) return false
  
  // 如果选择了"其他"，必须填写说明
  if (isOtherSelected.value && !description.value.trim()) return false
  
  return true
})

// 监听"其他"选项的变化
watch(isOtherSelected, (newVal) => {
  if (!newVal) {
    showError.value = false
  }
})

const resetForm = () => {
  selectedReasons.value = []
  description.value = ''
  showError.value = false
}

const handleCancel = () => {
  if (submitting.value) return
  resetForm()
  emit('update:visible', false)
}

const handleSubmit = async () => {
  // 验证表单
  if (!canSubmit.value) {
    if (isOtherSelected.value && !description.value.trim()) {
      showError.value = true
    }
    return
  }

  submitting.value = true
  showError.value = false

  try {
    // TODO: 后端举报API待实现，暂时跳过实际请求
    // const response = await reportContent({
    //   content_id: props.contentId,
    //   content_type: props.contentType,
    //   reasons: selectedReasons.value,
    //   description: description.value.trim()
    // })
    
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 直接显示成功
    console.log('[举报] 举报信息:', {
      content_type: props.contentType,
      content_id: props.contentId,
      reasons: selectedReasons.value,
      description: description.value.trim()
    })
    
    // 成功提示
    window.$message?.success?.('举报成功，感谢您对社区良好风气做出的贡献！')
    
    // 重置表单并关闭对话框
    resetForm()
    emit('update:visible', false)
    emit('success')
    
  } catch (err) {
    console.error('[ReportDialog] 举报失败:', err)
    const errorMsg = err?.response?.data?.message || err?.message || '举报失败，请稍后重试'
    window.$message?.error?.(errorMsg)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* 对话框遮罩层 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 对话框内容 */
.dialog-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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

.dialog-content h3 {
  margin: 0 0 20px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

/* 表单 */
.report-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.required-mark {
  color: #F56C6C;
  margin-left: 4px;
  font-size: 12px;
}

/* 复选框组 */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px 12px;
  border-radius: 6px;
  background: #F5F7FA;
  transition: all 0.2s;
}

.checkbox-item:hover {
  background: #E4E7ED;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 10px;
  cursor: pointer;
  accent-color: var(--color-accent);
}

.checkbox-item span {
  font-size: 14px;
  color: #303133;
  user-select: none;
}

/* 文本域 */
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #DCDFE6;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

textarea:focus {
  outline: none;
  border-color: var(--color-accent);
}

textarea.is-required {
  border-color: #F56C6C;
}

textarea::placeholder {
  color: #C0C4CC;
}

.error-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #F56C6C;
}

/* 按钮组 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn,
.confirm-btn {
  padding: 10px 24px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background: #F5F7FA;
  color: #606266;
}

.cancel-btn:hover:not(:disabled) {
  background: #E4E7ED;
}

.cancel-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.confirm-btn {
  background: #F56C6C;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #F78989;
}

.confirm-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background: #FAB6B6;
}

/* 响应式 */
@media (max-width: 768px) {
  .dialog-content {
    width: 95%;
    padding: 20px;
  }

  .dialog-content h3 {
    font-size: 16px;
  }

  .checkbox-item {
    padding: 8px 10px;
  }

  .cancel-btn,
  .confirm-btn {
    padding: 8px 20px;
    font-size: 13px;
  }
}
</style>
