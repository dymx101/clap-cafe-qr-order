import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

client.interceptors.request.use(config => {
  const params = new URLSearchParams(window.location.search)
  const seat = params.get('seat')
  if (seat) config.headers['X-Seat-ID'] = seat
  const lang = params.get('lang') || 'zh'
  config.headers['Accept-Language'] = lang
  return config
})

client.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 422) {
      console.error('API Error:', err.response.data)
    }
    return Promise.reject(err)
  }
)

export default client
