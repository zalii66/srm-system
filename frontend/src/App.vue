<template>
  <router-view />
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getToken, isTokenExpired, isUserIdle, getIdleTime, updateLastActivity, clearLastActivity } from '@/utils/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

let activityCheckTimer = null
const IDLE_MINUTES = 30 // 30分钟无活动后自动退出

// 检查用户活动状态
const checkUserActivity = () => {
  const token = getToken()
  if (!token) {
    clearLastActivity()
    return
  }

  const currentPath = router.currentRoute.value.path
  // 登录页不需要检查活动
  if (currentPath === '/login') {
    clearLastActivity()
    return
  }

  // 只基于用户活动时间检查，不检查token过期时间
  // 如果后端token真的过期了，后端会返回401，在响应拦截器中处理
  // 这里只检查用户是否30分钟无活动
  if (isUserIdle(IDLE_MINUTES)) {
    const idleTime = getIdleTime()
    ElMessage.warning(`您已 ${idleTime} 分钟未操作，系统将自动退出登录`)
    userStore.reset()
    router.push('/login')
    return
  }

  // 如果用户有活动但接近空闲时间（剩余5分钟），给出提示
  const idleTime = getIdleTime()
  const warningThreshold = IDLE_MINUTES - 5 // 提前5分钟警告
  if (idleTime >= warningThreshold && idleTime < IDLE_MINUTES) {
    const remainingMinutes = IDLE_MINUTES - idleTime
    // 只显示一次提示，避免重复提示
    if (!window.idleWarned) {
      window.idleWarned = true
      ElMessage.warning(`您已 ${idleTime} 分钟未操作，${remainingMinutes} 分钟后将自动退出登录`)
      // 5分钟后重置警告标志
      setTimeout(() => {
        window.idleWarned = false
      }, 5 * 60 * 1000)
    }
  } else {
    // 重置警告标志
    window.idleWarned = false
  }
}

// 监听路由变化，更新活动时间
watch(
  () => router.currentRoute.value.path,
  () => {
    const token = getToken()
    if (token && router.currentRoute.value.path !== '/login') {
      updateLastActivity() // 页面切换也算作活动
    }
  }
)

onMounted(() => {
  // 初始化活动时间（如果已登录）
  const token = getToken()
  if (token) {
    updateLastActivity()
  }
  
  // 立即检查一次
  checkUserActivity()
  
  // 每60秒检查一次用户活动状态
  activityCheckTimer = setInterval(() => {
    checkUserActivity()
  }, 60 * 1000)
})

onBeforeUnmount(() => {
  if (activityCheckTimer) {
    clearInterval(activityCheckTimer)
    activityCheckTimer = null
  }
})
</script>

<style lang="scss">
@import '@/styles/index.scss';
</style>
