import service from './axios.js'

/**
 * @brief 提交评论（事件和告警共用）
 * @param {string|number} eventId - 事件ID或告警ID
 * @param {string} comment - 评论内容
 * @param {File[]} files - 可选的文件列表
 * @returns {Promise} 返回提交结果
 */
export const postComment = (eventId, comment, files = []) => {
  // 如果有文件，使用 FormData 上传
  if (files && files.length > 0) {
    const formData = new FormData()
    formData.append('event_id', eventId)
    formData.append('comment', comment || '')
    
    // 如果有多个文件，只上传第一个（根据需求可以修改为支持多文件）
    if (files.length > 0) {
      formData.append('file', files[0])
    }
    
    return service.post('/comments', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  } else {
    // 没有文件，使用 JSON 格式
    return service.post('/comments', {
      event_id: eventId,
      comment: comment
    })
  }
}

