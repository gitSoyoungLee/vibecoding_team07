const API_BASE = 'http://127.0.0.1:8000'

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
