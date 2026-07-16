<script setup>
import { onMounted, ref } from 'vue'
import { loadKakaoMaps } from './kakaoMap'

const props = defineProps({
  location: { type: Object, required: true },
})
const emit = defineEmits(['close'])

const mapContainer = ref(null)
const mapError = ref('')

function close() {
  emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape') close()
}

const hasCoords = props.location.latitude != null && props.location.longitude != null

onMounted(async () => {
  if (!hasCoords) return

  try {
    const kakao = await loadKakaoMaps()
    const center = new kakao.maps.LatLng(props.location.latitude, props.location.longitude)
    const map = new kakao.maps.Map(mapContainer.value, {
      center,
      level: 4,
    })
    new kakao.maps.Marker({ map, position: center })
  } catch (e) {
    mapError.value = e.message
  }
})
</script>

<template>
  <Transition name="modal" appear>
    <div class="modal-overlay" @click.self="close" @keydown="onKeydown" tabindex="-1" ref="overlayEl">
      <div class="modal-box">
        <button class="modal-close" @click="close" aria-label="닫기">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>

        <div v-if="location.image_url" class="modal-image">
          <img :src="location.image_url" :alt="location.title" />
        </div>
        <div v-else class="modal-image modal-image-fallback">이미지 없음</div>

        <div class="modal-body">
          <h2 class="modal-title">{{ location.title }}</h2>
          <p class="modal-address">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10z" />
              <circle cx="12" cy="11" r="2.2" />
            </svg>
            {{ location.addr1 }}<span v-if="location.addr2"> {{ location.addr2 }}</span>
          </p>
          <p v-if="location.tel" class="modal-tel">{{ location.tel }}</p>

          <div v-show="hasCoords && !mapError" ref="mapContainer" class="modal-map"></div>
          <p v-if="mapError" class="modal-map-fallback">{{ mapError }}</p>
          <p v-else-if="!hasCoords" class="modal-map-fallback">지도 정보 없음</p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(28, 25, 23, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-box {
  position: relative;
  background: var(--bg, #fff);
  border-radius: 18px;
  width: min(560px, 100%);
  max-height: 88vh;
  overflow-y: auto;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
}

.modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: #fff;
  color: var(--ink, #1c1917);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
}

.modal-image {
  position: relative;
  aspect-ratio: 16 / 9;
  background: var(--surface, #faf9f7);
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.modal-image-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-faint, #a8a29e);
}

.modal-body {
  padding: 22px 26px 26px;
  text-align: left;
}

.modal-title {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.modal-address {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0 0 8px;
  font-size: 13.5px;
  color: var(--text-muted, #78716c);
}

.modal-tel {
  margin: 0;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text, #57534e);
}

.modal-map {
  margin-top: 16px;
  width: 100%;
  height: 190px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border, #ece7df);
}

.modal-map-fallback {
  margin-top: 16px;
  color: var(--text-muted, #78716c);
  font-size: 0.85rem;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-box,
.modal-leave-active .modal-box {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-box,
.modal-leave-to .modal-box {
  transform: scale(0.92);
}
</style>
