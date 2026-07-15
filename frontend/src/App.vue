<template>
  <div id="app-container">
    <header class="app-header">
      <RouterLink to="/" class="brand">🌏 ExploreSeoul</RouterLink>
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
  border-bottom: 3px solid var(--accent);
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.brand {
  text-decoration: none;
  color: #1a1a1a;
  font-size: 1.5em;
  font-weight: 900;
  font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  letter-spacing: -0.5px;
  transition: all 0.3s ease;
}

.brand:hover {
  color: var(--primary-blue);
  transform: scale(1.05);
}

.nav-links {
  display: flex;
  gap: 24px;
}

.nav-links a {
  text-decoration: none;
  color: #666;
  font-weight: 600;
  font-size: 1em;
  transition: all 0.3s ease;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
}

.nav-links a:hover {
  color: var(--primary-blue);
  border-bottom-color: var(--accent);
}

.nav-links a.router-link-active {
  color: var(--primary-blue);
  border-bottom-color: var(--accent);
}

.main-content {
  background: #fff;
}
</style>