import request from '@/utils/request'

/**
 * 获取项目类别列表
 */
export function getProjectCategoryList(params) {
  return request({
    url: '/project-categories/',
    method: 'get',
    params
  })
}

/**
 * 获取项目类别详情
 */
export function getProjectCategoryDetail(id) {
  return request({
    url: `/project-categories/${id}`,
    method: 'get'
  })
}

/**
 * 创建项目类别
 */
export function createProjectCategory(data) {
  return request({
    url: '/project-categories/',
    method: 'post',
    data
  })
}

/**
 * 更新项目类别
 */
export function updateProjectCategory(id, data) {
  return request({
    url: `/project-categories/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除项目类别
 */
export function deleteProjectCategory(id) {
  return request({
    url: `/project-categories/${id}`,
    method: 'delete'
  })
}
