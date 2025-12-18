/**
 * 格式化工具函数库
 */

/**
 * 格式化日期时间
 * @param {string|Date|number} date - 日期字符串、Date对象或时间戳
 * @param {string} format - 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'

  let dateObj
  if (date instanceof Date) {
    dateObj = date
  } else if (typeof date === 'number') {
    dateObj = new Date(date)
  } else if (typeof date === 'string') {
    dateObj = new Date(date)
  } else {
    return '-'
  }

  // 检查日期是否有效
  if (isNaN(dateObj.getTime())) {
    return '-'
  }

  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  const hours = String(dateObj.getHours()).padStart(2, '0')
  const minutes = String(dateObj.getMinutes()).padStart(2, '0')
  const seconds = String(dateObj.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期时间（中文格式）
 * @param {string|Date|number} date - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的日期字符串
 */
export function formatDateZh(date) {
  if (!date) return '-'

  let dateObj
  if (date instanceof Date) {
    dateObj = date
  } else if (typeof date === 'number') {
    dateObj = new Date(date)
  } else if (typeof date === 'string') {
    dateObj = new Date(date)
  } else {
    return '-'
  }

  if (isNaN(dateObj.getTime())) {
    return '-'
  }

  return dateObj.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

/**
 * 格式化日期（仅日期部分，不含时间）
 * @param {string|Date|number} date - 日期字符串、Date对象或时间戳
 * @returns {string} 格式化后的日期字符串 (YYYY-MM-DD)
 */
export function formatDateOnly(date) {
  return formatDate(date, 'YYYY-MM-DD')
}

/**
 * 格式化金额
 * @param {number|string} amount - 金额
 * @param {number} decimals - 小数位数，默认 2
 * @returns {string} 格式化后的金额字符串
 */
export function formatAmount(amount, decimals = 2) {
  if (amount === null || amount === undefined || amount === '') return '0.00'

  const num = Number(amount)
  if (isNaN(num)) return '0.00'

  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 规范化单价（保留指定小数位，默认2位）
 * @param {number|string} price - 单价
 * @param {number} decimals - 小数位数，默认 2
 * @returns {number} 规范化后的单价
 */
export function normalizePrice(price, decimals = 2) {
  const num = Number(price)
  if (isNaN(num) || num < 0) return 0
  const multiplier = Math.pow(10, decimals)
  return Math.round(num * multiplier) / multiplier
}

/**
 * 规范化数量（四舍五入到整数）
 * @param {number|string} quantity - 数量
 * @returns {number} 规范化后的数量（整数）
 */
export function normalizeQuantity(quantity) {
  const num = Number(quantity)
  if (isNaN(num) || num < 0) return 0
  return Math.round(num)
}

/**
 * 精确计算金额（避免浮点数精度问题）
 * 注意：函数内部会自动规范化单价和数量，无需外部预处理
 * @param {number|string} unitPrice - 单价
 * @param {number|string} quantity - 数量（会自动规范化为整数）
 * @param {number} decimals - 小数位数，默认 2
 * @returns {number} 精确计算的金额
 */
export function calculateAmount(unitPrice, quantity, decimals = 2) {
  // 规范化单价和数量
  const price = normalizePrice(unitPrice, decimals)
  const qty = normalizeQuantity(quantity)
  
  // 检查是否为有效数字
  if (price <= 0 || qty <= 0) return 0
  
  // 使用整数运算避免浮点数精度问题
  const multiplier = Math.pow(10, decimals)
  
  // 转换为整数进行计算（完全避免浮点数）
  const priceInt = Math.round(price * multiplier)
  const qtyInt = qty // 数量已经是整数
  
  // 整数相乘
  const resultInt = priceInt * qtyInt
  
  // 除以 multiplier，得到结果
  const result = resultInt / multiplier
  
  // 最后再次四舍五入到指定小数位，确保精度
  return parseFloat(result.toFixed(decimals))
}

/**
 * 格式化金额（带货币符号）
 * @param {number|string} amount - 金额
 * @param {string} symbol - 货币符号，默认 '¥'
 * @param {number} decimals - 小数位数，默认 2
 * @returns {string} 格式化后的金额字符串
 */
export function formatCurrency(amount, symbol = '¥', decimals = 2) {
  return `${symbol}${formatAmount(amount, decimals)}`
}

/**
 * 格式化文件大小
 * @param {number|string} bytes - 文件大小（字节）
 * @param {number} decimals - 小数位数，默认 2
 * @returns {string} 格式化后的文件大小字符串
 */
export function formatFileSize(bytes, decimals = 2) {
  if (!bytes || bytes === 0) return '0 B'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * 格式化数字（千分位）
 * @param {number|string} num - 数字
 * @param {number} decimals - 小数位数，默认 0
 * @returns {string} 格式化后的数字字符串
 */
export function formatNumber(num, decimals = 0) {
  if (num === null || num === undefined || num === '') return '0'

  const number = Number(num)
  if (isNaN(number)) return '0'

  return number.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 格式化百分比
 * @param {number|string} value - 数值（0-1之间的小数或0-100之间的整数）
 * @param {number} decimals - 小数位数，默认 2
 * @param {boolean} isDecimal - 是否为小数形式（0-1），默认 false
 * @returns {string} 格式化后的百分比字符串
 */
export function formatPercent(value, decimals = 2, isDecimal = false) {
  if (value === null || value === undefined || value === '') return '0%'

  const num = Number(value)
  if (isNaN(num)) return '0%'

  const percentValue = isDecimal ? num * 100 : num
  return `${percentValue.toFixed(decimals)}%`
}

/**
 * 格式化手机号（隐藏中间4位）
 * @param {string} phone - 手机号
 * @returns {string} 格式化后的手机号
 */
export function formatPhone(phone) {
  if (!phone || typeof phone !== 'string') return phone
  if (phone.length !== 11) return phone

  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 格式化银行卡号（显示后4位）
 * @param {string} cardNo - 银行卡号
 * @returns {string} 格式化后的银行卡号
 */
export function formatBankCard(cardNo) {
  if (!cardNo || typeof cardNo !== 'string') return cardNo
  if (cardNo.length < 4) return cardNo

  const lastFour = cardNo.slice(-4)
  const stars = '*'.repeat(cardNo.length - 4)
  return stars + lastFour
}

/**
 * 格式化相对时间（如：1分钟前、2小时前、3天前）
 * @param {string|Date|number} date - 日期字符串、Date对象或时间戳
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(date) {
  if (!date) return '-'

  let dateObj
  if (date instanceof Date) {
    dateObj = date
  } else if (typeof date === 'number') {
    dateObj = new Date(date)
  } else if (typeof date === 'string') {
    dateObj = new Date(date)
  } else {
    return '-'
  }

  if (isNaN(dateObj.getTime())) {
    return '-'
  }

  const now = new Date()
  const diff = now - dateObj
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)

  if (years > 0) {
    return `${years}年前`
  } else if (months > 0) {
    return `${months}个月前`
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}
