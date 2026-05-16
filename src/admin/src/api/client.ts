import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT token to every request
client.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  console.log('[Client] Request:', config.method?.toUpperCase(), config.url, 'token:', token ? `Bearer ${token.substring(0, 15)}...` : 'MISSING')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally — redirect to login
client.interceptors.response.use(
  res => res,
  err => {
    const status = err.response?.status
    const url = err.config?.url
    const method = err.config?.method?.toUpperCase()
    const authHeader = err.config?.headers?.Authorization
    console.log(`[Client] ${method} ${url} → ${status}`, {
      authHeader: authHeader ? `Bearer ${authHeader.substring(0, 20)}...` : 'MISSING',
      response: err.response?.data
    })
    if (status === 401) {
      localStorage.removeItem('admin_token')
      if (window.location.pathname !== '/login') {
        window.location.replace('/login')
      }
    }
    return Promise.reject(err)
  }
)

export default client
