<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { POST_CATEGORIES } from '../../constants/postCategories'
import PasswordConfirmModal from './PasswordConfirmModal.vue'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const route = useRoute()
const router = useRouter()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const editingPost = ref(false)
const editingComment = ref(null)
const pendingAction = ref(null)

const editForm = ref({ nickname: '', password: '', category_id: null, title: '', content: '' })
const commentForm = ref({ nickname: '', password: '', content: '' })
const commentEdit = ref({ content: '', password: '' })

function categoryName(id) {
  return POST_CATEGORIES.find((c) => c.id === Number(id))?.name || '자유게시판'
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
}

async function loadPost() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/posts/${route.params.id}`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    post.value = data.post
    comments.value = data.comments
    editingPost.value = false
    editingComment.value = null
  } catch {
    alert('게시글을 불러오지 못했습니다.')
    router.push('/posts')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/posts')
}

function requestEditPost() {
  pendingAction.value = { type: 'edit-post' }
}

function requestDeletePost() {
  pendingAction.value = { type: 'delete-post' }
}

function requestEditComment(comment) {
  pendingAction.value = { type: 'edit-comment', comment }
}

function requestDeleteComment(id) {
  pendingAction.value = { type: 'delete-comment', id }
}

function cancelPending() {
  pendingAction.value = null
}

async function onPasswordConfirm(password) {
  const action = pendingAction.value
  pendingAction.value = null

  if (action.type === 'edit-post') {
    editForm.value = {
      nickname: post.value.nickname,
      password,
      category_id: post.value.category_id,
      title: post.value.title,
      content: post.value.content,
    }
    editingPost.value = true
  } else if (action.type === 'delete-post') {
    await handleDeletePost(password)
  } else if (action.type === 'edit-comment') {
    commentEdit.value = { content: action.comment.content, password }
    editingComment.value = action.comment.id
  } else if (action.type === 'delete-comment') {
    await handleDeleteComment(action.id, password)
  }
}

async function updatePost() {
  const res = await fetch(`${API_BASE}/api/posts/${post.value.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(editForm.value),
  })

  if (!res.ok) {
    alert('비밀번호가 올바르지 않습니다.')
    return
  }

  editingPost.value = false
  await loadPost()
}

async function handleDeletePost(password) {
  const res = await fetch(`${API_BASE}/api/posts/${post.value.id}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })

  if (!res.ok) {
    alert('비밀번호가 올바르지 않습니다.')
    return
  }

  router.push('/posts')
}

async function handleCreateComment() {
  const res = await fetch(`${API_BASE}/api/posts/${post.value.id}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(commentForm.value),
  })

  if (!res.ok) {
    alert('댓글 등록 실패')
    return
  }

  commentForm.value = { nickname: '', password: '', content: '' }
  await loadPost()
}

function cancelEditComment() {
  editingComment.value = null
}

async function updateComment(id) {
  const res = await fetch(`${API_BASE}/api/posts/comments/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(commentEdit.value),
  })

  if (!res.ok) {
    alert('비밀번호가 올바르지 않습니다.')
    return
  }

  editingComment.value = null
  await loadPost()
}

async function handleDeleteComment(id, password) {
  const res = await fetch(`${API_BASE}/api/posts/comments/${id}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })

  if (!res.ok) {
    alert('비밀번호가 올바르지 않습니다.')
    return
  }

  await loadPost()
}

onMounted(loadPost)
</script>

<template>
  <div class="post-detail-page">
    <div v-if="loading" class="state-msg">불러오는 중...</div>

    <template v-else-if="post">
      <button class="back-link" @click="goBack">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M15 6l-6 6 6 6" />
        </svg>
        목록으로
      </button>

      <template v-if="!editingPost">
        <div class="post-head">
          <div class="post-head-top">
            <span class="post-cat">{{ categoryName(post.category_id) }}</span>
            <h1 class="post-title">{{ post.title }}</h1>
          </div>
          <div class="post-meta">
            <span class="meta-item">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="8" r="4" />
                <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
              </svg>
              {{ post.nickname }}
            </span>
            <span class="meta-item">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" />
                <circle cx="12" cy="12" r="2.5" />
              </svg>
              조회 {{ post.views }}
            </span>
            <span class="meta-item">{{ formatDate(post.created_at) }}</span>
            <div class="post-actions">
              <button class="btn-outline" @click="requestEditPost">수정</button>
              <button class="btn-danger-soft" @click="requestDeletePost">삭제</button>
            </div>
          </div>
        </div>

        <p class="post-body">{{ post.content }}</p>
      </template>

      <template v-else>
        <div class="edit-card">
          <h2 class="edit-title">게시글 수정</h2>
          <input v-model="editForm.nickname" placeholder="닉네임" />
          <select v-model="editForm.category_id">
            <option v-for="c in POST_CATEGORIES.slice(1)" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <input v-model="editForm.title" placeholder="제목" />
          <textarea rows="6" v-model="editForm.content"></textarea>
          <div class="edit-actions">
            <button class="btn-primary" @click="updatePost">수정 완료</button>
            <button class="btn-outline" @click="editingPost = false">취소</button>
          </div>
        </div>
      </template>

      <div class="comments-section">
        <h2 class="comments-title">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z" />
          </svg>
          댓글 {{ comments.length }}
        </h2>

        <div v-if="comments.length === 0" class="no-comments">댓글이 없습니다.</div>

        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <template v-if="editingComment !== comment.id">
            <div class="comment-head">
              <span class="comment-author">{{ comment.nickname }}</span>
              <div class="comment-actions">
                <button @click="requestEditComment(comment)">수정</button>
                <button class="danger" @click="requestDeleteComment(comment.id)">삭제</button>
              </div>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </template>

          <template v-else>
            <textarea rows="3" v-model="commentEdit.content"></textarea>
            <div class="edit-actions">
              <button class="btn-primary" @click="updateComment(comment.id)">저장</button>
              <button class="btn-outline" @click="cancelEditComment">취소</button>
            </div>
          </template>
        </div>

        <form class="comment-form" @submit.prevent="handleCreateComment">
          <div class="form-row">
            <input v-model="commentForm.nickname" placeholder="닉네임" required />
            <input v-model="commentForm.password" type="password" placeholder="비밀번호" required />
          </div>
          <textarea rows="3" v-model="commentForm.content" placeholder="댓글을 입력하세요." required></textarea>
          <button class="btn-dark" type="submit">댓글 등록</button>
        </form>
      </div>
    </template>

    <PasswordConfirmModal
      v-if="pendingAction"
      @confirm="onPasswordConfirm"
      @cancel="cancelPending"
    />
  </div>
</template>

<style scoped>
.post-detail-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px 40px 48px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.state-msg {
  padding: 60px 0;
  text-align: center;
  color: var(--text-muted, #78716c);
}

.back-link {
  display: flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
  border: none;
  background: none;
  padding: 0;
  font-size: 13px;
  color: var(--text-muted, #78716c);
  cursor: pointer;
}

.post-head {
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-bottom: 1px solid var(--border, #ece7df);
  padding-bottom: 22px;
}

.post-head-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.post-cat {
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-ink, #a16207);
  background: var(--accent-soft, #fef3c7);
  border-radius: 4px;
  padding: 3px 9px;
  white-space: nowrap;
}

.post-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.post-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 13px;
  color: var(--text-muted, #78716c);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.post-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.post-body {
  margin: 0;
  font-size: 15px;
  line-height: 1.7;
  color: var(--ink, #292524);
  min-height: 80px;
  white-space: pre-wrap;
}

.edit-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-title {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 4px;
}

input,
textarea,
select {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 9px;
  font-family: inherit;
  font-size: 13.5px;
  color: var(--ink, #1c1917);
  box-sizing: border-box;
}

.edit-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.btn-primary,
.btn-outline,
.btn-danger-soft,
.btn-dark {
  border-radius: 9px;
  padding: 11px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.btn-primary {
  border: none;
  background: var(--accent, #facc15);
  color: var(--ink, #1c1917);
}

.btn-outline {
  border: 1px solid var(--border-strong, #e3ddd3);
  background: transparent;
  color: var(--text, #57534e);
  padding: 7px 14px;
}

.btn-danger-soft {
  border: 1px solid #fde68a;
  background: #fef9e7;
  color: var(--accent-ink, #a16207);
  padding: 7px 14px;
}

.btn-dark {
  border: none;
  background: var(--ink, #1c1917);
  color: #fff;
  padding: 12px 0;
  text-align: center;
}

.comments-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
  border-top: 1px solid var(--border, #ece7df);
  padding-top: 22px;
}

.comments-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 16px;
  font-weight: 800;
  color: var(--accent-ink-strong, #ca8a04);
}

.no-comments {
  text-align: center;
  color: var(--text-muted, #78716c);
  padding: 20px 0;
}

.comment-item {
  background: var(--surface, #faf9f7);
  border: 1px solid var(--border, #ece7df);
  border-radius: 12px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.comment-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.comment-author {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink, #1c1917);
}

.comment-actions {
  display: flex;
  gap: 10px;
  font-size: 12px;
}

.comment-actions button {
  border: none;
  background: none;
  color: var(--text-muted, #78716c);
  cursor: pointer;
  padding: 0;
}

.comment-actions button.danger {
  color: var(--accent-ink, #a16207);
}

.comment-content {
  margin: 0;
  font-size: 14px;
  color: var(--ink, #292524);
}

.comment-date {
  font-size: 12px;
  color: var(--text-faint, #a8a29e);
}

.comment-form {
  border: 1px solid var(--border, #ece7df);
  border-radius: 12px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-row input {
  flex: 1;
}
</style>
