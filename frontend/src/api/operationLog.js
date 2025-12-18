import request from '@/utils/request'

/**
 * 获取操作日志列表
 */
export function getOperationLogs(params) {
  return request({
    url: '/operation-logs/',
    method: 'get',
    params
  })
}

/**
 * 获取操作日志详情
 */
export function getOperationLog(id) {
  return request({
    url: `/operation-logs/${id}`,
    method: 'get'
  })
}

/**
 * 获取资源操作日志
 */
export function getResourceLogs(resourceType, resourceId, params) {
  return request({
    url: `/operation-logs/resource/${resourceType}/${resourceId}`,
    method: 'get',
    params
  })
}

/**
 * 获取用户操作日志
 */
export function getUserLogs(userId, params) {
  return request({
    url: `/operation-logs/user/${userId}`,
    method: 'get',
    params
  })
}

/**
 * 清理旧日志
 */
export function cleanupOldLogs(days = 90) {
  return request({
    url: '/operation-logs/cleanup',
    method: 'delete',
    params: { days }
  })
}

