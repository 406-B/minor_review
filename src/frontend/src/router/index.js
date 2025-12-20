import { createRouter, createWebHistory } from 'vue-router';
import { isProtectedPath } from '@/constants/permissions.js'
import { getProfileSections } from '@/api/profile'
import OnboardingTags from '@/views/OnboardingTags.vue'

const Recommend = () => import('@/views/Recommend.vue')

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  { path: '/home', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/canteen', name: 'CanteenBrowser', component: () => import('../views/CanteenBrowser.vue') },
  { path: '/dish/:id', name: 'DishDetail', component: () => import('../views/DishDetail.vue') },
  { path: '/search', name: 'DishSearch', component: () => import('../views/DishSearch.vue') },
  { path: '/community', name: 'CommunityHome', component: () => import('../views/CommunityHome.vue') },
  { path: '/community/create', name: 'PostCreate', component: () => import('../views/PostCreate.vue') },
  { path: '/community/:id', name: 'PostDetail', component: () => import('../views/PostDetail.vue') },
  { path: '/profile', name: 'Profile', component: () => import('@/views/ProfileHome.vue') },
  { path: '/onboarding/tags', name: 'OnboardingTags', component: OnboardingTags, meta: { requiresAuth: true } },
  { path: '/recommend', name: 'Recommend', component: Recommend, meta: { requiresAuth: true } },
  { path: '/profile/posts', name: 'MyPosts', component: () => import('../views/MyPosts.vue') },
  { path: '/profile/edit', name: 'ProfileEdit', component: () => import('../views/ProfileEdit.vue') },
  { path: '/profile/food-calendar', name: 'FoodCalendarDetail', component: () => import('../views/FoodCalendarDetail.vue'), meta: { requiresAuth: true } },
  { path: '/profile/liked-posts', name: 'MyLikedPosts', component: () => import('../views/MyLikedPosts.vue'), meta: { requiresAuth: true } },
  { path: '/profile/my-comments', name: 'MyCommentsPage', component: () => import('../views/MyCommentsPage.vue'), meta: { requiresAuth: true } },
  { path: '/profile/received-comments', name: 'ReceivedComments', component: () => import('../views/ReceivedComments.vue'), meta: { requiresAuth: true } },
  { path: '/achievements', name: 'Achievements', component: () => import('../views/Achievements.vue'), meta: { requiresAuth: true } },
  { path: '/canteen-consumption', name: 'CanteenConsumption', component: () => import('../views/CanteenConsumption.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../views/NotFound.vue') },
  { path: '/', redirect: '/profile' }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 当使用浏览器后退/前进或 router.back() 时，Vue 会提供 savedPosition
    if (savedPosition) {
      return savedPosition
    }
    // 对于新导航，滚动到顶部；也可根据页面需要定制
    return { left: 0, top: 0 }
  }
});

// 禁用浏览器默认滚动恢复，交由我们手动控制
try { if ('scrollRestoration' in history) history.scrollRestoration = 'manual' } catch (_) {}


function getActualScroller() {
  const el = document.querySelector('.canteen-main');
  if (el && el.scrollHeight > el.clientHeight) return el;
  return document.scrollingElement || document.documentElement;
}

router.beforeEach((to, from, next) => {
  // 在从食堂浏览页进入菜品详情前，记录主容器滚动位置
  if (from?.name === 'CanteenBrowser' && to?.name === 'DishDetail') {
    try {
      const scroller = getActualScroller();
      const scroll = scroller === document.documentElement || scroller === document.scrollingElement
        ? (window.pageYOffset || document.scrollingElement?.scrollTop || document.documentElement.scrollTop || 0)
        : (scroller?.scrollTop || 0);
      sessionStorage.setItem('canteenScroll', String(scroll || 0));
    } catch (_) { /* 忽略 DOM 访问异常 */ }
  }
  // 标记“从详情返回到食堂”，供页面决定是否跳过浮现动画
  if (from?.name === 'DishDetail' && to?.name === 'CanteenBrowser') {
    try {
      sessionStorage.setItem('returningFromDetail', '1')
      // 添加全局禁用动画类，避免闪动
      document.documentElement.classList.add('no-animate')
    } catch (_) {}
  }
  const token = localStorage.getItem('jwt');
  const needAuth = isProtectedPath(to.path) || to.meta?.requiresAuth
  if (!token && needAuth) {
    return next('/login');
  }
  // 首次登录引导（仅在已登录、非引导页、且未明确跳过时）
  if (token && to.path !== '/onboarding/tags') {
    const passed = sessionStorage.getItem('__onboarding_checked') === '1'
    if (!passed) {
      sessionStorage.setItem('__onboarding_checked', '1')
      getProfileSections().then((prof) => {
        try {
          const tags = prof?.user?.preference_tags || []
          if (Array.isArray(tags) && tags.length === 0) {
            return next('/onboarding/tags')
          }
        } catch (_) {}
        next()
      }).catch(() => next())
      return
    }
  }
  next();
});


export default router;
