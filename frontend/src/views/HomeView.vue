<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CATEGORIES } from '../features/locations/api'
import { POST_CATEGORIES } from '../constants/postCategories'
import heroBanner from '../assets/hero-banner.jpg'

const router = useRouter()

const keyword = ref('')
function onSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/locations', query: q ? { keyword: q } : {} })
}

const locationCategories = CATEGORIES

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const posts = ref([])
const postsLoading = ref(false)
const postsError = ref('')
const selectedPostCategory = ref(POST_CATEGORIES[0])

// 상세 모달 및 에디터 관련 반응형 상태
const selectedPost = ref(null)
const comments = ref([])
const editingPost = ref(false)
const editingComment = ref(null)

const editForm = ref({
  nickname: '',
  password: '',
  category_id: null,
  title: '',
  content: ''
})

const commentForm = ref({
  nickname: '',
  password: '',
  content: ''
})

const commentEdit = ref({
  content: '',
  password: ''
})

const previewPosts = computed(() => {
  const list =
    selectedPostCategory.value.id === 0
      ? posts.value
      : posts.value.filter((p) => Number(p.category_id) === selectedPostCategory.value.id)
  return list.slice(0, 6)
})

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleString('ko-KR', {
    timeZone: 'Asia/Seoul'
  })
}

async function loadPosts() {
  postsLoading.value = true
  postsError.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/posts/?limit=50`)
    if (!res.ok) throw new Error('게시글을 불러오지 못했습니다.')
    posts.value = await res.json()
  } catch (e) {
    postsError.value = e.message
    posts.value = []
  } finally {
    postsLoading.value = false
  }
}

async function openPost(postId) {
  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}`)
    if (!res.ok) throw new Error()
    const data = await res.json()

    selectedPost.value = data.post
    comments.value = data.comments
    editingPost.value = false
    editingComment.value = null
  } catch {
    alert('게시글을 불러오지 못했습니다.')
  }
}

function closeModal() {
  selectedPost.value = null
  comments.value = []
  editingPost.value = false
  editingComment.value = null
}

// 게시글 수정 시작
function startEditPost() {
  editForm.value = {
    nickname: selectedPost.value.nickname,
    password: '',
    category_id: selectedPost.value.category_id,
    title: selectedPost.value.title,
    content: selectedPost.value.content
  }
  editingPost.value = true
}

// 게시글 수정 완료
async function updatePost() {
  const res = await fetch(
    `${API_BASE}/api/posts/${selectedPost.value.id}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editForm.value)
    }
  )

  if (!res.ok) {
    alert('비밀번호가 올바르지 않습니다.')
    return
  }

  editingPost.value = false
  await openPost(selectedPost.value.id)
  await loadPosts()
}

// 게시글 삭제
async function handleDeletePost(id) {
  const password = prompt('비밀번호를 입력하세요.')
  if (!password) return

  const res = await fetch(
    `${API_BASE}/api/posts/${id}`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password })
    }
  )

  if (!res.ok) {
    alert('비밀번호 오류')
    return
  }

  closeModal()
  await loadPosts()
}

// 댓글 등록
async function handleCreateComment() {
  const res = await fetch(
    `${API_BASE}/api/posts/${selectedPost.value.id}/comments`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(commentForm.value)
    }
  )

  if (!res.ok) {
    alert('댓글 등록 실패')
    return
  }

  commentForm.value = {
    nickname: '',
    password: '',
    content: ''
  }

  await openPost(selectedPost.value.id)
  await loadPosts()
}

// 댓글 수정 시작
function startEditComment(comment) {
  editingComment.value = comment.id
  commentEdit.value = {
    content: comment.content,
    password: ''
  }
}

// 댓글 수정 취소
function cancelEditComment() {
  editingComment.value = null
}

// 댓글 수정 완료
async function updateComment(id) {
  const res = await fetch(
    `${API_BASE}/api/posts/comments/${id}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(commentEdit.value)
    }
  )

  if (!res.ok) {
    alert('비밀번호가 올바르지 않습니다.')
    return
  }

  editingComment.value = null
  await openPost(selectedPost.value.id)
}

// 댓글 삭제
async function handleDeleteComment(id) {
  const password = prompt('비밀번호를 입력하세요.')
  if (!password) return

  const res = await fetch(
    `${API_BASE}/api/posts/comments/${id}`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password })
    }
  )

  if (!res.ok) {
    alert('삭제 실패')
    return
  }

  await openPost(selectedPost.value.id)
  await loadPosts()
}

onMounted(loadPosts)
</script>

<template>
  <div class="home-page">
    <div class="search-row">
      <div class="search-input-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2" />
          <line x1="16.2" y1="16.2" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input
          v-model="keyword"
          class="search-input"
          placeholder="궁금한 건 검색해보세요!"
          @keyup.enter="onSearch"
        />
      </div>
    </div>

    <div class="category-row">
      <RouterLink
        v-for="cat in locationCategories"
        :key="cat.key"
        :to="{ path: '/locations', query: { category: cat.key } }"
        class="category-chip"
      >
        {{ cat.label }}
      </RouterLink>
    </div>

    <img :src="heroBanner" alt="2026 Seoul" class="hero-banner" />

    <section class="board-preview">
      <h2 class="section-title">게시판</h2>

      <div class="board-row">
        <aside class="post-category-sidebar">
          <button
            v-for="cat in POST_CATEGORIES"
            :key="cat.id"
            class="category-btn"
            :class="{ active: cat.id === selectedPostCategory.id }"
            @click="selectedPostCategory = cat"
          >
            {{ cat.name }}
          </button>
        </aside>

        <div class="post-list">
          <div v-if="postsLoading">불러오는 중...</div>
          <div v-else-if="postsError">{{ postsError }}</div>
          <div v-else-if="previewPosts.length === 0">게시글이 없습니다.</div>
          <template v-else>
            <div
              v-for="post in previewPosts"
              :key="post.id"
              class="post-row"
              @click="openPost(post.id)"
            >
              <span class="post-title">{{ post.title }}</span>
              <span class="post-meta">{{ post.nickname }} · 댓글 {{ post.comment_count }}</span>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- 게시글 상세 & 수정 & 댓글 모달 -->
    <div
      v-if="selectedPost"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-content">
        <button
          class="close-btn"
          @click="closeModal"
        >
          ✕
        </button>

        <!-- 일반 조회 모드 -->
        <template v-if="!editingPost">
          <h2>{{ selectedPost.title }}</h2>

          <div class="post-info">
            <span>{{ selectedPost.nickname }}</span>
            <span>·</span>
            <span>{{ POST_CATEGORIES.find(c => c.id === Number(selectedPost.category_id))?.name || '자유게시판' }}</span>
            <span>·</span>
            <span>조회수 {{ selectedPost.views }}</span>
          </div>

          <div class="post-body">
            {{ selectedPost.content }}
          </div>

          <div class="action-buttons">
            <button
              class="btn-edit"
              @click="startEditPost"
            >
              수정
            </button>
            <button
              class="btn-delete"
              @click="handleDeletePost(selectedPost.id)"
            >
              삭제
            </button>
          </div>
        </template>

        <!-- 게시글 수정 모드 -->
        <template v-else>
          <h2>게시글 수정</h2>

          <div class="post-form">
            <input
              v-model="editForm.nickname"
              placeholder="닉네임"
            />

            <input
              type="password"
              v-model="editForm.password"
              placeholder="비밀번호"
            />

            <select v-model="editForm.category_id">
              <option
                v-for="category in POST_CATEGORIES.slice(1)"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>

            <input
              v-model="editForm.title"
              placeholder="제목"
            />

            <textarea
              rows="5"
              v-model="editForm.content"
            ></textarea>

            <div class="action-buttons">
              <button
                class="btn-primary"
                @click="updatePost"
              >
                수정 완료
              </button>
              <button
                class="btn-secondary"
                @click="editingPost = false"
              >
                취소
              </button>
            </div>
          </div>
        </template>

        <hr />

        <!-- 댓글 섹션 -->
        <div class="comments-section">
          <h3>💬 댓글</h3>

          <div
            v-if="comments.length === 0"
            class="no-comments"
          >
            댓글이 없습니다.
          </div>

          <div
            v-for="comment in comments"
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-header">
              <strong>{{ comment.nickname }}</strong>

              <div class="comment-actions">
                <button
                  class="btn-edit"
                  @click="startEditComment(comment)"
                >
                  수정
                </button>
                <button
                  class="btn-delete"
                  @click="handleDeleteComment(comment.id)"
                >
                  삭제
                </button>
              </div>
            </div>

            <!-- 댓글 내용 보기 상태 -->
            <template v-if="editingComment !== comment.id">
              <p>{{ comment.content }}</p>
              <small>{{ formatDate(comment.created_at) }}</small>
            </template>

            <!-- 댓글 수정 상태 -->
            <template v-else>
              <div class="comment-form edit-box">
                <textarea
                  rows="3"
                  v-model="commentEdit.content"
                ></textarea>

                <input
                  type="password"
                  v-model="commentEdit.password"
                  placeholder="비밀번호"
                />

                <div class="action-buttons edit-actions">
                  <button
                    class="btn-primary"
                    @click="updateComment(comment.id)"
                  >
                    저장
                  </button>
                  <button
                    class="btn-secondary"
                    @click="cancelEditComment"
                  >
                    취소
                  </button>
                </div>
              </div>
            </template>
          </div>

          <!-- 댓글 작성 -->
          <form
            class="comment-form"
            @submit.prevent="handleCreateComment"
          >
            <div class="form-row">
              <input
                v-model="commentForm.nickname"
                placeholder="닉네임"
                required
              />

              <input
                type="password"
                v-model="commentForm.password"
                placeholder="비밀번호"
                required
              />
            </div>

            <textarea
              rows="3"
              v-model="commentForm.content"
              placeholder="댓글을 입력하세요."
              required
            ></textarea>

            <button
              class="btn-secondary"
              type="submit"
            >
              댓글 등록
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-input-wrap {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text, #6b6375);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 6px;
  font-weight: 500;
  box-sizing: border-box;
}

.category-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.category-chip {
  padding: 8px 14px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 999px;
  text-decoration: none;
  color: inherit;
  font-weight: 600;
  font-size: 0.9rem;
}

.category-chip:hover {
  background: rgba(250, 204, 21, 0.2);
  border-color: rgba(234, 179, 8, 0.6);
}

.hero-banner {
  width: 100%;
  height: 280px;
  object-fit: cover;
  display: block;
  margin-bottom: 32px;
}

.section-title {
  text-align: left;
  margin: 0 0 16px;
  font-size: 1.3rem;
  font-weight: 700;
}

.board-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.post-category-sidebar {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 160px;
  flex-shrink: 0;
}

.category-btn {
  text-align: left;
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  font-weight: 500;
  cursor: pointer;
}

.category-btn.active {
  background: rgba(250, 204, 21, 0.2);
  border-color: rgba(234, 179, 8, 0.6);
  color: #92720a;
  font-weight: 700;
}

@media (prefers-color-scheme: dark) {
  .category-btn.active {
    background: rgba(250, 204, 21, 0.22);
    border-color: rgba(250, 204, 21, 0.55);
    color: #fde68a;
  }
}

.post-list {
  flex: 1;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 8px;
  overflow: hidden;
}

.post-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #e5e4e7);
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.post-row:last-child {
  border-bottom: none;
}

.post-row:hover {
  background: var(--code-bg, #f4f3ec);
}

.post-title {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-meta {
  flex-shrink: 0;
  font-size: 0.8rem;
  color: var(--text, #6b6375);
}

/* --- 모달 레이아웃 및 폼 통합 스타일 --- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 800px;
  max-width: 95%;
  max-height: 85vh;
  overflow: auto;
  background: white;
  border-radius: 10px;
  padding: 30px;
  position: relative;
  box-sizing: border-box;
}

.close-btn {
  position: absolute;
  right: 20px;
  top: 20px;
  border: none;
  background: none;
  font-size: 28px;
  cursor: pointer;
}

.post-info {
  display: flex;
  gap: 8px;
  color: var(--text, #6b6375);
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.post-body {
  margin: 25px 0;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 포스트 작성 및 댓글 폼 관련 */
.post-form,
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-row input {
  flex: 1;
}

input,
textarea,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 6px;
  box-sizing: border-box;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.comments-section {
  margin-top: 20px;
}

.comment-item {
  background: #f7f7f7;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.comment-item p {
  margin: 6px 0;
  line-height: 1.5;
}

.comment-item small {
  color: #888;
  font-size: 11px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.no-comments {
  text-align: center;
  color: #777;
  padding: 20px;
}

/* --- 공통 기능 버튼 클래스 --- */
.btn-primary {
  background: #0d6efd;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 600;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 600;
}

.btn-edit,
.btn-delete {
  width: 70px;
  height: 34px;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.btn-edit {
  background: #6c757d;
}

.btn-delete {
  background: #dc3545;
}

.edit-box {
  margin-top: 10px;
}

.edit-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
</style>