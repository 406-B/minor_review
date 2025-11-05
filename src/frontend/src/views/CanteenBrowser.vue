<template>
  <div class="canteen-browser">
    <CanteenSidebar
      :canteens="canteens"
      :active-canteen="activeCanteen"
      @update:active-canteen="onCanteenChange"
    />
    <div class="canteen-main">
      <CanteenFloors
        v-if="activeCanteen"
        :canteen-id="activeCanteen"
      />
      <div v-else class="empty-tip">请选择一个食堂</div>
    </div>
  </div>
</template>

<script setup>

import { getCanteens } from '../api/canteenApi'

const canteens = ref([])
const activeCanteen = ref('')


const fetchCanteens = async () => {
  // 使用 getCanteens API 获取食堂列表
  const res = await getCanteens()
  if (res && res.data) {
    canteens.value = res.data
    if (canteens.value.length > 0) {
      activeCanteen.value = canteens.value[0].id
    }
  }
}

function onCanteenChange(id) {
  activeCanteen.value = id
}

onMounted(fetchCanteens)
</script>

<style scoped>
.canteen-browser {
  display: flex;
  flex-direction: row;
  height: 100vh;
  background: #fff7ed;
}
.canteen-main {
  flex: 1 1 0;
  min-width: 0;
  padding: 32px;
  overflow-y: auto;
  background: #fff;
}
.empty-tip {
  color: #aaa;
  text-align: center;
  margin-top: 100px;
  font-size: 20px;
}
</style>
