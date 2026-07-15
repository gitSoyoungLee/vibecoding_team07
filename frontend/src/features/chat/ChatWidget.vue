<template>
  <div class="chat-widget">
    <button class="float-btn" @click="toggleChat">
      💬 {{ isOpen ? '닫기' : '챗봇' }}
    </button>

    <div v-if="isOpen" class="chat-box" :style="boxStyle">
      <div class="chat-header" @pointerdown="startDrag">
        <div>
          <strong>AI 챗봇</strong>
          <div class="sub-title">여행지와 게시판을 도와드려요</div>
        </div>
        <button class="close-btn" @click.stop="toggleChat">✕</button>
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

        <div v-if="isLoading" class="message-row bot">
          <div class="bubble typing">답변 생성 중...</div>
        </div>
      </div>

      <div class="resize-handle" @pointerdown="startResize" />

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

const STORAGE_KEY = 'exploreseoul-chat-history'
const isOpen = ref(false)
const input = ref('')
const isLoading = ref(false)
const isDragging = ref(false)
const isResizing = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 320, height: 420 })
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
    size.value = {
      width: clamp(resizeStart.value.width + (event.clientX - resizeStart.value.x), 280, window.innerWidth - 24),
      height: clamp(resizeStart.value.height + (event.clientY - resizeStart.value.y), 320, window.innerHeight - 24),
    }
    position.value = {
      x: clamp(position.value.x, 8, window.innerWidth - size.value.width - 8),
      y: clamp(position.value.y, 8, window.innerHeight - size.value.height - 8),
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
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.2);
  font-weight: 700;
}

.chat-box {
  position: fixed;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  cursor: grab;
}

.chat-header strong {
  color: #0f172a;
}

.sub-title {
  font-size: 0.8rem;
  color: #475569;
  margin-top: 2px;
}

.close-btn {
  border: none;
  background: transparent;
  font-size: 1rem;
  cursor: pointer;
  color: #334155;
}

.chat-body {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  background: #f8fafc;
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
  padding: 8px 10px;
  border-radius: 12px;
  line-height: 1.4;
  font-size: 0.95rem;
  white-space: pre-wrap;
}

.message-row.user .bubble {
  background: #2563eb;
  color: white;
}

.message-row.bot .bubble {
  background: #e2e8f0;
  color: #0f172a;
}

.resize-handle {
  width: 16px;
  height: 16px;
  align-self: flex-end;
  cursor: nwse-resize;
  margin-right: 4px;
  margin-bottom: 4px;
  background: linear-gradient(135deg, transparent 40%, #94a3b8 40%, #94a3b8 60%, transparent 60%);
}

.chat-input-area {
  display: flex;
  border-top: 1px solid #e2e8f0;
  padding: 10px;
  gap: 8px;
  background: white;
}

.chat-input-area input {
  flex: 1;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 10px;
  outline: none;
}

.chat-input-area button {
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
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