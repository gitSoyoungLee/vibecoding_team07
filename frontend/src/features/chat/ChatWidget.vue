<template>
  <div class="chat-widget">
    <button class="float-btn" @click="toggleChat">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z" />
      </svg>
      {{ isOpen ? '닫기' : '챗봇' }}
    </button>

    <div v-if="isOpen" class="chat-box" :style="boxStyle">
      <div class="resize-handle" @pointerdown="startResize" />

      <div class="chat-header" @pointerdown="startDrag">
        <div class="chat-header-left">
          <div class="chat-avatar">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2">
              <path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z" />
            </svg>
          </div>
          <div>
            <strong>AI 챗봇</strong>
            <div class="sub-title">여행지와 게시판을 도와드려요</div>
          </div>
        </div>
        <button class="close-btn" @click.stop="toggleChat" aria-label="닫기">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <div class="chat-body">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message-row', message.role === 'user' ? 'user' : 'bot']"
        >
          <div class="bubble">
            {{ message.content }}
          </div>
        </div>

        <div v-if="messages.length <= 1" class="faq-chips">
          <button
            v-for="faq in faqSuggestions"
            :key="faq"
            class="faq-chip"
            @click="sendSuggestion(faq)"
          >
            {{ faq }}
          </button>
        </div>

        <div v-if="isLoading" class="message-row bot">
          <div class="bubble typing">답변 생성 중...</div>
        </div>
      </div>

      <form class="chat-input-area" @submit.prevent="submitMessage">
        <input
          v-model="input"
          type="text"
          placeholder="메시지를 입력하세요"
          :disabled="isLoading"
        />
        <button type="submit" :disabled="isLoading || !input.trim()">전송</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { sendChatMessage } from './api'

const STORAGE_KEY = 'localhub-chat-history'
const faqSuggestions = ['관광지 추천해줘', '이번 주 축제 알려줘', '쇼핑하는 곳 추천해줘']
const isOpen = ref(false)
const input = ref('')
const isLoading = ref(false)
const isDragging = ref(false)
const isResizing = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 320, height: 420, left: 0, top: 0 })
const position = ref({ x: 0, y: 0 })
const size = ref({ width: 320, height: 420 })

const messages = ref(loadMessages())

const boxStyle = computed(() => ({
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  width: `${size.value.width}px`,
  height: `${size.value.height}px`,
}))

function loadMessages() {
  if (typeof window === 'undefined') return [{ role: 'bot', content: '안녕하세요! 여행 정보나 게시판 질문이 있으면 무엇이든 물어보세요.' }]

  try {
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (error) {
    console.warn('대화 히스토리를 불러오지 못했습니다.', error)
  }

  return [{ role: 'bot', content: '안녕하세요! 여행 정보나 게시판 질문이 있으면 무엇이든 물어보세요.' }]
}

function persistMessages() {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
}

watch(messages, persistMessages, { deep: true })

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function setDefaultPosition() {
  const width = Math.min(320, window.innerWidth - 24)
  const height = Math.min(460, window.innerHeight - 120)
  size.value = { width, height }
  position.value = {
    x: Math.max(12, window.innerWidth - width - 12),
    y: Math.max(12, window.innerHeight - height - 12),
  }
}

function toggleChat() {
  isOpen.value = !isOpen.value
}

function startDrag(event) {
  if (window.innerWidth < 768) return
  const rect = event.currentTarget.getBoundingClientRect()
  dragOffset.value = { x: event.clientX - rect.left, y: event.clientY - rect.top }
  isDragging.value = true
}

function startResize(event) {
  event.preventDefault()
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: size.value.width,
    height: size.value.height,
    left: position.value.x,
    top: position.value.y,
  }
  isResizing.value = true
}

function handlePointerMove(event) {
  if (isDragging.value) {
    position.value = {
      x: clamp(event.clientX - dragOffset.value.x, 8, window.innerWidth - size.value.width - 8),
      y: clamp(event.clientY - dragOffset.value.y, 8, window.innerHeight - size.value.height - 8),
    }
  }

  if (isResizing.value) {
    // 좌측 상단 핸들: 우측/하단 모서리를 고정한 채 좌측·상단으로 커진다.
    const rightEdge = resizeStart.value.left + resizeStart.value.width
    const bottomEdge = resizeStart.value.top + resizeStart.value.height

    const newWidth = clamp(
      resizeStart.value.width - (event.clientX - resizeStart.value.x),
      280,
      window.innerWidth - 24
    )
    const newHeight = clamp(
      resizeStart.value.height - (event.clientY - resizeStart.value.y),
      320,
      window.innerHeight - 24
    )

    size.value = { width: newWidth, height: newHeight }
    position.value = {
      x: clamp(rightEdge - newWidth, 8, window.innerWidth - newWidth - 8),
      y: clamp(bottomEdge - newHeight, 8, window.innerHeight - newHeight - 8),
    }
  }
}

function handlePointerUp() {
  isDragging.value = false
  isResizing.value = false
}

async function submitMessage() {
  const trimmed = input.value.trim()
  if (!trimmed || isLoading.value) return

  messages.value.push({ role: 'user', content: trimmed })
  input.value = ''
  isLoading.value = true

  try {
    const data = await sendChatMessage(trimmed)
    messages.value.push({ role: 'bot', content: data.reply })
  } catch (error) {
    messages.value.push({ role: 'bot', content: '죄송해요. 잠시 후 다시 시도해주세요.' })
  } finally {
    isLoading.value = false
  }
}

function sendSuggestion(text) {
  input.value = text
  submitMessage()
}

onMounted(() => {
  setDefaultPosition()
  window.addEventListener('pointermove', handlePointerMove)
  window.addEventListener('pointerup', handlePointerUp)
})

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerup', handlePointerUp)
})
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.float-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #2563eb;
  color: #fff;
  border: none;
  padding: 14px 20px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
  font-weight: 700;
  font-size: 14px;
  font-family: inherit;
}

.chat-box {
  position: fixed;
  background: var(--bg, #fff);
  border-radius: 18px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: var(--ink, #1c1917);
  color: #fff;
  cursor: grab;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-avatar {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  background: #2563eb;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-header strong {
  font-size: 14.5px;
  font-weight: 800;
}

.sub-title {
  font-size: 11.5px;
  color: #a8a29e;
  margin-top: 2px;
}

.close-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #a8a29e;
  display: flex;
}

.chat-body {
  flex: 1;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  background: var(--surface, #faf9f7);
}

.message-row {
  display: flex;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.bot {
  justify-content: flex-start;
}

.bubble {
  max-width: 85%;
  padding: 11px 14px;
  line-height: 1.55;
  font-size: 13.5px;
  white-space: pre-wrap;
}

.message-row.bot .bubble {
  background: #fff;
  border: 1px solid var(--border, #ece7df);
  color: var(--ink, #1c1917);
  border-radius: 4px 14px 14px 14px;
}

.message-row.user .bubble {
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  border-radius: 14px 4px 14px 14px;
}

.faq-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.faq-chip {
  border: 1px solid #2563eb;
  color: #1d4ed8;
  background: #fff;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  font-family: inherit;
}

.resize-handle {
  position: absolute;
  left: 3px;
  top: 3px;
  width: 16px;
  height: 16px;
  z-index: 1;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 40%, #cbd5e1 40%, #cbd5e1 60%, transparent 60%);
  border-radius: 3px;
}

.chat-input-area {
  display: flex;
  border-top: 1px solid var(--border, #ece7df);
  padding: 10px;
  gap: 8px;
  background: #fff;
}

.chat-input-area input {
  flex: 1;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 8px;
  padding: 8px 10px;
  outline: none;
  font-family: inherit;
}

.chat-input-area button {
  border: none;
  background: var(--ink, #1c1917);
  color: white;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-family: inherit;
}

.chat-input-area button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-widget {
    bottom: 12px;
    right: 12px;
  }

  .chat-box {
    left: 12px !important;
    right: 12px !important;
    top: auto !important;
    bottom: 70px !important;
    width: auto !important;
    height: min(460px, calc(100vh - 90px)) !important;
  }
}
</style>
