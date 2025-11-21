/**
 * 统一配置文件 - 用于 vite.config.js（构建时）和运行时
 */
export function getAppConfig(env = {}, isProd = false) { 
  return {
    enableAuth: env.VITE_ENABLE_AUTH !== 'false',
    authMode: env.VITE_AUTH_MODE || 'local',
    tianyanWebBaseURL: env.VITE_TIANYAN_WEB_BASE_URL || 'http://localhost:3000',
    apiBaseURL: env.VITE_API_BASE_URL || '/api',
    apiTarget: env.VITE_API_TARGET || (isProd ? 'http://pisces.eu.dearcharles.cn:8080' : 'http://localhost:8080'),
    aiChatApi: env.VITE_AI_CHAT_API || '',
    aiChatKey: env.VITE_AI_CHAT_KEY || ''
  }
}

