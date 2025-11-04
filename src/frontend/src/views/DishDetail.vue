<template>
  <div class="dish-detail" v-if="dish">
    <img :src="dish.image" alt="菜品图片" class="dish-image" />
    <div class="dish-info">
      <h2>{{ dish.name }}</h2>
      <div class="dish-tags">
        <el-tag v-for="tag in dish.tags" :key="tag.id" type="warning">{{ tag.name }}</el-tag>
      </div>
      <div class="dish-rating">
        <el-rate v-model="dish.rating" disabled show-score />
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
import { getDishDetail, getReviews } from '../api/canteenApi'

const route = useRoute()
const dish = ref(null)
const reviews = ref([])

const fetchDish = async () => {
  const res = await getDishDetail(route.params.id)
  if (res && res.data) {
    dish.value = res.data
  }
}
const fetchReviews = async () => {
  const res = await getReviews(route.params.id)
  if (res && res.data && res.data.reviews) {
    reviews.value = res.data.reviews
  }
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
  padding: 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px #f5c16c22;
  max-width: 800px;
  margin: 32px auto;
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
