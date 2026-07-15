<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchLocations, districtOf, CATEGORIES, PAGE_SIZE } from './api'
import LocationDetailModal from './LocationDetailModal.vue'

const route = useRoute()

const locations = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref('')
const initialCategory =
  CATEGORIES.find((c) => c.key === route.query.category) || CATEGORIES[0]
const selectedCategory = ref(initialCategory)
const keywordInput = ref(typeof route.query.keyword === 'string' ? route.query.keyword : '')
const activeKeyword = ref(keywordInput.value)
const selectedLocation = ref(null)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

const pageNumbers = computed(() => {
  const current = page.value
  const last = totalPages.value
  const window = 2
  const pages = []
  let prev = 0
  for (let p = 1; p <= last; p++) {
    if (p === 1 || p === last || (p >= current - window && p <= current + window)) {
      if (prev && p - prev > 1) pages.push('...')
      pages.push(p)
      prev = p
    }
  }
  return pages
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchLocations({
      contentTypeIds: selectedCategory.value.ids,
      keyword: activeKeyword.value,
      page: page.value,
    })
    locations.value = data.items
    total.value = data.total
  } catch (e) {
    error.value = e.message
    locations.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function selectCategory(cat) {
  selectedCategory.value = cat
  page.value = 1
  load()
}

function onSearch() {
  activeKeyword.value = keywordInput.value.trim()
  page.value = 1
  load()
}

function goToPage(p) {
  if (p < 1 || p > totalPages.value || p === page.value) return
  page.value = p
  load()
}

function openDetail(loc) {
  selectedLocation.value = loc
}

function closeDetail() {
  selectedLocation.value = null
}

onMounted(load)
</script>

<template>
  <div class="location-page">
    <h1 class="page-title">서울 어디로 갈까?</h1>

    <div class="search-row">
      <div class="search-input-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2" />
          <line x1="16.2" y1="16.2" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input
          v-model="keywordInput"
          class="search-input"
          placeholder="장소명, 주소로 검색"
          @keyup.enter="onSearch"
        />
      </div>
    </div>

    <div class="content-row">
      <aside class="category-sidebar">
        <button
          v-for="cat in CATEGORIES"
          :key="cat.key"
          class="category-btn"
          :class="{ active: cat.label === selectedCategory.label }"
          @click="selectCategory(cat)"
        >
          {{ cat.label }}
        </button>
      </aside>

      <section class="card-gallery">
        <div v-if="loading">불러오는 중...</div>
        <div v-else-if="error">{{ error }}</div>
        <div v-else-if="locations.length === 0">표시할 장소가 없습니다.</div>
        <div v-else class="card-grid">
          <div
            v-for="loc in locations"
            :key="loc.id"
            class="location-card"
            @click="openDetail(loc)"
          >
            <div class="card-image">
              <img v-if="loc.image_url" :src="loc.image_url" :alt="loc.title" />
              <div v-else class="card-image-fallback">이미지 없음</div>
            </div>
            <div class="card-title">{{ loc.title }}</div>
            <div class="card-district">{{ districtOf(loc.addr1) }}</div>
          </div>
        </div>

        <nav v-if="!loading && !error && total > 0" class="pagination">
          <button
            class="page-btn"
            :disabled="page === 1"
            @click="goToPage(page - 1)"
          >
            이전
          </button>
          <template v-for="(p, idx) in pageNumbers" :key="idx">
            <span v-if="p === '...'" class="page-ellipsis">…</span>
            <button
              v-else
              class="page-btn"
              :class="{ active: p === page }"
              @click="goToPage(p)"
            >
              {{ p }}
            </button>
          </template>
          <button
            class="page-btn"
            :disabled="page === totalPages"
            @click="goToPage(page + 1)"
          >
            다음
          </button>
        </nav>
      </section>
    </div>

    <LocationDetailModal
      v-if="selectedLocation"
      :location="selectedLocation"
      @close="closeDetail"
    />
  </div>
</template>

<style scoped>
.location-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.page-title {
  text-align: left;
  margin: 0 0 32px;
  font-size: 1.9em;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
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

.content-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.category-sidebar {
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

.card-gallery {
  flex: 1;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.location-card {
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.location-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.card-image {
  aspect-ratio: 4 / 3;
  background: var(--code-bg, #f4f3ec);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-image-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text, #6b6375);
  font-size: 0.85em;
}

.card-title {
  padding: 8px 10px 0;
  font-weight: 700;
  font-size: 1rem;
  text-align: left;
}

.card-district {
  padding: 2px 10px 10px;
  color: var(--text, #6b6375);
  font-size: 0.8rem;
  font-weight: 500;
  text-align: left;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  margin-top: 32px;
  flex-wrap: wrap;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 6px;
  background: transparent;
  font-weight: 500;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.page-btn.active {
  background: rgba(250, 204, 21, 0.2);
  border-color: rgba(234, 179, 8, 0.6);
  color: #92720a;
  font-weight: 700;
}

.page-ellipsis {
  padding: 0 4px;
  color: var(--text, #6b6375);
}

@media (prefers-color-scheme: dark) {
  .page-btn.active {
    background: rgba(250, 204, 21, 0.22);
    border-color: rgba(250, 204, 21, 0.55);
    color: #fde68a;
  }
}
</style>
