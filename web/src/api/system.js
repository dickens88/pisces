import request from './axios'

// 获取平台信息（当前登录用户名、平台版本等）
export function getSystemInfo() {
  return request({
    url: '/system/info',
    method: 'get'
  })
}