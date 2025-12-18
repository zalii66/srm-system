/**
 * 表单验证错误处理 Composable
 * 提供统一的表单验证错误处理功能，包括：
 * - 处理 HTTP 422 验证错误
 * - 字段级错误提示
 * - 自动滚动到错误字段
 * - 错误字段高亮显示
 * - 中文错误消息转换
 */
import { nextTick } from 'vue'
import { ElMessage } from 'element-plus'

/**
 * 错误消息翻译字典
 * 将后端返回的英文错误消息转换为中文
 */
const ERROR_MESSAGE_MAP = {
  'at least': (match) => {
    const numMatch = match.match(/at least (\d+)/)
    if (numMatch) {
      return `至少需要 ${numMatch[1]} 个字符`
    }
    return '长度不符合要求'
  },
  'required': '此字段为必填项',
  'invalid': '格式不正确',
  'greater than': '值必须大于指定值',
  'less than': '值必须小于指定值',
  'maximum': (match) => {
    const numMatch = match.match(/maximum (\d+)/)
    if (numMatch) {
      return `最多 ${numMatch[1]} 个字符`
    }
    return '长度超过限制'
  },
  'minimum': (match) => {
    const numMatch = match.match(/minimum (\d+)/)
    if (numMatch) {
      return `最少 ${numMatch[1]} 个字符`
    }
    return '长度不足'
  },
  'type_error': '数据类型错误',
  'value_error': '值错误'
}

/**
 * 翻译错误消息
 * @param {string} errorMessage - 原始错误消息
 * @returns {string} 翻译后的错误消息
 */
function translateErrorMessage(errorMessage) {
  if (!errorMessage || typeof errorMessage !== 'string') {
    return '验证失败'
  }

  // 查找匹配的错误消息模式
  for (const [key, value] of Object.entries(ERROR_MESSAGE_MAP)) {
    if (errorMessage.toLowerCase().includes(key.toLowerCase())) {
      if (typeof value === 'function') {
        return value(errorMessage)
      }
      return value
    }
  }

  return errorMessage
}

/**
 * 解析字段路径
 * @param {Array} loc - 错误位置数组，例如 ['body', 'project_name'] 或 ['body', 'items', 0, 'item_name']
 * @returns {string} 字段名
 */
function parseFieldPath(loc) {
  if (!Array.isArray(loc) || loc.length < 2) {
    return null
  }

  // 跳过 'body' 前缀，获取实际字段名
  const fieldPath = loc.slice(1)
  let fieldName = fieldPath[0]

  // 处理嵌套字段（如 items[0].item_name）
  if (fieldPath.length > 1) {
    fieldName = `${fieldPath[0]}[${fieldPath[1]}]`
    if (fieldPath.length > 2) {
      fieldName = `${fieldName}.${fieldPath[2]}`
    }
  }

  return fieldName
}

/**
 * 滚动到错误字段
 * @param {string} fieldName - 字段名（表单项的 prop）
 * @param {number} delay - 延迟时间（毫秒）
 */
function scrollToErrorField(fieldName, delay = 100) {
  nextTick(() => {
    setTimeout(() => {
      let errorElement = null

      // 如果提供了字段名，先尝试查找对应的表单项
      if (fieldName) {
        const formItems = document.querySelectorAll('.el-form-item')
        for (const item of formItems) {
          const prop = item.getAttribute('prop')
          if (prop === fieldName) {
            errorElement = item
            break
          }
        }
      }

      // 如果找不到，尝试查找第一个有错误的表单项
      if (!errorElement) {
        errorElement = document.querySelector('.el-form-item.is-error')
      }

      if (errorElement) {
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        highlightErrorField(errorElement)
      }
    }, delay)
  })
}

/**
 * 高亮错误输入框
 * @param {HTMLElement} formItemElement - 表单项元素
 * @param {number} duration - 高亮持续时间（毫秒），默认 3000ms
 */
function highlightErrorField(formItemElement, duration = 3000) {
  if (!formItemElement) return

  const inputElement = formItemElement.querySelector(
    '.el-input__wrapper, .el-select__wrapper, .el-textarea__inner'
  )

  if (inputElement) {
    // 添加高亮样式
    inputElement.style.boxShadow = '0 0 0 2px rgba(245, 108, 108, 0.2)'
    inputElement.style.borderColor = '#f56c6c'

    // 延迟后移除高亮
    setTimeout(() => {
      inputElement.style.boxShadow = ''
      inputElement.style.borderColor = ''
    }, duration)
  }
}

/**
 * 处理前端验证失败
 * 当 Element Plus 表单验证失败时，滚动到第一个错误字段
 */
function handleFrontendValidationError() {
  scrollToErrorField(null)
}

/**
 * 表单验证错误处理 Composable
 * @param {Ref} formRef - Element Plus 表单引用
 * @param {Object} form - 表单数据对象（用于设置字段值）
 * @param {Object} options - 配置选项
 * @param {Object} options.fieldNameMap - 字段名映射，将后端字段名映射到前端表单项的 prop
 * @param {Object} options.fieldLabelMap - 字段标签映射，用于显示字段中文名称（可选）
 * @param {boolean} options.showTopMessage - 是否显示顶部错误提示消息，默认 true
 * @param {string} options.topMessage - 顶部错误提示消息，默认 '表单验证失败，请检查下方红色标记的字段'
 * @returns {Object} 验证错误处理函数
 */
export function useFormValidation(formRef, form = null, options = {}) {
  const {
    fieldNameMap = {},
    fieldLabelMap = {},
    showTopMessage = true,
    topMessage = '表单验证失败，请检查下方红色标记的字段'
  } = options

  /**
   * 处理验证错误
   * @param {Array} errors - 错误数组，格式：[{ loc: ['body', 'field'], msg: 'error message' }, ...]
   * @param {Object} customForm - 自定义表单对象（可选，如果不提供则使用传入的 form）
   */
  const handleValidationErrors = (errors, customForm = null) => {
    if (!formRef.value || !errors || !Array.isArray(errors) || errors.length === 0) {
      return
    }

    const formData = customForm || form
    const fieldErrors = {}
    let firstErrorField = null

    // 处理每个错误
    errors.forEach(error => {
      // 解析字段路径
      const fieldName = parseFieldPath(error.loc)
      if (!fieldName) return

      // 映射到表单项 prop
      const formField = fieldNameMap[fieldName] || fieldName

      // 翻译错误消息
      const errorMessage = translateErrorMessage(error.msg || '验证失败')

      // 收集字段错误
      if (!fieldErrors[formField]) {
        fieldErrors[formField] = []
      }
      fieldErrors[formField].push(errorMessage)

      // 记录第一个错误字段，用于滚动定位
      if (!firstErrorField) {
        firstErrorField = formField
      }
    })

    // 设置字段错误
    const fieldsToSet = {}
    Object.keys(fieldErrors).forEach(field => {
      fieldsToSet[field] = {
        message: fieldErrors[field].join('；'),
        value: formData && formData[field] !== undefined ? formData[field] : undefined
      }
    })

    if (Object.keys(fieldsToSet).length > 0) {
      formRef.value.setFields(fieldsToSet)

      // 显示顶部错误提示
      if (showTopMessage) {
        ElMessage.error(topMessage)
      }

      // 滚动到第一个错误字段
      if (firstErrorField) {
        scrollToErrorField(firstErrorField)
      }
    }
  }

  /**
   * 处理 API 错误
   * 自动识别 422 验证错误并调用 handleValidationErrors
   * @param {Error} error - API 错误对象
   * @param {Object} customForm - 自定义表单对象（可选）
   * @returns {boolean} 是否已处理验证错误
   */
  const handleApiError = (error, customForm = null) => {
    // 处理验证错误（422）
    if (error.response?.status === 422) {
      const errors = error.response?.data?.errors || []
      if (errors.length > 0) {
        handleValidationErrors(errors, customForm)
        return true
      } else {
        // 如果没有 errors 数组，尝试显示 detail
        const errorMsg = error.response?.data?.detail || '请求参数验证失败'
        ElMessage.error(errorMsg)
        return true
      }
    }

    return false
  }

  /**
   * 处理完整的表单提交错误
   * 结合前端验证失败和 API 错误处理
   * @param {Error} error - 错误对象
   * @param {Object} customForm - 自定义表单对象（可选）
   * @param {string} defaultMessage - 默认错误消息
   */
  const handleSubmitError = (error, customForm = null, defaultMessage = '操作失败') => {
    // 先尝试处理验证错误
    if (handleApiError(error, customForm)) {
      return
    }

    // 处理其他错误
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      defaultMessage
    ElMessage.error(errorMsg)
  }

  return {
    // 核心函数
    handleValidationErrors, // 处理验证错误
    handleApiError, // 处理 API 错误（自动识别 422）
    handleSubmitError, // 处理完整的表单提交错误

    // 工具函数
    scrollToErrorField, // 滚动到错误字段
    highlightErrorField, // 高亮错误字段
    translateErrorMessage, // 翻译错误消息
    handleFrontendValidationError // 处理前端验证失败
  }
}

