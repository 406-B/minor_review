<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <el-button type="primary" @click="$router.push('/canteen')" class="back-btn">返回食堂主页</el-button>
    <SectionTitle>菜品搜索</SectionTitle>
    <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent="onSearch">
      <el-form-item label="菜品名">
        <el-input v-model="searchForm.name" placeholder="输入菜品名" clearable style="min-width: 220px" />
      </el-form-item>
      <el-form-item label="价格区间">
        <el-input-number v-model="searchForm.min_price" :min="0" placeholder="最低价" style="width: 90px" />
        <span style="margin: 0 8px;">-</span>
        <el-input-number v-model="searchForm.max_price" :min="0" placeholder="最高价" style="width: 90px" />
      </el-form-item>
      <el-form-item label="标签">
        <!-- 直接在下拉框内输入文字以筛选标签；必须选择至少一个标签后才能搜索 -->
        <el-select v-model="searchForm.tag_ids" multiple filterable placeholder="输入以筛选并选择标签" style="min-width: 240px">
          <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSearch" :disabled="!canSearch">搜索</el-button>
      </el-form-item>
    </el-form>
    <div class="dish-list-wrap">
      <el-empty v-if="dishes.length === 0 && !loading" description="暂无菜品" />
      <el-row :gutter="24">
        <el-col v-for="dish in dishes" :key="dish.id" :span="6">
          <el-card class="dish-card" shadow="hover" @click="goToDish(dish.id)">
            <AchievementImage
              :dish-id="dish.id"
              :src="dish.image"
              :width="'100%'"
              :height="140"
              :radius="varRadiusSm"
            />
            <div class="dish-info">
              <div class="dish-title">{{ dish.name }}</div>
              <div class="dish-tags">
                <el-tag v-for="tag in dish.tags" :key="tag.id" size="small">{{ tag.name }}</el-tag>
              </div>
              <div class="dish-price">￥{{ dish.price }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDishes, getTags } from '@/utils/api/listApi'
import PageContainer from '@/components/ui/PageContainer.vue'
import SectionTitle from '@/components/ui/SectionTitle.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import AchievementImage from '@/components/common/AchievementImage.vue'

const route = useRoute()
const router = useRouter()
const searchForm = ref({
  name: '',
  min_price: null,
  max_price: null,
  tag_ids: []
})
const dishes = ref([])
const tags = ref([])
const loading = ref(false)
const varRadiusSm = 'var(--radius-sm)'
const canSearch = computed(() => !!(searchForm.value.name?.trim() || searchForm.value.tag_ids.length))

const fetchTags = async () => {
  const res = await getTags()
  if (res && res.data) tags.value = res.data
}

const fetchDishes = async () => {
  loading.value = true
  const params = {}
  if (searchForm.value.name?.trim()) params.search = searchForm.value.name.trim()
  if (searchForm.value.min_price) params.min_price = searchForm.value.min_price
  if (searchForm.value.max_price) params.max_price = searchForm.value.max_price
  if (searchForm.value.tag_ids.length) params.tag_ids = searchForm.value.tag_ids
  const res = await getDishes(params)
  if (res && res.data) dishes.value = res.data
  loading.value = false
}

function onSearch() {
  if (!canSearch.value) return
  fetchDishes()
}
function goToDish(id) {
  router.push({ name: 'DishDetail', params: { id } })
}

onMounted(() => {
  fetchTags()
  // 侧边栏 q 默认作为菜品名搜索
  if (route.query.q) {
    searchForm.value.name = String(route.query.q)
    fetchDishes()
  }
})
</script>

<style scoped>
.back-btn {
  margin-bottom: 18px;
}
.search-form {
  margin-bottom: 24px;
}
.dish-list-wrap {
  margin-top: 16px;
}
.dish-card {
  cursor: pointer;
  margin-bottom: 24px;
  transition: box-shadow 0.2s;
  border-radius: var(--radius-sm);
  /* 保持圆角但不阻断滚动 */
  overflow: visible;
}
.dish-card:hover {
  box-shadow: var(--shadow-md);
}
.dish-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
}
.dish-info {
  padding: 10px 0 0 0;
}
.dish-title {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 6px;
}
.dish-tags {
  margin-bottom: 6px;
}
.dish-price {
  color: var(--color-accent);
  font-size: 16px;
  font-weight: bold;
}
</style>
