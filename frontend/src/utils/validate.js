/**
 * 验证工具函数库
 */

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否为有效的邮箱格式
 */
export function validateEmail(email) {
  if (!email || typeof email !== 'string') return false

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email.trim())
}

/**
 * 验证手机号格式（中国大陆）
 * @param {string} phone - 手机号
 * @returns {boolean} 是否为有效的手机号格式
 */
export function validatePhone(phone) {
  if (!phone || typeof phone !== 'string') return false

  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone.trim())
}

/**
 * 验证固定电话格式（中国大陆）
 * @param {string} tel - 固定电话
 * @returns {boolean} 是否为有效的固定电话格式
 */
export function validateTel(tel) {
  if (!tel || typeof tel !== 'string') return false

  const telRegex = /^0\d{2,3}-?\d{7,8}$/
  return telRegex.test(tel.trim())
}

/**
 * 验证必填项
 * @param {any} value - 要验证的值
 * @returns {boolean} 是否不为空
 */
export function validateRequired(value) {
  if (value === null || value === undefined) return false
  if (typeof value === 'string' && value.trim() === '') return false
  if (Array.isArray(value) && value.length === 0) return false
  if (typeof value === 'object' && Object.keys(value).length === 0) return false
  return true
}

/**
 * 验证身份证号格式（18位）
 * @param {string} idCard - 身份证号
 * @returns {boolean} 是否为有效的身份证号格式
 */
export function validateIdCard(idCard) {
  if (!idCard || typeof idCard !== 'string') return false

  const idCardRegex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/
  if (!idCardRegex.test(idCard.trim())) {
    return false
  }

  // 验证校验位
  const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
  const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

  let sum = 0
  for (let i = 0; i < 17; i++) {
    sum += parseInt(idCard[i]) * weights[i]
  }

  const checkCode = checkCodes[sum % 11]
  return idCard[17].toUpperCase() === checkCode
}

/**
 * 验证URL格式
 * @param {string} url - URL地址
 * @returns {boolean} 是否为有效的URL格式
 */
export function validateUrl(url) {
  if (!url || typeof url !== 'string') return false

  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证IP地址格式
 * @param {string} ip - IP地址
 * @returns {boolean} 是否为有效的IP地址格式
 */
export function validateIp(ip) {
  if (!ip || typeof ip !== 'string') return false

  const ipRegex =
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return ipRegex.test(ip.trim())
}

/**
 * 验证密码强度
 * @param {string} password - 密码
 * @param {object} options - 选项配置
 * @param {number} options.minLength - 最小长度，默认 6
 * @param {number} options.maxLength - 最大长度，默认 20
 * @param {boolean} options.requireUppercase - 是否必须包含大写字母，默认 false
 * @param {boolean} options.requireLowercase - 是否必须包含小写字母，默认 false
 * @param {boolean} options.requireNumber - 是否必须包含数字，默认 false
 * @param {boolean} options.requireSpecial - 是否必须包含特殊字符，默认 false
 * @returns {object} 验证结果 { valid: boolean, message: string }
 */
export function validatePassword(password, options = {}) {
  const {
    minLength = 6,
    maxLength = 20,
    requireUppercase = false,
    requireLowercase = false,
    requireNumber = false,
    requireSpecial = false
  } = options

  if (!password || typeof password !== 'string') {
    return { valid: false, message: '密码不能为空' }
  }

  if (password.length < minLength) {
    return { valid: false, message: `密码长度不能少于${minLength}位` }
  }

  if (password.length > maxLength) {
    return { valid: false, message: `密码长度不能超过${maxLength}位` }
  }

  if (requireUppercase && !/[A-Z]/.test(password)) {
    return { valid: false, message: '密码必须包含大写字母' }
  }

  if (requireLowercase && !/[a-z]/.test(password)) {
    return { valid: false, message: '密码必须包含小写字母' }
  }

  if (requireNumber && !/\d/.test(password)) {
    return { valid: false, message: '密码必须包含数字' }
  }

  if (requireSpecial && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    return { valid: false, message: '密码必须包含特殊字符' }
  }

  return { valid: true, message: '密码格式正确' }
}

/**
 * 验证数字范围
 * @param {number|string} value - 数值
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {boolean} 是否在范围内
 */
export function validateRange(value, min, max) {
  const num = Number(value)
  if (isNaN(num)) return false
  return num >= min && num <= max
}

/**
 * 验证字符串长度
 * @param {string} str - 字符串
 * @param {number} min - 最小长度
 * @param {number} max - 最大长度
 * @returns {boolean} 长度是否在范围内
 */
export function validateLength(str, min, max) {
  if (typeof str !== 'string') return false
  const length = str.trim().length
  return length >= min && length <= max
}

/**
 * 验证是否为整数
 * @param {number|string} value - 要验证的值
 * @returns {boolean} 是否为整数
 */
export function validateInteger(value) {
  if (value === null || value === undefined || value === '') return false
  const num = Number(value)
  return !isNaN(num) && Number.isInteger(num)
}

/**
 * 验证是否为浮点数
 * @param {number|string} value - 要验证的值
 * @returns {boolean} 是否为浮点数
 */
export function validateFloat(value) {
  if (value === null || value === undefined || value === '') return false
  const num = Number(value)
  return !isNaN(num) && isFinite(num)
}

/**
 * 验证日期格式
 * @param {string} dateStr - 日期字符串
 * @param {string} format - 日期格式，默认 'YYYY-MM-DD'
 * @returns {boolean} 是否为有效的日期格式
 */
export function validateDate(dateStr, format = 'YYYY-MM-DD') {
  if (!dateStr || typeof dateStr !== 'string') return false

  // 简单的日期格式验证
  if (format === 'YYYY-MM-DD') {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(dateStr)) return false

    const date = new Date(dateStr)
    return !isNaN(date.getTime())
  }

  // 可以扩展其他格式
  const date = new Date(dateStr)
  return !isNaN(date.getTime())
}

/**
 * 验证中国邮政编码
 * @param {string} postalCode - 邮政编码
 * @returns {boolean} 是否为有效的邮政编码
 */
export function validatePostalCode(postalCode) {
  if (!postalCode || typeof postalCode !== 'string') return false

  const postalCodeRegex = /^[1-9]\d{5}$/
  return postalCodeRegex.test(postalCode.trim())
}

/**
 * 验证统一社会信用代码
 * @param {string} creditCode - 统一社会信用代码
 * @returns {boolean} 是否为有效的统一社会信用代码
 */
export function validateCreditCode(creditCode) {
  if (!creditCode || typeof creditCode !== 'string') return false

  const creditCodeRegex = /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/
  return creditCodeRegex.test(creditCode.trim().toUpperCase())
}
