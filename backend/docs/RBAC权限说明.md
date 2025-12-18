# RBAC权限控制说明

## 后端权限控制

### 1. 依赖注入函数

在 `backend/app/core/deps.py` 中定义了以下权限检查函数：

- **`get_current_user`**: 获取当前登录用户（所有认证用户）
- **`get_current_superuser`**: 获取当前超级管理员（仅管理员）
- **`get_current_admin_or_project_manager`**: 获取管理员或项目经理

### 2. 权限检查逻辑

#### 供应商列表API (`GET /api/v1/suppliers/`)
- **权限要求**: 超级管理员 (`get_current_superuser`)
- **说明**: 只有管理员可以查看所有供应商列表

#### 供应商详情API (`GET /api/v1/suppliers/{supplier_id}`)
- **权限要求**: 当前用户
- **权限逻辑**: 
  - 超级管理员可以查看所有供应商
  - 供应商只能查看自己的信息

#### 供应商审核API (`POST /api/v1/suppliers/{supplier_id}/audit`)
- **权限要求**: 超级管理员
- **说明**: 只有管理员可以审核供应商

#### 项目列表API (`GET /api/v1/projects/`)
- **权限要求**: 当前用户
- **权限逻辑**:
  - 供应商：只能看到已发布的项目
  - 项目经理：看到自己创建的项目
  - 管理员：看到所有项目

#### 项目创建/更新/删除API
- **权限要求**: 项目经理或管理员
- **说明**: 使用 `is_project_manager` 函数检查

### 3. 角色代码对照

- **`admin`**: 超级管理员（`is_superuser=True`）
- **`project_manager`**: 项目经理
- **`supplier`**: 供应商

## 前端权限控制

### 1. 路由守卫

在 `frontend/src/router/index.js` 中：

```javascript
// 检查角色权限
if (to.meta.roles && to.meta.roles.length > 0) {
  const userRoles = userStore.roles || []
  const hasPermission = to.meta.roles.some(role => 
    userRoles.includes(role) || userStore.isSuperuser
  )
  
  if (!hasPermission) {
    next({ name: 'Dashboard' })
    return
  }
}
```

### 2. 菜单显示控制

在 `frontend/src/layout/index.vue` 中：

```vue
<!-- 供应商菜单（仅供应商角色显示，管理员不显示） -->
<template v-if="hasRole('supplier') && !isAdmin">
  <el-menu-item index="/supplier/latest-projects">最新项目</el-menu-item>
  <el-menu-item index="/supplier/participated-projects">参与项目</el-menu-item>
  <el-menu-item index="/supplier/profile">我的资料</el-menu-item>
</template>

<!-- 管理员供应商管理菜单 -->
<el-sub-menu v-if="isAdmin" index="supplier">
  <el-menu-item index="/suppliers">供应商列表</el-menu-item>
</el-sub-menu>
```

### 3. 角色权限函数

```javascript
const isAdmin = computed(() => {
  return userInfo.value?.is_superuser
})

const hasRole = (roleCode) => {
  if (isAdmin.value) return true  // 管理员拥有所有权限
  return userInfo.value?.roles?.some(role => role.code === roleCode)
}
```

## 菜单权限分配

### 管理员（admin）
- ✅ 仪表盘
- ✅ 供应商管理 > 供应商列表
- ✅ 项目管理 > 项目列表、创建项目
- ✅ 系统管理 > 公司管理、品牌管理
- ✅ 用户管理 > 用户管理、角色管理

### 项目经理（project_manager）
- ✅ 仪表盘
- ✅ 项目管理 > 项目列表、创建项目

### 供应商（supplier）
- ✅ 仪表盘
- ✅ 最新项目
- ✅ 参与项目
- ✅ 我的资料

## 权限检查流程

1. **登录时**: 获取用户信息和角色
2. **路由跳转**: 检查路由meta中的roles配置
3. **API请求**: 后端依赖注入检查权限
4. **菜单显示**: 前端根据角色显示/隐藏菜单项

## 注意事项

1. 超级管理员 (`is_superuser=True`) 拥有所有权限，前端和后端都会特殊处理
2. 角色代码必须与数据库中的 `roles.code` 字段一致
3. 前端菜单控制只是UI层面的控制，真正的权限验证在后端API
4. 供应商访问 `/api/suppliers/me` 时，如果用户不是供应商，会返回404（这是正常的）

