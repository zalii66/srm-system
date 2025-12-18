import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser, logout as logoutApi } from '@/api/auth'
import {
  setToken,
  removeToken,
  setUserInfo,
  removeUserInfo,
  getToken,
  getUserInfo
} from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 恢复 token 和 userInfo
  const savedToken = getToken()
  const savedUserInfo = getUserInfo()

  const userInfo = ref(savedUserInfo)
  const token = ref(savedToken || '')

  const roles = computed(() => {
    if (!userInfo.value?.roles) return []
    return userInfo.value.roles.map(role => role.code || role)
  })

  const isSuperuser = computed(() => {
    return userInfo.value?.is_superuser || false
  })

  // 获取用户的所有权限编码
  const permissions = computed(() => {
    if (!userInfo.value?.roles) return []
    const permissionSet = new Set()
    userInfo.value.roles.forEach(role => {
      if (role.permissions && Array.isArray(role.permissions)) {
        role.permissions.forEach(permission => {
          if (permission.code && permission.is_active !== false) {
            permissionSet.add(permission.code)
          }
        })
      }
    })
    return Array.from(permissionSet)
  })

  // 检查用户是否有某个权限
  const hasPermission = (permissionCode) => {
    if (isSuperuser.value) return true
    return permissions.value.includes(permissionCode)
  }

  async function login(loginForm) {
    try {
      const data = await loginApi(loginForm)
      token.value = data.access_token
      setToken(data.access_token)
      await fetchUserInfo()
      return data
    } catch (error) {
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      const data = await getCurrentUser()
      userInfo.value = data
      setUserInfo(data)
      return data
    } catch (error) {
      // 如果获取用户信息失败（token 过期等），清除本地存储
      // 注意：401错误已在request.js中统一处理，这里只清除数据，不显示提示
      if (error.response?.status === 401 || error.response?.status === 403) {
        reset()
      }
      throw error
    }
  }

  // 初始化：如果有 token 但没有 userInfo，尝试获取用户信息
  async function initUserInfo() {
    if (token.value && !userInfo.value) {
      try {
        await fetchUserInfo()
      } catch (error) {
        // 如果获取失败，清除 token（可能已过期）
        console.error('初始化用户信息失败:', error)
        if (error.response?.status === 401 || error.response?.status === 403) {
          reset()
        }
      }
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      token.value = ''
      userInfo.value = null
      removeToken()
      removeUserInfo()
    }
  }

  function reset() {
    token.value = ''
    userInfo.value = null
    removeToken()
    removeUserInfo()
  }

  return {
    userInfo,
    token,
    roles,
    isSuperuser,
    permissions,
    hasPermission,
    login,
    fetchUserInfo,
    logout,
    reset,
    initUserInfo
  }
})
