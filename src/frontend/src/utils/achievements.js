// 成就缓存与工具
// 负责加载用户菜品历史并在内存中缓存 dishId -> count，提供边框/徽章等级计算

import { getUserDishHistory } from '@/utils/api/listApi'

let _loaded = false
let _loading = null
const _map = new Map() // dishId:number -> count:number

// 简单的全局事件用于通知组件刷新
const EVENT_NAME = 'achievements:updated'

export function onAchievementsUpdated(handler) {
  window.addEventListener(EVENT_NAME, handler)
}
export function offAchievementsUpdated(handler) {
  window.removeEventListener(EVENT_NAME, handler)
}
function emitUpdated(dishId) {
  window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: { dishId } }))
}

export async function ensureAchievementsLoaded() {
  if (_loaded) return _map
  if (_loading) return _loading
  const token = localStorage.getItem('jwt')
  if (!token) {
    _loaded = true
    return _map
  }
  _loading = (async () => {
    try {
      const res = await getUserDishHistory({ page_size: 1000 })
      const list = Array.isArray(res?.data?.histories) ? res.data.histories : []
      _map.clear()
      for (const item of list) {
        const id = Number(item?.dish)
        const count = Number(item?.count) || 0
        if (id) _map.set(id, count)
      }
      _loaded = true
    } catch (e) {
      _loaded = true
    } finally {
      _loading = null
    }
    return _map
  })()
  return _loading
}

export function getDishCheckinCount(dishId) {
  const id = Number(dishId)
  return _map.get(id) || 0
}

export function bumpDishCheckinCount(dishId, delta = 1) {
  const id = Number(dishId)
  const v = (_map.get(id) || 0) + delta
  _map.set(id, v)
  emitUpdated(id)
  return v
}

export function getAchievementByCount(count) {
  if (count >= 100) return { label: '院士', key: 'rainbow' }
  if (count >= 10) return { label: '博士', key: 'gold' }
  if (count >= 3) return { label: '硕士', key: 'silver' }
  if (count >= 1) return { label: '本科', key: 'bronze' }
  return { label: '', key: '' }
}

// 返回所有已加载的成就计数（数组形式），用于统计页面
export function getAllAchievements() {
  const out = []
  for (const [dishId, count] of _map.entries()) {
    out.push({ dishId, count })
  }
  return out
}
