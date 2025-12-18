import request from '@/utils/request'

export function registerSupplier(data) {
  return request({
    url: '/suppliers/register',
    method: 'post',
    data
  })
}

export function getSupplierList(params) {
  return request({
    url: '/suppliers/',
    method: 'get',
    params
  })
}

export function getSupplierDetail(id) {
  return request({
    url: `/suppliers/${id}`,
    method: 'get'
  })
}

export function getCurrentSupplier() {
  return request({
    url: '/suppliers/me',
    method: 'get'
  })
}

export function updateSupplier(data) {
  return request({
    url: '/suppliers/me',
    method: 'put',
    data
  })
}

export function auditSupplier(id, data) {
  return request({
    url: `/suppliers/${id}/audit`,
    method: 'post',
    data
  })
}

/**
 * 上传证件资质文件（支持多个文件）
 */
export function uploadQualification(files) {
  const formData = new FormData()
  // 如果 files 是单个文件，转为数组
  const fileList = Array.isArray(files) ? files : [files]
  fileList.forEach(file => {
    // 确保每个文件都使用 'files' 作为字段名（FastAPI 期望 List[UploadFile]）
    formData.append('files', file)
  })
  return request({
    url: '/suppliers/me/qualification',
    method: 'post',
    data: formData
    // 不设置 Content-Type，axios 会自动检测 FormData 并设置正确的 multipart/form-data 和 boundary
  })
}

/**
 * 删除证件资质文件
 */
export function deleteQualificationFile(fileIndex) {
  return request({
    url: `/suppliers/me/qualification/${fileIndex}`,
    method: 'delete'
  })
}

export function getSupplierProjects(id, params) {
  return request({
    url: `/suppliers/${id}/projects`,
    method: 'get',
    params
  })
}

/**
 * 上传营业执照图片
 */
export function uploadBusinessLicense(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/suppliers/me/business-license',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取营业执照图片URL
 */
export function getBusinessLicenseUrl(filename) {
  return `/api/v1/uploads/business_license/${filename}`
}

/**
 * 删除供应商
 */
export function deleteSupplier(id) {
  return request({
    url: `/suppliers/${id}`,
    method: 'delete'
  })
}
