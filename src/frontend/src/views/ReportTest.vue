<!--
  举报功能测试页面
  这个页面展示了如何在不同场景下使用 ReportDialog 组件
-->

<template>
  <div class="report-test-page">
    <h1>举报功能测试</h1>
    
    <div class="test-section">
      <h2>1. 举报帖子</h2>
      <div class="test-card">
        <div class="mock-post">
          <h3>这是一个测试帖子</h3>
          <p>这里是帖子内容...</p>
          <button class="report-btn" @click="openReportDialog('post', 123)">
            🚨 举报此帖子
          </button>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>2. 举报评论</h2>
      <div class="test-card">
        <div class="mock-comment">
          <p>这是一条测试评论内容</p>
          <button class="report-btn small" @click="openReportDialog('comment', 456)">
            举报
          </button>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h2>3. 举报评价</h2>
      <div class="test-card">
        <div class="mock-review">
          <p>⭐⭐⭐⭐⭐</p>
          <p>这是一条菜品评价</p>
          <button class="report-btn small" @click="openReportDialog('review', 789)">
            举报
          </button>
        </div>
      </div>
    </div>

    <!-- 举报对话框组件 -->
    <ReportDialog 
      v-model:visible="reportDialogVisible"
      :content-id="reportContentId"
      :content-type="reportContentType"
      @success="handleReportSuccess"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ReportDialog from '@/components/ReportDialog.vue'

const reportDialogVisible = ref(false)
const reportContentId = ref(null)
const reportContentType = ref('post')

const openReportDialog = (type, id) => {
  reportContentType.value = type
  reportContentId.value = id
  reportDialogVisible.value = true
}

const handleReportSuccess = () => {
  const typeText = reportContentType.value === 'post' ? '帖子' : 
                   reportContentType.value === 'comment' ? '评论' : '评价'
  console.log(`${typeText}举报成功！ID: ${reportContentId.value}`)
  
  // 这里可以执行其他操作，如刷新页面、更新状态等
  window.$message?.success?.(`${typeText}举报已提交`)
}
</script>

<style scoped>
.report-test-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 32px;
  text-align: center;
}

.test-section {
  margin-bottom: 40px;
}

.test-section h2 {
  font-size: 20px;
  color: #606266;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #DCDFE6;
}

.test-card {
  background: white;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  padding: 20px;
}

.mock-post,
.mock-comment,
.mock-review {
  position: relative;
}

.mock-post h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 12px;
}

.mock-post p,
.mock-comment p,
.mock-review p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.report-btn {
  padding: 10px 20px;
  background: #F56C6C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.report-btn:hover {
  background: #F78989;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.report-btn:active {
  transform: translateY(0);
}

.report-btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .report-test-page {
    padding: 20px 16px;
  }

  h1 {
    font-size: 24px;
  }

  .test-section h2 {
    font-size: 18px;
  }

  .test-card {
    padding: 16px;
  }
}
</style>
