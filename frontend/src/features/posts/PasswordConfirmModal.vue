<script setup>
import { ref } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: '글 작성 시 등록한 수정용 비밀번호를 입력하세요.',
  },
})
const emit = defineEmits(['confirm', 'cancel'])

const password = ref('')

function confirm() {
  if (!password.value) return
  emit('confirm', password.value)
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('cancel')">
    <div class="modal-box">
      <div class="modal-head">
        <span class="modal-title">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <rect x="4" y="10" width="16" height="11" rx="2" />
            <path d="M8 10V7a4 4 0 0 1 8 0v3" />
          </svg>
          비밀번호 확인
        </span>
        <button class="modal-close" @click="emit('cancel')" aria-label="닫기">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <p class="modal-message">{{ message }}</p>

      <input
        v-model="password"
        type="password"
        class="password-input"
        placeholder="비밀번호"
        autofocus
        @keyup.enter="confirm"
      />

      <div class="modal-actions">
        <button class="btn-cancel" @click="emit('cancel')">취소</button>
        <button class="btn-confirm" @click="confirm">확인</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(28, 25, 23, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 16px;
}

.modal-box {
  width: 330px;
  max-width: 100%;
  background: var(--bg, #fff);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.modal-title svg {
  color: var(--accent-ink-strong, #ca8a04);
}

.modal-close {
  border: none;
  background: none;
  color: var(--text-muted, #78716c);
  cursor: pointer;
  padding: 2px;
  display: flex;
}

.modal-message {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted, #78716c);
  line-height: 1.5;
}

.password-input {
  border: 1.5px solid var(--border-strong, #e3ddd3);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13.5px;
  font-family: inherit;
  outline: none;
  color: var(--ink, #1c1917);
}

.modal-actions {
  display: flex;
  gap: 8px;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  border-radius: 10px;
  padding: 12px 0;
  text-align: center;
  font-size: 13.5px;
  cursor: pointer;
  border: none;
}

.btn-cancel {
  border: 1px solid var(--border-strong, #e3ddd3);
  background: transparent;
  color: var(--text, #57534e);
  font-weight: 600;
}

.btn-confirm {
  background: var(--accent, #facc15);
  color: var(--ink, #1c1917);
  font-weight: 700;
}
</style>
