import service from './axios.js'

/**
 * @brief 提交评论（事件和告警共用）
 * @param {string|number} eventId - 事件ID或告警ID
 * @param {string} comment - 评论内容
 * @param {File[]} files - 可选的文件列表
 * @param {string} workspace - 工作空间（可选，如 'asm'）
 * @returns {Promise} 返回提交结果
 */
export const postComment = (eventId, comment, files = [], workspace = null) => {
  const url = workspace ? `/comments?workspace=${encodeURIComponent(workspace)}` : '/comments'
  
  if (files && files.length > 0) {
    const formData = new FormData()
    formData.append('event_id', eventId)
    formData.append('comment', comment || '')
    if (workspace) formData.append('workspace', workspace)
    formData.append('file', files[0])
    
    return service.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
  
  return service.post(url, {
    event_id: eventId,
    comment: comment,
    ...(workspace && { workspace })
  })
}

