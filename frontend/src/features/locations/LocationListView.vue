<script setup>
import { ref, onMounted } from 'vue'
import { fetchLocations, districtOf } from './api'

const CATEGORIES = [
  { label: '전체', ids: null },
  { label: '관광지', ids: [12] },
  { label: '레포츠·문화시설', ids: [28, 14] },
  { label: '쇼핑', ids: [38] },
  { label: '숙박', ids: [32] },
  { label: '여행코스', ids: [25] },
  { label: '축제공연행사', ids: [15] },
]

const locations = ref([])
const loading = ref(false)
const error = ref('')
const selectedCategory = ref(CATEGORIES[0])
const keywordInput = ref('')
const activeKeyword = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    locations.value = await fetchLocations({
      contentTypeIds: selectedCategory.value.ids,
      keyword: activeKeyword.value,
    })
  } catch (e) {
    error.value = e.message
    locations.value = []
  } finally {
    loading.value = false
  }
}

function selectCategory(cat) {
  selectedCategory.value = cat
  load()
}

function onSearch() {
  activeKeyword.value = keywordInput.value.trim()
  load()
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
          :key="cat.label"
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
          <div v-for="loc in locations" :key="loc.id" class="location-card">
            <div class="card-image">
              <img v-if="loc.image_url" :src="loc.image_url" :alt="loc.title" />
              <div v-else class="card-image-fallback">이미지 없음</div>
            </div>
            <div class="card-title">{{ loc.title }}</div>
            <div class="card-district">{{ districtOf(loc.addr1) }}</div>
          </div>
        </div>
      </section>
    </div>
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
</style>
