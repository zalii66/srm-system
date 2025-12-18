/**
 * 确认对话框 Composable
 * 提供统一的确认对话框功能
 */
import { ElMessageBox } from 'element-plus'

export function useConfirm() {
  /**
   * 显示删除确认对话框
   * @param {string} message - 确认消息
   * @returns {Promise} 用户确认时 resolve，取消时 reject
   */
  const confirmDelete = (message = '确定要删除吗？') => {
    return ElMessageBox.confirm(message, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    })
      .then(() => {
        return Promise.resolve()
      })
      .catch(action => {
        if (action === 'cancel') {
          return Promise.reject('cancel')
        }
        return Promise.reject(action)
      })
  }

  /**
   * 显示通用确认对话框
   * @param {string} message - 确认消息
   * @param {string} title - 标题
   * @param {Object} options - 其他选项
   * @returns {Promise} 用户确认时 resolve，取消时 reject
   */
  const confirm = (message, title = '提示', options = {}) => {
    return ElMessageBox.confirm(message, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      ...options
    })
      .then(() => {
        return Promise.resolve()
      })
      .catch(action => {
        if (action === 'cancel') {
          return Promise.reject('cancel')
        }
        return Promise.reject(action)
      })
  }

  return {
    confirmDelete,
    confirm
  }
}
