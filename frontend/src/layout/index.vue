<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo">
        <span v-if="!isCollapse">SRM系统</span>
        <span v-else>S</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        :router="true"
        :collapse-transition="false"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <!-- 动态渲染菜单 -->
        <template v-for="menuItem in visibleMenus" :key="menuItem.path || menuItem.title">
          <!-- 单个菜单项 -->
          <el-menu-item v-if="!menuItem.children || menuItem.children.length === 0" :index="menuItem.path">
            <el-icon>
              <component :is="getIconComponent(menuItem.icon)" />
            </el-icon>
            <template #title>{{ menuItem.title }}</template>
          </el-menu-item>

          <!-- 带子菜单的菜单项 -->
          <el-sub-menu v-else :index="menuItem.path || menuItem.title">
            <template #title>
              <el-icon>
                <component :is="getIconComponent(menuItem.icon)" />
              </el-icon>
              <span>{{ menuItem.title }}</span>
            </template>
            <template v-for="child in menuItem.children" :key="child.path">
              <el-menu-item :index="child.path">
                <el-icon>
                  <component :is="getIconComponent(child.icon)" />
                </el-icon>
                <template #title>{{ child.title }}</template>
              </el-menu-item>
            </template>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleSidebar">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>

        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-dropdown">
              <el-avatar :size="32" :icon="User" />
              <div class="user-info">
                <div class="user-name">{{ getUserDisplayName() }}</div>
                <div class="user-role">{{ getUserRoleText() }}</div>
              </div>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component v-if="Component" :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  ArrowDown,
  User,
  SwitchButton,
  HomeFilled,
  Shop,
  Document,
  Setting,
  FolderOpened,
  List,
  Plus,
  OfficeBuilding,
  Star,
  Grid,
  Goods,
  Menu as IconMenu,
  Key
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { getVisibleMenus } from '@/config/menu-config'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapse)
const userInfo = computed(() => userStore.userInfo)
const activeMenu = computed(() => route.path)

const isAdmin = computed(() => {
  return userInfo.value?.is_superuser
})

const hasRole = roleCode => {
  if (isAdmin.value) return true
  return userInfo.value?.roles?.some(role => role.code === roleCode)
}

// 计算可见菜单
const visibleMenus = computed(() => {
  if (!userInfo.value) return []
  return getVisibleMenus(
    userStore.permissions,
    userStore.roles,
    userStore.isSuperuser
  )
})

// 图标映射
const iconMap = {
  HomeFilled,
  Shop,
  Document,
  Setting,
  FolderOpened,
  List,
  Plus,
  OfficeBuilding,
  Star,
  Grid,
  Goods,
  User,
  Menu: IconMenu,
  Key
}

// 获取图标组件
const getIconComponent = (iconName) => {
  return iconMap[iconName] || Document
}

const getUserDisplayName = () => {
  if (userInfo.value?.full_name) {
    return userInfo.value.full_name
  }
  return userInfo.value?.username || '用户'
}

const getUserRoleText = () => {
  if (isAdmin.value) return '超级管理员'
  if (userInfo.value?.roles && userInfo.value.roles.length > 0) {
    return userInfo.value.roles[0].name || '用户'
  }
  return '普通用户'
}

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const handleMenuSelect = index => {
  if (index && index.startsWith('/')) {
    router.push(index)
  }
}

const handleCommand = command => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await userStore.logout()
      ElMessage.success('退出成功')
      router.push('/login')
    })
    .catch(() => {})
}

if (!userInfo.value) {
  userStore.fetchUserInfo().catch(error => {
    // 如果获取用户信息失败，可能是未登录或token过期
    // 401错误已在request.js中统一处理，这里只做跳转，不显示提示
    if (error.response?.status === 401) {
      // 如果已经在登录页，不重复跳转
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
  })
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.layout-container {
  height: 100vh;
}

.sidebar {
  background: $sidebar-bg;
  transition: width 0.2s ease;
  will-change: width;
}

.logo {
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 20px;
  font-weight: bold;
  background: $sidebar-bg;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  border-right: none;
  background: $sidebar-bg;
  transition: none !important;
}

// 优化手风琴动画性能
:deep(.el-sub-menu) {
  .el-sub-menu__title {
    transition: none !important;
  }

  .el-menu {
    transition: none !important;
  }
}

:deep(.el-menu-item) {
  transition: none !important;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: $sidebar-text;
  background: $sidebar-bg;
  cursor: pointer;
  user-select: none;
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 20px;
  
  .el-icon {
    margin-right: 8px;
  }
}

:deep(.el-sub-menu__title) {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 20px;
  
  .el-icon {
    margin-right: 8px;
  }
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: $sidebar-hover-bg !important;
  color: $sidebar-active-text;
}

:deep(.el-menu-item.is-active) {
  background: $sidebar-active-bg !important;
  color: $sidebar-active-text !important;

  .el-icon {
    color: $sidebar-active-text !important;
  }
}

:deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: $sidebar-text;
}

:deep(.el-sub-menu .el-menu) {
  background: rgba(0, 0, 0, 0.2);
}

:deep(.el-sub-menu .el-menu-item) {
  background: rgba(0, 0, 0, 0.2);
  padding-left: 50px !important;
  
  .el-icon {
    margin-right: 8px;
  }
}

:deep(.el-icon) {
  color: inherit;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: $bg-color;
  border-bottom: 1px solid $border-color-light;
  padding: 0 $spacing-lg;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-icon {
  font-size: 24px;
  cursor: pointer;
  color: $text-secondary;

  &:hover {
    color: $primary-color;
  }
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-base;
  gap: $spacing-sm;
  transition: background-color 0.3s;

  &:hover {
    background: $bg-color-overlay;
  }
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: $text-primary;
}

.user-role {
  font-size: 12px;
  color: $text-secondary;
  margin-top: 2px;
}

.dropdown-arrow {
  font-size: 12px;
  color: $text-secondary;
  margin-left: $spacing-xs;
}

.avatar-text {
  font-size: 14px;
  font-weight: 500;
}

.main-content {
  background: $bg-color-page;
  padding: $spacing-lg;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
