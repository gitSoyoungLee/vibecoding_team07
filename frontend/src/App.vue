<template>
  <div id="app-container">
    <header class="app-header">
      <RouterLink to="/" class="brand">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-ink-strong)" stroke-width="2.2">
          <path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10z"></path>
          <circle cx="12" cy="11" r="2.2"></circle>
        </svg>
        <span class="brand-name">ExploreSeoul</span>
        <span class="city-badge">서울</span>
      </RouterLink>

      <nav class="nav-links">
        <RouterLink to="/" class="nav-link">홈</RouterLink>
        <RouterLink to="/locations" class="nav-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10z"></path>
          </svg>
          장소
        </RouterLink>
        <RouterLink to="/posts" class="nav-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="4" width="16" height="17" rx="2"></rect>
            <path d="M8 9h8M8 13h8M8 17h5"></path>
          </svg>
          게시판
        </RouterLink>
        <RouterLink to="/festivals" class="nav-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="5" width="18" height="16" rx="2"></rect>
            <path d="M3 10h18M8 3v4M16 3v4"></path>
          </svg>
          축제 캘린더
        </RouterLink>
        <RouterLink to="/map" class="nav-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 4l6 2 6-2v14l-6 2-6-2-6 2V6z"></path>
            <path d="M9 4v14M15 6v14"></path>
          </svg>
          지도 탐색
        </RouterLink>
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
  min-height: 100vh;
  background: var(--bg, #fff);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 40px;
  border-bottom: 1px solid var(--border, #ece7df);
  background: var(--bg, #fff);
}

.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  text-decoration: none;
  color: inherit;
}

.brand-name {
  font-weight: 800;
  font-size: 19px;
  letter-spacing: -0.02em;
  color: var(--ink, #1c1917);
  white-space: nowrap;
}

.city-badge {
  font-size: 11px;
  color: var(--text-muted, #78716c);
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 999px;
  padding: 3px 9px;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 26px;
  font-size: 14px;
  color: var(--text-muted, #78716c);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  color: inherit;
  font-weight: 600;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
}

.nav-link.router-link-active {
  color: var(--ink, #1c1917);
  font-weight: 700;
  border-bottom-color: var(--accent, #facc15);
}

.main-content {
  min-height: calc(100vh - 64px);
}
</style>
