import request from '@/utils/request'

export function createProject(data) {
  return request({
    url: '/projects/',
    method: 'post',
    data
  })
}

export function getProjectList(params) {
  return request({
    url: '/projects/',
    method: 'get',
    params
  })
}

export function getProjectDetail(id) {
  return request({
    url: `/projects/${id}`,
    method: 'get'
  })
}

export function updateProject(id, data) {
  return request({
    url: `/projects/${id}`,
    method: 'put',
    data
  })
}

export function deleteProject(id) {
  return request({
    url: `/projects/${id}`,
    method: 'delete'
  })
}

export function publishProject(id) {
  return request({
    url: `/projects/${id}/publish`,
    method: 'post'
  })
}

export function stopProject(id) {
  return request({
    url: `/projects/${id}/stop`,
    method: 'post'
  })
}

export function cancelProject(id) {
  return request({
    url: `/projects/${id}/cancel`,
    method: 'post'
  })
}

export function getProjectItems(id) {
  return request({
    url: `/projects/${id}/items`,
    method: 'get'
  })
}

export function createProjectItem(projectId, data) {
  return request({
    url: `/projects/${projectId}/items`,
    method: 'post',
    data
  })
}

export function updateProjectItem(projectId, itemId, data) {
  return request({
    url: `/projects/${projectId}/items/${itemId}`,
    method: 'put',
    data
  })
}

export function deleteProjectItem(projectId, itemId) {
  return request({
    url: `/projects/${projectId}/items/${itemId}`,
    method: 'delete'
  })
}
