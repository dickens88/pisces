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

export const getProjectList = async ({ project_name = 'warroom' } = {}) => {
  const baseEndpoint = config.wetaskAgentApi
  if (!baseEndpoint) {
    throw new Error('wetask Agent API endpoint is not configured (VITE_WETASK_AGENT_API)')
  }

  if (!config.wetaskAgentKey) {
    throw new Error('wetask Agent API key is not configured (VITE_WETASK_AGENT_KEY)')
  }

  const authStore = useAuthStore()
  const resolvedUserName = (await resolveUserIdentity(authStore)) || 'Guest'

  let baseUrl = baseEndpoint.replace(/\/v1\/?.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const requestBody = {
    inputs: {
      action: 'get project list',
      project_name: project_name
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

  const data = await response.json()

  return data.data?.outputs?.project_list || []
}

export const getProjectUuidList = async ({ project_name = 'warroom' } = {}) => {
  const result = await getProjectList({ project_name })
  
  if (!Array.isArray(result)) {
    return []
  }
  
  const projectUuids = result
    .map(item => String(item.projectUuid || ''))
    .filter(id => id)
  
  return [...new Set(projectUuids)].sort()
}

export const getTaskDetail = async ({ project_uuid, group_name } = {}) => {
  if (!project_uuid) {
    throw new Error('Project UUID is required')
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

  let baseUrl = baseEndpoint.replace(/\/v1\/?.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const inputs = {
    action: 'get task detail',
    project_uuid: String(project_uuid).trim()
  }
  
  // 可选参数：group_name
  if (group_name) {
    inputs.group_name = String(group_name).trim()
  }

  const requestBody = {
    inputs,
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

  const data = await response.json()

  // 调试日志
  console.log('getTaskDetail response:', data)
  console.log('task_detail:', data.data?.outputs?.task_detail)

  return data.data?.outputs?.task_detail || []
}

/**
 * 创建task组（给task打标签后创建对应的group）
 * @param {Object} params
 * @param {string} params.project_uuid - 项目UUID（必需）
 * @param {string} params.group_name - 组名称（必需），如：攻击溯源、攻击拦截、风险消减、漏洞定位
 * @returns {Promise<Object>} 返回 { result: { group_id, status } }
 */
export const createGroup = async ({ project_uuid, group_name } = {}) => {
  if (!project_uuid) {
    throw new Error('Project UUID is required')
  }

  if (!group_name) {
    throw new Error('Group name is required')
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

  let baseUrl = baseEndpoint.replace(/\/v1\/?.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const requestBody = {
    inputs: {
      action: 'create group',
      project_uuid: String(project_uuid).trim(),
      group_name: String(group_name).trim()
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

  const data = await response.json()

  return data.data?.outputs?.result
}

/**
 * 修改task的内容
 * @param {Object} params
 * @param {string} params.project_uuid - 项目UUID（必需）
 * @param {string} params.task_id - 任务ID（必需）
 * @param {string} [params.task_name] - 任务名称（可选）
 * @param {number} [params.priority] - 优先级（可选）
 * @param {string} [params.status] - 状态（可选）
 * @param {string} [params.start_time] - 开始时间（可选）
 * @param {string} [params.end_time] - 结束时间（可选）
 * @param {string} [params.group_name] - 组名称（可选）
 * @param {string} [params.owner] - 负责人（可选）
 * @param {string} [params.notes] - 备注（可选）
 * @returns {Promise<Object>} 返回 { status: "success" }
 */
export const modifyTask = async ({
  project_uuid,
  task_id,
  task_name,
  priority,
  status,
  start_time,
  end_time,
  group_name,
  owner,
  notes
} = {}) => {
  if (!project_uuid) {
    throw new Error('Project UUID is required')
  }

  if (!task_id) {
    throw new Error('Task ID is required')
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

  let baseUrl = baseEndpoint.replace(/\/v1\/?.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const inputs = {
    action: 'modify task',
    project_uuid: String(project_uuid).trim(),
    task_id: String(task_id).trim()
  }

  // 可选参数
  if (task_name !== undefined && task_name !== null) {
    inputs.task_name = String(task_name).trim()
  }
  if (priority !== undefined && priority !== null) {
    inputs.priority = Number(priority)
  }
  if (status !== undefined && status !== null) {
    inputs.status = String(status).trim()
  }
  if (start_time !== undefined && start_time !== null) {
    inputs.start_time = String(start_time).trim()
  }
  if (end_time !== undefined && end_time !== null) {
    inputs.end_time = String(end_time).trim()
  }
  if (group_name !== undefined && group_name !== null) {
    inputs.group_name = String(group_name).trim()
  }
  if (owner !== undefined && owner !== null) {
    inputs.owner = String(owner).trim()
  }
  if (notes !== undefined && notes !== null) {
    inputs.notes = String(notes).trim()
  }

  const requestBody = {
    inputs,
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

  const data = await response.json()

  return { status: data.data?.outputs?.status || data.data?.status || 'success' }
}

/**
 * 创建task
 * @param {Object} params
 * @param {string} params.project_uuid - 项目UUID（必需）
 * @param {string} params.task_name - 任务名称（必需）
 * @param {number} params.priority - 优先级（必需）
 * @param {string} params.start_time - 开始时间（必需）
 * @param {string} params.end_time - 结束时间（必需）
 * @param {string} params.group_name - 组名称（必需）
 * @param {string} params.owner - 负责人（必需）
 * @param {string} params.notes - 备注（必需）
 * @returns {Promise<Object>} 返回 { status: "success" }
 */
export const createTask = async ({
  project_uuid,
  task_name,
  priority,
  start_time,
  end_time,
  group_name,
  owner,
  notes
} = {}) => {
  if (!project_uuid) {
    throw new Error('Project UUID is required')
  }

  if (!task_name) {
    throw new Error('Task name is required')
  }

  if (priority === undefined || priority === null) {
    throw new Error('Priority is required')
  }

  if (!start_time) {
    throw new Error('Start time is required')
  }

  if (!end_time) {
    throw new Error('End time is required')
  }

  if (!group_name) {
    throw new Error('Group name is required')
  }

  if (!owner) {
    throw new Error('Owner is required')
  }

  if (notes === undefined || notes === null) {
    throw new Error('Notes is required')
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

  let baseUrl = baseEndpoint.replace(/\/v1\/?.*$/, '').replace(/\/$/, '')
  const isDev = import.meta.env.DEV
  const endpoint = isDev ? `/dify-api/v1/workflows/run` : `${baseUrl}/v1/workflows/run`

  const inputs = {
    action: 'create task',
    project_uuid: String(project_uuid).trim(),
    task_name: String(task_name).trim(),
    priority: Number(priority),
    start_time: String(start_time).trim(),
    end_time: String(end_time).trim(),
    group_name: String(group_name).trim(),
    owner: String(owner).trim(),
    notes: String(notes).trim(),
    status: '未完成' // 默认设置为未完成
  }

  const requestBody = {
    inputs,
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

  const data = await response.json()

  // 返回完整的响应数据，以便前端可以访问 data.outputs.task_detail
  return data
}
