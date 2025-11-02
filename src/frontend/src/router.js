import { createRouter, createWebHistory } from 'vue-router';

import Login from './views/Login.vue';
import Register from './views/Register.vue';
import Home from './views/Home.vue';

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/home', component: Home },
  { path: '/', redirect: '/login' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
