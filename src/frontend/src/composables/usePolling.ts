import { ref, onUnmounted } from 'vue'

export function usePolling<T>(
  fetcher: () => Promise<T>,
  onUpdate: (data: T) => void,
  intervalMs = 3000
) {
  const data = ref<T | null>(null) as { value: T | null }
  const loading = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  async function poll() {
    loading.value = true
    try {
      const result = await fetcher()
      data.value = result
      onUpdate(result)
    } finally {
      loading.value = false
    }
  }

  function start() {
    poll()
    timer = setInterval(poll, intervalMs)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onUnmounted(stop)

  return { data, loading, start, stop }
}
