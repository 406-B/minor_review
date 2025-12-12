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
  <div class="canteen-main" ref="mainRef" :class="{ 'invisible-until-ready': !contentReady }">
        <template v-if="activeCanteen">
          <CanteenFloors :canteen-id="activeCanteen" @floorsLoaded="onFloorsLoaded" />
        </template>
        <template v-else>
          <EmptyState text="请选择一个食堂" />
        </template>
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
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
function getActualScroller() {
  const el = mainRef.value;
  if (el && el.scrollHeight > el.clientHeight) return el;
  return document.scrollingElement || document.documentElement;
}
import { getCanteens } from '@/utils/api/listApi'

const canteens = ref([])
const activeCanteen = ref('')
const mainRef = ref(null)
const floorsLoaded = ref(false)
const contentReady = ref(false)
function onFloorsLoaded(val) {
  floorsLoaded.value = val
}
const fetchCanteens = async () => {
  // 使用 getCanteens API 获取食堂列表
  const res = await getCanteens()
  if (res && res.data) {
    canteens.value = res.data
    if (canteens.value.length > 0) {
      // 优先恢复之前选择的食堂
      const savedId = sessionStorage.getItem('activeCanteenId')
      const exists = savedId && canteens.value.some(c => String(c.id) === String(savedId))
      activeCanteen.value = exists ? String(savedId) : String(canteens.value[0].id)
    }
  }
}

function onCanteenChange(id) {
  activeCanteen.value = String(id)
  // 记住当前选择，便于返回恢复
  sessionStorage.setItem('activeCanteenId', String(id))
}

onMounted(fetchCanteens)

// 刷新（关闭/重新加载）前记录当前滚动位置，保证刷新前后状态一致
function recordScroll() {
  try {
    const scroller = getActualScroller();
    const isHtmlRoot = (scroller === document.documentElement) || (scroller === document.scrollingElement) || (scroller === document.body);
    const scroll = isHtmlRoot
      ? (window.pageYOffset || document.scrollingElement?.scrollTop || document.documentElement.scrollTop || 0)
      : (scroller?.scrollTop || 0);
    sessionStorage.setItem('canteenScroll', String(scroll || 0));
  } catch (_) {}
}

function beforeUnloadHandler() {
  // 标记返回场景与禁用动画，避免刷新后闪动
  try {
    sessionStorage.setItem('returningFromDetail', '1');
    document.documentElement.classList.add('no-animate');
  } catch (_) {}
  recordScroll();
}

onMounted(() => {
  window.addEventListener('beforeunload', beforeUnloadHandler);
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler);
});

// 返回后恢复容器滚动位置（主内容区而非窗口）
// 监听楼层数据加载完成后再恢复滚动
watch(floorsLoaded, (loaded) => {
  if (!loaded) return;
  nextTick(async () => {
  const saved = Number(sessionStorage.getItem('canteenScroll') || 0);
  const isReturning = saved > 0; // 只要有保存值就尝试恢复
    const scroller = getActualScroller();
    const isHtmlRoot = (scroller === document.documentElement) || (scroller === document.scrollingElement) || (scroller === document.body);
    const getCurrent = () => {
      return isHtmlRoot
        ? (window.pageYOffset || document.scrollingElement?.scrollTop || document.documentElement.scrollTop || 0)
        : scroller.scrollTop;
    };

  if (saved > 0 && isReturning) {
      // 仅在返回详情时恢复，临时禁用动画与滚动锚点
      document.documentElement.classList.add('no-animate');
      document.documentElement.style.scrollBehavior = 'auto';
      const prevAnchor = document.documentElement.style.overflowAnchor;
      document.documentElement.style.overflowAnchor = 'none';

      // 等待内容高度足够，使目标滚动位置可达
      const targetNode = isHtmlRoot ? document.documentElement : scroller;
      const viewportH = window.innerHeight;
  // 目标位置限制为最大可滚位置，防止越界导致滚到底
  const maxScrollable = Math.max((targetNode.scrollHeight || document.body.scrollHeight) - viewportH - 1, 0);
  const target = Math.min(saved, maxScrollable);
  const minHeight = Math.max(target + viewportH - 1, viewportH);
      const waitForHeight = async () => {
        const ok = () => (targetNode.scrollHeight || document.body.scrollHeight) >= minHeight;
        let tries = 0;
        while (!ok() && tries < 50) {
          await new Promise(r => setTimeout(r, 50));
          tries++;
        }
      };
  await waitForHeight();

      // rAF 循环恢复，直到达到容差或超过最大尝试
      let attempts = 0;
      const maxAttempts = 20; // 更小重试次数
      const tolerance = 1.5;
      const doScroll = () => {
        if (isHtmlRoot) {
          window.scrollTo({ top: target, behavior: 'auto' });
          document.scrollingElement && (document.scrollingElement.scrollTop = target);
          document.documentElement.scrollTop = target;
          document.body && (document.body.scrollTop = target);
        } else {
          scroller.scrollTo({ top: target, behavior: 'auto' });
          scroller.scrollTop = target;
        }
      };
      
  const tick = () => {
  const current = getCurrent();
        if (Math.abs(current - target) <= tolerance) {
          contentReady.value = true;
          document.documentElement.classList.remove('no-animate');
          document.documentElement.style.overflowAnchor = prevAnchor || '';
          document.documentElement.style.scrollBehavior = '';
          sessionStorage.removeItem('returningFromDetail');
          return;
        }
        if (attempts >= maxAttempts) {
          // 直接显示，不再反复
          contentReady.value = true;
          document.documentElement.classList.remove('no-animate');
          document.documentElement.style.overflowAnchor = prevAnchor || '';
          document.documentElement.style.scrollBehavior = '';
          sessionStorage.removeItem('returningFromDetail');
          return;
        }
        attempts++;
        doScroll();
        // 仅使用 rAF，避免额外延时
        requestAnimationFrame(tick);
      };
      doScroll();
      requestAnimationFrame(tick);
    } else {
      // 非返回详情场景，直接显示并移除限制
      contentReady.value = true;
      document.documentElement.classList.remove('no-animate');
      document.documentElement.style.overflowAnchor = '';
      document.documentElement.style.scrollBehavior = '';
    }
  });
});
</script>

<style scoped>
/* 主体双栏布局 */
.canteen-layout {
  display: flex;
  align-items: stretch;
  gap: 0;
  min-height: calc(100vh - 60px - 48px); /* 减去顶部栏与容器上下 padding 估算 */
}
.invisible-until-ready { visibility: hidden; }
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

/* 返回时临时禁用动画，避免闪动 */
:root.no-animate *,
html.no-animate *,
body.no-animate * {
  transition: none !important;
  animation: none !important;
}
html.no-animate { scroll-behavior: auto !important; }
html.no-animate { overflow-anchor: none; }
</style>

<!-- 全局样式：确保作用到 html/body 根元素 -->
<style>
html.no-animate *,
body.no-animate *,
:root.no-animate * {
  transition: none !important;
  animation: none !important;
}
html.no-animate { scroll-behavior: auto !important; overflow-anchor: none; }
</style>
