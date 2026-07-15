const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export async function sendChatMessage(message) {
  const res = await fetch(`${API_BASE}/chat/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!res.ok) {
    throw new Error('챗봇 응답을 받아오지 못했습니다.')
  }

  const data = await res.json()
  return data
}
