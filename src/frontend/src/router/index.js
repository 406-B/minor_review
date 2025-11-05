import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Home from '../views/Home.vue';
import CanteenBrowser from '../views/CanteenBrowser.vue';
import DishDetail from '../views/DishDetail.vue';
import DishSearch from '../views/DishSearch.vue';

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/home', component: Home },
  { path: '/', name: 'CanteenBrowser', component: CanteenBrowser },
  { path: '/canteen', name: 'CanteenBrowserAlt', component: CanteenBrowser },
  { path: '/dish/:id', name: 'DishDetail', component: DishDetail },
  { path: '/search', name: 'DishSearch', component: DishSearch },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫：未登录跳转登录
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  // 只有 /login 和 /register 不需要 token
  if (!['/login', '/register'].includes(to.path) && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
