<template>
  <div class="chat-widget">
    <button class="float-btn" @click="toggleChat">
      💬 {{ isOpen ? '닫기' : '챗봇' }}
    </button>

    <div v-if="isOpen" class="chat-box">
      <div class="chat-header">
        <div>
          <strong>AI 챗봇</strong>
          <div class="sub-title">여행지와 게시판을 도와드려요</div>
        </div>
        <button class="close-btn" @click="toggleChat">✕</button>
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
import { ref } from 'vue'
import { sendChatMessage } from './api'

const isOpen = ref(false)
const input = ref('')
const isLoading = ref(false)
const messages = ref([
  {
    role: 'bot',
    content: '안녕하세요! 여행 정보나 게시판 질문이 있으면 무엇이든 물어보세요.',
  },
])

function toggleChat() {
  isOpen.value = !isOpen.value
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
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.float-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.chat-box {
  position: absolute;
  bottom: 56px;
  right: 0;
  width: 300px;
  height: 380px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: #f5f7ff;
  border-bottom: 1px solid #e6e8f0;
}

.sub-title {
  font-size: 0.8rem;
  color: #666;
  margin-top: 2px;
}

.close-btn {
  border: none;
  background: transparent;
  font-size: 1rem;
  cursor: pointer;
}

.chat-body {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  background: #fafafa;
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
  background: #007bff;
  color: white;
}

.message-row.bot .bubble {
  background: #e9ecef;
  color: #222;
}

.chat-input-area {
  display: flex;
  border-top: 1px solid #e6e8f0;
  padding: 10px;
  gap: 8px;
  background: white;
}

.chat-input-area input {
  flex: 1;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 8px 10px;
  outline: none;
}

.chat-input-area button {
  border: none;
  background: #007bff;
  color: white;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
}

.chat-input-area button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>