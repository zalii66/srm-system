import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateLastActivity, getToken } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register/index.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile/index.vue'),
        meta: { title: '个人资料' }
      },
      { path: 'suppliers', name: 'SupplierList', component: () => import('@/views/Supplier/List.vue'), meta: { title: '供应商列表', roles: ['admin', 'project_manager'] } },
      {
        path: 'supplier/latest-projects',
        name: 'SupplierLatestProjects',
        component: () => import('@/views/Supplier/LatestProjects.vue'),
        meta: { title: '最新项目', roles: ['supplier'] }
      },
      {
        path: 'supplier/participated-projects',
        name: 'SupplierParticipatedProjects',
        component: () => import('@/views/Supplier/ParticipatedProjects.vue'),
        meta: { title: '参与项目', roles: ['supplier'] }
      },
      {
        path: 'supplier/profile',
        name: 'SupplierProfile',
        component: () => import('@/views/Supplier/Profile.vue'),
        meta: { title: '公司资料', roles: ['supplier'] }
      },
      { path: 'supplier/product-library', name: 'SupplierProductLibrary', component: () => import('@/views/Supplier/ProductLibrary.vue'), meta: { title: '产品库', roles: ['supplier', 'admin', 'project_manager'] } },
      {
        path: 'supplier/detail/:id',
        name: 'SupplierDetail',
        component: () => import('@/views/Supplier/Detail.vue'),
        meta: { title: '供应商详情' }
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/views/Project/List.vue'),
        meta: { title: '项目列表' }
      },
      {
        path: 'project/create',
        name: 'ProjectCreate',
        component: () => import('@/views/Project/Form.vue'),
        meta: { title: '创建项目', roles: ['project_manager', 'admin'] }
      },
      {
        path: 'project/edit/:id',
        name: 'ProjectEdit',
        component: () => import('@/views/Project/Form.vue'),
        meta: { title: '编辑项目', roles: ['project_manager', 'admin'] }
      },
      {
        path: 'project/detail/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/Project/Detail.vue'),
        meta: { title: '项目详情' }
      },
      {
        path: 'project/:id/requirements',
        name: 'ProjectRequirements',
        component: () => import('@/views/Project/Requirements.vue'),
        meta: { title: '项目需求报价' }
      },
      {
        path: 'project/:id/milestones',
        name: 'ProjectMilestones',
        component: () => import('@/views/Project/Milestones.vue'),
        meta: { title: '项目时间节点管理', roles: ['project_manager', 'admin'] }
      },
      {
        path: 'quotations',
        name: 'QuotationList',
        component: () => import('@/views/Quotation/List.vue'),
        meta: { title: '报价列表' }
      },
      {
        path: 'quotation/create',
        name: 'QuotationCreate',
        component: () => import('@/views/Quotation/Form.vue'),
        meta: { title: '创建报价', roles: ['supplier'] }
      },
      {
        path: 'quotation/edit/:id',
        name: 'QuotationEdit',
        component: () => import('@/views/Quotation/Form.vue'),
        meta: { title: '编辑报价', roles: ['supplier'] }
      },
      {
        path: 'quotation/detail/:id',
        name: 'QuotationDetail',
        component: () => import('@/views/Quotation/Detail.vue'),
        meta: { title: '报价详情' }
      },
      {
        path: 'companies',
        name: 'CompanyList',
        component: () => import('@/views/Company/List.vue'),
        meta: { title: '公司列表', roles: ['admin'] }
      },
      {
        path: 'company/create',
        name: 'CompanyCreate',
        component: () => import('@/views/Company/Form.vue'),
        meta: { title: '新增公司', roles: ['admin'] }
      },
      {
        path: 'company/edit/:id',
        name: 'CompanyEdit',
        component: () => import('@/views/Company/Form.vue'),
        meta: { title: '编辑公司', roles: ['admin'] }
      },
      {
        path: 'brands',
        name: 'BrandList',
        component: () => import('@/views/Brand/List.vue'),
        meta: { title: '品牌列表', roles: ['admin'] }
      },
      {
        path: 'brand/create',
        name: 'BrandCreate',
        component: () => import('@/views/Brand/Form.vue'),
        meta: { title: '新增品牌', roles: ['admin'] }
      },
      {
        path: 'brand/edit/:id',
        name: 'BrandEdit',
        component: () => import('@/views/Brand/Form.vue'),
        meta: { title: '编辑品牌', roles: ['admin'] }
      },
      {
        path: 'project-categories',
        name: 'ProjectCategoryList',
        component: () => import('@/views/ProjectCategory/List.vue'),
        meta: { title: '项目类别列表', roles: ['admin'] }
      },
      {
        path: 'project-category/create',
        name: 'ProjectCategoryCreate',
        component: () => import('@/views/ProjectCategory/Form.vue'),
        meta: { title: '新增项目类别', roles: ['admin'] }
      },
      {
        path: 'project-category/edit/:id',
        name: 'ProjectCategoryEdit',
        component: () => import('@/views/ProjectCategory/Form.vue'),
        meta: { title: '编辑项目类别', roles: ['admin'] }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/User/List.vue'),
        meta: { title: '用户管理', roles: ['admin'] }
      },
      {
        path: 'user/create',
        name: 'UserCreate',
        component: () => import('@/views/User/Form.vue'),
        meta: { title: '新增用户', roles: ['admin'] }
      },
      {
        path: 'user/edit/:id',
        name: 'UserEdit',
        component: () => import('@/views/User/Form.vue'),
        meta: { title: '编辑用户', roles: ['admin'] }
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: () => import('@/views/Role/List.vue'),
        meta: { title: '角色管理', roles: ['admin'] }
      },
      {
        path: 'role/create',
        name: 'RoleCreate',
        component: () => import('@/views/Role/Form.vue'),
        meta: { title: '新增角色', roles: ['admin'] }
      },
      {
        path: 'role/edit/:id',
        name: 'RoleEdit',
        component: () => import('@/views/Role/Form.vue'),
        meta: { title: '编辑角色', roles: ['admin'] }
      },
      {
        path: 'permissions',
        name: 'PermissionList',
        component: () => import('@/views/Permission/List.vue'),
        meta: { title: '权限管理', roles: ['admin'], permission: 'permission:manage' }
      },
      {
        path: 'permission/create',
        name: 'PermissionCreate',
        component: () => import('@/views/Permission/Form.vue'),
        meta: { title: '新增权限', roles: ['admin'], permission: 'permission:create' }
      },
      {
        path: 'permission/edit/:id',
        name: 'PermissionEdit',
        component: () => import('@/views/Permission/Form.vue'),
        meta: { title: '编辑权限', roles: ['admin'], permission: 'permission:update' }
      },
      {
        path: 'operation-logs',
        name: 'OperationLogList',
        component: () => import('@/views/OperationLog/List.vue'),
        meta: { title: '操作日志', roles: ['admin'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/Error/404.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 更新用户活动时间（路由切换也算作活动）
  const token = getToken()
  if (token && to.path !== '/login') {
    updateLastActivity()
  }

  // 如果是首次访问且需要认证，先尝试初始化用户信息
  if (to.meta.requiresAuth !== false && !userStore.userInfo && userStore.token) {
    await userStore.initUserInfo()
  }

  if (to.meta.title) {
    document.title = `${to.meta.title} - SRM供应商管理系统`
  }

  if (to.meta.requiresAuth !== false) {
    if (!userStore.token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  // 检查用户信息是否完善（姓名和邮箱为必填项）
  // 如果未完善，只能访问个人资料页
  if (userStore.userInfo) {
    const needsCompleteInfo = !userStore.userInfo.full_name || !userStore.userInfo.email
    if (needsCompleteInfo && to.path !== '/profile') {
      ElMessage.warning('请先完善个人信息：姓名和邮箱为必填项')
      next({ path: '/profile' })
      return
    }
  }

  if (to.meta.roles && to.meta.roles.length > 0) {
    const userRoles = userStore.roles || []
    const hasPermission = to.meta.roles.some(
      role => userRoles.includes(role) || userStore.isSuperuser
    )

    if (!hasPermission) {
      next({ name: 'Dashboard' })
      return
    }
  }

  // 检查供应商资料是否完整（仅对供应商角色且不是管理员）
  if (userStore.roles?.includes('supplier') && !userStore.isSuperuser) {
    // 如果正在访问资料页，允许通过
    if (to.path === '/supplier/profile') {
      next()
      return
    }

    // 检查供应商资料是否完整
    try {
      const { getCurrentSupplier } = await import('@/api/supplier')
      const supplierData = await getCurrentSupplier()

      // 检查必填字段是否为空
      const isProfileIncomplete =
        !supplierData ||
        !supplierData.company_name ||
        !supplierData.contact_person ||
        !supplierData.contact_phone

      if (isProfileIncomplete) {
        // 资料不完整，跳转到资料页
        ElMessage.warning('请先完善公司信息')
        next({ name: 'SupplierProfile' })
        return
      }
    } catch (error) {
      // 403错误表示用户没有供应商角色，允许继续（可能是管理员）
      if (error.response?.status === 403) {
        next()
        return
      }
      // 其他错误也允许继续，避免阻塞
      console.error('检查供应商资料失败:', error)
    }
  }

  next()
})

export default router
