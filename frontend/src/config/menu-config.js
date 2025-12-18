/**
 * 菜单配置
 * 基于权限和角色动态生成菜单
 */

export const MENU_CONFIG = [
  {
    path: '/dashboard',
    title: '仪表盘',
    icon: 'HomeFilled',
    permission: 'dashboard:view',
    roles: ['admin', 'supplier', 'project_manager'],
    showAlways: true // 所有登录用户都可以看到
  },
  // 供应商菜单组
  {
    title: '供应商中心',
    icon: 'Shop',
    roles: ['supplier'],
    excludeRoles: ['admin'], // 管理员不显示
    children: [
      {
        path: '/supplier/latest-projects',
        title: '最新项目',
        icon: 'Document',
        roles: ['supplier']
      },
      {
        path: '/supplier/participated-projects',
        title: '参与项目',
        icon: 'FolderOpened',
        roles: ['supplier']
      },
      {
        path: '/supplier/product-library',
        title: '产品库',
        icon: 'Goods',
        roles: ['supplier']
      },
      {
        path: '/supplier/profile',
        title: '公司资料',
        icon: 'User',
        roles: ['supplier']
      }
    ]
  },
  // 管理员供应商管理
  {
    title: '供应商管理',
    icon: 'Shop',
    roles: ['admin', 'project_manager'],
    children: [
      {
        path: '/suppliers',
        title: '供应商列表',
        icon: 'List',
        permission: 'supplier:view',
        roles: ['admin', 'project_manager']
      },
      {
        path: '/supplier/product-library',
        title: '产品库',
        icon: 'Goods',
        permission: 'supplier:view',
        roles: ['admin', 'project_manager']
      }
    ]
  },
  // 项目管理菜单
  {
    title: '项目管理',
    icon: 'Document',
    permission: 'project:view',
    roles: ['project_manager', 'admin'],
    excludeRoles: ['supplier'],
    children: [
      {
        path: '/project/create',
        title: '创建项目',
        icon: 'Plus',
        permission: 'project:create',
        roles: ['project_manager', 'admin'],
        order: 1 // 第一个显示
      },
      {
        path: '/projects',
        title: '项目列表',
        icon: 'List',
        permission: 'project:view',
        roles: ['project_manager', 'admin', 'supplier'],
        order: 2
      },
      {
        path: '/project-categories',
        title: '项目类别',
        icon: 'Grid',
        permission: 'project_category:manage',
        roles: ['admin'],
        order: 3
      }
    ]
  },
  // 系统管理菜单
  {
    title: '系统管理',
    icon: 'Setting',
    roles: ['admin'],
    children: [
      {
        path: '/companies',
        title: '公司管理',
        icon: 'OfficeBuilding',
        permission: 'company:manage',
        roles: ['admin']
      },
      {
        path: '/brands',
        title: '品牌管理',
        icon: 'Star',
        permission: 'brand:manage',
        roles: ['admin']
      }
    ]
  },
  // 用户管理菜单
  {
    title: '用户管理',
    icon: 'User',
    roles: ['admin'],
    children: [
      {
        path: '/users',
        title: '用户管理',
        icon: 'User',
        permission: 'user:manage',
        roles: ['admin']
      },
      {
        path: '/roles',
        title: '角色管理',
        icon: 'Menu',
        permission: 'role:manage',
        roles: ['admin']
      },
      {
        path: '/permissions',
        title: '权限管理',
        icon: 'Key',
        permission: 'permission:manage',
        roles: ['admin']
      },
      {
        path: '/operation-logs',
        title: '操作日志',
        icon: 'Document',
        roles: ['admin']
      }
    ]
  }
]

/**
 * 检查菜单项是否应该显示
 */
export function shouldShowMenuItem(menuItem, userPermissions, userRoles, isSuperuser) {
  // 如果设置了 showAlways，则显示
  if (menuItem.showAlways) {
    return true
  }

  // 超级管理员显示所有菜单
  if (isSuperuser) {
    // 但如果设置了 excludeRoles，超级管理员也要排除
    if (menuItem.excludeRoles && menuItem.excludeRoles.includes('admin')) {
      return false
    }
    return true
  }

  // 检查排除的角色
  if (menuItem.excludeRoles && menuItem.excludeRoles.length > 0) {
    if (menuItem.excludeRoles.some(role => userRoles.includes(role))) {
      return false
    }
  }

  // 检查权限
  if (menuItem.permission) {
    if (!userPermissions.includes(menuItem.permission)) {
      return false
    }
  }

  // 检查角色
  if (menuItem.roles && menuItem.roles.length > 0) {
    if (!menuItem.roles.some(role => userRoles.includes(role))) {
      return false
    }
  }

  return true
}

/**
 * 过滤菜单项
 */
export function filterMenuItems(menuConfig, userPermissions, userRoles, isSuperuser) {
  return menuConfig.filter(menuItem => {
    // 检查父菜单是否应该显示
    if (!shouldShowMenuItem(menuItem, userPermissions, userRoles, isSuperuser)) {
      return false
    }

    // 如果有子菜单，过滤子菜单
    if (menuItem.children && menuItem.children.length > 0) {
      const filteredChildren = menuItem.children.filter(child =>
        shouldShowMenuItem(child, userPermissions, userRoles, isSuperuser)
      )

      // 如果子菜单都被过滤掉了，父菜单也不显示
      if (filteredChildren.length === 0) {
        return false
      }

      // 对子菜单进行排序
      menuItem.children = filteredChildren.sort((a, b) => {
        const orderA = a.order || 999
        const orderB = b.order || 999
        return orderA - orderB
      })
    }

    return true
  })
}

/**
 * 获取可见菜单
 */
export function getVisibleMenus(userPermissions, userRoles, isSuperuser) {
  return filterMenuItems(MENU_CONFIG, userPermissions, userRoles, isSuperuser)
}

