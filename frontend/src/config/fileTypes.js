/**
 * 文件类型配置
 * 与后端 backend/app/core/config.py 中的配置保持一致
 */

// 项目附件支持的文件类型（更灵活，支持多种文档和图片格式）
export const PROJECT_FILE_EXTENSIONS = [
  'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', // 图片格式
  'pdf', // PDF文档
  'doc', 'docx', // Word文档
  'xls', 'xlsx', // Excel文档
  'ppt', 'pptx' // PowerPoint文档
]

// 证件资质支持的文件类型（更严格，仅支持图片和PDF，用于证明资质）
export const QUALIFICATION_FILE_EXTENSIONS = [
  'jpg', 'jpeg', 'png', // 图片格式
  'pdf' // PDF文档
]

// 获取文件类型的 accept 属性值（用于 el-upload）
export function getAcceptString(extensions) {
  return extensions.map(ext => `.${ext}`).join(',')
}

// 获取文件类型的提示文本
export function getFileTypeTip(extensions, maxSizeMB = 10) {
  return `支持上传多个文件，单个文件不超过${maxSizeMB}MB；支持格式：${extensions.join(', ')}`
}

// 验证文件类型
export function validateFileType(filename, allowedExtensions) {
  if (!filename) return false
  const fileExtension = filename.split('.').pop()?.toLowerCase()
  return fileExtension && allowedExtensions.includes(fileExtension)
}

