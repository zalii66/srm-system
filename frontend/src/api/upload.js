import request from '@/utils/request'

export function uploadFiles(files, category = 'project') {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  formData.append('category', category)

  return request({
    url: '/upload/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getFiles(params) {
  return request({
    url: '/upload/',
    method: 'get',
    params
  })
}

export function getFileDetail(fileId) {
  return request({
    url: `/upload/${fileId}`,
    method: 'get'
  })
}

export function deleteFile(fileId) {
  return request({
    url: `/upload/${fileId}`,
    method: 'delete'
  })
}

export function downloadFile(fileId, projectId = null) {
  const params = {}
  if (projectId) {
    params.project_id = projectId
  }
  return request({
    url: `/upload/${fileId}/download`,
    method: 'get',
    params,
    responseType: 'blob'
  })
}
