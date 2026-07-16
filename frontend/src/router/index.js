import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LocationListView from '../features/locations/LocationListView.vue'
import MapExploreView from '../features/locations/MapExploreView.vue'
import PostsView from '../features/posts/PostsView.vue'
import PostDetailView from '../features/posts/PostDetailView.vue'
import FestivalCalendarView from '../features/festivals/FestivalCalendarView.vue'
import SearchResultsView from '../features/search/SearchResultsView.vue'

// 각 도메인은 자기 라우트를 여기에 한 줄씩 추가한다.
const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/locations', name: 'locations', component: LocationListView },
  { path: '/map', name: 'map', component: MapExploreView },
  { path: '/posts', name: 'posts', component: PostsView },
  { path: '/posts/:id', name: 'post-detail', component: PostDetailView, props: true },
  { path: '/festivals', name: 'festivals', component: FestivalCalendarView },
  { path: '/search', name: 'search', component: SearchResultsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
