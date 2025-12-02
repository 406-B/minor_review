<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
  <ProfileInfo :user="user" />

  <!-- 偏好标签展示 -->
  <div class="pref-tags" v-if="user && user.preference_tags">
    <span class="label">我的偏好：</span>
    <template v-if="user.preference_tags.length">
      <el-tag
        v-for="t in user.preference_tags"
        :key="t.id"
        size="small"
        class="mr8"
      >{{ t.name }}</el-tag>
      <el-button link type="primary" @click="editTags">修改偏好</el-button>
    </template>
    <template v-else>
      <span class="hint">你还没有设置偏好标签</span>
      <el-button link type="primary" @click="editTags">去设置</el-button>
    </template>
  </div>

  <!-- 已发布与 我的互动 同行 -->
  <div class="grid top-grid">
      <div class="col left">
  <SectionCard class="equal-card" title="已发布内容">
          <template #actions>
            <button class="link" @click.prevent="viewAllPublished">查看全部</button>
          </template>
          <template #content>
            <div class="posts">
              <PostItem
                v-for="p in published"
                :key="p.id"
                :post="p"
                :showStats="false"
              />
              <p v-if="(!published || published.length === 0)" class="empty">暂无已发布内容</p>
            </div>
          </template>
        </SectionCard>
      </div>

      <div class="col right">
  <SectionCard class="equal-card" title="我的互动">
          <template #content>
            <div class="interactions">
              <InteractionStat
                v-for="(it, i) in interactions"
                :key="i"
                :name="it.name"
                :count="it.count"
                :to="it.to"
                @navigate="onNavigate"
              />
            </div>
            <p v-if="loading" class="hint">加载中...</p>
          </template>
        </SectionCard>
      </div>
    </div>

    <!-- 个性化推荐入口（与上面两卡同风格） -->
    <div class="grid recommend-grid">
      <div class="col">
        <SectionCard class="equal-card" title="个性化推荐">
          <template #actions>
            <el-select v-model="recoSource" size="small" style="width: 120px; margin-right: 8px">
              <el-option label="综合" value="mix" />
              <el-option label="偏好" value="pref" />
              <el-option label="位置" value="geo" />
            </el-select>
            <button class="link" @click.prevent="viewAllRecommend">查看全部</button>
          </template>
          <template #content>
            <div v-if="reco.dishes && reco.dishes.length" class="slider" @mouseenter="pauseAuto" @mouseleave="resumeAuto">
              <button v-if="pages.length > 1" class="nav prev" type="button" @click="onPrev" aria-label="上一页">‹</button>
              <div class="slides" ref="slidesRef" :style="slidesStyle" @transitionend="onTransitionEnd">
                <div class="page" v-for="(page, i) in extendedPages" :key="'p-'+i">
                  <div v-for="d in page" :key="d.id" class="dish-card" @click="goDish(d.id)">
                    <div class="thumb">
                      <el-image :src="imageUrl(d.image)" fit="cover">
                        <template #error>
                          <div class="thumb placeholder">{{ d.name?.[0] || '图' }}</div>
                        </template>
                      </el-image>
                    </div>
                    <div class="dish-name" :title="d.name">{{ d.name }}</div>
                  </div>
                </div>
              </div>
              <button v-if="pages.length > 1" class="nav next" type="button" @click="onNext" aria-label="下一页">›</button>
              <div v-if="pages.length > 1" class="dots">
                <span v-for="(p, i) in pages" :key="'d-'+i" class="dot" :class="{ active: i === activeDot }" @click="goToPage(i)" />
              </div>
            </div>
            <el-empty v-else description="暂无推荐数据" />
          </template>
        </SectionCard>
      </div>
    </div>
    <!-- 控制组件板块（在底部） -->
    <ControlPanel />
  </PageContainer>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getRecommendedDishes, getNearbyRecommendedDishes } from '@/api/profile'
import { getProfileSections } from '@/api/profile'
import { getMyPosts, getUserStats } from '@/api/community'
// Local components
import AppTopBar from '@/components/ui/AppTopBar.vue'
import PageContainer from '@/components/ui/PageContainer.vue'
import ProfileInfo from '@/components/ProfileInfo.vue'
import PostItem from '@/components/PostItem.vue'
import SectionCard from '@/components/SectionCard.vue'
import InteractionStat from '@/components/InteractionStat.vue'
import ControlPanel from '@/components/ControlPanel.vue'

const router = useRouter()
const published = ref([])
const interactions = ref([])
const user = ref({})
const loading = ref(false)
const hasTags = computed(() => Array.isArray(user.value?.preference_tags) && user.value.preference_tags.length > 0)
const reco = ref({ dishes: [] })
const recoSource = ref('mix')
const geoPos = ref(null)
let autoTimer = null
const slideIndex = ref(1) // 使用首尾克隆，初始为第1个真实页
const transitioning = ref(true)
const slidesRef = ref(null)

const imageUrl = (src) => {
  if (!src) return '/favicon.ico'
  if (/^(https?:|data:|blob:)/.test(src)) return src
  if (src.startsWith('/media/')) return src
  return src.startsWith('/') ? src : '/media/' + src
}

const pages = computed(() => {
  const arr = reco.value?.dishes || []
  const size = 3
  const out = []
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size))
  return out
})

const extendedPages = computed(() => {
  const p = pages.value
  if (!p.length) return []
  if (p.length === 1) return p
  return [p[p.length - 1], ...p, p[0]]
})

const activeDot = computed(() => {
  if (!pages.value.length) return 0
  // slideIndex: 0..N+1; 真实页索引: slideIndex-1
  let idx = slideIndex.value - 1
  if (idx < 0) idx = pages.value.length - 1
  if (idx >= pages.value.length) idx = 0
  return idx
})

const slidesStyle = computed(() => ({
  transform: `translateX(-${(pages.value.length > 1 ? slideIndex.value : 0) * 100}%)`,
  transition: transitioning.value ? 'transform .25s ease-out' : 'none'
}))

const startAuto = () => {
  stopAuto()
  if (pages.value.length <= 1) return
  autoTimer = setInterval(() => {
    onNext()
  }, 3000)
}
const stopAuto = () => { if (autoTimer) { clearInterval(autoTimer); autoTimer = null } }
const pauseAuto = () => stopAuto()
const resumeAuto = () => startAuto()

const onNext = () => {
  if (pages.value.length <= 1) return
  transitioning.value = true
  slideIndex.value += 1
}
const onPrev = () => {
  if (pages.value.length <= 1) return
  transitioning.value = true
  slideIndex.value -= 1
}
const onTransitionEnd = () => {
  const n = pages.value.length
  if (!n) return
  // 尾部克隆 -> 跳回首个真实页
  if (slideIndex.value === n + 1) {
    transitioning.value = false
    slideIndex.value = 1
    nextTick(() => {
      try { void (slidesRef.value && slidesRef.value.offsetWidth) } catch {}
      requestAnimationFrame(() => { transitioning.value = true })
    })
  }
  // 头部克隆 -> 跳回最后一个真实页
  if (slideIndex.value === 0) {
    transitioning.value = false
    slideIndex.value = n
    nextTick(() => {
      try { void (slidesRef.value && slidesRef.value.offsetWidth) } catch {}
      requestAnimationFrame(() => { transitioning.value = true })
    })
  }
}
const goToPage = (i) => {
  if (i < 0 || i >= pages.value.length) return
  pauseAuto()
  transitioning.value = true
  slideIndex.value = i + 1
  resumeAuto()
}

const load = async () => {
  loading.value = true
  try {
    // 获取个人资料和基础数据
    const res = await getProfileSections()
    user.value = res.user || {}
    
    // 获取用户统计信息
    let receivedCommentsCount = 0
    try {
      const stats = await getUserStats()
      
      // 获取我的帖子列表以统计收到的评论数
      try {
        const postsRes = await getMyPosts(1, 100) // 获取更多帖子以准确统计
        if (postsRes.code === 200 && postsRes.data) {
          // 计算所有帖子收到的评论总数
          receivedCommentsCount = (postsRes.data.posts || []).reduce((sum, post) => {
            return sum + (post.comments_count || 0)
          }, 0)
          
          // 设置已发布内容列表（只显示前5条）
          published.value = (postsRes.data.posts || []).slice(0, 5).map(post => ({
            id: post.id,
            title: post.subject || '无标题', // 直接使用 subject 字段
            createdAt: formatTime(post.created_at)
          }))
        }
      } catch (err) {
        console.error('获取我的帖子失败:', err)
      }
      
      // 设置交互统计数据
      interactions.value = [
        { name: '我点赞的帖子', count: stats.liked_posts_count || 0, to: '/community' },
        { name: '我收到的评论', count: receivedCommentsCount, to: '/community' },
        { name: '我发布的评论', count: stats.commented_posts_count || 0, to: '/community' }
      ]
    } catch (err) {
      console.error('获取用户统计失败:', err)
      // 使用默认值
      interactions.value = [
        { name: '我点赞的帖子', count: 0, to: '/community' },
        { name: '我收到的评论', count: 0, to: '/community' },
        { name: '我发布的评论', count: 0, to: '/community' }
      ]
      published.value = res.published || []
    }
  } catch (e) {
    console.error('加载个人主页数据失败', e)
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  // 先加载用户信息（用于 hasTags 之类的判定）
  await load()
  // 再加载推荐
  await loadRecommendMix()
  // 初始到首个真实页：仅1页时用0，多页时用1（因首尾克隆）
  slideIndex.value = pages.value.length > 1 ? 1 : 0
  startAuto()
})
onUnmounted(() => stopAuto())

const viewAllPublished = () => {
  router.push('/profile/posts')
}

const onNavigate = (to) => {
  router.push(to)
}

const openRecommend = (tab) => {
  if (!hasTags.value && (tab === 'pref' || tab === 'mix')) {
    window.$message?.info?.('先设置你的偏好标签，更精准哦')
    router.push('/onboarding/tags')
  } else {
    router.push({ path: '/recommend', query: { tab } })
  }
}

const editTags = () => router.push('/onboarding/tags')
const goDish = (id) => router.push(`/dish/${id}`)
const viewAllRecommend = () => router.push({ path: '/recommend', query: { tab: recoSource.value } })

const loadRecommendPref = async () => {
  try {
    const res = await getRecommendedDishes()
    reco.value = res?.data ?? res ?? { dishes: [] }
  } catch (err) {
    // 无偏好标签时后端返回 404，尝试位置推荐作为回退
    if (err?.response?.status === 404) {
      const ok = await ensureGeo()
      if (ok) { await loadRecommendGeo(); return }
      window.$message?.info?.('请先设置偏好标签，或开启定位获取附近推荐')
    }
    reco.value = { dishes: [] }
  }
}
const loadRecommendMix = async () => {
  try {
    // 尝试带定位的综合推荐（若可用）
    if (!geoPos.value) { await ensureGeo() }
    const params = geoPos.value ? { latitude: geoPos.value.lat, longitude: geoPos.value.lng } : undefined
    const res = await getRecommendedDishes(params)
    reco.value = res?.data ?? res ?? { dishes: [] }
  } catch (err) {
    if (err?.response?.status === 404) {
      // 用户未设置偏好标签 -> 回退到附近推荐
      const ok = await ensureGeo()
      if (ok) { await loadRecommendGeo(); return }
      window.$message?.info?.('请先设置偏好标签，或开启定位获取附近推荐')
    }
    reco.value = { dishes: [] }
  }
}
const loadRecommendGeo = async () => {
  if (!geoPos.value) return
  try {
    const res = await getNearbyRecommendedDishes({ latitude: geoPos.value.lat, longitude: geoPos.value.lng })
    reco.value = res?.data ?? res ?? { dishes: [] }
  } catch { reco.value = { dishes: [] } }
}

const ensureGeo = () => new Promise((resolve) => {
  if (geoPos.value) return resolve(true)
  if (!('geolocation' in navigator)) return resolve(false)
  navigator.geolocation.getCurrentPosition((pos) => {
    geoPos.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
    resolve(true)
  }, () => resolve(false))
})

watch(recoSource, async (v) => {
  if (v === 'pref') await loadRecommendPref()
  if (v === 'mix') await loadRecommendMix()
  if (v === 'geo') {
    const ok = await ensureGeo()
    if (ok) await loadRecommendGeo(); else { reco.value = { dishes: [] }; window.$message?.info?.('无法获取定位') }
  }
})

watch(() => reco.value?.dishes, () => {
  slideIndex.value = pages.value.length > 1 ? 1 : 0
  startAuto()
}, { deep: true })

</script>

<style scoped>
.title { font-size: 1.4rem; margin-bottom: 0.75rem }
.grid { display: grid; grid-template-columns: 1fr; gap: 1rem; margin-top: 1rem }
.recommend-grid { grid-template-columns: 1fr; }
.col { display: flex; flex-direction: column; gap: 1rem }
/* 让列内的卡片等高 */
.equal-card { height: 100%; min-height: 220px; display: flex; flex-direction: column }
.equal-card :deep(.content) { flex: 1; display: flex; flex-direction: column }

/* 推荐卡片自适应内容高度，避免多余留白 */
.recommend-grid .equal-card { min-height: auto; }

.posts { list-style: none; padding: 0; margin: 0; max-height: 380px; overflow: auto }
.post { padding: 0.5rem 0; border-bottom: 1px dashed rgba(0,0,0,0.04) }
.post-title { font-weight: 600 }
.post-meta { font-size: 0.85rem; color: var(--color-muted) }
.interactions { display: flex; flex-wrap: wrap }
.hint { color: var(--color-muted); font-size: 0.85rem; margin-top: 0.5rem }
.link { background: none; border: none; color: var(--color-accent); cursor: pointer }
.reco-entry { margin-top: 16px; display: flex; justify-content: center }
.pref-tags { margin-top: 12px; display:flex; align-items:center; flex-wrap: wrap; gap: 8px }
.pref-tags .label { color: var(--color-muted) }
.mr8 { margin-right: 8px }

/* 推荐小卡片布局适配等高容器 */
.reco-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px }
.reco-cards.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.reco-card { display:flex; align-items:center; gap:10px; min-height: 76px; border: 1px solid rgba(0,0,0,0.08); border-radius: 10px; padding: 12px 14px; cursor: pointer; background: #f8fbf8; transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease }
.reco-card .icon { width: 36px; height: 36px; display:flex; align-items:center; justify-content:center; border-radius: 10px; font-size: 18px }
.reco-card .info { flex: 1; min-width: 0 }
.reco-card.pref { background: #f3fbf5; border-color: #bfe8c9 }
.reco-card.pref .icon { background:#c8f1d3 }
.reco-card.geo { background: #f3f8ff; border-color: #c6dbff }
.reco-card.geo .icon { background:#d6e6ff }
.reco-card.mix { background: #fff7f3; border-color: #ffd9c6 }
.reco-card.mix .icon { background:#ffe6d9 }
.reco-card:hover { border-color: var(--color-accent); box-shadow: 0 4px 14px rgba(0,0,0,0.08); transform: translateY(-1px) }
.reco-title { font-weight: 600; margin-bottom: 4px }
.reco-desc { font-size: 12px; color: var(--color-muted) }

.slider { position: relative; overflow: hidden }
.slides { display: flex; width: 100%; will-change: transform }
.page { min-width: 100%; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding: 6px 0 }

/* 导航按钮 */
.nav { position: absolute; top: 50%; transform: translateY(-50%); z-index: 3; width: 32px; height: 32px; border-radius: 50%; border: 1px solid rgba(0,0,0,0.08); background: rgba(255,255,255,0.9); color: #333; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: background .15s ease, box-shadow .15s ease }
.nav:hover { background: #fff; box-shadow: 0 4px 14px rgba(0,0,0,0.12) }
.nav.prev { left: 6px }
.nav.next { right: 6px }

/* 指示点 */
.dots { position: absolute; left: 0; right: 0; bottom: 4px; display: flex; gap: 6px; justify-content: center; z-index: 2 }
.dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(0,0,0,0.18); cursor: pointer; transition: background .15s ease, transform .15s ease }
.dot.active { background: var(--color-accent); transform: scale(1.1) }

.dish-card { width: 100%; cursor: pointer; border: 1px solid rgba(0,0,0,0.06); border-radius: 10px; padding: 8px; background: #fff; transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease }
.thumb { width: 100%; height: 96px; border-radius: 8px; overflow: hidden; background: #f4f6f8; transition: transform .22s ease }
.thumb :deep(img), .thumb :deep(.el-image__inner) { width: 100%; height: 100%; object-fit: cover }
.thumb.placeholder { display:flex; align-items:center; justify-content:center; color:#999; font-weight:600; font-size: 20px }
.dish-name { margin-top: 6px; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.dish-card:hover { border-color: var(--color-accent); box-shadow: 0 8px 22px rgba(0,0,0,0.10); transform: translateY(-2px); position: relative; z-index: 2 }
.dish-card:hover .thumb { transform: scale(1.03) }

@media (min-width: 1024px) {
  .grid { grid-template-columns: 1fr 1fr }
  .recommend-grid { grid-template-columns: 1fr 1fr; justify-items: center; }
  .recommend-grid .col { width: 100%; max-width: 680px; }
  /* 限制上方两张卡片的最大宽度，减少卡内留白 */
  .top-grid { justify-items: center; }
  .top-grid .col { width: 100%; max-width: 680px; }
  /* 固定等高：两列时卡片充满列高 */
  .col { align-items: stretch }
  .equal-card { height: 100%; min-height: 240px }
  .posts { max-height: 460px }
}
</style>
