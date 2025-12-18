/**
 * API配置工具
 * 统一管理API基础URL，避免硬编码
 */

/**
 * 获取API基础URL
 * 优先使用环境变量，开发环境使用默认值
 */
export function getApiBaseUrl() {
  // 生产环境使用环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // 开发环境：如果使用代理，返回空字符串（使用相对路径）
  // 如果直接访问后端，使用默认地址
  if (import.meta.env.DEV) {
    // 开发模式下，默认使用代理，返回空字符串
    // 如果需要直接访问后端，可以在 .env.development 中设置 VITE_API_BASE_URL
    return ''
  }
  
  // 生产环境必须设置 VITE_API_BASE_URL
  // 如果未设置，使用当前域名
  return window.location.origin
}

/**
 * 获取完整文件URL
 * @param {string} filePath 文件路径（相对路径或绝对路径）
 * @returns {string} 完整的文件URL
 */
export function getFileUrl(filePath) {
  if (!filePath) return ''
  
  // 如果已经是完整URL，直接返回
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath
  }
  
  // 标准化路径：移除 /api/v1 前缀（如果存在）
  let normalizedPath = filePath
  if (normalizedPath.startsWith('/api/v1/uploads/')) {
    normalizedPath = normalizedPath.replace('/api/v1', '')
  }
  
  // 确保路径以 /uploads/ 开头
  if (!normalizedPath.startsWith('/uploads/')) {
    console.warn('文件路径格式不正确:', filePath)
    return filePath
  }
  
  const baseURL = getApiBaseUrl()
  
  // 如果baseURL为空（开发环境使用代理），文件路径直接使用 /uploads（不在 /api/v1 下）
  if (!baseURL) {
    // 开发环境：文件服务在 /uploads 路径下，需要代理到后端
    // 注意：文件路径不在 /api/v1 下，需要单独配置代理
    return normalizedPath
  }
  
  // 生产环境：拼接完整URL
  return `${baseURL}${normalizedPath}`
}

/**
 * 获取API完整URL
 * @param {string} path API路径（如 /api/v1/users）
 * @returns {string} 完整的API URL
 */
export function getApiUrl(path) {
  const baseURL = getApiBaseUrl()
  
  // 如果baseURL为空（开发环境使用代理），使用相对路径
  if (!baseURL) {
    return path.startsWith('/') ? path : `/${path}`
  }
  
  // 生产环境：拼接完整URL
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${baseURL}${normalizedPath}`
}

