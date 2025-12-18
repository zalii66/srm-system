import request from '@/utils/request'

export function createBrand(data) {
  return request({
    url: '/brands/',
    method: 'post',
    data
  })
}

export function getBrandList(params) {
  return request({
    url: '/brands/',
    method: 'get',
    params
  })
}

export function getBrandDetail(id) {
  return request({
    url: `/brands/${id}`,
    method: 'get'
  })
}

export function updateBrand(id, data) {
  return request({
    url: `/brands/${id}`,
    method: 'put',
    data
  })
}

export function deleteBrand(id) {
  return request({
    url: `/brands/${id}`,
    method: 'delete'
  })
}
