import request from '@/utils/request'

/**
 * 获取产品库列表
 */
export function getProductLibraryList(params) {
  return request({
    url: '/product-library/',
    method: 'get',
    params
  })
}

/**
 * 获取产品详情
 */
export function getProductDetail(id) {
  return request({
    url: `/product-library/${id}`,
    method: 'get'
  })
}

/**
 * 获取产品库统计
 */
export function getProductStatistics() {
  return request({
    url: '/product-library/statistics/summary',
    method: 'get'
  })
}

