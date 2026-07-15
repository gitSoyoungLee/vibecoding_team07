<template>
  <div class="search-results-page">
    <div class="search-panel">
      <input
        v-model="searchKeyword"
        @keyup.enter="onSearch"
        placeholder="검색어를 입력하세요. 장소와 게시판을 동시에 검색합니다."
      />
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
        더보기(+) 장소 더 보기
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
        <article
          v-for="post in pagedPosts"
          :key="post.id"
          class="post-card"
        >
          <h3>{{ post.title }}</h3>
          <p class="post-preview">{{ post.content }}</p>
          <div class="post-meta">
            <span>👤 {{ post.nickname }}</span>
            <span>📅 {{ formatDate(post.created_at) }}</span>
          </div>
        </article>
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
  display: flex;
  flex-direction: column;
  gap: 28px;
  padding: 20px;
}

.search-panel {
  display: flex;
  gap: 10px;
}

.search-panel input {
  flex: 1;
  padding: 12px 14px;
  border: 1px solid #d2d6dc;
  border-radius: 10px;
  font-size: 1rem;
}

.btn-search {
  padding: 12px 20px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 10px;
  cursor: pointer;
}

.section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.15rem;
}

.result-count {
  color: #6b7280;
  font-size: 0.95rem;
}

.location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.location-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  background: #fafafa;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.location-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
}

.card-image {
  aspect-ratio: 4 / 3;
  background: #f3f4f6;
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
  color: #9ca3af;
  padding: 16px;
  text-align: center;
}

.card-title {
  padding: 8px 10px 0;
  font-weight: 700;
  font-size: 1rem;
  text-align: left;
}

.card-district {
  padding: 2px 10px 10px;
  color: #6b7280;
  font-size: 0.95rem;
  font-weight: 500;
  text-align: left;
}

.btn-more {
  margin-top: 18px;
  display: inline-flex;
  padding: 10px 16px;
  background: #1d4ed8;
  color: white;
  border: none;
  border-radius: 999px;
  cursor: pointer;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.post-card {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #ffffff;
}

.post-card h3 {
  margin: 0 0 8px;
  font-size: 1.05rem;
}

.post-preview {
  margin: 0 0 12px;
  color: #4b5563;
  line-height: 1.5;
}

.post-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: #6b7280;
  font-size: 0.9rem;
}

.pagination {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.pagination button {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 10px;
  cursor: pointer;
}

.pagination button.active {
  background: #2563eb;
  color: white;
  border-color: transparent;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  color: #6b7280;
  padding: 24px 0;
  text-align: center;
}

.empty-state.error {
  color: #dc2626;
}
</style>