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
            <ul class="dish-list">
              <li v-for="dish in window.dishes" :key="dish.id" class="dish-item" @click="goToDish(dish.id)">
                <img v-if="dish.image" :src="dish.image" alt="菜品图片" class="dish-thumb" />
                <span class="dish-name">{{ dish.name }}</span>
                <span class="dish-price">￥{{ dish.price }}</span>
              </li>
            </ul>
import { useRouter } from 'vue-router'
const router = useRouter()

function goToDish(id) {
  router.push({ name: 'DishDetail', params: { id } })
}
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>

import { getCanteenFloors } from '../api/canteenApi'

const props = defineProps({
  canteenId: {
    type: String,
    required: true
  }
})

const floors = ref([])
const activeFloor = ref('')


const fetchFloors = async () => {
  // 使用 getCanteenFloors API 获取楼层和窗口
  const res = await getCanteenFloors(props.canteenId)
  if (res && res.data) {
    floors.value = res.data
    if (floors.value.length > 0) {
      activeFloor.value = floors.value[0].id
    }
  }
}

watch(() => props.canteenId, fetchFloors, { immediate: true })
</script>

<style scoped>
.canteen-floors {
  width: 100%;
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
}
.window-title {
  font-weight: bold;
  color: orange;
  margin-bottom: 8px;
}
.dish-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.dish-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  cursor: pointer;
  border-bottom: 1px dashed #ffe0b2;
  transition: background 0.15s;
}
.dish-item:last-child {
  border-bottom: none;
}
.dish-item:hover {
  background: #fff3e0;
}
.dish-thumb {
  width: 48px;
  height: 36px;
  object-fit: cover;
  border-radius: 4px;
  box-shadow: 0 1px 4px #ff980033;
}
.dish-name {
  font-weight: 500;
  color: #333;
  font-size: 16px;
}
.dish-price {
  color: #ff9800;
  margin-left: auto;
  font-weight: bold;
}
</style>
