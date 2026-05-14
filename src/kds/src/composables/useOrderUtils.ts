import type { KDSOrder } from '@/types/kds'

export function useOrderUtils() {
  function formatTime(isoString: string): string {
    const date = new Date(isoString)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }

  function formatWaitTime(isoString: string): { minutes: number, isWarning: boolean } {
    const now = Date.now()
    const orderTime = new Date(isoString).getTime()
    const minutes = Math.floor((now - orderTime) / 60000)
    return {
      minutes,
      isWarning: minutes >= 10 // Warn if waiting more than 10 minutes
    }
  }

  function formatOptions(options: Record<string, unknown>): string {
    if (!options || Object.keys(options).length === 0) return ''

    const parts: string[] = []

    if (options.size) parts.push(String(options.size))
    if (options.sweetness) parts.push(String(options.sweetness))
    if (options.temperature) parts.push(String(options.temperature))
    if (options.extras && Array.isArray(options.extras)) {
      parts.push((options.extras as string[]).join(', '))
    }

    return parts.length > 0 ? `(${parts.join(', ')})` : ''
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      submitted: '待接单',
      confirmed: '已接单',
      preparing: '制作中',
      ready: '待取餐',
      completed: '已完成',
      cancelled: '已取消',
      rejected: '已拒单'
    }
    return labels[status] || status
  }

  function sortOrders(orders: KDSOrder[]): KDSOrder[] {
    return [...orders].sort((a, b) => {
      // Sort by status priority (submitted > confirmed > preparing > ready)
      const statusPriority: Record<string, number> = {
        submitted: 0,
        confirmed: 1,
        preparing: 2,
        ready: 3
      }
      const priorityDiff = (statusPriority[a.status] ?? 9) - (statusPriority[b.status] ?? 9)
      if (priorityDiff !== 0) return priorityDiff

      // Then by creation time (oldest first)
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    })
  }

  return {
    formatTime,
    formatWaitTime,
    formatOptions,
    getStatusLabel,
    sortOrders
  }
}
