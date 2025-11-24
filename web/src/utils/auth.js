import { getAppConfig } from '@config'

const config = getAppConfig(import.meta.env, import.meta.env.PROD)

/**
 * 重定向到 tianyan-web 登录页面
 * 会自动保存当前 URL 到 sessionStorage 作为备选方案
 * @param {string} customUrl - 可选，自定义要保存的 URL（默认使用当前页面 URL）
 */
export function redirectToTianyanLogin(customUrl = null) {
  if (config.authMode !== 'tianyan') {
    return false
  }

  const currentUrl = customUrl || window.location.href
  // 保存到 sessionStorage 作为备选方案（防止 tianyan-web 没有正确传递 redirect）
  sessionStorage.setItem('redirect_after_login', currentUrl)
  const loginUrl = `${config.tianyanWebBaseURL}/login?redirect=${encodeURIComponent(currentUrl)}`
  window.location.href = loginUrl
  return true
}

/**
 * 验证 redirect URL 是否安全（同源）
 * @param {string} url - 要验证的 URL
 * @returns {boolean} 是否为安全的同源 URL
 */
export function isValidRedirectUrl(url) {
  try {
    const redirectUrl = new URL(url)
    const currentUrl = new URL(window.location.origin)
    // 只允许同源重定向，防止开放重定向漏洞
    return redirectUrl.origin === currentUrl.origin
  } catch {
    return false
  }
}

/**
 * 处理从 tianyan-web 登录返回后的重定向逻辑
 * @param {Router} router - Vue Router 实例
 * @returns {Promise<void>}
 */
export function handleTianyanLoginRedirect(router) {
  const urlParams = new URLSearchParams(window.location.search)
  const redirectFromUrl = urlParams.get('redirect')
  const redirectFromStorage = sessionStorage.getItem('redirect_after_login')
  const redirectTarget = redirectFromUrl || redirectFromStorage

  // 清理 URL 参数和 sessionStorage
  const newUrl = new URL(window.location.href)
  newUrl.searchParams.delete('token')
  newUrl.searchParams.delete('redirect')
  window.history.replaceState({}, '', newUrl.toString())

  // 清理 sessionStorage
  if (redirectFromStorage) {
    sessionStorage.removeItem('redirect_after_login')
  }

  // 如果有有效的重定向目标，则重定向
  if (redirectTarget && isValidRedirectUrl(redirectTarget)) {
    window.location.href = redirectTarget
  } else if (redirectTarget) {
    // 如果 redirect 无效，尝试只使用路径部分
    try {
      const redirectUrl = new URL(redirectTarget)
      const pathOnly = redirectUrl.pathname + redirectUrl.search + redirectUrl.hash
      router.push(pathOnly)
    } catch {
      // 如果解析失败，重定向到首页
      router.push('/')
    }
  }
}

