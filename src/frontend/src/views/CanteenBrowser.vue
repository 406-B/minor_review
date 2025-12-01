<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="canteen-layout">
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
        <EmptyState v-else text="请选择一个食堂" />
      </div>
    </div>
  </PageContainer>
</template>

<script setup>
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PageContainer from '@/components/ui/PageContainer.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
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
/* 主体双栏布局 */
.canteen-layout {
  display: flex;
  align-items: stretch;
  gap: 0;
  min-height: calc(100vh - 60px - 48px); /* 减去顶部栏与容器上下 padding 估算 */
}
.canteen-main {
  flex: 1 1 0;
  min-width: 0;
  padding: 24px 32px 40px 32px;
  overflow-y: auto;
}
@media (max-width: 940px) {
  .canteen-layout { flex-direction: column; }
  .canteen-main { padding: 20px 20px 32px 20px; }
}
</style>
