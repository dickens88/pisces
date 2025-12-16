import { getAppConfig } from '@config'
import { useAuthStore } from '@/stores/auth'

const config = getAppConfig(import.meta.env, import.meta.env.PROD)

const resolveUserIdentity = async (authStore) => {
  const immediateName =
    authStore.user?.username ||
    authStore.user?.cn ||
    authStore.user?.name ||
    authStore.user?.user_name ||
    null

  if (immediateName) {
    return immediateName
  }

  if (!config.enableAuth || typeof authStore.fetchCurrentUser !== 'function') {
    return null
  }

  try {
    const user = await authStore.fetchCurrentUser()
    return (
      user?.username ||
      user?.cn ||
      user?.name ||
      user?.user_name ||
      null
    )
  } catch (error) {
    console.warn('Security Agent chat: unable to resolve user identity', error)
    return null
  }
}

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
export const sendSecurityAgentMessage = async ({
  alertId,
  message,
  files = [],
  conversationId,
  onEvent
}) => {
  const endpoint = config.aiChatApi
  if (!endpoint) {
    throw new Error('AI chat API endpoint is not configured (VITE_AI_CHAT_API)')
  }

  const authStore = useAuthStore()
  const sanitizedMessage = (message || '').trim()
  const hasFiles = Array.isArray(files) && files.length > 0
  const resolvedUserName = (await resolveUserIdentity(authStore)) || 'Guest'

  if (!sanitizedMessage && !hasFiles) {
    throw new Error('Message content is required')
  }

  let body
  const headers = {}

  const inputs = {}
  if (alertId) {
    inputs.alert_id = alertId
  }

  const requestBody = {
    inputs,
    query: sanitizedMessage,
    response_mode: 'streaming',
    user: resolvedUserName
  }

  if (conversationId) {
    requestBody.conversation_id = conversationId
  }

  body = JSON.stringify(requestBody)
  headers['Content-Type'] = 'application/json'

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


