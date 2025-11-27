import { ref, onMounted, onUnmounted } from 'vue'

const getDarkState = () => {
  if (typeof document === 'undefined') return false
  return document.documentElement.classList.contains('dark')
}

export const useDarkModeObserver = () => {
  const isDarkMode = ref(getDarkState())
  let observer = null

  const updateDarkState = () => {
    isDarkMode.value = getDarkState()
  }

  onMounted(() => {
    updateDarkState()
    if (typeof MutationObserver === 'undefined' || typeof document === 'undefined') {
      return
    }
    observer = new MutationObserver(updateDarkState)
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })
  })

  onUnmounted(() => {
    if (observer) {
      observer.disconnect()
      observer = null
    }
  })

  return {
    isDarkMode
  }
}

