/**
 * Toast composable for showing notifications
 * Usage:
 *   import { useToast } from '@/composables/useToast'
 *   const toast = useToast()
 *   toast.info('信息提示')
 *   toast.warn('警告提示', '警告标题')
 *   toast.error('错误提示')
 *   toast.success('操作成功', '成功')
 */
export const useToast = () => {
  const showToast = (message, type = 'info', title = null) => {
    if (window.$toast) {
      return window.$toast[type](message, title)
    } else {
      console.warn('Toast component not mounted yet')
      // Fallback to console
      console[type === 'error' ? 'error' : type === 'warn' ? 'warn' : 'log'](message)
    }
  }

  return {
    info: (message, title) => showToast(message, 'info', title),
    warn: (message, title) => showToast(message, 'warn', title),
    error: (message, title) => showToast(message, 'error', title),
    success: (message, title) => showToast(message, 'info', title) // success uses info style
  }
}

