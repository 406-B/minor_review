<template>
  <div class="dish-detail" v-if="dish">
    <el-button type="primary" @click="$router.push('/canteen')" class="back-btn">返回食堂主页</el-button>
    <img :src="getImageUrl(dish.image)" alt="菜品图片" class="dish-image" />
    <!-- 打分栏 -->
    <div class="rate-section">
      <div class="rate-title">我要打分：</div>
      <el-rate v-model="userRating" :max="5" allow-half />
      <el-button type="primary" size="small" @click="submitRating" :disabled="ratingLoading">提交评分</el-button>
    </div>
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
      <el-button type="primary" size="small" @click="submitComment" :disabled="commentLoading || commentContent.length < 5">发表评论</el-button>
    </div>
    <div class="dish-info">
      <h2>{{ dish.name }}</h2>
      <div class="dish-tags">
        <el-tag v-for="tag in dish.tags" :key="tag.id" type="warning">{{ tag.name }}</el-tag>
        <el-button type="info" size="small" class="edit-tags-btn" @click="() => {}">修改标签</el-button>
      </div>
      <div class="dish-rating">
        <el-rate v-model="dishRatingNumber" disabled show-score />
        <span class="dish-price">￥{{ dish.price }}</span>
      </div>
      <div class="dish-desc">{{ dish.description }}</div>
    </div>
    <div class="dish-reviews">
      <h3>评论</h3>
      <el-empty v-if="!reviews.length" description="暂无评论" />
      <el-card v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-header">
          <span class="review-user">{{ review.user_name }}</span>
          <el-rate v-model="review.rating_score" disabled :max="5" />
        </div>
        <div class="review-content">{{ review.content }}</div>
      </el-card>
    </div>
  </div>
  <el-empty v-else description="未找到该菜品" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getDishDetail, getReviews, rateDish, createReview } from '@/utils/api/listApi'

const route = useRoute()
const dish = ref(null)
const reviews = ref([])
const dishRatingNumber = ref(0)

// 打分栏
const userRating = ref(0)
const ratingLoading = ref(false)
const submitRating = async () => {
  if (!userRating.value) return;
  ratingLoading.value = true;
  try {
    await rateDish(route.params.id, { rating: userRating.value });
    await fetchDish();
    userRating.value = 0;
    window.$message?.success?.('评分成功！')
  } catch (e) {
    window.$message?.error?.(e.message || '评分失败')
  } finally {
    ratingLoading.value = false;
  }
}

// 评论栏
const commentContent = ref('')
const commentLoading = ref(false)
const submitComment = async () => {
  if (commentContent.value.length < 5) return;
  commentLoading.value = true;
  try {
    await createReview(route.params.id, { content: commentContent.value });
    await fetchReviews();
    commentContent.value = '';
    window.$message?.success?.('评论成功！')
  } catch (e) {
    window.$message?.error?.(e.message || '评论失败')
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
</script>

<style scoped>
.dish-detail {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 24px;
  padding: 48px 80px 48px 80px;
  background: #fff;
  border-radius: 0;
  box-shadow: none;
  width: 100vw;
  min-height: 100vh;
  margin: 0;
}
.rate-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.rate-title {
  font-weight: bold;
  color: #ff9800;
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
  width: 320px;
  height: 220px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px #ff980033;
}
.dish-info {
  width: 100%;
}
.dish-tags {
  margin: 8px 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.edit-tags-btn {
  margin-left: 8px;
  padding: 2px 12px;
  font-size: 13px;
  border-radius: 12px;
  background: #ffe0b2;
  color: #ff9800;
  border: none;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.edit-tags-btn:hover {
  background: #ffecb3;
  color: #fb8c00;
}
.dish-rating {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.dish-price {
  color: #ff9800;
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
  color: #ff9800;
}
.review-content {
  margin-top: 6px;
  color: #333;
}
</style>
