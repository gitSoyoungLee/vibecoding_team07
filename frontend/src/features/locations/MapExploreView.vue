<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchLocations, districtOf, CATEGORIES } from './api'
import { loadKakaoMaps } from './kakaoMap'
import LocationDetailModal from './LocationDetailModal.vue'

const PAGE_SIZE = 8

const locations = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref('')
const selectedCategory = ref(CATEGORIES[0])
const keyword = ref('')
const activeKeyword = ref('')
const selectedLocation = ref(null)
const detailLocation = ref(null)
const mapReady = ref(false)
const mapMessage = ref('')

const mapContainer = ref(null)
let mapInstance = null
let kakaoRef = null
let markers = []
let requestSeq = 0

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

async function load() {
  const requestId = ++requestSeq
  loading.value = true
  error.value = ''
  try {
    const data = await fetchLocations({
      contentTypeIds: selectedCategory.value.ids,
      keyword: activeKeyword.value,
      page: page.value,
      limit: PAGE_SIZE,
    })
    if (requestId !== requestSeq) return // 더 최신 요청이 이미 나갔다면 이 응답은 버린다

    locations.value = data.items
    total.value = data.total
    // 사용자가 마커/목록을 직접 클릭하기 전까지는 자동으로 선택하지 않는다.
    // load()는 selectedLocation을 절대 건드리지 않으므로, 한 번 선택되면
    // 카테고리 변경·검색·페이지 이동으로 목록이 갱신돼도 카드가 계속 떠 있는다.
    renderMarkers()
  } catch (e) {
    if (requestId !== requestSeq) return

    error.value = e.message
    locations.value = []
    total.value = 0
  } finally {
    if (requestId === requestSeq) loading.value = false
  }
}

function renderMarkers() {
  if (!mapReady.value || !mapInstance) return

  markers.forEach((m) => m.setMap(null))
  markers = []

  const withCoords = locations.value.filter((loc) => loc.latitude != null && loc.longitude != null)
  if (withCoords.length === 0) return

  const bounds = new kakaoRef.maps.LatLngBounds()

  withCoords.forEach((loc) => {
    const position = new kakaoRef.maps.LatLng(loc.latitude, loc.longitude)
    const marker = new kakaoRef.maps.Marker({ map: mapInstance, position })
    kakaoRef.maps.event.addListener(marker, 'click', () => {
      selectedLocation.value = loc
    })
    markers.push(marker)
    bounds.extend(position)
  })

  mapInstance.setBounds(bounds)
}

function selectCategory(cat) {
  selectedCategory.value = cat
  page.value = 1
  load()
}

function onSearch() {
  activeKeyword.value = keyword.value.trim()
  page.value = 1
  load()
}

function goToPage(delta) {
  const next = page.value + delta
  if (next < 1 || next > totalPages.value) return
  page.value = next
  load()
}

function selectLocation(loc) {
  selectedLocation.value = loc
  if (mapInstance && loc.latitude != null && loc.longitude != null) {
    mapInstance.panTo(new kakaoRef.maps.LatLng(loc.latitude, loc.longitude))
  }
}

function openDetail(loc) {
  detailLocation.value = loc
}

function closeDetail() {
  detailLocation.value = null
}

watch(mapReady, (ready) => {
  if (ready) renderMarkers()
})

onMounted(async () => {
  try {
    kakaoRef = await loadKakaoMaps()
    mapInstance = new kakaoRef.maps.Map(mapContainer.value, {
      center: new kakaoRef.maps.LatLng(37.5665, 126.978),
      level: 8,
    })
    mapReady.value = true
  } catch (e) {
    mapMessage.value = e.message
  }
  load()
})
</script>

<template>
  <div class="map-page">
    <div class="map-list">
      <div class="list-head">
        <div class="search-input-wrap">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" stroke-linecap="round" />
          </svg>
          <input v-model="keyword" placeholder="지도에서 장소 검색" @keyup.enter="onSearch" />
        </div>
        <div class="category-chips">
          <button
            v-for="cat in CATEGORIES"
            :key="cat.key"
            class="chip"
            :class="{ active: cat.label === selectedCategory.label }"
            @click="selectCategory(cat)"
          >
            {{ cat.label }}
          </button>
        </div>
      </div>

      <div class="list-body">
        <div v-if="loading" class="list-empty">불러오는 중...</div>
        <div v-else-if="error" class="list-empty">{{ error }}</div>
        <div v-else-if="locations.length === 0" class="list-empty">표시할 장소가 없습니다.</div>
        <div
          v-for="loc in locations"
          v-else
          :key="loc.id"
          class="list-item"
          :class="{ active: selectedLocation && selectedLocation.id === loc.id }"
          @click="selectLocation(loc)"
        >
          <div class="thumb">
            <img v-if="loc.image_url" :src="loc.image_url" :alt="loc.title" />
          </div>
          <div class="item-body">
            <span class="item-title">
              {{ loc.title }}
              <span v-if="selectedLocation && selectedLocation.id === loc.id" class="selected-tag">선택됨</span>
            </span>
            <span class="item-sub">{{ districtOf(loc.addr1) }} · {{ selectedCategory.label === '전체' ? '장소' : selectedCategory.label }}</span>
          </div>
        </div>
      </div>

      <div class="list-foot">
        <span>{{ page }} / {{ totalPages }} 페이지</span>
        <div class="foot-nav">
          <button :disabled="page === 1" @click="goToPage(-1)">‹</button>
          <button :disabled="page === totalPages" @click="goToPage(1)">›</button>
        </div>
      </div>
    </div>

    <div class="map-pane">
      <div ref="mapContainer" class="map-canvas"></div>
      <p v-if="mapMessage" class="map-message">{{ mapMessage }}</p>

      <div v-if="selectedLocation" class="map-info-card">
        <div class="info-thumb">
          <img v-if="selectedLocation.image_url" :src="selectedLocation.image_url" :alt="selectedLocation.title" />
        </div>
        <div class="info-body">
          <span class="info-title">{{ selectedLocation.title }}</span>
          <span class="info-sub">{{ selectedLocation.addr1 }}</span>
          <div class="info-actions">
            <button class="btn-detail" @click="openDetail(selectedLocation)">상세 보기</button>
          </div>
        </div>
      </div>
    </div>

    <LocationDetailModal v-if="detailLocation" :location="detailLocation" @close="closeDetail" />
  </div>
</template>

<style scoped>
.map-page {
  display: grid;
  grid-template-columns: 380px 1fr;
  height: calc(100vh - 64px);
}

.map-list {
  border-right: 1px solid var(--border, #ece7df);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-head {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 11px;
  border-bottom: 1px solid var(--border, #ece7df);
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface, #faf9f7);
  border: 1px solid var(--border, #ece7df);
  border-radius: 10px;
  padding: 11px 14px;
  color: var(--text-faint, #a8a29e);
}

.search-input-wrap input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 13px;
  color: var(--ink, #1c1917);
}

.category-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  color: var(--text, #57534e);
  background: transparent;
  cursor: pointer;
  font-family: inherit;
}

.chip.active {
  background: var(--ink, #1c1917);
  border-color: var(--ink, #1c1917);
  color: #fff;
  font-weight: 600;
}

.list-body {
  flex: 1;
  overflow-y: auto;
}

.list-empty {
  padding: 24px 20px;
  color: var(--text-muted, #78716c);
  font-size: 13px;
}

.list-item {
  display: flex;
  gap: 13px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border, #ece7df);
  cursor: pointer;
}

.list-item.active {
  background: var(--accent-soft, #fef3c7);
}

.thumb {
  width: 66px;
  height: 52px;
  border-radius: 9px;
  background: var(--surface, #faf9f7);
  flex-shrink: 0;
  overflow: hidden;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--ink, #1c1917);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-tag {
  font-size: 10.5px;
  color: var(--accent-ink-strong, #ca8a04);
  font-weight: 700;
  margin-left: 4px;
}

.item-sub {
  font-size: 12px;
  color: var(--text-muted, #78716c);
}

.list-foot {
  padding: 13px 20px;
  border-top: 1px solid var(--border, #ece7df);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface, #faf9f7);
  font-size: 12.5px;
  color: var(--text-muted, #78716c);
}

.foot-nav {
  display: flex;
  gap: 6px;
}

.foot-nav button {
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 8px;
  background: transparent;
  color: var(--ink, #1c1917);
  cursor: pointer;
}

.foot-nav button:disabled {
  opacity: 0.4;
  cursor: default;
}

.map-pane {
  position: relative;
  background: var(--surface, #faf9f7);
}

.map-canvas {
  width: 100%;
  height: 100%;
}

.map-message {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  color: var(--text-muted, #78716c);
  background: var(--surface, #faf9f7);
}

.map-info-card {
  /* 카카오맵 내부 DOM(줌/스크롤 시 자체적으로 다시 그려지는 타일 레이어 등)이
     어떤 영향을 줘도 가려지거나 사라지지 않도록, 지도 영역에 종속되지 않는
     뷰포트 기준 고정 위치로 뺀다. */
  position: fixed;
  left: 398px;
  bottom: 18px;
  z-index: 30;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(30, 24, 14, 0.18);
  padding: 15px;
  display: flex;
  gap: 13px;
  max-width: 400px;
}

.info-thumb {
  width: 90px;
  height: 70px;
  border-radius: 10px;
  background: var(--surface, #faf9f7);
  flex-shrink: 0;
  overflow: hidden;
}

.info-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.info-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.info-sub {
  font-size: 12px;
  color: var(--text-muted, #78716c);
}

.info-actions {
  margin-top: 2px;
}

.btn-detail {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--ink, #1c1917);
  background: var(--accent, #facc15);
  border: none;
  border-radius: 6px;
  padding: 4px 9px;
  cursor: pointer;
}
</style>
