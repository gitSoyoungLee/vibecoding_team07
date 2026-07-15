<template>
  <div id="app-container">
    <header class="app-header">
      <h1>📍 LocalHub</h1>
      <nav class="nav-links">
        <RouterLink to="/posts">📋 게시판</RouterLink>
      </nav>
    </header>

    <main class="main-content">
      <!-- 라우터 주소(/posts)에 맞춰 PostsView.vue가 마운트되는 자리 -->
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
#app-container {
  font-family: 'Noto Sans KR', sans-serif;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.nav-links a {
  margin-left: 20px;
  text-decoration: none;
  color: #333;
  font-weight: bold;
}

.nav-links a.router-link-active {
  color: #007bff;
}
</style>