/**
 * 表单对话框 Composable
 * 提供统一的表单对话框逻辑
 *
 * @returns {Object} 返回表单对话框的状态和方法
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useErrorHandler } from './useErrorHandler'

export function useFormDialog(options = {}) {
  const {
    onSubmit,
    onSuccess,
    onError,
    successMessage = '操作成功',
    validateForm
  } = options

  const dialogVisible = ref(false)
  const loading = ref(false)
  const formRef = ref(null)
  const { handleApiError, handleValidationError } = useErrorHandler()

  /**
   * 打开对话框
   */
  const open = () => {
    dialogVisible.value = true
  }

  /**
   * 关闭对话框
   */
  const close = () => {
    dialogVisible.value = false
    if (formRef.value) {
      formRef.value.resetFields()
    }
  }

  /**
   * 提交表单
   */
  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      // 表单验证
      if (validateForm) {
        const valid = await validateForm(formRef.value)
        if (!valid) return
      } else {
        await formRef.value.validate()
      }

      loading.value = true

      // 执行提交
      if (onSubmit) {
        const result = await onSubmit()
        
        // 如果返回 false，不关闭对话框
        if (result === false) {
          loading.value = false
          return
        }

        ElMessage.success(successMessage)
        
        // 执行成功回调
        if (onSuccess) {
          onSuccess(result)
        }

        close()
      }
    } catch (error) {
      // 如果是表单验证错误
      if (error?.fields) {
        handleValidationError(error)
      } else {
        // API 错误
        handleApiError(error, '操作失败')
        
        // 执行错误回调
        if (onError) {
          onError(error)
        }
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置表单
   */
  const resetForm = () => {
    if (formRef.value) {
      formRef.value.resetFields()
    }
  }

  return {
    dialogVisible,
    loading,
    formRef,
    open,
    close,
    handleSubmit,
    resetForm
  }
}

