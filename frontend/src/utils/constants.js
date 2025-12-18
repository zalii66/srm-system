/**
 * 系统常量配置
 * 统一管理模板中使用的硬编码值
 */

// 对话框宽度
export const DIALOG_WIDTH = {
  SMALL: '500px',
  MEDIUM: '600px',
  LARGE: '800px',
  XLARGE: '80%'
}

// 表单标签宽度
export const FORM_LABEL_WIDTH = {
  DEFAULT: '120px',
  SMALL: '100px'
}

// 供应商状态常量
export const SupplierStatus = {
  PENDING: -1,   // 待审核
  REJECTED: 0,   // 审核失败
  APPROVED: 1    // 审核通过
}
