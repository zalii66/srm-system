/**
 * 错误处理 Composable
 * 提供统一的错误处理功能
 */
import { ElMessage } from 'element-plus'

export function useErrorHandler() {
  /**
   * 处理 API 错误
   * @param {Error} error - 错误对象
   * @param {string} defaultMessage - 默认错误消息
   */
  const handleApiError = (error, defaultMessage = '操作失败') => {
    let errorMessage = defaultMessage

    if (error.response) {
      // 后端返回的错误
      const { data, status } = error.response

      // FastAPI 通常使用 detail 字段
      if (data?.detail) {
        errorMessage = data.detail
      } else if (data?.message) {
        errorMessage = data.message
      } else if (data?.error) {
        errorMessage = data.error
      } else if (status === 401) {
        errorMessage = '未授权，请重新登录'
      } else if (status === 403) {
        errorMessage = '没有权限执行此操作'
      } else if (status === 404) {
        errorMessage = '资源不存在'
      } else if (status === 422) {
        errorMessage = '请求参数错误'
      } else if (status === 500) {
        errorMessage = '服务器内部错误'
      }
    } else if (error.message) {
      // 网络错误或其他错误
      if (error.message.includes('Network Error')) {
        errorMessage = '网络连接失败，请检查网络'
      } else if (error.message.includes('timeout')) {
        errorMessage = '请求超时，请稍后重试'
      } else {
        errorMessage = error.message
      }
    }

    ElMessage.error(errorMessage)
    console.error('API Error:', error)
  }

  /**
   * 获取错误消息（不显示）
   * @param {Error} error - 错误对象
   * @param {string} defaultMessage - 默认错误消息
   * @returns {string} 错误消息
   */
  const getErrorMessage = (error, defaultMessage = '操作失败') => {
    if (error.response?.data?.detail) {
      return error.response.data.detail
    } else if (error.response?.data?.message) {
      return error.response.data.message
    } else if (error.message) {
      return error.message
    }
    return defaultMessage
  }

  return {
    handleApiError,
    getErrorMessage
  }
}
