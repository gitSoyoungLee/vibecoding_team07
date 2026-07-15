import { createRouter, createWebHistory } from 'vue-router'
import PostsView from '../features/posts/PostsView.vue'

const routes = [
  { path: '/', redirect: '/posts' },
  { path: '/posts', name: 'posts', component: PostsView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router