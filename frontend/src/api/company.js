import request from '@/utils/request'

export function createCompany(data) {
  return request({
    url: '/companies/',
    method: 'post',
    data
  })
}

export function getCompanyList(params) {
  return request({
    url: '/companies/',
    method: 'get',
    params
  })
}

export function getCompanyDetail(id) {
  return request({
    url: `/companies/${id}`,
    method: 'get'
  })
}

export function updateCompany(id, data) {
  return request({
    url: `/companies/${id}`,
    method: 'put',
    data
  })
}

export function deleteCompany(id) {
  return request({
    url: `/companies/${id}`,
    method: 'delete'
  })
}
