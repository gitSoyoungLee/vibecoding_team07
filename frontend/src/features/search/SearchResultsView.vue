<template>
  <div class="search-results-page">
    <div class="search-panel">
      <div class="search-input-wrap">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" stroke-linecap="round" />
        </svg>
        <input
          v-model="searchKeyword"
          @keyup.enter="onSearch"
          placeholder="검색어를 입력하세요. 장소와 게시판을 동시에 검색합니다."
        />
      </div>
      <button class="btn-search" @click="onSearch">검색</button>
    </div>

    <section class="section">
      <div class="section-header">
        <h2>장소 검색결과</h2>
        <span class="result-count">{{ locationTotal }}건</span>
      </div>

      <div v-if="locationLoading" class="empty-state">장소 검색 중...</div>
      <div v-else-if="locationError" class="empty-state error">{{ locationError }}</div>
      <div v-else-if="locations.length === 0" class="empty-state">
        검색된 장소가 없습니다.
      </div>

      <div v-else class="location-grid">
        <div
          v-for="loc in locations"
          :key="loc.id"
          class="location-card"
          @click="gotoLocationDetail(loc)"
        >
          <div class="card-image">
            <img
              v-if="loc.image_url"
              :src="loc.image_url"
              :alt="loc.title"
            />
            <div v-else class="card-image-fallback">이미지 없음</div>
          </div>
          <div class="card-title">{{ loc.title }}</div>
          <div class="card-district">{{ districtOf(loc.addr1) }}</div>
        </div>
      </div>

      <button
        v-if="locationTotal > locations.length"
        class="btn-more"
        @click="gotoLocationList"
      >
        장소 더 보기 →
      </button>
    </section>

    <section class="section">
      <div class="section-header">
        <h2>게시판 검색결과</h2>
        <span class="result-count">{{ posts.length }}건</span>
      </div>

      <div v-if="postsLoading" class="empty-state">게시판 검색 중...</div>
      <div v-else-if="postsError" class="empty-state error">{{ postsError }}</div>
      <div v-else-if="posts.length === 0" class="empty-state">
        검색된 게시글이 없습니다.
      </div>

      <div v-else class="post-list">
        <RouterLink
          v-for="post in pagedPosts"
          :key="post.id"
          :to="`/posts/${post.id}`"
          class="post-card"
        >
          <h3>{{ post.title }}</h3>
          <p class="post-preview">{{ post.content }}</p>
          <div class="post-meta">
            <span>{{ post.nickname }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
          </div>
        </RouterLink>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
        >
          이전
        </button>

        <button
          v-for="page in totalPages"
          :key="page"
          :class="{ active: page === currentPage }"
          @click="changePage(page)"
        >
          {{ page }}
        </button>

        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
        >
          다음
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchLocations, districtOf } from '../locations/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const PAGE_SIZE = 5

const route = useRoute()
const router = useRouter()

const searchKeyword = ref(route.query.q ? String(route.query.q) : '')
const locations = ref([])
const locationTotal = ref(0)
const locationLoading = ref(false)
const locationError = ref('')
const posts = ref([])
const postsLoading = ref(false)
const postsError = ref('')

const currentPage = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(posts.value.length / PAGE_SIZE)))
const pagedPosts = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return posts.value.slice(start, start + PAGE_SIZE)
})

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
}

async function loadLocationResults() {
  if (!searchKeyword.value.trim()) {
    locations.value = []
    locationTotal.value = 0
    return
  }

  locationLoading.value = true
  locationError.value = ''

  try {
    const data = await fetchLocations({
      keyword: searchKeyword.value.trim(),
      page: 1,
      limit: 3,
    })
    locations.value = data.items
    locationTotal.value = data.total
  } catch (error) {
    locationError.value = error.message || '장소 검색에 실패했습니다.'
    locations.value = []
    locationTotal.value = 0
  } finally {
    locationLoading.value = false
  }
}

async function loadPostResults() {
  if (!searchKeyword.value.trim()) {
    posts.value = []
    return
  }

  postsLoading.value = true
  postsError.value = ''

  try {
    const res = await fetch(
      `${API_BASE}/api/posts?search=${encodeURIComponent(searchKeyword.value.trim())}`
    )
    if (!res.ok) throw new Error('게시판 검색에 실패했습니다.')
    posts.value = await res.json()
  } catch (error) {
    postsError.value = error.message || '게시판 검색에 실패했습니다.'
    posts.value = []
  } finally {
    postsLoading.value = false
  }
}

async function loadResults() {
  currentPage.value = 1
  router.replace({ query: { q: searchKeyword.value.trim() } })
  await Promise.all([loadLocationResults(), loadPostResults()])
}

function onSearch() {
  loadResults()
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

function gotoLocationList() {
  router.push({
    path: '/locations',
    query: { keyword: searchKeyword.value.trim() },
  })
}

function gotoLocationDetail(loc) {
  router.push({
    path: '/locations',
    query: { keyword: searchKeyword.value.trim() },
  })
}

watch(
  () => route.query.q,
  (q) => {
    searchKeyword.value = q ? String(q) : ''
    loadResults()
  }
)

onMounted(loadResults)
</script>

<style scoped>
.search-results-page {
  max-width: 1080px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
  padding: 24px 40px 56px;
}

.search-panel {
  display: flex;
  gap: 10px;
}

.search-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg, #fff);
  border: 1.5px solid var(--border-strong, #e3ddd3);
  border-radius: 999px;
  padding: 13px 20px;
  color: var(--text-faint, #a8a29e);
}

.search-input-wrap input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 14.5px;
  color: var(--ink, #1c1917);
}

.btn-search {
  padding: 0 24px;
  border: none;
  background: var(--ink, #1c1917);
  color: #fff;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 700;
  font-size: 13.5px;
}

.section {
  background: var(--bg, #fff);
  border: 1px solid var(--border, #ece7df);
  border-radius: 16px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-header h2 {
  font-size: 17px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.result-count {
  color: var(--text-muted, #78716c);
  font-size: 13px;
}

.location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.location-card {
  border: 1px solid var(--border, #ece7df);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  background: var(--surface, #faf9f7);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.location-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.card-image {
  aspect-ratio: 4 / 3;
  background: var(--surface, #faf9f7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-image-fallback {
  color: var(--text-faint, #a8a29e);
  padding: 16px;
  text-align: center;
}

.card-title {
  padding: 10px 12px 0;
  font-weight: 700;
  font-size: 14.5px;
  color: var(--ink, #1c1917);
}

.card-district {
  padding: 3px 12px 12px;
  color: var(--text-muted, #78716c);
  font-size: 12.5px;
  font-weight: 500;
}

.btn-more {
  margin-top: 18px;
  display: inline-flex;
  padding: 10px 18px;
  background: var(--ink, #1c1917);
  color: #fff;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.post-card {
  display: block;
  padding: 16px;
  border: 1px solid var(--border, #ece7df);
  border-radius: 14px;
  background: var(--bg, #fff);
  text-decoration: none;
}

.post-card h3 {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.post-preview {
  margin: 0 0 12px;
  color: var(--text, #57534e);
  line-height: 1.5;
  font-size: 13.5px;
}

.post-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--text-faint, #a8a29e);
  font-size: 12.5px;
}

.pagination {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.pagination button {
  padding: 8px 12px;
  border: 1px solid var(--border-strong, #e3ddd3);
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text, #57534e);
  font-family: inherit;
}

.pagination button.active {
  background: var(--ink, #1c1917);
  color: #fff;
  border-color: var(--ink, #1c1917);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  color: var(--text-muted, #78716c);
  padding: 24px 0;
  text-align: center;
  font-size: 13.5px;
}

.empty-state.error {
  color: #dc2626;
}
</style>
