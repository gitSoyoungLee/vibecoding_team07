<script setup>
import { ref } from 'vue'

const isOpen = ref(false)
const messages = ref([
  { role: 'assistant', text: '안녕하세요! 여행 관련 질문을 편하게 물어보세요.' }
])
const input = ref('')
const isLoading = ref(false)

async function sendMessage() {
  const text = input.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', text })
  input.value = ''
  isLoading.value = true

  try {
    const response = await fetch('http://127.0.0.1:8000/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })

    const data = await response.json()
    messages.value.push({ role: 'assistant', text: data.reply })
  } catch (error) {
    messages.value.push({ role: 'assistant', text: '챗봇 응답을 가져오지 못했습니다.' })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="page">
    <RouterView />

    <button class="float-button" @click="isOpen = !isOpen">
      {{ isOpen ? '닫기' : '챗봇 열기' }}
    </button>

    <div v-if="isOpen" class="chat-panel">
      <div class="chat-header">AI 챗봇</div>
      <div class="chat-body">
        <div v-for="(msg, idx) in messages" :key="idx" class="bubble" :class="msg.role">
          {{ msg.text }}
        </div>
        <div v-if="isLoading" class="bubble assistant">답변 생성 중...</div>
      </div>
      <div class="chat-input-row">
        <input v-model="input" @keyup.enter="sendMessage" placeholder="메시지를 입력하세요" />
        <button @click="sendMessage">전송</button>
      </div>
    </div>
  </div>
</template>
