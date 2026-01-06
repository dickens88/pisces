import service from './axios.js'

/**
 * @brief 提交评论（事件和告警共用）
 * @param {string|number} eventId - 事件ID或告警ID
 * @param {string} comment - 评论内容
 * @param {File[]} files - 可选的文件列表
 * @param {string} workspace - 工作空间（可选，如 'asm'）
 * @param {string} commentType - 评论类型（可选）
 * @returns {Promise} 返回提交结果
 */
export const postComment = (eventId, comment, files = [], workspace = null, commentType = 'comment') => {
  const url = workspace ? `/comments?workspace=${encodeURIComponent(workspace)}` : '/comments'
  
  if (files && files.length > 0) {
    const formData = new FormData()
    formData.append('event_id', eventId)
    formData.append('comment', comment || '')
    if (workspace) formData.append('workspace', workspace)
    if (commentType) formData.append('comment_type', commentType)
    formData.append('file', files[0])
    
    return service.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
  
  return service.post(url, {
    event_id: eventId,
    comment: comment,
    ...(workspace && { workspace }),
    ...(commentType && { comment_type: commentType })
  })
}

/**
 * @brief 更新评论
 * @param {string|number} eventId - 事件ID或告警ID
 * @param {string} commentId - 评论ID
 * @param {string} comment - 评论内容
 * @param {string} commentType - 评论类型（可选）
 * @returns {Promise} 返回更新结果
 */
export const updateComment = (eventId, commentId, comment, commentType = null) => {
  const url = `/comments/${eventId}/${commentId}`
  return service.put(url, {
    comment: comment,
    ...(commentType && { comment_type: commentType })
  })
}

/**
 * @brief 删除评论
 * @param {string|number} eventId - 事件ID或告警ID
 * @param {string} commentId - 评论ID
 * @returns {Promise} 返回删除结果
 */
export const deleteComment = (eventId, commentId) => {
  const url = `/comments/${eventId}/${commentId}`
  return service.delete(url)
}

