import { getAppConfig } from '@config'
import { useAuthStore } from '@/stores/auth'

const config = getAppConfig(import.meta.env, import.meta.env.PROD)

/**
 * Send a chat message to the external Security Agent API.
 * Falls back to plain JSON when there is no attachment.
 *
 * @param {Object} params
 * @param {string|number} params.alertId - Current alert identifier.
 * @param {string} params.message - Message body from the analyst.
 * @param {File[]} [params.files] - Optional attachment list (max 1 from CommentInput).
 * @returns {Promise<any>} Response payload from the external API.
 */
export const sendSecurityAgentMessage = async ({ alertId, message, files = [] }) => {
  const endpoint = config.aiChatApi
  if (!endpoint) {
    throw new Error('AI chat API endpoint is not configured (VITE_AI_CHAT_API)')
  }

  const authStore = useAuthStore()
  const sanitizedMessage = (message || '').trim()
  const hasFiles = Array.isArray(files) && files.length > 0

  if (!sanitizedMessage && !hasFiles) {
    throw new Error('Message content is required')
  }

  let body
  const headers = {}

//   if (hasFiles) {
//     const formData = new FormData()
//     formData.append('alertId', alertId)
//     formData.append('message', sanitizedMessage)
//     files.forEach((file, index) => {
//       formData.append('files', file, file?.name || `attachment-${index + 1}`)
//     })
//     body = formData
//   } else {
    body = JSON.stringify({
      inputs: {},  
      query: sanitizedMessage,
      response_mode: 'blocking',
      user: 'Botond Varhalmi 84400683'
    })
    headers['Content-Type'] = 'application/json'
 // }

  if (config.aiChatKey) {
    headers.Authorization = `Bearer ${config.aiChatKey}`
  }

  const response = await fetch(endpoint, {
    method: 'POST',
    headers,
    body
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => '')
    throw new Error(errorText || `External AI chat API responded with ${response.status}`)
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }

  try {
    const text = await response.text()
    return { raw: text }
  } catch {
    return {}
  }
}


