import request from '@/utils/request'

/**
 * 获取项目时间节点列表
 */
export function getMilestones(projectId, includeInvisible = false) {
  return request({
    url: `/projects/${projectId}/milestones`,
    method: 'get',
    params: {
      include_invisible: includeInvisible
    }
  })
}

/**
 * 获取单个时间节点详情
 */
export function getMilestone(projectId, milestoneId) {
  return request({
    url: `/projects/${projectId}/milestones/${milestoneId}`,
    method: 'get'
  })
}

/**
 * 创建时间节点
 */
export function createMilestone(projectId, data) {
  return request({
    url: `/projects/${projectId}/milestones`,
    method: 'post',
    data
  })
}

/**
 * 更新时间节点
 */
export function updateMilestone(projectId, milestoneId, data) {
  return request({
    url: `/projects/${projectId}/milestones/${milestoneId}`,
    method: 'put',
    data
  })
}

/**
 * 删除时间节点
 */
export function deleteMilestone(projectId, milestoneId) {
  return request({
    url: `/projects/${projectId}/milestones/${milestoneId}`,
    method: 'delete'
  })
}

/**
 * 标记节点完成
 */
export function completeMilestone(projectId, milestoneId, actualDate = null) {
  return request({
    url: `/projects/${projectId}/milestones/${milestoneId}/complete`,
    method: 'post',
    data: {
      actual_date: actualDate
    }
  })
}

/**
 * 批量更新节点顺序
 */
export function reorderMilestones(projectId, milestoneIds) {
  return request({
    url: `/projects/${projectId}/milestones/reorder`,
    method: 'put',
    data: {
      milestone_ids: milestoneIds
    }
  })
}

/**
 * 导入默认节点模板
 */
export function importMilestoneTemplate(projectId) {
  return request({
    url: `/projects/${projectId}/milestones/import-template`,
    method: 'post'
  })
}

/**
 * 获取项目进度
 */
export function getProjectProgress(projectId) {
  return request({
    url: `/projects/${projectId}/progress`,
    method: 'get'
  })
}

