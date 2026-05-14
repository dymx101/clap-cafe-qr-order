import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

client.interceptors.response.use(
  res => res.data,
  err => {
    console.error('KDS API Error:', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export default client
