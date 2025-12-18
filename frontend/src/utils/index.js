/**
 * 工具函数统一导出
 */

// 格式化函数
export {
  formatDate,
  formatDateZh,
  formatDateOnly,
  formatAmount,
  formatCurrency,
  calculateAmount,
  normalizePrice,
  normalizeQuantity,
  formatFileSize,
  formatNumber,
  formatPercent,
  formatPhone,
  formatBankCard,
  formatRelativeTime
} from './format'

// 验证函数
export {
  validateEmail,
  validatePhone,
  validateTel,
  validateRequired,
  validateIdCard,
  validateUrl,
  validateIp,
  validatePassword,
  validateRange,
  validateLength,
  validateInteger,
  validateFloat,
  validateDate,
  validatePostalCode,
  validateCreditCode
} from './validate'

// 常量
export * from './constants'

// 导出常量（方便使用）
export { DIALOG_WIDTH, FORM_LABEL_WIDTH } from './constants'

// 防抖函数
export { debounce } from './debounce'

// API配置工具
export { getApiBaseUrl, getFileUrl, getApiUrl } from './api'
