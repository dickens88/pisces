import { getAppConfig } from '@config'
import { useAuthStore } from '@/stores/auth'

const config = getAppConfig(import.meta.env, import.meta.env.PROD)

/**
 * Send a chat message to the external Security Agent API.
 * Uses streaming response mode and emits each event through onEvent callback.
 *
 * @param {Object} params
 * @param {string|number} params.alertId - Current alert identifier.
 * @param {string} params.message - Message body from the analyst.
 * @param {File[]} [params.files] - Optional attachment list (currently unused).
 * @param {(event: object) => void} [params.onEvent] - Callback for each streamed event.
 * @returns {Promise<any>} The last event received from the stream.
 */
export const sendSecurityAgentMessage = async ({ alertId, message, files = [], onEvent }) => {
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
      response_mode: 'streaming',
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

  if (!response.body) {
    const fallbackText = await response.text().catch(() => '')
    let parsed = null
    try {
      parsed = fallbackText ? JSON.parse(fallbackText) : null
    } catch {
      parsed = { raw: fallbackText }
    }
    if (parsed) {
      onEvent?.(parsed)
    }
    return parsed
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let lastEvent = null

  const flushBuffer = (line) => {
    if (!line) return
    const trimmedLine = line.trim()
    if (!trimmedLine) return
    const normalized = trimmedLine.startsWith('data:')
      ? trimmedLine.slice(5).trim()
      : trimmedLine
    if (!normalized) return
    try {
      const parsed = JSON.parse(normalized)
      lastEvent = parsed
      if (onEvent) {
        onEvent(parsed)
      }
    } catch (err) {
      console.warn('Failed to parse Security Agent stream chunk:', normalized, err)
    }
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) {
      break
    }
    buffer += decoder.decode(value, { stream: true })
    let newlineIndex
    while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
      const line = buffer.slice(0, newlineIndex)
      buffer = buffer.slice(newlineIndex + 1)
      flushBuffer(line)
    }
  }

  if (buffer.trim()) {
    flushBuffer(buffer)
  }

  return lastEvent
}


