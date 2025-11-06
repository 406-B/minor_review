<template>
  <div class="canteen-browser">
    <div class="top-bar">
      <div class="app-title">小众点评</div>
      <div class="nav-options">
  <span class="nav-item active" @click="$router.push('/canteen')">食堂浏览</span>
  <span class="nav-item" @click="$router.push('/community')">美食论坛</span>
      </div>
  <div class="user-profile-text" @click="$router.push('/profile')">个人主页</div>
    </div>
    <div style="display: flex; flex: 1 1 0; min-height: 0;">
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
  flex-direction: column;
}
.top-bar {
  width: 100vw;
  height: 60px;
  background: #fffbe6;
  border-bottom: 2px solid #ff9800;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 36px 0 32px;
  box-sizing: border-box;
  position: sticky;
  top: 0;
  z-index: 10;
}
.app-title {
  font-size: 2rem;
  color: #ff9800;
  font-weight: bold;
  letter-spacing: 6px;
  user-select: none;
}
.nav-options {
  display: flex;
  gap: 32px;
  margin-left: 40px;
}
.nav-item {
  font-size: 1.1rem;
  color: #666;
  cursor: pointer;
  padding: 6px 18px;
  border-radius: 18px;
  transition: background 0.18s, color 0.18s;
  user-select: none;
}
.nav-item.active,
.nav-item:hover {
  background: #ffecb3;
  color: #ff9800;
}
.user-profile-text {
  margin-left: auto;
  font-size: 1.1rem;
  color: #ff9800;
  font-weight: bold;
  padding: 6px 18px;
  border-radius: 18px;
  background: #fffbe6;
  user-select: none;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.user-profile-text:hover {
  background: #ffecb3;
  color: #fb8c00;
}
.canteen-main {
  flex: 1 1 0;
  min-width: 0;
  padding: 32px 48px 32px 48px;
  overflow-y: auto;
  background: #fff;
  height: calc(100vh - 60px);
  min-height: calc(100vh - 60px);
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
