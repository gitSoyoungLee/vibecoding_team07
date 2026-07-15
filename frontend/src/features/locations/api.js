const API_BASE = 'http://127.0.0.1:8000'

export const CATEGORIES = [
  { key: 'all', label: '전체', ids: null },
  { key: 'tour', label: '관광지', ids: [12] },
  { key: 'sports-culture', label: '레포츠·문화시설', ids: [28, 14] },
  { key: 'shopping', label: '쇼핑', ids: [38] },
  { key: 'lodging', label: '숙박', ids: [32] },
  { key: 'course', label: '여행코스', ids: [25] },
  { key: 'festival', label: '축제공연행사', ids: [15] },
]

export async function fetchLocations({ contentTypeIds, keyword, limit = 100 } = {}) {
  const params = new URLSearchParams()
  if (contentTypeIds && contentTypeIds.length) {
    params.set('content_type_id', contentTypeIds.join(','))
  }
  if (keyword) params.set('keyword', keyword)
  if (limit) params.set('limit', limit)

  const res = await fetch(`${API_BASE}/locations?${params.toString()}`)
  if (!res.ok) throw new Error('장소 목록을 불러오지 못했습니다.')
  return res.json()
}

export function districtOf(addr1) {
  if (!addr1) return ''
  const token = addr1.split(/\s+/).find((t) => t.endsWith('구'))
  return token || ''
}
