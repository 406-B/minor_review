<template>
  <PageContainer>
    <template #header><AppTopBar /></template>

    <div class="wrap">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <span>←</span>
            <span>返回</span>
          </button>
          <h2>个性化推荐</h2>
        </div>
      </div>
      <el-tabs v-model="active">
        <el-tab-pane label="按偏好推荐" name="pref">
          <RecommendList :loading="loading.pref" :dishes="data.pref.dishes" />
          <el-empty
            v-if="!loading.pref && (!data.pref.dishes || data.pref.dishes.length === 0)"
            description="暂无数据"
          />
        </el-tab-pane>
        <el-tab-pane label="按热度推荐" name="hot">
          <RecommendList :loading="loading.hot" :dishes="data.hot.dishes" />
          <el-empty
            v-if="!loading.hot && (!data.hot.dishes || data.hot.dishes.length === 0)"
            description="暂无数据"
          />
        </el-tab-pane>
        <el-tab-pane label="综合推荐" name="mix">
          <RecommendList :loading="loading.mix" :dishes="data.mix.dishes" />
          <el-empty
            v-if="!loading.mix && (!data.mix.dishes || data.mix.dishes.length === 0)"
            description="暂无数据"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import PageContainer from '@/components/ui/PageContainer.vue';
import AppTopBar from '@/components/ui/AppTopBar.vue';
import RecommendList from '@/components/RecommendList.vue';
import { getRecommendedDishes } from '@/api/profile';
import { getHotDishes } from '@/utils/api/listApi';

const route = useRoute();
const active = ref('pref');
const loading = ref({ pref: false, hot: false, mix: false });
const data = ref({ pref: { dishes: [] }, hot: { dishes: [] }, mix: { dishes: [] } });

const loadPref = async () => {
  loading.value.pref = true;
  try {
    const res = await getRecommendedDishes();
    data.value.pref = res?.data ?? res ?? { dishes: [] };
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) {
      // 可能是“未设置偏好标签”
      window.$message?.info?.('请先设置你的偏好标签，更精准哦');
      // 延迟片刻避免和 Tab 切换冲突
      setTimeout(() => {
        try {
          window?.appRouter?.push?.('/onboarding/tags');
        } catch (_) {}
      }, 50);
    } else {
      window.$message?.error?.(e?.message || '加载失败');
    }
  } finally {
    loading.value.pref = false;
  }
};

const loadHot = async () => {
  loading.value.hot = true;
  try {
    const res = await getHotDishes({ limit: 30 });
    const list = res?.data ?? res ?? [];
    data.value.hot = Array.isArray(list) ? { dishes: list } : list || { dishes: [] };
  } catch (e) {
    window.$message?.error?.(e?.message || '加载失败');
    data.value.hot = { dishes: [] };
  } finally {
    loading.value.hot = false;
  }
};

const loadMix = async () => {
  loading.value.mix = true;
  try {
    // 使用后端综合推荐结果，传递mode=mix参数，热度推荐和tag推荐各取0.5系数
    const res = await getRecommendedDishes({ mode: 'mix' });
    data.value.mix = res?.data ?? res ?? { dishes: [] };
  } catch (e) {
    const status = e?.response?.status;
    if (status === 404) {
      window.$message?.info?.('请先设置你的偏好标签，更精准哦');
      setTimeout(() => {
        try {
          window?.appRouter?.push?.('/onboarding/tags');
        } catch (_) {}
      }, 50);
    } else {
      window.$message?.error?.(e?.message || '加载失败');
    }
  } finally {
    loading.value.mix = false;
  }
};

// 位置推荐已下线，改用热度推荐

onMounted(() => {
  const t = route.query.tab;
  if (t === 'hot' || t === 'mix' || t === 'pref') active.value = t;
  if (active.value === 'pref') loadPref();
  if (active.value === 'hot') loadHot();
  if (active.value === 'mix') loadMix();
});

watch(active, (tab) => {
  if (tab === 'pref') loadPref();
  if (tab === 'hot') loadHot();
  if (tab === 'mix') loadMix();
});
</script>

<style scoped>
.wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text);
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--brand-50);
  border-color: var(--brand-200);
  color: var(--brand-600);
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--color-text);
}
.row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
}
.row.between {
  justify-content: space-between;
}
.hint {
  color: var(--color-muted);
}
</style>
