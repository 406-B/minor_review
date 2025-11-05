import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/community'
  },
  {
    path: '/community',
    name: 'CommunityHome',
    component: () => import('../views/CommunityHome.vue')
  },
  {
    path: '/community/create',
    name: 'PostCreate',
    component: () => import('../views/PostCreate.vue')
  },
  {
    path: '/community/:id',
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue')
  },
  {
    path: '/',
    name: 'Home',
    // keep existing App as root; App.vue may contain its own content
    component: () => import('@/App.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileHome.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
