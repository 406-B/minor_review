<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>

    <div class="achievements-detail">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <span>←</span>
            <span>返回</span>
          </button>
          <h2>我的成就</h2>
        </div>
      </div>
      
      <SectionCard>
        <template #content>
        <div class="tabs-wrap">
          <el-tabs v-model="activeTab" @tab-change="onTabChange">
            <el-tab-pane label="全部" name="all" />
            <el-tab-pane label="本科" name="bronze" />
            <el-tab-pane label="硕士" name="silver" />
            <el-tab-pane label="博士" name="gold" />
            <el-tab-pane label="院士" name="rainbow" />
          </el-tabs>
        </div>

        <div v-if="loading" class="hint">加载中...</div>
        <div v-else>
          <div v-if="filtered.length" class="grid-list">
            <div
              v-for="it in filtered"
              :key="it.dish"
              class="achi-item"
              @click="goDish(it.dish)"
            >
              <AchievementImage
                :dish-id="it.dish"
                :src="imageUrl(it.dish_image)"
                :width="'100%'"
                :height="120"
                :radius="10"
              />
              <div class="meta">
                <div class="name" :title="it.dish_name || `菜品 #${it.dish}`">{{ it.dish_name || `菜品 #${it.dish}` }}</div>
                <div class="sub">打卡：{{ it.count }}</div>
                <div class="progress" v-if="progressOf(it.count).next">
                  <div class="bar">
                    <div class="fill" :style="{ width: progressOf(it.count).percent + '%' }" />
                  </div>
                  <div class="progress-text">{{ it.count }} / {{ progressOf(it.count).next }}</div>
                </div>
                <div class="progress done" v-else>
                  <div class="progress-text">已满级</div>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </div>
      </template>
    </SectionCard>    </div>  </PageContainer>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PageContainer from '@/components/ui/PageContainer.vue'
import SectionCard from '@/components/SectionCard.vue'
import AchievementImage from '@/components/common/AchievementImage.vue'
import { ensureAchievementsLoaded, getAchievementByCount } from '@/utils/achievements'
import { getUserDishHistory } from '@/utils/api/listApi'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const items = ref([])
const activeTab = ref(route.query.tab && ['all','bronze','silver','gold','rainbow'].includes(route.query.tab) ? route.query.tab : 'all')

function imageUrl(src) {
  if (!src) return '/favicon.ico'
  if (/^(https?:|data:|blob:)/.test(src)) return src
  if (src.startsWith('/media/')) return src
  return src.startsWith('/') ? src : '/media/' + src
}

const filtered = computed(() => {
  if (!items.value?.length) return []
  if (activeTab.value === 'all') return items.value
  return items.value.filter(it => getAchievementByCount(it.count).key === activeTab.value)
})

const thresholds = [1, 3, 10, 100]
function nextThreshold(count) {
  for (const t of thresholds) { if (count < t) return t }
  return null
}
function progressOf(count) {
  const next = nextThreshold(count)
  if (!next) return { next: null, percent: 100 }
  const percent = Math.max(0, Math.min(100, Math.round((count / next) * 100)))
  return { next, percent }
}

async function load() {
  loading.value = true
  try {
    await ensureAchievementsLoaded()
    const res = await getUserDishHistory({ page_size: 1000, ordering: '-count' })
    const list = Array.isArray(res?.data?.histories) ? res.data.histories : []
    items.value = list.map(h => ({
      dish: Number(h?.dish),
      count: Number(h?.count) || 0,
      dish_image: h?.dish_image || h?.image || '',
      dish_name: h?.dish_name || h?.name || ''
    }))
  } catch (e) {
    console.error('加载成就失败', e)
    items.value = []
  } finally {
    loading.value = false
  }
}

function onTabChange(name) {
  // 同步到 URL
  router.replace({ query: { ...route.query, tab: name } })
}

function goDish(id) { router.push(`/dish/${id}`) }

watch(() => route.query.tab, (v) => {
  if (!v) return
  if (['all','bronze','silver','gold','rainbow'].includes(v)) activeTab.value = v
})

onMounted(load)
</script>

<style scoped>
.tabs-wrap { margin-bottom: 8px }
.grid-list { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px }
.achi-item { cursor: pointer; border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; padding: 8px; background: #fff; transition: box-shadow .15s ease, transform .15s ease }
.achi-item:hover { box-shadow: 0 8px 22px rgba(0,0,0,0.10); transform: translateY(-2px) }
.meta { margin-top: 6px }
.name { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.sub { font-size: 12px; color: var(--color-muted) }
/* 进度条样式 */
.progress { margin-top: 6px; display: flex; align-items: center; gap: 8px }
.progress .bar { flex: 1; height: 6px; background: #eef0f3; border-radius: 999px; overflow: hidden }
.progress .fill { height: 100%; background: linear-gradient(90deg, var(--color-accent), #8bd2ff); border-radius: 999px; transition: width .25s ease }
.progress .progress-text { font-size: 12px; color: #666; white-space: nowrap }
.progress.done .progress-text { color: var(--color-accent) }
@media (max-width: 1024px) { .grid-list { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
