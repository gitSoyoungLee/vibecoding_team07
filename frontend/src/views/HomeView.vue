<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CATEGORIES } from '../features/locations/api'
import heroBanner from '../assets/hero-banner.jpg'

const router = useRouter()

const keyword = ref('')
function onSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/locations', query: q ? { keyword: q } : {} })
}

const locationCategories = CATEGORIES.filter((c) => c.key !== 'all')

const POST_CATEGORIES = [
  { id: 0, name: '전체' },
  { id: 1, name: '관광지' },
  { id: 2, name: '레포츠' },
  { id: 3, name: '문화시설' },
  { id: 4, name: '쇼핑' },
  { id: 5, name: '숙박' },
  { id: 6, name: '여행코스' },
  { id: 7, name: '축제' },
]

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

onMounted(loadPosts)
</script>

<template>
  <div class="home-page">
    <div class="search-row">
      <div class="search-input-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2" />
          <line x1="16.2" y1="16.2" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input
          v-model="keyword"
          class="search-input"
          placeholder="장소명, 주소로 검색"
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

    <img :src="heroBanner" alt="2026 Seoul" class="hero-banner" />

    <section class="board-preview">
      <h2 class="section-title">게시판</h2>

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
          <div v-if="postsLoading">불러오는 중...</div>
          <div v-else-if="postsError">{{ postsError }}</div>
          <div v-else-if="previewPosts.length === 0">게시글이 없습니다.</div>
          <template v-else>
            <RouterLink
              v-for="post in previewPosts"
              :key="post.id"
              to="/posts"
              class="post-row"
            >
              <span class="post-title">{{ post.title }}</span>
              <span class="post-meta">{{ post.nickname }} · 댓글 {{ post.comment_count }}</span>
            </RouterLink>
          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input-wrap {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text, #6b6375);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 6px;
  font-weight: 500;
  box-sizing: border-box;
}

.category-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.category-chip {
  padding: 8px 14px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 999px;
  text-decoration: none;
  color: inherit;
  font-weight: 600;
  font-size: 0.9rem;
}

.category-chip:hover {
  background: rgba(250, 204, 21, 0.2);
  border-color: rgba(234, 179, 8, 0.6);
}

.hero-banner {
  width: 100%;
  height: 280px;
  object-fit: cover;
  border-radius: 12px;
  display: block;
  margin-bottom: 32px;
}

.section-title {
  text-align: left;
  margin: 0 0 16px;
  font-size: 1.3rem;
  font-weight: 700;
}

.board-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.post-category-sidebar {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 160px;
  flex-shrink: 0;
}

.category-btn {
  text-align: left;
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  font-weight: 500;
  cursor: pointer;
}

.category-btn.active {
  background: rgba(250, 204, 21, 0.2);
  border-color: rgba(234, 179, 8, 0.6);
  color: #92720a;
  font-weight: 700;
}

@media (prefers-color-scheme: dark) {
  .category-btn.active {
    background: rgba(250, 204, 21, 0.22);
    border-color: rgba(250, 204, 21, 0.55);
    color: #fde68a;
  }
}

.post-list {
  flex: 1;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 8px;
  overflow: hidden;
}

.post-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #e5e4e7);
  text-decoration: none;
  color: inherit;
}

.post-row:last-child {
  border-bottom: none;
}

.post-row:hover {
  background: var(--code-bg, #f4f3ec);
}

.post-title {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-meta {
  flex-shrink: 0;
  font-size: 0.8rem;
  color: var(--text, #6b6375);
}
</style>
