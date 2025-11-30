<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="header">
      <h1 class="page-title">编辑个人资料</h1>
    </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else class="edit-form">
        <!-- 头像编辑 -->
        <div class="form-section">
          <label class="section-label">头像</label>
          <div class="avatar-edit">
            <div class="avatar-preview">
              <img :src="avatarPreview" alt="头像" class="avatar-img" />
            </div>
            <el-button type="primary" @click="showCropper = true">更换头像</el-button>
          </div>
        </div>

        <!-- 昵称编辑 -->
        <div class="form-section">
          <label class="section-label">昵称</label>
          <div class="nickname-edit">
            <input
              v-model="nickname"
              type="text"
              class="nickname-input"
              :class="{ 'error': nicknameError }"
              placeholder="请输入昵称（最多10个字符）"
              maxlength="10"
              @input="validateNickname"
            />
            <div class="char-count">{{ nickname.length }}/10</div>
          </div>
          <p v-if="nicknameError" class="error-hint">{{ nicknameError }}</p>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button @click="handleCancel">返回</el-button>
          <el-button type="primary" @click="handleSave" :disabled="saving || !!nicknameError">
            {{ saving ? '保存中...' : '保存' }}
          </el-button>
        </div>
  </div>

    <!-- 头像裁剪弹窗 -->
    <AvatarCropper
      v-model:visible="showCropper"
      @cropped="handleAvatarCropped"
    />
  </PageContainer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import AvatarCropper from '@/components/AvatarCropper.vue'
import { getProfile, updateProfile } from '@/api/profile'

const router = useRouter()

// 数据状态
const loading = ref(false)
const saving = ref(false)
const showCropper = ref(false)

// 原始数据
const originalProfile = ref({})

// 编辑数据
const nickname = ref('')
const avatarFile = ref(null)
const avatarPreview = ref('')

// 验证错误
const nicknameError = ref('')

// 加载用户资料
const loadProfile = async () => {
  loading.value = true
  try {
    const data = await getProfile()
    originalProfile.value = data
    nickname.value = data.nickname || ''
    avatarPreview.value = data.avatar || getDefaultAvatar()
  } catch (err) {
    console.error('加载个人资料失败:', err)
    alert('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取默认头像
const getDefaultAvatar = () => {
  try {
    return new URL('../assets/logo.svg', import.meta.url).href
  } catch (e) {
    return ''
  }
}

// 验证昵称
const validateNickname = () => {
  nicknameError.value = ''
  
  if (!nickname.value.trim()) {
    nicknameError.value = '昵称不能为空'
    return
  }

  // 检查是否包含空格
  if (/\s/.test(nickname.value)) {
    nicknameError.value = '昵称不能包含空格'
    return
  }

  // 检查长度
  if (nickname.value.length > 10) {
    nicknameError.value = '昵称不能超过10个字符'
    return
  }
}

// 处理头像裁剪完成
const handleAvatarCropped = (file) => {
  avatarFile.value = file
  // 创建预览 URL
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// 检查是否有修改
const hasChanges = computed(() => {
  const nicknameChanged = nickname.value !== (originalProfile.value.nickname || '')
  const avatarChanged = avatarFile.value !== null
  return nicknameChanged || avatarChanged
})

// 取消编辑
const handleCancel = () => {
  if (hasChanges.value) {
    if (confirm('有未保存的修改，确定要离开吗？')) {
      router.push('/profile')
    }
  } else {
    router.push('/profile')
  }
}

// 保存修改
const handleSave = async () => {
  // 验证昵称
  validateNickname()
  if (nicknameError.value) {
    return
  }

  // 检查是否有修改
  if (!hasChanges.value) {
    router.push('/profile')
    return
  }

  saving.value = true
  try {
    const formData = new FormData()
    
    // 只添加修改过的字段
    if (nickname.value !== (originalProfile.value.nickname || '')) {
      formData.append('nickname', nickname.value)
    }
    
    if (avatarFile.value) {
      formData.append('avatar', avatarFile.value)
    }

    await updateProfile(formData)
    
    alert('保存成功！')
    router.push('/profile')
  } catch (err) {
    console.error('保存失败:', err)
    alert(err.message || '保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
/* PageContainer 承载背景与容器，这里精简 */

.header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
}

.edit-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
}

.section-label {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

/* 头像编辑 */
.avatar-edit {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}


/* 昵称编辑 */
.nickname-edit {
  position: relative;
}

.nickname-input {
  width: 100%;
  padding: 0.75rem;
  padding-right: 4rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.nickname-input:focus {
  outline: none;
  border-color: #2b8aef;
}

.nickname-input.error {
  border-color: #e74c3c;
}

.char-count {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.85rem;
  color: #999;
  pointer-events: none;
}

.error-hint {
  color: #e74c3c;
  font-size: 0.85rem;
  margin: 0.5rem 0 0;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

/* 按钮采用 Element Plus 默认样式 */

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.4rem;
  }

  .edit-form {
    padding: 1.5rem;
  }

  .avatar-edit {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
