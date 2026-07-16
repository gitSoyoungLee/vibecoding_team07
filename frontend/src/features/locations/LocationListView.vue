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
        <svg class="search-icon" viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-4-4" stroke-linecap="round" />
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
        <div v-if="loading" class="gallery-empty">불러오는 중...</div>
        <div v-else-if="error" class="gallery-empty">{{ error }}</div>
        <div v-else-if="locations.length === 0" class="gallery-empty">표시할 장소가 없습니다.</div>
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
            <div class="card-district">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10z" />
              </svg>
              {{ districtOf(loc.addr1) }}
            </div>
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 40px 56px;
}

.page-title {
  text-align: left;
  margin: 0 0 24px;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--ink, #1c1917);
}

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
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
  padding: 13px 20px;
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

.content-row {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

.category-sidebar {
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

.card-gallery {
  flex: 1;
}

.gallery-empty {
  padding: 40px 0;
  text-align: center;
  color: var(--text-muted, #78716c);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.location-card {
  border: 1px solid var(--border, #ece7df);
  border-radius: 14px;
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
  background: var(--surface, #faf9f7);
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
  color: var(--text-faint, #a8a29e);
  font-size: 0.85em;
}

.card-title {
  padding: 13px 16px 0;
  font-weight: 700;
  font-size: 15px;
  color: var(--ink, #1c1917);
}

.card-district {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 16px 13px;
  color: var(--text-muted, #78716c);
  font-size: 12.5px;
  font-weight: 500;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 32px;
  flex-wrap: wrap;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 8px;
  background: transparent;
  font-weight: 500;
  color: var(--text, #57534e);
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.page-btn.active {
  background: var(--ink, #1c1917);
  border-color: var(--ink, #1c1917);
  color: #fff;
  font-weight: 700;
}

.page-ellipsis {
  padding: 0 4px;
  color: var(--text-faint, #a8a29e);
}
</style>
