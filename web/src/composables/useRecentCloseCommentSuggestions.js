import { ref, onUnmounted } from 'vue'
import { getRecentCloseComments, saveRecentCloseComment } from '@/utils/recentCloseComments'

/**
 * Provide reusable state + handlers for close-comment suggestions.
 * @param {Object} options
 * @param {(comment: string) => void} [options.onApply] callback when user picks one
 */
export const useRecentCloseCommentSuggestions = (options = {}) => {
  const recentComments = ref([])
  const showDropdown = ref(false)
  const hideTimer = ref(null)

  const clearTimer = () => {
    if (hideTimer.value) {
      clearTimeout(hideTimer.value)
      hideTimer.value = null
    }
  }

  const refresh = () => {
    recentComments.value = getRecentCloseComments()
    return recentComments.value
  }

  const persist = (comment) => {
    recentComments.value = saveRecentCloseComment(comment)
    return recentComments.value
  }

  const hideDropdown = () => {
    clearTimer()
    showDropdown.value = false
  }

  const maybeOpenDropdown = () => {
    refresh()
    if (recentComments.value.length > 0) {
      showDropdown.value = true
    }
  }

  const handleFocus = () => {
    maybeOpenDropdown()
  }

  const handleClick = () => {
    maybeOpenDropdown()
  }

  const handleBlur = () => {
    clearTimer()
    hideTimer.value = setTimeout(() => {
      showDropdown.value = false
      hideTimer.value = null
    }, 120)
  }

  const handleSelect = (comment) => {
    if (typeof options.onApply === 'function') {
      options.onApply(comment)
    }
    hideDropdown()
  }

  onUnmounted(() => {
    clearTimer()
  })

  return {
    recentComments,
    showDropdown,
    refresh,
    persist,
    handleFocus,
    handleClick,
    handleBlur,
    handleSelect,
    hideDropdown
  }
}

