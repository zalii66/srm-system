import request from '@/utils/request'

export function createQuotation(data) {
  return request({
    url: '/quotations/',
    method: 'post',
    data
  })
}

export function getQuotationList(params) {
  return request({
    url: '/quotations/',
    method: 'get',
    params
  })
}

export function getProjectQuotations(projectId, params) {
  return request({
    url: '/quotations/',
    method: 'get',
    params: {
      project_id: projectId,
      ...params
    }
  })
}

export function getMyQuotations(params) {
  return request({
    url: '/quotations/my',
    method: 'get',
    params
  })
}

export function getQuotationDetail(id) {
  return request({
    url: `/quotations/${id}`,
    method: 'get'
  })
}

export function updateQuotation(id, data) {
  return request({
    url: `/quotations/${id}`,
    method: 'put',
    data
  })
}

export function submitQuotation(id) {
  return request({
    url: `/quotations/${id}/submit`,
    method: 'post'
  })
}

export function deleteQuotation(id) {
  return request({
    url: `/quotations/${id}`,
    method: 'delete'
  })
}

export function cancelQuotation(id) {
  return request({
    url: `/quotations/${id}/cancel`,
    method: 'post'
  })
}

export function evaluateQuotation(id, data) {
  return request({
    url: `/quotations/${id}/evaluate`,
    method: 'post',
    data
  })
}
