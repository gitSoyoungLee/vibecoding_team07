import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LocationListView from '../features/locations/LocationListView.vue'

// 각 도메인은 자기 라우트를 여기에 한 줄씩 추가한다.
const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/locations', name: 'locations', component: LocationListView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
