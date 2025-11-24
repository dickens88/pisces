const STORAGE_KEY = 'pisces_recent_close_comments'
const MAX_ITEMS = 5

const isBrowser = () => typeof window !== 'undefined' && !!window.localStorage

const normalizeList = (list) => {
  if (!Array.isArray(list)) return []
  return list
    .map(item => (typeof item === 'string' ? item.trim() : ''))
    .filter(item => item.length > 0)
}

export const getRecentCloseComments = () => {
  if (!isBrowser()) return []
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return normalizeList(parsed).slice(0, MAX_ITEMS)
  } catch {
    return []
  }
}

export const saveRecentCloseComment = (comment) => {
  if (!isBrowser()) return []
  const value = typeof comment === 'string' ? comment.trim() : ''
  if (!value) return getRecentCloseComments()

  const existing = getRecentCloseComments().filter(item => item !== value)
  const next = [value, ...existing].slice(0, MAX_ITEMS)
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  } catch {
    // Ignore write errors (storage full, etc.)
  }
  return next
}

