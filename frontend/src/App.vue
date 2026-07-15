<template>
  <div id="app-container">
    <header class="app-header">
      <RouterLink to="/" class="brand">📍 LocalHub</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/locations">🗺️ 장소</RouterLink>
        <RouterLink to="/posts">📋 게시판</RouterLink>
      </nav>
    </header>

    <main class="main-content">
      <!-- 라우터 주소에 맞춰 화면이 마운트되는 자리 -->
      <RouterView />
    </main>

    <!-- 플로팅 챗봇 위젯 -->
    <ChatWidget />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import ChatWidget from './features/chat/ChatWidget.vue'
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

.brand {
  text-decoration: none;
  color: inherit;
  font-size: 1.2em;
  font-weight: bold;
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
