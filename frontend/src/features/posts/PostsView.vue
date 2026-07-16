<template>
  <div class="posts-view">
    <div class="page-head">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <rect x="4" y="4" width="16" height="17" rx="2" />
        <path d="M8 9h8M8 13h8M8 17h5" />
      </svg>
      <h1>자유 게시판</h1>
    </div>

    <!-- 게시글 작성 -->
    <div class="form-card">
      <h3>새 글 작성</h3>

      <form class="post-form" @submit.prevent="handleCreatePost">
        <div class="form-row">
          <input v-model="form.nickname" placeholder="닉네임" required />
          <input v-model="form.password" type="password" placeholder="수정용 비밀번호" required />
        </div>

        <select v-model="form.category_id" required>
          <option :value="null" disabled>카테고리를 선택하세요</option>
          <option v-for="category in categories.slice(1)" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>

        <input v-model="form.title" placeholder="제목" required />

        <textarea rows="5" v-model="form.content" placeholder="내용을 입력하세요." required></textarea>

        <button class="btn-submit" type="submit">글 등록</button>
      </form>
    </div>

    <!-- 카테고리 -->
    <div class="category-bar">
      <button
        v-for="category in categories"
        :key="category.id"
        class="category-chip"
        :class="{ active: selectedCategory === category.id }"
        @click="changeCategory(category.id)"
      >
        {{ category.name }}
      </button>
    </div>

    <!-- 검색 -->
    <div class="search-bar">
      <input
        v-model="searchQuery"
        placeholder="제목 또는 내용을 검색하세요."
        @keyup.enter="loadPosts"
      />
      <button class="btn-search" @click="loadPosts">검색</button>
    </div>

    <!-- 게시글 목록 -->
    <div v-if="loading" class="loading">로딩중...</div>

    <div v-else class="post-list">
      <div
        v-for="post in pagedPosts"
        :key="post.id"
        class="post-card"
        @click="openPostDetail(post.id)"
      >
        <div class="post-top">
          <h3 class="post-title">{{ post.title }}</h3>
          <span class="post-category">{{ getCategoryName(post.category_id) }}</span>
        </div>

        <div class="post-preview">{{ post.content }}</div>

        <div class="post-meta">
          <span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
            </svg>
            {{ post.nickname }}
          </span>
          <span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" /><circle cx="12" cy="12" r="2.5" />
            </svg>
            {{ post.views }}
          </span>
          <span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z" />
            </svg>
            {{ post.comment_count }}
          </span>
          <span>{{ formatDate(post.created_at) }}</span>
        </div>
      </div>

      <div v-if="pagedPosts.length === 0" class="empty-state">게시글이 없습니다.</div>
    </div>

    <!-- 페이지네이션 -->
    <div class="pagination" v-if="totalPage > 1">
      <button @click="currentPage--" :disabled="currentPage === 1">이전</button>
      <button
        v-for="page in totalPage"
        :key="page"
        :class="{ active: page === currentPage }"
        @click="currentPage = page"
      >
        {{ page }}
      </button>
      <button @click="currentPage++" :disabled="currentPage === totalPage">다음</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { POST_CATEGORIES as categories } from '../../constants/postCategories'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const posts = ref([])
const loading = ref(false)

const searchQuery = ref('')
const selectedCategory = ref(0)

const currentPage = ref(1)
const pageSize = 20

const form = ref({
  nickname: '',
  password: '',
  category_id: null,
  title: '',
  content: '',
})

const filteredPosts = computed(() => {
  let result = [...posts.value]
  if (selectedCategory.value !== 0) {
    result = result.filter((post) => post.category_id === selectedCategory.value)
  }
  return result
})

const totalPage = computed(() => Math.ceil(filteredPosts.value.length / pageSize))

const pagedPosts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredPosts.value.slice(start, start + pageSize)
})

function getCategoryName(id) {
  const category = categories.find((c) => c.id === id)
  return category ? category.name : '-'
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
}

function changeCategory(id) {
  selectedCategory.value = id
  currentPage.value = 1
}

async function loadPosts() {
  loading.value = true
  try {
    let url = `${API_BASE}/api/posts`
    if (searchQuery.value) {
      url += `?search=${encodeURIComponent(searchQuery.value)}`
    }
    const res = await fetch(url)
    posts.value = await res.json()
  } catch (err) {
    alert('게시글을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

async function handleCreatePost() {
  const res = await fetch(`${API_BASE}/api/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })

  if (!res.ok) {
    alert('등록 실패')
    return
  }

  form.value = { nickname: '', password: '', category_id: null, title: '', content: '' }
  await loadPosts()
}

function openPostDetail(id) {
  router.push(`/posts/${id}`)
}

onMounted(loadPosts)
</script>

<style scoped>
.posts-view {
  max-width: 860px;
  margin: 0 auto;
  padding: 24px 40px 56px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.page-head {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--accent-ink-strong, #ca8a04);
}

.page-head h1 {
  font-size: 24px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.form-card {
  border: 1px solid var(--border, #ece7df);
  border-radius: 16px;
  padding: 24px;
  background: var(--surface, #faf9f7);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-card h3 {
  font-size: 15px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-row input {
  flex: 1;
}

input,
textarea,
select {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 10px;
  font-family: inherit;
  font-size: 13.5px;
  color: var(--ink, #1c1917);
  box-sizing: border-box;
  background: #fff;
}

.btn-submit {
  border: none;
  background: var(--accent, #facc15);
  color: var(--ink, #1c1917);
  border-radius: 10px;
  padding: 13px 0;
  font-size: 14.5px;
  font-weight: 700;
  cursor: pointer;
}

.category-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip {
  padding: 7px 15px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 999px;
  cursor: pointer;
  background: transparent;
  color: var(--text, #57534e);
  font-size: 13px;
  font-family: inherit;
}

.category-chip.active {
  background: var(--ink, #1c1917);
  border-color: var(--ink, #1c1917);
  color: #fff;
  font-weight: 600;
}

.search-bar {
  display: flex;
  gap: 10px;
}

.search-bar input {
  flex: 1;
}

.btn-search {
  border: none;
  background: var(--ink, #1c1917);
  color: #fff;
  border-radius: 10px;
  padding: 0 24px;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.post-card {
  border: 1px solid var(--border, #ece7df);
  border-radius: 14px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition: box-shadow 0.15s ease;
}

.post-card:hover {
  box-shadow: var(--shadow);
}

.post-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.post-title {
  margin: 0;
  font-size: 17px;
  font-weight: 800;
  color: var(--ink, #1c1917);
}

.post-category {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-ink, #a16207);
  background: var(--accent-soft, #fef3c7);
  border-radius: 4px;
  padding: 3px 9px;
  white-space: nowrap;
}

.post-preview {
  color: var(--text, #57534e);
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  color: var(--text-faint, #a8a29e);
  font-size: 12.5px;
}

.post-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.loading,
.empty-state {
  text-align: center;
  padding: 30px;
  color: var(--text-muted, #78716c);
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
}

.pagination button {
  min-width: 32px;
  height: 32px;
  border: 1px solid var(--border-strong, #e3ddd3);
  border-radius: 8px;
  cursor: pointer;
  background: transparent;
  color: var(--text, #57534e);
  font-family: inherit;
}

.pagination button.active {
  background: var(--ink, #1c1917);
  border-color: var(--ink, #1c1917);
  color: #fff;
  font-weight: 700;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
