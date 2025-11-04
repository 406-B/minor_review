import { createRouter, createWebHistory } from 'vue-router'


import DishSearch from '../views/DishSearch.vue'

const routes = [
  {
    path: '/',
    name: 'CanteenBrowser',
    component: CanteenBrowser
  },
  {
    path: '/dish/:id',
    name: 'DishDetail',
    component: DishDetail
  },
  {
    path: '/search',
    name: 'DishSearch',
    component: DishSearch
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
