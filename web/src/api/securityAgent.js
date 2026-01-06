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
 * 调用dify workflow获取任务列表
 * @param {Object} params
 * @param {string|number} params.taskId - 任务ID（可选）
 * @returns {Promise<any>} 任务列表数据
 */
export const getTaskList = async ({ taskId } = {}) => {
  const baseEndpoint = config.aiChatApi
  if (!baseEndpoint) {
    throw new Error('AI chat API endpoint is not configured (VITE_AI_CHAT_API)')
  }

  const authStore = useAuthStore()
  const resolvedUserName = (await resolveUserIdentity(authStore)) || 'Guest'

  // 构建workflow API endpoint: /v1/workflows/run
  // 从baseEndpoint中提取基础URL（去掉可能的路径）
  let baseUrl = baseEndpoint
  // 移除可能的路径部分（如 /v1/chat-messages, /v1/apps/xxx/chat-messages 等）
  baseUrl = baseUrl.replace(/\/v1\/.*$/, '').replace(/\/$/, '')
  
  // 判断是否使用代理（开发环境）
  const isDev = import.meta.env.DEV
  let endpoint
  if (isDev) {
    // 开发环境使用 Vite 代理（解决 CORS 问题）
    // 代理会将 /dify-api 转发到 VITE_AI_CHAT_API 配置的服务器
    endpoint = `/dify-api/v1/workflows/run`
  } else {
    // 生产环境直接调用
    endpoint = `${baseUrl}/v1/workflows/run`
  }

  const headers = {}
  const inputs = {
    action: 'get task list'
  }
  
  if (taskId) {
    inputs.task_id = taskId
  }

  // 使用workflow API格式
  // 根据Dify文档：POST /v1/workflows/run
  // Body: { "inputs": {}, "response_mode": "streaming"|"blocking", "user": "user_id" }
  // workflow 通过 api_key 区分
  const requestBody = {
    inputs,
    response_mode: 'blocking', // 使用阻塞模式，等待完整响应
    user: resolvedUserName
  }

  const body = JSON.stringify(requestBody)
  headers['Content-Type'] = 'application/json'

  // 检查API key是否配置
  if (!config.aiChatKey) {
    throw new Error('AI chat API key is not configured (VITE_AI_CHAT_KEY). Please set it in your environment variables.')
  }
  
  headers.Authorization = `Bearer ${config.aiChatKey}`

  let response
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body,
      // 添加 CORS 相关配置
      mode: 'cors',
      credentials: 'omit'
    })
  } catch (fetchError) {
    // 处理网络错误（包括 CORS 错误）
    console.error('Fetch error details:', {
      endpoint,
      error: fetchError,
      message: fetchError.message,
      stack: fetchError.stack
    })
    
    // 提供更友好的错误信息
    let errorMessage = '网络请求失败'
    if (fetchError.message.includes('Failed to fetch') || fetchError.message.includes('NetworkError')) {
      errorMessage = `无法连接到 Dify API 服务器。可能的原因：
1. CORS 跨域问题：请检查服务器是否允许跨域请求
2. 网络连接问题：请检查网络连接和服务器地址
3. SSL 证书问题：请检查 HTTPS 配置
4. 服务器未响应：请确认服务器地址 ${baseUrl} 是否正确

当前请求的 endpoint: ${endpoint}
请检查浏览器控制台的 Network 标签页查看详细错误信息。`
    } else {
      errorMessage = fetchError.message || '网络请求失败'
    }
    
    throw new Error(errorMessage)
  }

  if (!response.ok) {
    const errorText = await response.text().catch(() => '')
    let errorData
    try {
      errorData = JSON.parse(errorText)
    } catch {
      errorData = { message: errorText }
    }
    
    // 处理各种错误情况
    if (errorData.code === 'not_found' || response.status === 404) {
      throw new Error(
        `Workflow 未找到。` +
        `请确认 API Key 是否正确，或检查该 Workflow 是否已被删除。` +
        `\n当前使用的 endpoint: ${endpoint}`
      )
    }
    
    if (errorData.code === 'not_workflow_app' || errorText.includes('not_workflow_app')) {
      throw new Error(
        `应用模式不匹配：当前 API Key 对应的应用不是 workflow 模式。` +
        `请确认应用类型，或检查 API endpoint 是否正确。` +
        `\n当前使用的 endpoint: ${endpoint}`
      )
    }
    
    if (errorData.code === 'unauthorized' || response.status === 401) {
      throw new Error(
        `认证失败：API Key 无效或已过期。` +
        `请检查 VITE_AI_CHAT_KEY 环境变量配置是否正确。`
      )
    }
    
    throw new Error(
      errorData.message || 
      errorText || 
      `API 请求失败 (状态码: ${response.status})` +
      `\nEndpoint: ${endpoint}`
    )
  }

  const data = await response.json().catch(async () => {
    // 如果不是JSON，尝试解析文本
    const text = await response.text().catch(() => '')
    return { answer: text, data: null }
  })

  // 解析返回的数据，提取任务列表
  // Dify workflow API 返回格式: { data: { outputs: { task_list: [...] } } }
  // 或者: { outputs: { task_list: [...] } }
  // 或者: { data: { outputs: { tasks: [...] } } }
  
  // 优先从 data.outputs 中提取
  if (data.data && data.data.outputs) {
    const outputs = data.data.outputs
    if (outputs.task_list && Array.isArray(outputs.task_list)) {
      return outputs.task_list
    }
    if (outputs.tasks && Array.isArray(outputs.tasks)) {
      return outputs.tasks
    }
    if (outputs.data) {
      return outputs.data
    }
    // 返回整个 outputs
    return outputs
  }
  
  // 兼容直接返回 outputs 的情况
  if (data.outputs) {
    if (data.outputs.task_list && Array.isArray(data.outputs.task_list)) {
      return data.outputs.task_list
    }
    if (data.outputs.tasks && Array.isArray(data.outputs.tasks)) {
      return data.outputs.tasks
    }
    return data.outputs
  }

  // 兼容其他可能的返回格式
  if (data.data) {
    return data.data
  }

  if (data.answer) {
    try {
      const parsed = JSON.parse(data.answer)
      return parsed
    } catch {
      return { tasks: [], raw: data.answer }
    }
  }

  return data || { tasks: [] }
}

/**
 * 获取任务ID列表
 * @returns {Promise<string[]>} 任务ID列表
 */
export const getTaskIdList = async () => {
  // 复用getTaskList函数，但不传taskId参数
  const result = await getTaskList({})
  
  // 从返回结果中提取任务ID列表
  // 可能的返回格式：
  // 1. { task_ids: [...] } 或 { taskIds: [...] }
  // 2. { tasks: [{ id: ... }, ...] } 或 { tasks: [{ task_id: ... }, ...] }
  // 3. 直接是数组 [{ id: ... }, ...]
  // 4. 数组 [id1, id2, ...]
  
  let taskIds = []
  
  if (Array.isArray(result)) {
    // 如果是数组，检查元素是对象还是字符串
    if (result.length > 0) {
      if (typeof result[0] === 'string' || typeof result[0] === 'number') {
        // 直接是ID数组
        taskIds = result.map(id => String(id))
      } else if (result[0].id) {
        // 对象数组，提取id字段
        taskIds = result.map(task => String(task.id))
      } else if (result[0].task_id) {
        // 对象数组，提取task_id字段
        taskIds = result.map(task => String(task.task_id))
      }
    }
  } else if (result.task_ids && Array.isArray(result.task_ids)) {
    taskIds = result.task_ids.map(id => String(id))
  } else if (result.taskIds && Array.isArray(result.taskIds)) {
    taskIds = result.taskIds.map(id => String(id))
  } else if (result.tasks && Array.isArray(result.tasks)) {
    // 从tasks数组中提取ID
    taskIds = result.tasks.map(task => {
      if (typeof task === 'string' || typeof task === 'number') {
        return String(task)
      }
      return String(task.id || task.task_id || task)
    })
  } else if (result.data && Array.isArray(result.data)) {
    // 从data数组中提取ID
    taskIds = result.data.map(item => {
      if (typeof item === 'string' || typeof item === 'number') {
        return String(item)
      }
      return String(item.id || item.task_id || item)
    })
  }
  
  // 去重并排序
  return [...new Set(taskIds)].sort()
}

/**
 * 调用dify workflow获取任务详情
 * @param {Object} params
 * @param {string|number} params.taskId - 任务ID（必需）
 * @returns {Promise<any>} 任务详情数据
 */
export const getTaskDetail = async ({ taskId }) => {
  if (!taskId) {
    throw new Error('Task ID is required')
  }

  const baseEndpoint = config.aiChatApi
  if (!baseEndpoint) {
    throw new Error('AI chat API endpoint is not configured (VITE_AI_CHAT_API)')
  }

  const authStore = useAuthStore()
  const resolvedUserName = (await resolveUserIdentity(authStore)) || 'Guest'

  // 构建workflow API endpoint: /v1/workflows/run
  // 从baseEndpoint中提取基础URL（去掉可能的路径）
  let baseUrl = baseEndpoint
  // 移除可能的路径部分（如 /v1/chat-messages, /v1/apps/xxx/chat-messages 等）
  baseUrl = baseUrl.replace(/\/v1\/.*$/, '').replace(/\/$/, '')
  
  // 判断是否使用代理（开发环境）
  const isDev = import.meta.env.DEV
  let endpoint
  if (isDev) {
    // 开发环境使用 Vite 代理（解决 CORS 问题）
    // 代理会将 /dify-api 转发到 VITE_AI_CHAT_API 配置的服务器
    endpoint = `/dify-api/v1/workflows/run`
  } else {
    // 生产环境直接调用
    endpoint = `${baseUrl}/v1/workflows/run`
  }

  const headers = {}
  const inputs = {
    action: 'get task detail',
    task_id: String(taskId).trim()
  }

  // 使用workflow API格式
  // 根据Dify文档：POST /v1/workflows/run
  // Body: { "inputs": {}, "response_mode": "streaming"|"blocking", "user": "user_id" }
  // workflow 通过 api_key 区分
  const requestBody = {
    inputs,
    response_mode: 'blocking', // 使用阻塞模式，等待完整响应
    user: resolvedUserName
  }

  const body = JSON.stringify(requestBody)
  headers['Content-Type'] = 'application/json'

  // 检查API key是否配置
  if (!config.aiChatKey) {
    throw new Error('AI chat API key is not configured (VITE_AI_CHAT_KEY). Please set it in your environment variables.')
  }
  
  headers.Authorization = `Bearer ${config.aiChatKey}`

  let response
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body,
      // 添加 CORS 相关配置
      mode: 'cors',
      credentials: 'omit'
    })
  } catch (fetchError) {
    // 处理网络错误（包括 CORS 错误）
    console.error('Fetch error details:', {
      endpoint,
      error: fetchError,
      message: fetchError.message,
      stack: fetchError.stack
    })
    
    // 提供更友好的错误信息
    let errorMessage = '网络请求失败'
    if (fetchError.message.includes('Failed to fetch') || fetchError.message.includes('NetworkError')) {
      errorMessage = `无法连接到 Dify API 服务器。可能的原因：
1. CORS 跨域问题：请检查服务器是否允许跨域请求
2. 网络连接问题：请检查网络连接和服务器地址
3. SSL 证书问题：请检查 HTTPS 配置
4. 服务器未响应：请确认服务器地址 ${baseUrl} 是否正确

当前请求的 endpoint: ${endpoint}
请检查浏览器控制台的 Network 标签页查看详细错误信息。`
    } else {
      errorMessage = fetchError.message || '网络请求失败'
    }
    
    throw new Error(errorMessage)
  }

  if (!response.ok) {
    const errorText = await response.text().catch(() => '')
    let errorData
    try {
      errorData = JSON.parse(errorText)
    } catch {
      errorData = { message: errorText }
    }
    
    // 处理各种错误情况
    if (errorData.code === 'not_found' || response.status === 404) {
      throw new Error(
        `Workflow 未找到。` +
        `请确认 API Key 是否正确，或检查该 Workflow 是否已被删除。` +
        `\n当前使用的 endpoint: ${endpoint}`
      )
    }
    
    if (errorData.code === 'not_workflow_app' || errorText.includes('not_workflow_app')) {
      throw new Error(
        `应用模式不匹配：当前 API Key 对应的应用不是 workflow 模式。` +
        `请确认应用类型，或检查 API endpoint 是否正确。` +
        `\n当前使用的 endpoint: ${endpoint}`
      )
    }
    
    if (errorData.code === 'unauthorized' || response.status === 401) {
      throw new Error(
        `认证失败：API Key 无效或已过期。` +
        `请检查 VITE_AI_CHAT_KEY 环境变量配置是否正确。`
      )
    }
    
    throw new Error(
      errorData.message || 
      errorText || 
      `API 请求失败 (状态码: ${response.status})` +
      `\nEndpoint: ${endpoint}`
    )
  }

  const data = await response.json().catch(async () => {
    // 如果不是JSON，尝试解析文本
    const text = await response.text().catch(() => '')
    return { answer: text, data: null }
  })

  // 解析返回的数据，提取任务详情
  // Dify workflow API 返回格式: { data: { outputs: { task_detail: {...} } } }
  // 或者: { outputs: { task_detail: {...} } }
  // 或者: { data: { outputs: { task: {...} } } }
  
  // 优先从 data.outputs 中提取
  if (data.data && data.data.outputs) {
    const outputs = data.data.outputs
    if (outputs.task_detail) {
      return outputs.task_detail
    }
    if (outputs.task) {
      return outputs.task
    }
    if (outputs.data) {
      return outputs.data
    }
    // 返回整个 outputs
    return outputs
  }
  
  // 兼容直接返回 outputs 的情况
  if (data.outputs) {
    if (data.outputs.task_detail) {
      return data.outputs.task_detail
    }
    if (data.outputs.task) {
      return data.outputs.task
    }
    return data.outputs
  }

  // 兼容其他可能的返回格式
  if (data.data) {
    return data.data
  }

  if (data.answer) {
    try {
      const parsed = JSON.parse(data.answer)
      return parsed
    } catch {
      return { raw: data.answer }
    }
  }

  return data || {}
}


