import { createRouter, createWebHistory } from 'vue-router';
import { isProtectedPath } from '@/constants/permissions.js'
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
  { path: '/achievements', name: 'Achievements', component: () => import('../views/Achievements.vue'), meta: { requiresAuth: true } },
  { path: '/canteen-consumption', name: 'CanteenConsumption', component: () => import('../views/CanteenConsumption.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../views/NotFound.vue') },
  { path: '/', redirect: '/canteen' }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('jwt');
  const needAuth = isProtectedPath(to.path) || to.meta?.requiresAuth
  if (!token && needAuth) {
    next('/login');
  } else {
    next();
  }
});

export default router;
