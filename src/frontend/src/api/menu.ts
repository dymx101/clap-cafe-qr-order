import client from './client'
import type { MenuResponse } from '@/types/menu'

export function getMenu(lang = 'zh') {
  return client.get<MenuResponse>('/menu', { params: { lang } }).then(res => res.data)
}

export function getMenuItem(itemId: string, lang = 'zh') {
  return client.get(`/menu/items/${itemId}`, { params: { lang } }).then(res => res.data)
}
