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


import CanteenSidebar from '../components/CanteenSidebar.vue'
import CanteenFloors from '../components/CanteenFloors.vue'
import { ref, onMounted } from 'vue'
import { getCanteens } from '@/utils/api/listApi'

const canteens = ref([])
const activeCanteen = ref('')


const fetchCanteens = async () => {
  // 使用 getCanteens API 获取食堂列表
  const res = await getCanteens()
  if (res && res.data) {
    canteens.value = res.data
    if (canteens.value.length > 0) {
      activeCanteen.value = String(canteens.value[0].id)
    }
  }
}

function onCanteenChange(id) {
  activeCanteen.value = String(id)
}

onMounted(fetchCanteens)
</script>

<style scoped>
.canteen-browser {
  display: flex;
  flex-direction: row;
  height: 100vh;
  min-height: 100vh;
  width: 100vw;
  background: #f7f7f7;
  justify-content: center;
  align-items: stretch;
}
.canteen-main {
  flex: 1 1 0;
  min-width: 0;
  padding: 32px 48px 32px 48px;
  overflow-y: auto;
  background: #fff;
  height: 100vh;
  min-height: 100vh;
  box-shadow: 0 0 24px #e0e0e0aa;
  border-radius: 0;
  max-width: 1600px;
  margin: 0 auto;
}
.empty-tip {
  color: #aaa;
  text-align: center;
  margin-top: 120px;
  font-size: 22px;
}
</style>
