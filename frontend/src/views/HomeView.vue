<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CATEGORIES } from '../features/locations/api'
import { POST_CATEGORIES } from '../constants/postCategories'
import heroBanner from '../assets/hero-banner.jpg'

const router = useRouter()

const keyword = ref('')
function onSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/search', query: q ? { q } : {} })
}

const locationCategories = CATEGORIES

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const posts = ref([])
const postsLoading = ref(false)
const postsError = ref('')
const selectedPostCategory = ref(POST_CATEGORIES[0])

const previewPosts = computed(() => {
  const list =
    selectedPostCategory.value.id === 0
      ? posts.value
      : posts.value.filter((p) => Number(p.category_id) === selectedPostCategory.value.id)
  return list.slice(0, 6)
})

function categoryName(id) {
  return POST_CATEGORIES.find((c) => c.id === Number(id))?.name || '전체'
}

async function loadPosts() {
  postsLoading.value = true
  postsError.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/posts/?limit=50`)
    if (!res.ok) throw new Error('게시글을 불러오지 못했습니다.')
    posts.value = await res.json()
  } catch (e) {
    postsError.value = e.message
    posts.value = []
  } finally {
    postsLoading.value = false
  }
}

function openPost(postId) {
  router.push(`/posts/${postId}`)
}

onMounted(loadPosts)
</script>

<template>
  <div class="home-page">
    <div class="search-row">
      <div class="search-input-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-4-4" stroke-linecap="round" />
        </svg>
        <input
          v-model="keyword"
          class="search-input"
          placeholder="궁금한 건 검색해보세요!"
          @keyup.enter="onSearch"
        />
      </div>
    </div>

    <div class="category-row">
      <RouterLink
        v-for="cat in locationCategories"
        :key="cat.key"
        :to="{ path: '/locations', query: { category: cat.key } }"
        class="category-chip"
      >
        {{ cat.label }}
      </RouterLink>
    </div>

    <div class="hero-banner">
      <img :src="heroBanner" alt="2026 Seoul" />
      <div class="hero-overlay">
        <span class="hero-title">서울, 오늘은 어디로 갈까요?</span>
        <span class="hero-subtitle">관광 정보를 한곳에서 보고, 경험은 익명으로 나눠요</span>
      </div>
    </div>

    <section class="board-preview">
      <div class="section-head">
        <h2 class="section-title">게시판</h2>
        <RouterLink to="/posts" class="see-all">전체 보기 →</RouterLink>
      </div>

      <div class="board-row">
        <aside class="post-category-sidebar">
          <button
            v-for="cat in POST_CATEGORIES"
            :key="cat.id"
            class="category-btn"
            :class="{ active: cat.id === selectedPostCategory.id }"
            @click="selectedPostCategory = cat"
          >
            {{ cat.name }}
          </button>
        </aside>

        <div class="post-list">
          <div v-if="postsLoading" class="post-list-empty">불러오는 중...</div>
          <div v-else-if="postsError" class="post-list-empty">{{ postsError }}</div>
          <div v-else-if="previewPosts.length === 0" class="post-list-empty">게시글이 없습니다.</div>
          <template v-else>
            <div
              v-for="post in previewPosts"
              :key="post.id"
              class="post-row"
              @click="openPost(post.id)"
            >
              <span class="post-cat">{{ categoryName(post.category_id) }}</span>
              <span class="post-title">{{ post.title }}</span>
              <span class="post-meta">{{ post.nickname }} · 댓글 {{ post.comment_count }}</span>
            </div>
          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 40px 56px;
}

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input-wrap {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg, #fff);
  border: 1.5px solid var(--border-strong, #e3ddd3);
  border-radius: 999px;
  padding: 14px 20px;
  box-shadow: 0 1px 4px rgba(28, 25, 23, 0.04);
}

.search-icon {
  color: var(--text-faint, #a8a29e);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14.5px;
  font-family: inherit;
  background: transparent;
  color: var(--ink, #1c1917);
}

.search-input::placeholder {
  color: var(--text-faint, #a8a29e);
}

.category-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.category-chip {
  padding: 8px 16px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 999px;
  text-decoration: none;
  color: var(--text, #57534e);
  font-weight: 600;
  font-size: 13px;
}

.category-chip:hover {
  background: var(--accent-soft, #fef3c7);
  border-color: var(--accent, #facc15);
  color: var(--accent-ink, #a16207);
}

.hero-banner {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  height: 280px;
  margin-bottom: 32px;
}

.hero-banner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.hero-overlay {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 22px 26px;
  background: linear-gradient(transparent, rgba(28, 25, 23, 0.6));
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hero-title {
  font-family: var(--serif, 'Gowun Batang', serif);
  font-size: 26px;
  font-weight: 700;
  color: #fff;
}

.hero-subtitle {
  font-size: 13.5px;
  color: rgba(255, 255, 255, 0.85);
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 21px;
  font-weight: 800;
}

.see-all {
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  color: var(--accent-ink-strong, #ca8a04);
}

.board-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.post-category-sidebar {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border, #ece7df);
  border-radius: 12px;
  overflow: hidden;
  width: 190px;
  flex-shrink: 0;
}

.category-btn {
  text-align: left;
  padding: 11px 16px;
  border: none;
  border-top: 1px solid var(--border, #ece7df);
  background: transparent;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text, #57534e);
  cursor: pointer;
}

.category-btn:first-child {
  border-top: none;
}

.category-btn.active {
  background: var(--accent-soft, #fef3c7);
  color: var(--accent-ink, #a16207);
  font-weight: 700;
  border-left: 3px solid var(--accent, #facc15);
}

.post-list {
  flex: 1;
  border: 1px solid var(--border, #ece7df);
  border-radius: 12px;
  overflow: hidden;
}

.post-list-empty {
  padding: 20px;
  color: var(--text-muted, #78716c);
  font-size: 13.5px;
}

.post-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  border-top: 1px solid var(--border, #ece7df);
  cursor: pointer;
}

.post-row:first-child {
  border-top: none;
}

.post-row:hover {
  background: var(--surface, #faf9f7);
}

.post-cat {
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-ink, #a16207);
  background: var(--accent-soft, #fef3c7);
  border-radius: 4px;
  padding: 2px 7px;
  white-space: nowrap;
  flex-shrink: 0;
}

.post-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink, #1c1917);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-meta {
  flex-shrink: 0;
  font-size: 12.5px;
  color: var(--text-faint, #a8a29e);
  white-space: nowrap;
}
</style>
