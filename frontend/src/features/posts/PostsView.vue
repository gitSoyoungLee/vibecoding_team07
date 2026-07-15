<template>
  <div class="posts-view">

    <h2>📋 자유 게시판</h2>

    <!-- 게시글 작성 -->
    <div class="card form-card">
      <h3>새 글 작성</h3>

      <form class="post-form" @submit.prevent="handleCreatePost">

        <div class="form-row">
          <input
            v-model="form.nickname"
            placeholder="닉네임"
            required
          />

          <input
            v-model="form.password"
            type="password"
            placeholder="비밀번호"
            required
          />
        </div>

        <select
          v-model="form.category_id"
          required
        >
          <option :value="null" disabled>
            카테고리를 선택하세요
          </option>

          <option
            v-for="category in categories.slice(1)"
            :key="category.id"
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </select>

        <input
          v-model="form.title"
          placeholder="제목"
          required
        />

        <textarea
          rows="5"
          v-model="form.content"
          placeholder="내용을 입력하세요."
          required
        ></textarea>

        <button
          class="btn-primary"
          type="submit"
        >
          글 등록
        </button>

      </form>
    </div>

    <!-- 카테고리 -->
    <div class="category-bar">
      <button
        v-for="category in categories"
        :key="category.id"
        :class="{ active:selectedCategory===category.id }"
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

      <button
        class="btn-secondary"
        @click="loadPosts"
      >
        검색
      </button>

    </div>

    <!-- 게시글 목록 -->
    <div
      v-if="loading"
      class="loading"
    >
      로딩중...
    </div>

    <div
      v-else
      class="post-list"
    >

      <div
        v-for="post in pagedPosts"
        :key="post.id"
        class="card post-card"
        @click="openPostDetail(post.id)"
      >

        <div class="post-header">

          <h3>{{ post.title }}</h3>

          <span class="author">
            {{ post.nickname }}
          </span>

        </div>

        <div class="post-category">
          {{ getCategoryName(post.category_id) }}
        </div>

        <div class="post-meta">
          <span>👀 {{ post.views }}</span>
          <span>💬 {{ post.comment_count }}</span>
          <span>{{ formatDate(post.created_at) }}</span>
        </div>

      </div>

    </div>

    <!-- 페이지네이션 -->
    <div
      class="pagination"
      v-if="totalPage > 1"
    >

      <button
        @click="currentPage--"
        :disabled="currentPage===1"
      >
        이전
      </button>

      <button
        v-for="page in totalPage"
        :key="page"
        :class="{active:page===currentPage}"
        @click="currentPage=page"
      >
        {{ page }}
      </button>

      <button
        @click="currentPage++"
        :disabled="currentPage===totalPage"
      >
        다음
      </button>

    </div>

    <!-- 게시글 상세 -->
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

        <!-- 일반 보기 -->
        <template v-if="!editingPost">

          <h2>{{ selectedPost.title }}</h2>

          <div class="post-info">
            <span>{{ selectedPost.nickname }}</span>
            <span>{{ getCategoryName(selectedPost.category_id) }}</span>
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

        <!-- 게시글 수정 -->
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
                v-for="category in categories.slice(1)"
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
                @click="editingPost=false"
              >
                취소
              </button>

            </div>

          </div>

        </template>

        <hr>

        <!-- 댓글 -->
        <div class="comments-section">

          <h3>💬 댓글</h3>

          <div
            v-if="comments.length===0"
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

              <strong>
                {{ comment.nickname }}
              </strong>

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

            <!-- 일반 댓글 -->
            <template
              v-if="editingComment!==comment.id"
            >

              <p>{{ comment.content }}</p>

              <small>
                {{ formatDate(comment.created_at) }}
              </small>

            </template>

            <!-- 댓글 수정 -->
            <template v-else>

              <textarea
                rows="3"
                v-model="commentEdit.content"
              ></textarea>

              <input
                type="password"
                v-model="commentEdit.password"
                placeholder="비밀번호"
              />

              <div class="action-buttons">

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

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const categories = [
  { id: 0, name: '전체' },
  { id: 1, name: '관광지' },
  { id: 2, name: '레포츠·문화시설' },
  { id: 3, name: '쇼핑' },
  { id: 4, name: '숙박' },
  { id: 5, name: '여행코스' },
  { id: 6, name: '축제' }
]

const posts = ref([])
const comments = ref([])
const loading = ref(false)

const searchQuery = ref('')
const selectedCategory = ref(0)

const selectedPost = ref(null)

const editingPost = ref(false)
const editingComment = ref(null)

const currentPage = ref(1)
const pageSize = 20

const form = ref({
  nickname: '',
  password: '',
  category_id: null,
  title: '',
  content: ''
})

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

const filteredPosts = computed(() => {

  let result = [...posts.value]

  if (selectedCategory.value !== 0) {
    result = result.filter(
      post => post.category_id === selectedCategory.value
    )
  }

  return result

})

const totalPage = computed(() =>

  Math.ceil(filteredPosts.value.length / pageSize)

)

const pagedPosts = computed(() => {

  const start = (currentPage.value - 1) * pageSize

  return filteredPosts.value.slice(start, start + pageSize)

})

function getCategoryName(id) {

  const category = categories.find(c => c.id === id)

  return category ? category.name : '-'

}

function formatDate(date) {

  if (!date) return ''

  return new Date(date).toLocaleString('ko-KR', {
    timeZone: 'Asia/Seoul'
  })

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

    headers: {
      'Content-Type': 'application/json'
    },

    body: JSON.stringify(form.value)

  })

  if (!res.ok) {

    alert('등록 실패')

    return

  }

  form.value = {
    nickname: '',
    password: '',
    category_id: null,
    title: '',
    content: ''
  }

  await loadPosts()

}

async function openPostDetail(id) {

  const res = await fetch(`${API_BASE}/api/posts/${id}`)

  const data = await res.json()

  selectedPost.value = data.post

  comments.value = data.comments

  editingPost.value = false

}

function closeModal() {

  selectedPost.value = null

  comments.value = []

  editingComment.value = null

}

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

  await openPostDetail(selectedPost.value.id)

  await loadPosts()

}

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

  await openPostDetail(selectedPost.value.id)

  await loadPosts()

}

function startEditComment(comment) {

  editingComment.value = comment.id

  commentEdit.value = {

    content: comment.content,

    password: ''

  }

}

function cancelEditComment() {

  editingComment.value = null

}

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

  await openPostDetail(selectedPost.value.id)

}

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

      body: JSON.stringify({

        password

      })

    }

  )

  if (!res.ok) {

    alert('삭제 실패')

    return

  }

  await openPostDetail(selectedPost.value.id)

  await loadPosts()

}

onMounted(() => {

  loadPosts()

})
</script>

<style scoped>
.posts-view{
  max-width:900px;
  margin:0 auto;
  padding:20px;
}

.card{
  background:#fff;
  border:1px solid #ddd;
  border-radius:10px;
  padding:16px;
  margin-bottom:16px;
}

.form-card{
  background:#fafafa;
}

.post-form,
.comment-form{
  display:flex;
  flex-direction:column;
  gap:10px;
}

.form-row{
  display:flex;
  gap:10px;
}

.form-row input{
  flex:1;
}

input,
textarea,
select{
  width:100%;
  padding:10px;
  border:1px solid #ccc;
  border-radius:6px;
  box-sizing:border-box;
}

.category-bar{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  margin:20px 0;
}

.category-bar button{
  padding:8px 14px;
  border:none;
  border-radius:20px;
  cursor:pointer;
  background:#e9ecef;
}

.category-bar button.active{
  background:#0d6efd;
  color:#fff;
}

.search-bar{
  display:flex;
  gap:10px;
  margin-bottom:20px;
}

.search-bar input{
  flex:1;
}

.post-card{
  cursor:pointer;
  transition:.2s;
}

.post-card:hover{
  background:#f8f9fa;
}

.post-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
}

.post-category{
  display:inline-block;
  margin:8px 0;
  padding:4px 10px;
  background:#eef5ff;
  border-radius:20px;
  color:#0d6efd;
  font-size:13px;
}

.post-meta{
  display:flex;
  gap:18px;
  color:#666;
  font-size:13px;
}

.loading{
  text-align:center;
  padding:30px;
}

.modal-overlay{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,.45);
  display:flex;
  justify-content:center;
  align-items:center;
  z-index:1000;
}

.modal-content{
  width:90%;
  max-width:700px;
  max-height:90vh;
  overflow-y:auto;
  background:#fff;
  padding:25px;
  border-radius:10px;
  position:relative;
}

.close-btn{
  position:absolute;
  top:12px;
  right:15px;
  border:none;
  background:none;
  font-size:20px;
  cursor:pointer;
}

.post-info{
  display:flex;
  gap:15px;
  color:#666;
  margin-bottom:15px;
}

.post-body{
  white-space:pre-wrap;
  line-height:1.7;
  margin-bottom:20px;
}

.action-buttons{
  display:flex;
  gap:10px;
  margin:15px 0;
}

.comments-section{
  margin-top:20px;
}

.comment-item{
  background:#f7f7f7;
  border-radius:8px;
  padding:12px;
  margin-bottom:12px;
}

.comment-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
}

.comment-actions{
  display:flex;
  gap:8px;
}

.btn-edit,
.btn-delete{
  width:70px;
  height:34px;
  border:none;
  border-radius:6px;
  color:white;
  cursor:pointer;
}

.btn-edit{
  background:#6c757d;
}

.btn-delete{
  background:#dc3545;
}

.edit-box{
  margin-top:10px;
}

.edit-actions{
  display:flex;
  gap:10px;
  margin-top:10px;
}

.pagination{
  display:flex;
  justify-content:center;
  gap:8px;
  margin-top:24px;
}

.pagination button{
  width:38px;
  height:38px;
  border:none;
  border-radius:6px;
  cursor:pointer;
  background:#f1f3f5;
}

.pagination button.active{
  background:#0d6efd;
  color:white;
}

.btn-primary{
  background:#0d6efd;
  color:white;
  border:none;
  border-radius:6px;
  padding:10px 16px;
  cursor:pointer;
}

.btn-secondary{
  background:#6c757d;
  color:white;
  border:none;
  border-radius:6px;
  padding:10px 16px;
  cursor:pointer;
}

.no-comments{
  text-align:center;
  color:#777;
  padding:20px;
}
</style>