<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchLocations, districtOf } from '../locations/api'
import LocationDetailModal from '../locations/LocationDetailModal.vue'

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']

const today = new Date()
today.setHours(0, 0, 0, 0)
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth()) // 0-based

const festivals = ref([])
const loading = ref(false)
const error = ref('')
const selectedDate = ref(null) // 'YYYY-MM-DD' | null
const selectedLocation = ref(null)

function openDetail(item) {
  selectedLocation.value = item
}

function closeDetail() {
  selectedLocation.value = null
}

const monthLabel = computed(() => `${viewYear.value}년 ${viewMonth.value + 1}월`)

function parseApiDate(value) {
  if (!value || value.length !== 8) return null
  const y = Number(value.slice(0, 4))
  const m = Number(value.slice(4, 6)) - 1
  const d = Number(value.slice(6, 8))
  const date = new Date(y, m, d)
  return Number.isNaN(date.getTime()) ? null : date
}

function toKey(date) {
  return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`
}

const datedFestivals = computed(() =>
  festivals.value
    .map((item) => ({
      ...item,
      startDate: parseApiDate(item.event_start_date),
      endDate: parseApiDate(item.event_end_date),
    }))
    .filter((item) => item.startDate && item.endDate),
)

const undatedFestivals = computed(() => festivals.value.filter((item) => !item.event_start_date))

function festivalsOn(date) {
  return datedFestivals.value.filter((item) => date >= item.startDate && date <= item.endDate)
}

const calendarCells = computed(() => {
  const firstOfMonth = new Date(viewYear.value, viewMonth.value, 1)
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  const startWeekday = firstOfMonth.getDay()

  const cells = []
  for (let i = 0; i < startWeekday; i++) {
    cells.push({ key: `lead-${i}`, day: null })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const cellDate = new Date(viewYear.value, viewMonth.value, d)
    const isToday = cellDate.getTime() === today.getTime()
    const weekday = cellDate.getDay()
    const dayFestivals = festivalsOn(cellDate)
    cells.push({
      key: `day-${d}`,
      day: d,
      isToday,
      weekday,
      dateKey: toKey(cellDate),
      count: dayFestivals.length,
      names: dayFestivals.slice(0, 2).map((f) => f.title),
    })
  }
  while (cells.length % 7 !== 0) {
    cells.push({ key: `trail-${cells.length}`, day: null })
  }
  return cells
})

const selectedDayFestivals = computed(() => {
  if (!selectedDate.value) return []
  const [y, m, d] = selectedDate.value.split('-').map(Number)
  return festivalsOn(new Date(y, m - 1, d))
})

const upcomingFestivals = computed(() =>
  datedFestivals.value
    .filter((item) => item.endDate >= today)
    .sort((a, b) => {
      const aOngoing = a.startDate <= today
      const bOngoing = b.startDate <= today
      if (aOngoing !== bOngoing) return aOngoing ? -1 : 1
      return a.startDate - b.startDate
    })
    .slice(0, 30),
)

const sidebarFestivals = computed(() => (selectedDate.value ? selectedDayFestivals.value : upcomingFestivals.value))

function goToday() {
  viewYear.value = today.getFullYear()
  viewMonth.value = today.getMonth()
  selectedDate.value = toKey(today)
}

function shiftMonth(delta) {
  const next = new Date(viewYear.value, viewMonth.value + delta, 1)
  viewYear.value = next.getFullYear()
  viewMonth.value = next.getMonth()
  selectedDate.value = null
}

function selectDay(cell) {
  if (!cell.day) return
  selectedDate.value = selectedDate.value === cell.dateKey ? null : cell.dateKey
}

function formatRange(item) {
  const s = item.startDate
  const e = item.endDate
  const fmt = (d) => `${d.getMonth() + 1}.${d.getDate()}`
  if (toKey(s) === toKey(e)) return fmt(s)
  return `${fmt(s)} ~ ${fmt(e)}`
}

async function loadFestivals() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchLocations({ contentTypeIds: [15], page: 1, limit: 250 })
    festivals.value = data.items
  } catch (e) {
    error.value = e.message
    festivals.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadFestivals)
</script>

<template>
  <div class="festival-page">
    <div class="calendar-pane">
      <div class="calendar-head">
        <h1>{{ monthLabel }}</h1>
        <div class="calendar-nav">
          <button @click="shiftMonth(-1)">‹</button>
          <button class="today-btn" @click="goToday">오늘</button>
          <button @click="shiftMonth(1)">›</button>
        </div>
      </div>

      <div class="calendar-grid">
        <div class="weekday-row">
          <span
            v-for="(w, idx) in WEEKDAYS"
            :key="w"
            class="weekday"
            :class="{ sun: idx === 0, sat: idx === 6 }"
          >
            {{ w }}
          </span>
        </div>
        <div class="days-grid">
          <div
            v-for="cell in calendarCells"
            :key="cell.key"
            class="day-cell"
            :class="{
              'sun-col': cell.weekday === 0,
              'sat-col': cell.weekday === 6,
              clickable: cell.day && cell.count > 0,
              selected: cell.day && cell.dateKey === selectedDate,
            }"
            @click="selectDay(cell)"
          >
            <span v-if="cell.day" class="day-number" :class="{ today: cell.isToday }">{{ cell.day }}</span>
            <div v-if="cell.count > 0" class="day-festivals">
              <span v-for="name in cell.names" :key="name" class="day-festival-chip">{{ name }}</span>
              <span v-if="cell.count > cell.names.length" class="day-festival-more">+{{ cell.count - cell.names.length }}</span>
            </div>
          </div>
        </div>
      </div>

      <p class="calendar-note">날짜가 표시된 축제만 캘린더에 배지로 나타납니다. 날짜 정보가 없는 축제는 사이드바 하단에서 확인하세요.</p>
    </div>

    <div class="festival-sidebar">
      <h2 class="sidebar-title">
        {{ selectedDate ? `${Number(selectedDate.split('-')[1])}월 ${Number(selectedDate.split('-')[2])}일 진행 축제` : '진행중 · 예정 축제' }}
      </h2>

      <div v-if="loading" class="sidebar-empty">불러오는 중...</div>
      <div v-else-if="error" class="sidebar-empty">{{ error }}</div>
      <div v-else-if="sidebarFestivals.length === 0" class="sidebar-empty">
        {{ selectedDate ? '이 날짜에 진행하는 축제가 없습니다.' : '진행중이거나 예정된 축제가 없습니다.' }}
      </div>

      <div v-else class="festival-list">
        <div
          v-for="item in sidebarFestivals"
          :key="item.id"
          class="festival-item"
          @click="openDetail(item)"
        >
          <div class="festival-badge">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" />
            </svg>
          </div>
          <div class="festival-info">
            <span class="festival-name">{{ item.title }}</span>
            <span class="festival-meta">{{ formatRange(item) }} · {{ districtOf(item.addr1) }}</span>
          </div>
        </div>
      </div>

      <RouterLink class="more-link" :to="{ path: '/locations', query: { category: 'festival' } }">
        전체 축제 더 보기 →
      </RouterLink>

      <div v-if="undatedFestivals.length" class="undated-section">
        <h3 class="undated-title">날짜 미정 축제 ({{ undatedFestivals.length }})</h3>
        <div class="festival-list">
          <div
            v-for="item in undatedFestivals.slice(0, 10)"
            :key="item.id"
            class="festival-item"
            @click="openDetail(item)"
          >
            <div class="festival-badge">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" />
              </svg>
            </div>
            <div class="festival-info">
              <span class="festival-name">{{ item.title }}</span>
              <span class="festival-meta">{{ districtOf(item.addr1) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <LocationDetailModal
      v-if="selectedLocation"
      :location="selectedLocation"
      @close="closeDetail"
    />
  </div>
</template>

<style scoped>
.festival-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 40px 44px;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 32px;
}

.calendar-pane {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.calendar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.calendar-head h1 {
  font-size: 24px;
  font-weight: 800;
}

.calendar-nav {
  display: flex;
  gap: 6px;
}

.calendar-nav button {
  height: 32px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 8px;
  background: transparent;
  color: var(--text, #57534e);
  cursor: pointer;
  font-family: inherit;
}

.calendar-nav button:not(.today-btn) {
  width: 32px;
}

.today-btn {
  padding: 0 12px;
  font-size: 12.5px;
  font-weight: 600;
}

.calendar-grid {
  border: 1px solid var(--border, #ece7df);
  border-radius: 14px;
  overflow: hidden;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--surface, #faf9f7);
  border-bottom: 1px solid var(--border, #ece7df);
}

.weekday {
  padding: 10px 0;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--text, #57534e);
}

.weekday.sun {
  color: #dc2626;
}

.weekday.sat {
  color: #2563eb;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.day-cell {
  border-bottom: 1px solid var(--border, #ece7df);
  border-left: 1px solid var(--border, #ece7df);
  padding: 7px 9px;
  min-height: 88px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.day-cell.clickable {
  cursor: pointer;
}

.day-cell.selected {
  background: var(--accent-soft, #fef3c7);
}

.day-cell:nth-child(7n + 1) {
  border-left: none;
}

.day-number {
  font-size: 12px;
  color: var(--ink, #1c1917);
}

.day-cell.sun-col .day-number {
  color: #dc2626;
}

.day-cell.sat-col .day-number {
  color: #2563eb;
}

.day-number.today {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--accent, #facc15);
  color: var(--ink, #1c1917) !important;
  border-radius: 999px;
  font-weight: 700;
  font-size: 11.5px;
}

.day-festivals {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.day-festival-chip {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 5px;
  border-radius: 5px;
  background: var(--accent-soft, #fef3c7);
  color: var(--accent-ink-strong, #ca8a04);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.day-festival-more {
  font-size: 10px;
  color: var(--text-faint, #a8a29e);
}

.calendar-note {
  margin: 0;
  font-size: 12px;
  color: var(--text-faint, #a8a29e);
  line-height: 1.5;
}

.festival-sidebar {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 800;
  margin-top: 6px;
}

.sidebar-empty {
  color: var(--text-muted, #78716c);
  font-size: 13px;
  padding: 12px 0;
}

.festival-list {
  border: 1px solid var(--border, #ece7df);
  border-radius: 14px;
  overflow: hidden;
  max-height: 420px;
  overflow-y: auto;
}

.festival-item {
  display: flex;
  gap: 13px;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #ece7df);
  cursor: pointer;
  text-decoration: none;
  color: inherit;
}

.festival-item:last-child {
  border-bottom: none;
}

.festival-badge {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 8px;
  background: var(--accent-soft, #fef3c7);
  color: var(--accent-ink, #a16207);
  display: flex;
  align-items: center;
  justify-content: center;
}

.festival-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.festival-name {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink, #1c1917);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.festival-meta {
  font-size: 11.5px;
  color: var(--text-muted, #78716c);
}

.more-link {
  align-self: flex-start;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--accent-ink-strong, #ca8a04);
  text-decoration: none;
}

.undated-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.undated-title {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-muted, #78716c);
}
</style>
