<template>
  <PageContainer v-if="dish">
    <template #header>
      <AppTopBar />
    </template>
    <el-button type="primary" @click="$router.push('/canteen')" class="back-btn">返回食堂主页</el-button>

    <el-row :gutter="24" class="dish-layout">
      <el-col :xs="24" :md="10">
        <img :src="getImageUrl(dish.image)" alt="菜品图片" class="dish-image" />
      </el-col>
      <el-col :xs="24" :md="14">
        <div class="dish-info">
          <h2 class="dish-title">{{ dish.name }}</h2>
          <div class="dish-tags">
            <el-tag v-for="tag in dish.tags" :key="tag.id" type="warning" effect="light">{{ tag.name }}</el-tag>
            <el-button link type="primary" size="small" @click="onEditTags">修改标签</el-button>
          </div>
          <div class="dish-rating">
            <el-rate v-model="dishRatingNumber" disabled show-score />
            <span class="dish-price">￥{{ dish.price }}</span>
          </div>
          <div class="dish-desc">{{ dish.description }}</div>
          <!-- 打分栏 -->
          <div class="rate-section">
            <div class="rate-title">我要打分：</div>
            <el-rate v-model="userRating" :max="5" allow-half />
            <el-button type="primary" size="small" @click="submitRating" :loading="ratingLoading" :disabled="!userRating">提交评分</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 评论栏 -->
    <div class="comment-section">
      <el-input
        v-model="commentContent"
        type="textarea"
        :rows="3"
        maxlength="200"
        show-word-limit
        placeholder="请输入评论（5-200字）"
        class="comment-input"
      />
      <el-button type="primary" size="small" @click="submitComment" :loading="commentLoading" :disabled="commentContent.length < 5">发表评论</el-button>
    </div>

    <div class="dish-reviews">
      <h3 class="section-title">评论</h3>
      <el-empty v-if="!reviews.length" description="暂无评论" />
      <el-card v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-header">
          <span class="review-user">{{ review.username || review.user_name }}</span>
          <el-rate :model-value="Number(review.user_rating || 0)" disabled :max="5" show-score />
        </div>
        <div class="review-content">{{ review.content }}</div>
      </el-card>
    </div>
  </PageContainer>
  <el-empty v-else description="未找到该菜品" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDishDetail, getReviews, rateDish, createReview } from '@/utils/api/listApi'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'

const route = useRoute()
const router = useRouter()
const dish = ref(null)
const reviews = ref([])
const dishRatingNumber = ref(0)

// 打分栏
const userRating = ref(0)
const ratingLoading = ref(false)
const lastSavedUserScore = ref(null)
const submitRating = async () => {
  if (!userRating.value) return;
  // 未登录拦截
  const token = localStorage.getItem('jwt')
  if (!token) {
    window.$message?.warning?.('您需要先登录')
    router.push('/login')
    return
  }
  ratingLoading.value = true;
  try {
    const res = await rateDish(route.params.id, { rating: userRating.value });
    // 后端返回 new_rating 与 user_score；保持本地评分不清零
    if (res?.data?.user_score) {
      lastSavedUserScore.value = Number(res.data.user_score)
    }
    // 更新菜品平均分展示
    await fetchDish();
    // 不将 userRating 清零，保持用户刚提交的分值在控件内
    window.$message?.success?.(res?.message === '已更改评分' ? '已更改评分' : '评分成功')
  } catch (e) {
    if (e?.response?.status === 401) {
      window.$message?.warning?.('您需要先登录')
      router.push('/login')
    } else {
      window.$message?.error?.(e.message || '评分失败')
    }
  } finally {
    ratingLoading.value = false;
  }
}

// 评论栏
const commentContent = ref('')
const commentLoading = ref(false)
const submitComment = async () => {
  if (commentContent.value.length < 5) return;
  // 未登录拦截
  const token = localStorage.getItem('jwt')
  if (!token) {
    window.$message?.warning?.('您需要先登录')
    router.push('/login')
    return
  }
  commentLoading.value = true;
  try {
    await createReview(route.params.id, { content: commentContent.value });
    await fetchReviews();
    commentContent.value = '';
    window.$message?.success?.('评论成功！')
  } catch (e) {
    if (e?.response?.status === 401) {
      window.$message?.warning?.('您需要先登录')
      router.push('/login')
    } else {
      window.$message?.error?.(e.message || '评论失败')
    }
  } finally {
    commentLoading.value = false;
  }
}

const fetchDish = async () => {
  const res = await getDishDetail(route.params.id)
  if (res && res.data) {
    dish.value = res.data
    // 保证评分为Number类型
    dishRatingNumber.value = Number(res.data.rating) || 0
  }
}
const fetchReviews = async () => {
  const res = await getReviews(route.params.id)
  if (res && res.data && res.data.reviews) {
    reviews.value = res.data.reviews
  }
}

function getImageUrl(image) {
  if (!image) return ''
  if (image.startsWith('http://') || image.startsWith('https://')) return image
  if (image.startsWith('/media/')) return image
  return '/media/' + image.replace(/^\/+/, '')
}

onMounted(() => {
  fetchDish()
  fetchReviews()
})

function onEditTags() {
  const token = localStorage.getItem('jwt')
  if (!token) {
    window.$message?.warning?.('您需要先登录')
    return router.push('/login')
  }
  // 占位：后续接入真实标签编辑弹窗或页面
  window.$message?.info?.('标签编辑功能开发中')
}
</script>

<style scoped>
.dish-layout{ margin-top: 12px; }
.rate-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.rate-title {
  font-weight: bold;
  color: var(--color-accent);
  font-size: 1.1rem;
}
.comment-section {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 18px;
  width: 100%;
}
.comment-input {
  flex: 1;
}
.back-btn {
  align-self: flex-start;
  margin-bottom: 12px;
}
.dish-image {
  width: 100%;
  height: 260px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px #ff980033;
}
.dish-info {
  width: 100%;
}
.dish-title { margin: 4px 0 8px; }
.dish-tags {
  margin: 8px 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.dish-rating {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.dish-price {
  color: var(--color-accent);
  font-size: 20px;
  font-weight: bold;
}
.dish-desc {
  color: #666;
  margin-top: 8px;
}
.dish-reviews {
  width: 100%;
  margin-top: 24px;
  /* 交由页面统一滚动，保持自然流 */
  min-height: 160px;
}
.review-card {
  margin-bottom: 16px;
}
.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: bold;
}
.review-user {
  color: var(--color-accent);
}
.review-content {
  margin-top: 6px;
  color: #333;
}

/* 自定义滚动条（Webkit 浏览器） */
/* 保留全局滚动条样式即可，无需局部覆盖 */
</style>
