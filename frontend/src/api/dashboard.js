import request from '@/utils/request'

export function getDashboardStats() {
  return request({
    url: '/dashboard/stats',
    method: 'get'
  })
}

export function getGanttData() {
  return request({
    url: '/dashboard/gantt',
    method: 'get'
  })
}
