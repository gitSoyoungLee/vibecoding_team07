<script setup>
const props = defineProps({
  location: { type: Object, required: true },
})
const emit = defineEmits(['close'])

function close() {
  emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape') close()
}
</script>

<template>
  <Transition name="modal" appear>
    <div class="modal-overlay" @click.self="close" @keydown="onKeydown" tabindex="-1" ref="overlayEl">
      <div class="modal-box">
        <button class="modal-close" @click="close" aria-label="닫기">×</button>

        <div v-if="location.image_url" class="modal-image">
          <img :src="location.image_url" :alt="location.title" />
        </div>
        <div v-else class="modal-image modal-image-fallback">이미지 없음</div>

        <div class="modal-body">
          <h2 class="modal-title">{{ location.title }}</h2>
          <p class="modal-address">
            {{ location.addr1 }}<span v-if="location.addr2"> {{ location.addr2 }}</span>
          </p>
          <p v-if="location.tel" class="modal-tel">📞 {{ location.tel }}</p>

          <!-- 카카오맵 시각화: 다음 작업에서 추가 예정 -->
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-box {
  position: relative;
  background: var(--bg, #fff);
  border-radius: 12px;
  width: min(480px, 100%);
  max-height: 88vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  z-index: 1;
}

.modal-image {
  position: relative;
  aspect-ratio: 4 / 3;
  background: var(--code-bg, #f4f3ec);
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
  color: var(--text, #6b6375);
}

.modal-body {
  padding: 20px;
  text-align: left;
}

.modal-title {
  margin: 0 0 8px;
  font-size: 1.4rem;
  font-weight: 700;
}

.modal-address {
  margin: 0 0 8px;
  font-size: 0.85rem;
  color: var(--text, #6b6375);
}

.modal-tel {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
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
