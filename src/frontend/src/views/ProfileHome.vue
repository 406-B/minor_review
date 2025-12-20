<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
    <div class="profile-wrap">
      <div class="profile-header">
        <!-- personal info card: always visible; when not authed show hint text on this card -->
        <div class="profile-info-card">
          <ProfileInfo v-if="isAuthed" :user="user" />
          <div v-else class="profile-info-placeholder">
            <div class="placeholder-title">个人主页</div>
            <div class="placeholder-text">登录以体验更多个性化内容，和社区成员一同探索美食世界！</div>
          </div>
        </div>
      </div>

    <!-- 偏好标签展示 -->
    <div class="pref-tags" v-if="user && user.preference_tags">
      <span class="label">我的偏好：</span>
      <template v-if="user.preference_tags.length">
        <el-tag v-for="t in user.preference_tags" :key="t.id" size="small" class="mr8">{{
          t.name
        }}</el-tag>
        <el-button link type="primary" @click="editTags">修改偏好</el-button>
      </template>
      <template v-else>
        <span class="hint">你还没有设置偏好标签</span>
        <el-button link type="primary" @click="editTags">去设置</el-button>
      </template>
    </div>

    <!-- 美食日历 -->
    
      <!-- blur overlay will be injected at end of profile-wrap -->
    <div class="col full-width">
      <SectionCard class="equal-card" title="美食日历">
        <template #actions>
            <button v-if="isAuthed" class="link" @click.prevent="viewFullCalendar">查看完整日历</button>
        </template>
        <template #content>
          <div class="card-content-wrap">
            <FoodCalendar :days="7" />
            <div v-if="!isAuthed" class="component-overlay"><div class="overlay-label">登录后查看详细内容</div></div>
          </div>
        </template>
      </SectionCard>
    </div>

    <!-- 已发布内容 与 我的互动 同行 -->
    <div class="grid top-grid">
      <div class="col left">
        <SectionCard class="equal-card" title="已发布内容">
          <template #actions>
            <button v-if="isAuthed" class="link" @click.prevent="viewAllPublished">查看全部</button>
          </template>
          <template #content>
            <div class="card-content-wrap">
              <div class="posts">
                <PostItem v-for="p in published" :key="p.id" :post="p" :showStats="false" />
                <p v-if="!published || published.length === 0" class="empty">暂无已发布内容</p>
              </div>
              <div v-if="!isAuthed" class="component-overlay"><div class="overlay-label">登录后查看详细内容</div></div>
            </div>
          </template>
        </SectionCard>
      </div>

      <div class="col right">
        <SectionCard class="equal-card" title="我的互动">
          <template #content>
            <div class="card-content-wrap">
              <div class="interactions">
                <InteractionStat
                  v-for="(it, i) in interactions"
                  :key="i"
                  :name="it.name"
                  :count="it.count"
                  :to="it.to"
                  @navigate="onNavigate"
                ></InteractionStat>
              </div>
              <p v-if="loading" class="hint">加载中...</p>
              <div v-if="!isAuthed" class="component-overlay"><div class="overlay-label">登录后查看详细内容</div></div>
            </div>
          </template>
        </SectionCard>
      </div>
    </div>

    <!-- 我的成就 与 个性化推荐 同行 -->
    <div class="grid middle-grid">
      <div class="col">
        <SectionCard class="equal-card" title="我的成就">
          <template #actions>
            <button v-if="isAuthed" class="link" @click.prevent="openAllAchievements">查看全部</button>
          </template>
          <template #content>
            <div class="card-content-wrap">
              <div class="achi-cards">
              <div class="achi-card bronze" @click="goAchievements('bronze')">
                <div class="icon" aria-hidden="true">🥉</div>
                <div class="achi-stack">
                  <div class="achi-count">{{ achiCounts.bronze }}</div>
                  <div class="achi-label">本科</div>
                </div>
              </div>
              <div class="achi-card silver" @click="goAchievements('silver')">
                <div class="icon" aria-hidden="true">🥈</div>
                <div class="achi-stack">
                  <div class="achi-count">{{ achiCounts.silver }}</div>
                  <div class="achi-label">硕士</div>
                </div>
              </div>
              <div class="achi-card gold" @click="goAchievements('gold')">
                <div class="icon" aria-hidden="true">🥇</div>
                <div class="achi-stack">
                  <div class="achi-count">{{ achiCounts.gold }}</div>
                  <div class="achi-label">博士</div>
                </div>
              </div>
              <div class="achi-card rainbow" @click="goAchievements('rainbow')">
                <div class="icon" aria-hidden="true">🏆</div>
                <div class="achi-stack">
                  <div class="achi-count">{{ achiCounts.rainbow }}</div>
                  <div class="achi-label">院士</div>
                </div>
              </div>
              </div>
              <div v-if="!isAuthed" class="component-overlay"><div class="overlay-label">登录后查看详细内容</div></div>
            </div>
          </template>
        </SectionCard>
      </div>

      <!-- 个性化推荐 -->
      <div class="col">
        <SectionCard class="equal-card" title="个性化推荐">
          <template #actions>
            <el-select v-if="isAuthed" v-model="recoSource" size="small" style="width: 120px; margin-right: 8px">
              <el-option label="综合" value="mix" />
              <el-option label="偏好" value="pref" />
              <el-option label="热度" value="hot" />
            </el-select>
            <button v-if="isAuthed" class="link" @click.prevent="viewAllRecommend">查看全部</button>
          </template>
          <template #content>
            <div class="card-content-wrap">
              <!-- 加载中文案占位 -->
              <div v-if="recoLoading" class="loading-placeholder">正在努力加载中（&gt;.&lt;）</div>
              <div
                v-else-if="reco.dishes && reco.dishes.length"
                class="slider"
                @mouseenter="pauseAuto"
                @mouseleave="resumeAuto"
              >
              <button
                v-if="pages.length > 1"
                class="nav prev"
                type="button"
                @click="onPrev"
                aria-label="上一页"
              >
              </button>
              <div
                class="slides"
                ref="slidesRef"
                :style="slidesStyle"
                @transitionend="onTransitionEnd"
              >
                <div class="page" v-for="(page, i) in extendedPages" :key="'p-' + i">
                  <div v-for="d in page" :key="d.id" class="dish-card" @click="goDish(d.id)">
                    <div class="thumb">
                      <AchievementImage
                        :dish-id="d.id"
                        :src="imageUrl(d.image)"
                        :width="'100%'"
                        :height="96"
                        :radius="8"
                      >
                        <template #placeholder>
                          <div class="thumb placeholder">{{ d.name?.[0] || '图' }}</div>
                        </template>
                      </AchievementImage>
                    </div>
                    <div class="dish-name" :title="d.name">{{ d.name }}</div>
                  </div>
                </div>
              </div>
              <button
                v-if="pages.length > 1"
                class="nav next"
                type="button"
                @click="onNext"
                aria-label="下一页"
              >
              </button>
              <div v-if="pages.length > 1" class="dots">
                <span
                  v-for="(p, i) in pages"
                  :key="'dot-' + i"
                  :class="['dot', { active: i === activeDot }]"
                  @click="goToPage(i)"
                  ></span>
              </div>
              </div>
            <el-empty v-else-if="recoFetched" description="暂无推荐数据" />
            <div v-if="!isAuthed" class="component-overlay"><div class="overlay-label">登录后查看详细内容</div></div>
            </div>
          </template>
        </SectionCard>
      </div>
    </div>

    <!-- 消费记录 -->
    <div class="grid bottom-grid">
      <div class="col left">
        <div class="card-content-wrap">
          <ConsumptionCard class="equal-card" />
          <div v-if="!isAuthed" class="component-overlay"><div class="overlay-label">登录后查看详细内容</div></div>
        </div>
      </div>
    </div>

    <!-- 控制组件板块（在底部） -->
    <ControlPanel />

    </div> <!-- .profile-wrap -->
  </PageContainer>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { getRecommendedDishes } from '@/api/profile';
import { getHotDishes } from '@/utils/api/listApi';
import { getProfileSections } from '@/api/profile';
import { getMyPosts, getUserStats } from '@/api/community';
// Local components
import AppTopBar from '@/components/ui/AppTopBar.vue';
import PageContainer from '@/components/ui/PageContainer.vue';
import ProfileInfo from '@/components/ProfileInfo.vue';
import PostItem from '@/components/PostItem.vue';
import SectionCard from '@/components/SectionCard.vue';
import InteractionStat from '@/components/InteractionStat.vue';
import ControlPanel from '@/components/ControlPanel.vue';
import AchievementImage from '@/components/common/AchievementImage.vue';
import {
  ensureAchievementsLoaded,
  getAllAchievements,
  getAchievementByCount,
  onAchievementsUpdated,
  offAchievementsUpdated,
} from '@/utils/achievements';
import ConsumptionCard from '@/components/ConsumptionCard.vue';
import FoodCalendar from '@/components/FoodCalendar.vue';

const router = useRouter();
const isAuthed = computed(() => !!localStorage.getItem('jwt'));
const goLogin = () => router.push('/login');
const published = ref([]);
const interactions = ref([]);
const user = ref({});
const loading = ref(false);
const hasTags = computed(
  () => Array.isArray(user.value?.preference_tags) && user.value.preference_tags.length > 0
);
const reco = ref({ dishes: [] });
const recoFetched = ref(false);
const recoSource = ref('mix');
const recoLoading = ref(false);
const geoPos = ref(null);
let autoTimer = null;
const slideIndex = ref(1); // 使用首尾克隆，初始为第1个真实页
const transitioning = ref(true);
const slidesRef = ref(null);

const imageUrl = (src) => {
  if (!src) return '/favicon.ico';
  if (/^(https?:|data:|blob:)/.test(src)) return src;
  if (src.startsWith('/media/')) return src;
  return src.startsWith('/') ? src : '/media/' + src;
};

const pages = computed(() => {
  const arr = reco.value?.dishes || [];
  const size = 3;
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
});

const extendedPages = computed(() => {
  const p = pages.value;
  if (!p.length) return [];
  if (p.length === 1) return p;
  return [p[p.length - 1], ...p, p[0]];
});

const activeDot = computed(() => {
  if (!pages.value.length) return 0;
  // slideIndex: 0..N+1; 真实页索引: slideIndex-1
  let idx = slideIndex.value - 1;
  if (idx < 0) idx = pages.value.length - 1;
  if (idx >= pages.value.length) idx = 0;
  return idx;
});

const slidesStyle = computed(() => ({
  transform: `translateX(-${(pages.value.length > 1 ? slideIndex.value : 0) * 100}%)`,
  transition: transitioning.value ? 'transform .25s ease-out' : 'none',
}));

const startAuto = () => {
  stopAuto();
  if (pages.value.length <= 1) return;
  autoTimer = setInterval(() => {
    onNext();
  }, 3000);
};
const stopAuto = () => {
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
  }
};
const pauseAuto = () => stopAuto();
const resumeAuto = () => startAuto();

// 成就统计
const achiCounts = ref({ bronze: 0, silver: 0, gold: 0, rainbow: 0 });
let achiHandler = null;
function computeAchi() {
  const all = getAllAchievements();
  const next = { bronze: 0, silver: 0, gold: 0, rainbow: 0 };
  for (const { count } of all) {
    const tier = getAchievementByCount(count).key;
    if (tier && next[tier] !== undefined) next[tier] += 1;
  }
  achiCounts.value = next;
}

const onNext = () => {
  if (pages.value.length <= 1) return;
  transitioning.value = true;
  slideIndex.value += 1;
};
const onPrev = () => {
  if (pages.value.length <= 1) return;
  transitioning.value = true;
  slideIndex.value -= 1;
};
const onTransitionEnd = () => {
  const n = pages.value.length;
  if (!n) return;
  // 尾部克隆 -> 跳回首个真实页
  if (slideIndex.value === n + 1) {
    transitioning.value = false;
    slideIndex.value = 1;
    nextTick(() => {
      try {
        void (slidesRef.value && slidesRef.value.offsetWidth);
      } catch {}
      requestAnimationFrame(() => {
        transitioning.value = true;
      });
    });
  }
  // 头部克隆 -> 跳回最后一个真实页
  if (slideIndex.value === 0) {
    transitioning.value = false;
    slideIndex.value = n;
    nextTick(() => {
      try {
        void (slidesRef.value && slidesRef.value.offsetWidth);
      } catch {}
      requestAnimationFrame(() => {
        transitioning.value = true;
      });
    });
  }
};
const goToPage = (i) => {
  if (i < 0 || i >= pages.value.length) return;
  pauseAuto();
  transitioning.value = true;
  slideIndex.value = i + 1;
  resumeAuto();
};

const load = async () => {
  loading.value = true;
  try {
    // 获取个人资料和基础数据
    const res = await getProfileSections();
    user.value = res.user || {};

    // 获取用户统计信息
    let receivedCommentsCount = 0;
    try {
      const stats = await getUserStats();

      // 获取我的帖子列表以统计收到的评论数
      try {
        const postsRes = await getMyPosts(1, 100); // 获取更多帖子以准确统计
        if (postsRes.code === 200 && postsRes.data) {
          // 计算所有帖子收到的评论总数
          receivedCommentsCount = (postsRes.data.posts || []).reduce((sum, post) => {
            return sum + (post.comments_count || 0);
          }, 0);

          // 设置已发布内容列表（只显示前5条）
          published.value = (postsRes.data.posts || []).slice(0, 5).map((post) => ({
            id: post.id,
            title: post.subject || '无标题', // 直接使用 subject 字段
            createdAt: formatTime(post.created_at),
          }));
        }
      } catch (err) {
        console.log('[ProfileHome] 获取我的帖子失败:', err?.response?.status || err.message);
        // 失败时使用空数组,不显示错误提示
      }

      // 设置交互统计数据
      interactions.value = [
        { name: '我点赞的帖子', count: stats.liked_posts_count || 0, to: '/profile/liked-posts' },
        { name: '我收到的评论', count: receivedCommentsCount, to: '/profile/received-comments' },
        {
          name: '我发布的评论',
          count: stats.commented_posts_count || 0,
          to: '/profile/my-comments',
        },
      ];
    } catch (err) {
      console.log('[ProfileHome] 获取用户统计失败:', err?.response?.status || err.message);
      // 使用默认值,不显示错误提示
      interactions.value = [
        { name: '我点赞的帖子', count: 0, to: '/profile/liked-posts' },
        { name: '我收到的评论', count: 0, to: '/profile/received-comments' },
        { name: '我发布的评论', count: 0, to: '/profile/my-comments' },
      ];
      published.value = res.published || [];
    }
  } catch (e) {
    console.log('[ProfileHome] 加载个人主页数据失败:', e?.response?.status || e.message);
    // 静默失败,不影响用户体验
  } finally {
    loading.value = false;
  }
};

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(async () => {
  // 先加载用户信息（用于 hasTags 之类的判定）
  await load();
  // 再加载推荐
  await loadRecommendMix();
  // 初始到首个真实页：仅1页时用0，多页时用1（因首尾克隆）
  slideIndex.value = pages.value.length > 1 ? 1 : 0;
  startAuto();
  await ensureAchievementsLoaded();
  computeAchi();
  achiHandler = () => computeAchi();
  onAchievementsUpdated(achiHandler);
});
onUnmounted(() => {
  stopAuto();
  if (achiHandler) offAchievementsUpdated(achiHandler);
});

const viewAllPublished = () => {
  router.push('/profile/posts');
};

const onNavigate = (to) => {
  router.push(to);
};

const openRecommend = (tab) => {
  if (!hasTags.value && (tab === 'pref' || tab === 'mix')) {
    window.$message?.info?.('先设置你的偏好标签，更精准哦');
    router.push('/onboarding/tags');
  } else {
    router.push({ path: '/recommend', query: { tab } });
  }
};

const editTags = () => router.push('/onboarding/tags');
const goDish = (id) => router.push(`/dish/${id}`);
const viewAllRecommend = () =>
  router.push({ path: '/recommend', query: { tab: recoSource.value } });
const goAchievements = (tab) => router.push({ path: '/achievements', query: { tab } });
const openAllAchievements = () => router.push('/achievements');
const viewFullCalendar = () => router.push('/profile/food-calendar');

const loadRecommendPref = async () => {
  try {
    recoLoading.value = true;
    const res = await getRecommendedDishes();
    reco.value = res?.data ?? res ?? { dishes: [] };
  } catch (err) {
    // 无偏好标签时后端返回 404，这是正常情况
    if (err?.response?.status === 404) {
      console.log('[ProfileHome] 未设置偏好标签,尝试位置推荐');
      const ok = await ensureGeo();
      if (ok) {
        await loadRecommendGeo();
        return;
      }
      // 静默处理,不显示提示
    }
    reco.value = { dishes: [] };
  } finally {
    recoLoading.value = false;
    recoFetched.value = true;
  }
};
const loadRecommendMix = async () => {
  try {
    recoLoading.value = true;
    // 使用后端综合推荐实现，传递mode=mix参数，热度推荐和tag推荐各取0.5系数
    const res = await getRecommendedDishes({ mode: 'mix' });
    reco.value = res?.data ?? res ?? { dishes: [] };
  } catch (err) {
    reco.value = { dishes: [] };
  } finally {
    recoLoading.value = false;
    recoFetched.value = true;
  }
};
const loadRecommendHot = async () => {
  try {
    recoLoading.value = true;
    const res = await getHotDishes({ limit: 12 });
    // 兼容后端返回格式，期望为 { dishes: [...] } 或数组
    const list = res?.data ?? res ?? [];
    reco.value = Array.isArray(list) ? { dishes: list } : list || { dishes: [] };
  } catch (err) {
    reco.value = { dishes: [] };
  } finally {
    recoLoading.value = false;
    recoFetched.value = true;
  }
};

const ensureGeo = () =>
  new Promise((resolve) => {
    if (geoPos.value) return resolve(true);
    if (!('geolocation' in navigator)) return resolve(false);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        geoPos.value = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        resolve(true);
      },
      () => resolve(false)
    );
  });

watch(recoSource, async (v) => {
  if (v === 'pref') await loadRecommendPref();
  if (v === 'mix') await loadRecommendMix();
  if (v === 'hot') await loadRecommendHot();
});

watch(
  () => reco.value?.dishes,
  () => {
    slideIndex.value = pages.value.length > 1 ? 1 : 0;
    startAuto();
  },
  { deep: true }
);

// expose auth helper to template
const __internal = { isAuthed };
</script>

<style scoped>
.title {
  font-size: 1.4rem;
  margin-bottom: 0.75rem;
}
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-top: 1rem;
}
.col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
/* 让列内的卡片等高 */
.equal-card {
  height: 100%;
  min-height: 220px;
  display: flex;
  flex-direction: column;
}
.equal-card :deep(.content) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.posts {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 380px;
  overflow: auto;
}
.post {
  padding: 0.5rem 0;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.04);
}
.post-title {
  font-weight: 600;
}
.post-meta {
  font-size: 0.85rem;
  color: var(--color-muted);
}
.interactions {
  display: flex;
  flex-wrap: wrap;
}
.hint {
  color: var(--color-muted);
  font-size: 0.85rem;
  margin-top: 0.5rem;
}
.link {
  background: none;
  border: none;
  color: var(--color-accent);
  cursor: pointer;
}
.reco-entry {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
.pref-tags {
  margin-top: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.pref-tags .label {
  color: var(--color-muted);
}
.mr8 {
  margin-right: 8px;
}

/* 推荐小卡片布局适配等高容器 */
.reco-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.reco-cards.two-cols {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.reco-card {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 76px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  padding: 12px 14px;
  cursor: pointer;
  background: #f8fbf8;
  transition:
    transform 0.12s ease,
    box-shadow 0.12s ease,
    border-color 0.12s ease;
}
.reco-card .icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 18px;
}
.reco-card .info {
  flex: 1;
  min-width: 0;
}
.reco-card.pref {
  background: #f3fbf5;
  border-color: #bfe8c9;
}
.reco-card.pref .icon {
  background: #c8f1d3;
}
.reco-card.geo {
  background: #f3f8ff;
  border-color: #c6dbff;
}
.reco-card.geo .icon {
  background: #d6e6ff;
}
.reco-card.mix {
  background: #fff7f3;
  border-color: #ffd9c6;
}
.reco-card.mix .icon {
  background: #ffe6d9;
}
.reco-card:hover {
  border-color: var(--color-accent);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}
.reco-title {
  font-weight: 600;
  margin-bottom: 4px;
}
.reco-desc {
  font-size: 12px;
  color: var(--color-muted);
}

.slider {
  position: relative;
  overflow: hidden;
}
.slides {
  display: flex;
  width: 100%;
  will-change: transform;
}
.page {
  min-width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 6px 0;
}

/* 导航按钮 */
.nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 3;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition:
    background 0.15s ease,
    box-shadow 0.15s ease;
}
.nav:hover {
  background: #fff;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}
.nav.prev {
  left: 6px;
}
.nav.next {
  right: 6px;
}

/* 指示点 */
.dots {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 4px;
  display: flex;
  gap: 6px;
  justify-content: center;
  z-index: 2;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.18);
  cursor: pointer;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
}
.dot.active {
  background: var(--color-accent);
  transform: scale(1.1);
}

.dish-card {
  width: 100%;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  padding: 8px;
  background: #fff;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease,
    border-color 0.16s ease;
}
.thumb {
  width: 100%;
  height: 96px;
  border-radius: 8px;
  overflow: hidden;
  background: #f4f6f8;
  transition: transform 0.22s ease;
}
.thumb :deep(img),
.thumb :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-weight: 600;
  font-size: 20px;
}
.dish-name {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dish-card:hover {
  border-color: var(--color-accent);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  position: relative;
  z-index: 2;
}
.dish-card:hover .thumb {
  transform: scale(1.03);
}

/* 个性化推荐：加载占位样式 */
.placeholder-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 6px 0;
}
.ph-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  padding: 8px;
  background: #fff;
}
.ph-thumb {
  width: 100%;
  height: 96px;
  border-radius: 8px;
  background: linear-gradient(90deg, #f3f5f7 25%, #e9edf2 37%, #f3f5f7 63%);
  background-size: 400% 100%;
  animation: shimmer 1.2s infinite;
}
.ph-lines {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ph-line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f3f5f7 25%, #e9edf2 37%, #f3f5f7 63%);
  background-size: 400% 100%;
  animation: shimmer 1.2s infinite;
}
.ph-line.short {
  width: 60%;
}
.ph-line.long {
  width: 85%;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
/* 加载中文案居中提示 */
.loading-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  color: var(--color-muted);
  font-size: 14px;
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: 1fr 1fr;
  }
  /* 限制卡片的最大宽度，减少卡内留白 */
  .top-grid,
  .middle-grid {
    justify-items: center;
  }
  .top-grid .col,
  .middle-grid .col {
    width: 100%;
    max-width: 680px;
  }
  /* 美食日历独占一行，全宽 */
  .calendar-grid {
    grid-template-columns: 1fr;
    justify-items: center;
  }
  .calendar-grid .col.full-width {
    width: 100%;
    max-width: 1400px;
  }
  /* 消费记录占左侧一列 */
  .bottom-grid {
    justify-items: center;
  }
  .bottom-grid .col {
    width: 100%;
    max-width: 680px;
  }
  /* 固定等高：两列时卡片充满列高 */
  .col {
    align-items: stretch;
  }
  .equal-card {
    height: 100%;
    min-height: 240px;
  }
  .posts {
    max-height: 460px;
  }
}

/* 我的成就：类似“我的互动”的小卡片风格 */
.achi-cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 8px;
}
.achi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 72px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  background: #fff;
  transition:
    transform 0.12s ease,
    box-shadow 0.12s ease,
    border-color 0.12s ease;
}
.achi-card .icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 22px;
  background: #f5f7fa;
  flex-shrink: 0;
}
.achi-card .info {
  flex: 1;
  min-width: 0;
}
.achi-stack {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}
.achi-count {
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
}
.achi-label {
  font-size: 12px;
  color: var(--color-muted);
  line-height: 1;
}
.achi-card:hover {
  border-color: var(--color-accent);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}
.achi-card.bronze {
  border-color: rgba(205, 127, 50, 0.65);
}
.achi-card.silver {
  border-color: rgba(192, 192, 192, 0.75);
}
.achi-card.gold {
  border-color: rgba(255, 215, 0, 0.75);
}
/* 移除右侧徽章，改为竖排文案（数字在上、文字在下） */
/* 不同等级的 icon 背景色微调 */
.achi-card.bronze .icon {
  background: #fff6ef;
  box-shadow: inset 0 0 0 1px rgba(205, 127, 50, 0.28);
  color: #b36a2e;
}
.achi-card.silver .icon {
  background: #f7f9ff;
  box-shadow: inset 0 0 0 1px rgba(128, 128, 128, 0.25);
  color: #6f6f6f;
}
.achi-card.gold .icon {
  background: #fffbea;
  box-shadow: inset 0 0 0 1px rgba(255, 215, 0, 0.35);
  color: #9c7b00;
}
.achi-card.rainbow .icon {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #aa4dc8;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06);
}
.achi-card.rainbow {
  border: 1px solid transparent;
  background-image:
    linear-gradient(#fff, #fff),
    linear-gradient(
      90deg,
      rgba(255, 0, 0, 0.75) 0%,
      rgba(255, 102, 0, 0.75) 14%,
      rgba(255, 165, 0, 0.75) 28%,
      rgba(255, 230, 0, 0.75) 42%,
      rgba(128, 255, 0, 0.75) 56%,
      rgba(0, 255, 170, 0.75) 70%,
      rgba(0, 128, 255, 0.75) 84%,
      rgba(139, 0, 255, 0.75) 100%
    );
  background-origin: border-box;
  background-clip: content-box, border-box;
}

/* Profile wrap and unauth overlays */
.profile-wrap { position: relative; }
.profile-header { margin-bottom: 12px; }
.profile-info-card { display:block; }
.profile-info-placeholder { padding:14px; border-radius:10px; background: linear-gradient(180deg,#fff,#fff); border:1px solid rgba(0,0,0,0.04); }
.profile-info-placeholder .placeholder-title { font-size:1.1rem; font-weight:600; margin-bottom:6px }
.profile-info-placeholder .placeholder-text { color:var(--color-muted); font-size:14px }

/* per-component overlay when unauthenticated */
.card-content-wrap { position: relative; }
.card-content-wrap { height: 100%; }
/* 如果 card-content-wrap 内包含嵌套的 SectionCard，使其 header 在遮罩之上 */
.card-content-wrap :deep(.section-card) .header { position: relative; z-index: 60; }
.component-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index: 40;
  pointer-events: auto; /* block interactions when covered */
}
.component-overlay .overlay-label { color: var(--color-muted); font-size: 14px }
</style>
