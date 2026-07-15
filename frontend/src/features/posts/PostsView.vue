<template>
  <div class="posts-view">
    <h2>📋 자유 게시판</h2>

    <!-- 게시글 작성 폼 -->
    <div class="card form-card">
      <h3>새 글 작성</h3>
      <form @submit.prevent="handleCreatePost" class="post-form">
        <div class="form-row">
          <input v-model="form.nickname" placeholder="닉네임" required />
          <input v-model="form.password" type="password" placeholder="비밀번호" required />
        </div>
        <input v-model="form.title" placeholder="제목" required />
        <textarea v-model="form.content" placeholder="내용을 입력하세요..." rows="3" required></textarea>
        <button type="submit" class="btn-primary">글 등록</button>
      </form>
    </div>

    <!-- 검색 바 -->
    <div class="search-bar">
      <input v-model="searchQuery" @keyup.enter="loadPosts" placeholder="검색어를 입력하세요..." />
      <button @click="loadPosts" class="btn-secondary">검색</button>
    </div>

    <!-- 게시글 목록 -->
    <div v-if="loading" class="loading">로딩 중...</div>
    <div v-else class="post-list">
      <div v-for="post in posts" :key="post.id" class="card post-card" @click="openPostDetail(post.id)">
        <div class="post-header">
          <h3>{{ post.title }}</h3>
          <span class="author">작성자: {{ post.nickname }}</span>
        </div>
        <div class="post-meta">
          <span>👀 조회수 {{ post.views }}</span>
          <span>💬 댓글 {{ post.comment_count }}</span>
          <span>📅 {{ formatDate(post.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 상세 모달 (상세 보기, 삭제, 댓글) -->
    <div v-if="selectedPost" class="modal-overlay" @click.self="selectedPost = null">
      <div class="modal-content">
        <button class="close-btn" @click="selectedPost = null">✕</button>
        <h2>{{ selectedPost.title }}</h2>
        <p class="post-info">작성자: {{ selectedPost.nickname }} | 조회수: {{ selectedPost.views }}</p>
        <div class="post-body">{{ selectedPost.content }}</div>

        <div class="action-buttons">
          <button @click="handleDeletePost(selectedPost.id)" class="btn-danger">글 삭제</button>
        </div>

        <hr />

        <!-- 댓글 섹션 -->
        <div class="comments-section">
          <h4>💬 댓글 목록</h4>
          <div v-if="comments.length === 0" class="no-comments">댓글이 없습니다.</div>
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <strong>{{ comment.nickname }}</strong>
              <button @click="handleDeleteComment(comment.id)" class="btn-sm-danger">삭제</button>
            </div>
            <p>{{ comment.content }}</p>
          </div>

          <!-- 댓글 작성 폼 -->
          <form @submit.prevent="handleCreateComment" class="comment-form">
            <div class="form-row">
              <input v-model="commentForm.nickname" placeholder="닉네임" required />
              <input v-model="commentForm.password" type="password" placeholder="비밀번호" required />
            </div>
            <textarea v-model="commentForm.content" placeholder="댓글 내용..." rows="2" required></textarea>
            <button type="submit" class="btn-secondary">댓글 등록</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = 'http://127.0.0.1:8000'

const posts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedPost = ref(null)
const comments = ref([])

// 새 글 작성 폼 상태
const form = ref({
  nickname: '',
  password: '',
  title: '',
  content: '',
  category_id: null
})

// 댓글 작성 폼 상태
const commentForm = ref({
  nickname: '',
  password: '',
  content: ''
})

// 날짜 포맷팅
function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

// 1. 게시글 목록 조회
async function loadPosts() {
  loading.value = true
  try {
    const url = searchQuery.value
      ? `${API_BASE}/api/posts?search=${encodeURIComponent(searchQuery.value)}`
      : `${API_BASE}/api/posts`
    const res = await fetch(url)
    if (!res.ok) throw new Error('게시글 불러오기 실패')
    posts.value = await res.json()
  } catch (err) {
    alert(err.message)
  } finally {
    loading.value = false
  }
}

// 2. 게시글 생성
async function handleCreatePost() {
  try {
    const res = await fetch(`${API_BASE}/api/posts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    if (!res.ok) throw new Error('게시글 작성 실패')
    
    // 폼 초기화 및 목록 새로고침
    form.value = { nickname: '', password: '', title: '', content: '', category_id: null }
    alert('게시글이 등록되었습니다!')
    loadPosts()
  } catch (err) {
    alert(err.message)
  }
}

// 3. 게시글 상세 조회 (+ 조회수 증가)
async function openPostDetail(postId) {
  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}`)
    if (!res.ok) throw new Error('상세 정보 불러오기 실패')
    const data = await res.json()
    selectedPost.value = data.post
    comments.value = data.comments
    loadPosts() // 목록의 조회수/댓글수도 갱신
  } catch (err) {
    alert(err.message)
  }
}

// 4. 게시글 삭제
async function handleDeletePost(postId) {
  const password = prompt('삭제 비밀번호를 입력하세요:')
  if (!password) return

  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || '삭제 실패')
    }
    alert('게시글이 삭제되었습니다.')
    selectedPost.value = null
    loadPosts()
  } catch (err) {
    alert(err.message)
  }
}

// 5. 댓글 작성
async function handleCreateComment() {
  if (!selectedPost.value) return
  try {
    const res = await fetch(`${API_BASE}/api/posts/${selectedPost.value.id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(commentForm.value)
    })
    if (!res.ok) throw new Error('댓글 작성 실패')
    
    commentForm.value = { nickname: '', password: '', content: '' }
    openPostDetail(selectedPost.value.id) // 댓글 목록 새로고침
  } catch (err) {
    alert(err.message)
  }
}

// 6. 댓글 삭제
async function handleDeleteComment(commentId) {
  const password = prompt('댓글 삭제 비밀번호를 입력하세요:')
  if (!password) return

  try {
    const res = await fetch(`${API_BASE}/api/posts/comments/${commentId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    })
    if (!res.ok) throw new Error('비밀번호가 올바르지 않거나 삭제 실패')
    
    openPostDetail(selectedPost.value.id) // 댓글 목록 새로고침
  } catch (err) {
    alert(err.message)
  }
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.posts-view { max-width: 800px; margin: 0 auto; padding: 20px; }
.card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
.form-card { background: #f9f9f9; }
.post-form, .comment-form { display: flex; flex-direction: column; gap: 10px; }
.form-row { display: flex; gap: 10px; }
.form-row input { flex: 1; }
input, textarea { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
button { cursor: pointer; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-sm-danger { background: #dc3545; color: white; font-size: 11px; padding: 2px 6px; }
.search-bar { display: flex; gap: 10px; margin-bottom: 20px; }
.search-bar input { flex: 1; }
.post-card { cursor: pointer; transition: background 0.2s; }
.post-card:hover { background: #f1f1f1; }
.post-header { display: flex; justify-content: space-between; align-items: center; }
.post-meta { display: flex; gap: 15px; font-size: 12px; color: #666; margin-top: 8px; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 25px; border-radius: 8px; width: 90%; max-width: 600px; position: relative; max-height: 85vh; overflow-y: auto; }
.close-btn { position: absolute; top: 10px; right: 15px; background: none; font-size: 18px; border: none; }
.post-body { margin: 15px 0; line-height: 1.6; white-space: pre-wrap; }
.comments-section { margin-top: 15px; }
.comment-item { background: #f8f9fa; padding: 8px 12px; border-radius: 4px; margin-bottom: 8px; }
.comment-header { display: flex; justify-content: space-between; align-items: center; font-size: 13px; margin-bottom: 4px; }
</style>