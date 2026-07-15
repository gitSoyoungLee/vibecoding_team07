<template>
  <div class="chat-widget">
    <button class="float-btn" @click="isOpen = !isOpen">
      💬 {{ isOpen ? '닫기' : '챗봇' }}
    </button>
    <div v-if="isOpen" class="chat-box">
      <div class="chat-header">AI 챗봇</div>
      <div class="chat-body">챗봇 영역입니다.</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const isOpen = ref(false)
</script>

<style scoped>
.chat-widget { position: fixed; bottom: 20px; right: 20px; }
.float-btn { background: #007bff; color: white; border: none; padding: 10px 16px; border-radius: 20px; cursor: pointer; }
.chat-box { position: absolute; bottom: 50px; right: 0; width: 250px; height: 300px; background: white; border: 1px solid #ccc; border-radius: 8px; padding: 10px; }
</style>