import service from './axios'

/**
 * 用户登录
 * @param {Object} credentials - 登录凭据
 * @param {string} credentials.username - 用户名
 * @param {string} credentials.password - 密码
 * @returns {Promise} 返回登录响应，包含 access_token 和 refresh_token
 */
export const login = (credentials) => {
  // 后端登录接口在 /api/login
  return service({
    url: '/login',
    method: 'post',
    data: credentials
  })
}

/**
 * 用户登出
 * @returns {Promise} 返回登出响应
 */
export const logout = () => {
  return service({
    url: '/logout',
    method: 'post'
  })
}

/**
 * 刷新访问令牌
 * @returns {Promise} 返回新的 access_token 和 refresh_token
 */
export const refreshToken = () => {
  return service({
    url: '/refresh',
    method: 'post'
  })
}

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_pwd - 旧密码
 * @param {string} passwordData.new_pwd - 新密码
 * @returns {Promise} 返回修改密码响应
 */
export const updatePassword = (passwordData) => {
  return service({
    url: '/user/password',
    method: 'put',
    data: passwordData
  })
}

