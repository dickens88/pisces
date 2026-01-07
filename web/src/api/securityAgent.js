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

  // 检查API key是否配置
  if (!config.aiChatKey) {
    throw new Error('AI chat API key is not configured (VITE_AI_CHAT_KEY). Please set it in your environment variables.')
  }
  
  headers.Authorization = `Bearer ${config.aiChatKey}`

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

/**
 * 调用dify workflow获取组列表
 * @returns {Promise<any>} 组列表数据
 */
export const getGroupList = async () => {
  const baseEndpoint = config.wetaskAgentApi
  if (!baseEndpoint) {
    throw new Error('wetask Agent API endpoint is not configured (VITE_WETASK_AGENT_API)')
  }

  if (!config.wetaskAgentKey) {
    throw new Error('wetask Agent API key is not configured (VITE_WETASK_AGENT_KEY)')
  }

  const authStore = useAuthStore()
  const resolvedUserName = (await resolveUserIdentity(authStore)) || 'Guest'

  let baseUrl = baseEndpoint.replace(/\/v1\/.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const requestBody = {
    inputs: {
      action: 'get group list'
    },
    response_mode: 'blocking',
    user: resolvedUserName
  }

  let response
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${config.wetaskAgentKey}`
      },
      body: JSON.stringify(requestBody),
      mode: 'cors',
      credentials: 'omit'
    })
  } catch (fetchError) {
    throw new Error(`网络请求失败: ${fetchError.message}`)
  }

  if (!response.ok) {
    const errorText = await response.text().catch(() => '')
    let errorData
    try {
      errorData = JSON.parse(errorText)
    } catch {
      errorData = { message: errorText }
    }
    throw new Error(errorData.message || `API 请求失败 (状态码: ${response.status})`)
  }

  const data = await response.json().catch(async () => {
    const text = await response.text().catch(() => '')
    return { answer: text, data: null }
  })

  if (data.data?.outputs?.group_list) {
    return data.data.outputs.group_list
  }

  return data.data?.outputs || []
}

/**
 * 获取组ID列表
 * @returns {Promise<string[]>} 组ID列表
 */
export const getGroupIdList = async () => {
  const result = await getGroupList()
  
  if (!Array.isArray(result)) {
    return []
  }
  
  const groupIds = result
    .map(item => String(item.group_id))
    .filter(id => id)
  
  return [...new Set(groupIds)].sort()
}

/**
 * 调用dify workflow获取任务详情
 * @param {Object} params
 * @param {string|number} params.groupId - 组ID（必需）
 * @returns {Promise<any>} 任务详情数据
 */
export const getTaskDetail = async ({ groupId }) => {
  if (!groupId) {
    throw new Error('Group ID is required')
  }

  const baseEndpoint = config.wetaskAgentApi
  if (!baseEndpoint) {
    throw new Error('wetask Agent API endpoint is not configured (VITE_WETASK_AGENT_API)')
  }

  if (!config.wetaskAgentKey) {
    throw new Error('wetask Agent API key is not configured (VITE_WETASK_AGENT_KEY)')
  }

  const authStore = useAuthStore()
  const resolvedUserName = (await resolveUserIdentity(authStore)) || 'Guest'

  let baseUrl = baseEndpoint.replace(/\/v1\/.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const requestBody = {
    inputs: {
      action: 'get task detail',
      group_id: String(groupId).trim()
    },
    response_mode: 'blocking',
    user: resolvedUserName
  }

  let response
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${config.wetaskAgentKey}`
      },
      body: JSON.stringify(requestBody),
      mode: 'cors',
      credentials: 'omit'
    })
  } catch (fetchError) {
    throw new Error(`网络请求失败: ${fetchError.message}`)
  }

  if (!response.ok) {
    const errorText = await response.text().catch(() => '')
    let errorData
    try {
      errorData = JSON.parse(errorText)
    } catch {
      errorData = { message: errorText }
    }
    throw new Error(errorData.message || `API 请求失败 (状态码: ${response.status})`)
  }

  const data = await response.json().catch(async () => {
    const text = await response.text().catch(() => '')
    return { answer: text, data: null }
  })

  if (data.data?.outputs?.task_detail) {
    return data.data.outputs.task_detail
  }

  return data.data?.outputs || []
}


