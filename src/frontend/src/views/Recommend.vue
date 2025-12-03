<template>
  <PageContainer>
    <template #header><AppTopBar /></template>

    <div class="wrap">
      <h2 class="title">个性化推荐</h2>
      <el-tabs v-model="active">
        <el-tab-pane label="按偏好推荐" name="pref">
          <RecommendList :loading="loading.pref" :dishes="data.pref.dishes"/>
          <el-empty v-if="!loading.pref && (!data.pref.dishes || data.pref.dishes.length===0)" description="暂无数据" />
        </el-tab-pane>
        <el-tab-pane label="按位置推荐" name="geo">
          <div class="row">
            <el-button type="primary" @click="locate" :loading="geo.loading">获取当前位置</el-button>
            <span class="hint" v-if="geo.pos">纬度 {{ geo.pos.lat.toFixed(5) }}, 经度 {{ geo.pos.lng.toFixed(5) }}</span>
          </div>
          <RecommendList :loading="loading.geo" :dishes="data.geo.dishes"/>
          <el-empty v-if="!loading.geo && (!data.geo.dishes || data.geo.dishes.length===0)" description="暂无数据" />
        </el-tab-pane>
        <el-tab-pane label="综合推荐" name="mix">
          <RecommendList :loading="loading.mix" :dishes="data.mix.dishes"/>
          <el-empty v-if="!loading.mix && (!data.mix.dishes || data.mix.dishes.length===0)" description="暂无数据" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </PageContainer>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import RecommendList from '@/components/RecommendList.vue'
import { getRecommendedDishes, getNearbyRecommendedDishes } from '@/api/profile'

const route = useRoute()
const active = ref('pref')
const loading = ref({ pref: false, geo: false, mix: false })
const data = ref({ pref: { dishes: [] }, geo: { dishes: [] }, mix: { dishes: [] } })
const geo = ref({ loading: false, pos: null })

const loadPref = async () => {
  loading.value.pref = true
  try {
    const res = await getRecommendedDishes()
    data.value.pref = res?.data ?? res ?? { dishes: [] }
  } catch (e) {
    const status = e?.response?.status
    if (status === 404) {
      // 可能是“未设置偏好标签”
      window.$message?.info?.('请先设置你的偏好标签，更精准哦')
      // 延迟片刻避免和 Tab 切换冲突
      setTimeout(() => {
        try { window?.appRouter?.push?.('/onboarding/tags') } catch (_) {}
      }, 50)
    } else {
      window.$message?.error?.(e?.message || '加载失败')
    }
  } finally {
    loading.value.pref = false
  }
}

const loadGeo = async () => {
  if (!geo.value.pos) return
  loading.value.geo = true
  try {
    const res = await getNearbyRecommendedDishes({ latitude: geo.value.pos.lat, longitude: geo.value.pos.lng })
    data.value.geo = res?.data ?? res ?? { dishes: [] }
  } catch (e) {
    const status = e?.response?.status
    if (status === 404) {
      window.$message?.info?.('附近暂无可用食堂位置信息')
      data.value.geo = { dishes: [] }
    } else {
      window.$message?.error?.(e?.message || '加载失败')
    }
  } finally {
    loading.value.geo = false
  }
}

const loadMix = async () => {
  loading.value.mix = true
  try {
    if (geo.value.pos) {
      const res = await getRecommendedDishes({ latitude: geo.value.pos.lat, longitude: geo.value.pos.lng })
      data.value.mix = res?.data ?? res ?? { dishes: [] }
    } else {
      const res = await getRecommendedDishes()
      data.value.mix = res?.data ?? res ?? { dishes: [] }
    }
  } catch (e) {
    const status = e?.response?.status
    if (status === 404) {
      window.$message?.info?.('请先设置你的偏好标签，更精准哦')
      setTimeout(() => { try { window?.appRouter?.push?.('/onboarding/tags') } catch (_) {} }, 50)
    } else {
      window.$message?.error?.(e?.message || '加载失败')
    }
  } finally {
    loading.value.mix = false
  }
}

const locate = () => {
  geo.value.loading = true
  if (!('geolocation' in navigator)) {
    geo.value.loading = false
    window.$message?.error?.('浏览器不支持定位')
    return
  }
  navigator.geolocation.getCurrentPosition((pos) => {
    geo.value.pos = { lat: pos.coords.latitude, lng: pos.coords.longitude }
    geo.value.loading = false
    loadGeo()
    if (active.value === 'mix') loadMix()
  }, () => {
    geo.value.loading = false
    window.$message?.error?.('无法获取定位权限')
  })
}

onMounted(() => {
  const t = route.query.tab
  if (t === 'geo' || t === 'mix' || t === 'pref') active.value = t
  if (active.value === 'pref') loadPref()
  if (active.value === 'geo') locate()
  if (active.value === 'mix') loadMix()
})

watch(active, (tab) => {
  if (tab === 'pref') loadPref()
  if (tab === 'geo') loadGeo()
  if (tab === 'mix') loadMix()
})
</script>

<style scoped>
.wrap { max-width: 960px; margin: 0 auto; padding: 8px 0 }
.title { margin: 8px 0 12px }
.row { display:flex; align-items:center; gap:8px; margin: 8px 0 }
.row.between { justify-content: space-between }
.hint { color: var(--color-muted) }
</style>
