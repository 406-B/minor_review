<template>
  <PageContainer v-if="dish">
    <template #header>
      <AppTopBar />
    </template>
    <el-button type="primary" @click="$router.push('/canteen')" class="back-btn">返回食堂主页</el-button>

    <el-row :gutter="24" class="dish-layout">
      <el-col :xs="24" :md="10">
        <AchievementImage
          v-if="dish"
          :dish-id="dish.id"
          :src="getImageUrl(dish.image)"
          alt="菜品图片"
          class="dish-image"
        />
      </el-col>
      <el-col :xs="24" :md="14">
        <div class="dish-info">
          <h2 class="dish-title">{{ dish.name }}</h2>
          <div class="dish-tags">
            <el-tag v-for="tag in dish.tags" :key="tag.id" type="warning" effect="light">{{ tag.name }}</el-tag>
      <el-button link type="primary" size="small" @click="onEditTags">添加标签</el-button>
          </div>
          <div class="dish-rating">
            <el-rate v-model="dishRatingNumber" disabled show-score />
            <span class="dish-price">￥{{ dish.price }}</span>
          </div>
          <div class="dish-desc">{{ dish.description }}</div>
          <!-- 打卡栏 -->
          <div class="checkin-section">
            <div class="checkin-left">
              <span class="checkin-label">打卡：</span>
              <span class="checkin-count" :class="tierClass">{{ checkinCount }} 次</span>
              <span v-if="tierLabel" class="checkin-tier" :class="tierClass">（{{ tierLabel }}）</span>
            </div>
            <!-- 下一等级进度条：置于打卡计数与按钮之间 -->
            <div class="checkin-progress" v-if="progressOf(checkinCount).next">
              <div class="bar"><div class="fill" :style="{ width: progressOf(checkinCount).percent + '%' }"></div></div>
              <div class="progress-text">{{ checkinCount }} / {{ progressOf(checkinCount).next }}</div>
            </div>
            <div class="checkin-progress done" v-else>
              <div class="progress-text">已满级</div>
            </div>
            <el-button type="success" size="small" @click="onCheckIn" :loading="checkinLoading">+ 打卡一次</el-button>
          </div>
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

  <!-- 添加标签弹窗 -->
  <el-dialog v-model="tagDialogVisible" title="添加标签" width="420px">
    <div class="tag-form">
      <el-input v-model="newTagName" maxlength="20" show-word-limit placeholder="输入新标签，例如：招牌、辣、必吃" />
      <div class="tag-actions">
        <el-button @click="tagDialogVisible=false" :disabled="tagSubmitting">取消</el-button>
        <el-button type="primary" @click="submitNewTag" :loading="tagSubmitting" :disabled="!newTagName.trim()">提交</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDishDetail, getReviews, rateDish, createReview, checkInDish, addTagToDish } from '@/utils/api/listApi'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import AchievementImage from '@/components/common/AchievementImage.vue'
import { ensureAchievementsLoaded, getDishCheckinCount, getAchievementByCount, bumpDishCheckinCount } from '@/utils/achievements'

const route = useRoute()
const router = useRouter()
const dish = ref(null)
const reviews = ref([])
const dishRatingNumber = ref(0)

// 打卡栏
const checkinCount = ref(0)
const tierLabel = ref('')
const tierKey = ref('')
const checkinLoading = ref(false)

function refreshCheckin() {
  if (!dish.value) return
  const cnt = getDishCheckinCount(dish.value.id)
  checkinCount.value = cnt
  const level = getAchievementByCount(cnt)
  tierLabel.value = level.label
  tierKey.value = level.key
}

const tierClass = computed(() => tierKey.value ? `achv-${tierKey.value}` : '')

// 进度条计算：阈值 1/3/10/100，超过 100 视为满级
const thresholds = [1, 3, 10, 100]
function nextThreshold(count) {
  for (const t of thresholds) { if (count < t) return t }
  return null
}
function progressOf(count) {
  const next = nextThreshold(Number(count) || 0)
  if (!next) return { next: null, percent: 100 }
  const percent = Math.max(0, Math.min(100, Math.round(((Number(count)||0) / next) * 100)))
  return { next, percent }
}

async function onCheckIn() {
  const token = localStorage.getItem('jwt')
  if (!token) {
    window.$message?.warning?.('您需要先登录')
    return router.push('/login')
  }
  if (!dish.value) return
  checkinLoading.value = true
  try {
    const res = await checkInDish(dish.value.id, {})
    // 本地缓存 +1，并刷新展示
    bumpDishCheckinCount(dish.value.id, 1)
    refreshCheckin()
    if (res?.message) window.$message?.success?.(res.message)
  } catch (e) {
    if (e?.code === 401) {
      window.$message?.warning?.('您需要先登录')
      router.push('/login')
    } else if (e?.code === 403) {
      window.$message?.error?.('没有权限打卡该菜品')
    } else {
      window.$message?.error?.(e?.message || '打卡失败')
    }
  } finally {
    checkinLoading.value = false
  }
}

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
  await ensureAchievementsLoaded()
  refreshCheckin()
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

// 标签添加弹窗状态
const tagDialogVisible = ref(false)
const newTagName = ref('')
const tagSubmitting = ref(false)

function onEditTags() {
  const token = localStorage.getItem('jwt')
  if (!token) {
    window.$message?.warning?.('You need to log in first')
    return router.push('/login')
  }
  newTagName.value = ''
  tagDialogVisible.value = true
}

async function submitNewTag() {
  if (!dish.value) return
  const name = newTagName.value.trim()
  if (!name) return
  tagSubmitting.value = true
  try {
  const res = await addTagToDish(dish.value.id, { tag_name: name })
  // 乐观更新：立即把新标签加入本地展示，避免网络/缓存延迟
    const newTag = { id: res?.data?.tag_id || Date.now(), name }
    if (dish.value?.tags && !dish.value.tags.some(t => String(t.name) === name)) {
      dish.value.tags = [...dish.value.tags, newTag]
    }
    // 之后刷新菜品详情以获取服务端的最终数据
    await fetchDish()
  tagDialogVisible.value = false
  window.$message?.success?.(res?.message || 'Tag submitted, awaiting approval')
  } catch (e) {
    if (e?.code === 401) {
      window.$message?.warning?.('You need to log in first')
      router.push('/login')
    } else if (e?.code === 403) {
      window.$message?.error?.('No permission to add tags')
    } else {
      window.$message?.error?.(e?.message || 'Failed to add tag')
    }
  } finally {
    tagSubmitting.value = false
  }
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

.tag-form { display:flex; flex-direction: column; gap: 12px; }
.tag-actions { display:flex; justify-content: flex-end; gap: 10px; }

/* 自定义滚动条（Webkit 浏览器） */
/* 保留全局滚动条样式即可，无需局部覆盖 */

/* 成就等级文本颜色（与边框主题对应） */
.achv-bronze { color: #cd7f32; font-weight: 700; }
.achv-silver { color: #909399; font-weight: 700; }
.achv-gold { color: #d4a017; font-weight: 700; }
.achv-rainbow { 
  background: linear-gradient(90deg, #ff0000, #ffa500, #ffff00, #00ff00, #00ffff, #0000ff, #8b00ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 800;
}
.checkin-section { display:flex; align-items:center; justify-content:space-between; margin: 10px 0 6px; }
.checkin-left { display:flex; align-items:center; gap: 8px; }
.checkin-label { color:#666; }
.checkin-count { font-size: 16px; }
.checkin-tier { font-size: 14px; }
/* 进度条：占据中间弹性空间 */
.checkin-progress { flex: 1; display:flex; align-items: center; gap: 10px; margin: 0 12px; min-width: 120px; }
.checkin-progress .bar { flex: 1; height: 6px; background: #eef0f3; border-radius: 999px; overflow: hidden }
.checkin-progress .fill { height: 100%; background: linear-gradient(90deg, var(--color-accent), #8bd2ff); border-radius: 999px; transition: width .25s ease }
.checkin-progress .progress-text { font-size: 12px; color: #666; white-space: nowrap }
.checkin-progress.done .progress-text { color: var(--color-accent) }
</style>
