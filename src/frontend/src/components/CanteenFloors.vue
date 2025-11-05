<template>
  <div class="canteen-floors">
    <el-tabs v-model="activeFloor" tab-position="top" type="card">
      <el-tab-pane
        v-for="floor in floors"
        :key="floor.id"
        :label="floor.name"
        :name="floor.id"
      >
        <div class="windows-list">
          <div
            v-for="window in floor.windows"
            :key="window.id"
            class="window-block"
          >
            <div class="window-title">{{ window.name }}</div>
            <div class="dish-card-list">
              <div v-for="dish in window.dishes" :key="dish.id" class="dish-card" @click="goToDish && goToDish(dish.id)">
                <img v-if="dish.image" :src="getImageUrl(dish.image)" alt="菜品图片" class="dish-card-img" />
                <div class="dish-card-info">
                  <div class="dish-card-name">{{ dish.name }}</div>
                  <div class="dish-card-price">￥{{ dish.price }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
function getImageUrl(image) {
  if (!image) return ''
  if (image.startsWith('http://') || image.startsWith('https://')) return image
  if (image.startsWith('/media/')) return image
  return '/media/' + image.replace(/^\/+/, '')
}


import { ref, watch } from 'vue'
import { getCanteenFloors } from '@/utils/api/listApi'
import { useRouter } from 'vue-router'

const props = defineProps({
  canteenId: {
    type: String,
    required: true
  }
})

const router = useRouter()

function goToDish(dishId) {
  router.push({ name: 'DishDetail', params: { id: dishId } })
}

const floors = ref([])
const activeFloor = ref('')


const fetchFloors = async () => {
  try {
    const res = await getCanteenFloors(props.canteenId)
    if (res && Array.isArray(res.data)) {
      floors.value = res.data
      if (floors.value.length > 0) {
        activeFloor.value = floors.value[0].id
      }
    } else {
      floors.value = []
    }
  } catch (e) {
    floors.value = []
  }
}

watch(() => props.canteenId, fetchFloors, { immediate: true })
</script>

<style scoped>
.canteen-floors {
  width: 100%;
  min-height: calc(100vh - 64px);
  background: transparent;
}
.windows-list {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 16px;
}
.window-block {
  background: #fff7ed;
  border: 1px solid #ffe0b2;
  border-radius: 8px;
  padding: 16px;
  min-width: 220px;
  flex: 1 1 220px;
  box-shadow: 0 2px 8px #f5c16c22;
  transition: none;
}
.window-block:hover {
  /* 悬浮时无任何放大和阴影变化 */
  box-shadow: 0 2px 8px #f5c16c22;
  transform: none;
}
.window-title {
  font-weight: bold;
  color: orange;
  margin-bottom: 8px;
}

.dish-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  margin-top: 8px;
}
.dish-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #f5c16c22;
  padding: 16px 12px 12px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: box-shadow 0.18s, transform 0.18s;
  border: 1px solid #ffe0b2;
}
.dish-card:hover {
  box-shadow: 0 8px 32px #ff980033;
  transform: translateY(-2px) scale(1.03);
}
.dish-card-img {
  width: 100px;
  height: 72px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 1px 4px #ff980033;
  margin-bottom: 10px;
}
.dish-card-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.dish-card-name {
  font-weight: 500;
  color: #333;
  font-size: 16px;
  margin-bottom: 4px;
  text-align: center;
}
.dish-card-price {
  color: #ff9800;
  font-weight: bold;
  font-size: 15px;
  text-align: center;
}
@media (min-width: 900px) {
  .dish-card-list {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
