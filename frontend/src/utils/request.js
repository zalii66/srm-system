import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken, removeToken, isTokenExpired, updateLastActivity } from './auth'
import router from '@/router'
import { useUserStore } from '@/stores/user'

const service = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 401错误处理标志，避免重复提示
let isHandling401 = false
// 正在进行的操作请求列表（用于判断是否在关键操作中）
// 使用请求的唯一标识：method + url
const getRequestKey = (config) => {
  if (!config) return 'unknown'
  return `${config.method || 'get'}_${config.url || 'unknown'}`
}
let pendingOperations = new Set()

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      // 更新用户活动时间（每次API请求都算作活动）
      updateLastActivity()
      
      // 不在这里检查token是否过期，让后端来验证
      // 如果后端返回401，在响应拦截器中处理
      config.headers.Authorization = `Bearer ${token}`
    }

    // 如果正在处理401，取消关键操作请求，避免重复操作
    if (isHandling401) {
      const isCriticalOperation = config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())
      if (isCriticalOperation) {
        const CancelToken = axios.CancelToken
        const source = CancelToken.source()
        config.cancelToken = source.token
        source.cancel('请求已取消，正在处理登录')
      }
    }

    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data

    // 请求成功，清理pendingOperations标记
    if (response.config) {
      pendingOperations.delete(getRequestKey(response.config))
    }

    // FastAPI 使用 response_model 时直接返回数据，没有 code 字段
    // 只有当后端明确返回 Response 格式时才有 code 字段
    if (res && typeof res === 'object' && 'code' in res && 'message' in res) {
      // 标准响应格式（有 code 和 message 字段）
      if (res.code === 200) {
        return res.data !== undefined ? res.data : res
      } else {
        ElMessage.error(res.message || '请求失败')
        return Promise.reject(new Error(res.message || '请求失败'))
      }
    }

    // FastAPI 直接返回数据（Pydantic 模型序列化后的对象），直接返回
    return res
  },
  error => {
    // 如果是取消的请求，直接返回，不显示错误
    if (axios.isCancel(error) || error.message === '请求已取消，正在处理登录') {
      return Promise.reject(error)
    }

    console.error('Response error:', error)

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // 如果已经在登录页，不拦截401错误，让登录页面自己处理错误信息
          const currentPath = router.currentRoute.value.path
          if (currentPath === '/login') {
            // 登录页面的401错误直接返回，不进行全局处理
            // 这样登录页面可以显示后端返回的具体错误信息
            return Promise.reject(error)
          }

          // 统一处理401错误，避免重复提示
          // 401错误可能是后端token验证失败，但不应该因为token过期就立即退出
          // 只有在后端明确返回401时才退出（比如token被撤销、用户被禁用等）
          // 如果只是因为token过期时间到了，但用户在30分钟内有活动，不应该退出
          // 这里我们仍然处理401，因为这是后端的安全验证，但提示信息会更友好
          if (!isHandling401) {
            isHandling401 = true

            // 检查是否是关键操作（POST/PUT/PATCH/DELETE）
            const requestKey = error.config ? getRequestKey(error.config) : 'unknown'
            const isCriticalOperation = 
              (error.config?.method && ['post', 'put', 'patch', 'delete'].includes(error.config.method.toLowerCase()))
            
            // 清理该请求的标记
            if (error.config) {
              pendingOperations.delete(requestKey)
            }

            // 清除token和用户信息
            removeToken()
            const userStore = useUserStore()
            userStore.reset()
            
            // 清理所有pending操作标记
            pendingOperations.clear()

            // 根据是否是关键操作显示不同的提示
            if (isCriticalOperation) {
              // 关键操作失败，显示更详细的提示
              ElMessageBox.alert(
                '登录已过期，操作未能完成。请重新登录后重试。',
                '登录已过期',
                {
                  confirmButtonText: '重新登录',
                  type: 'warning',
                  callback: () => {
                    const redirectPath = router.currentRoute.value.fullPath
                    router
                      .push({
                        path: '/login',
                        query: redirectPath && redirectPath !== '/login' ? { redirect: redirectPath } : {}
                      })
                      .catch(() => {
                        window.location.href = '/login'
                      })
                      .finally(() => {
                        setTimeout(() => {
                          isHandling401 = false
                        }, 1000)
                      })
                  }
                }
              )
            } else {
              // 普通请求，直接跳转（静默处理，不显示提示，因为可能是自动刷新的请求）
              // 只有在用户主动操作时才显示提示
              const redirectPath = router.currentRoute.value.fullPath
              setTimeout(() => {
                router
                  .push({
                    path: '/login',
                    query: redirectPath && redirectPath !== '/login' ? { redirect: redirectPath } : {}
                  })
                  .catch(() => {
                    window.location.href = '/login'
                  })
                  .finally(() => {
                    setTimeout(() => {
                      isHandling401 = false
                    }, 1000)
                  })
              }, 100)
            }
          }
          break
        case 403:
          // 403 错误不显示提示，由调用方处理
          break
        case 404:
          // 404 错误不显示提示，由调用方处理（某些接口可能正常返回404）
          break
        case 400:
        case 422:
          // 400/422 错误显示详细错误信息，但由调用方决定是否显示
          // 不在这里自动显示，避免重复提示
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          const defaultMsg = data?.detail || data?.message || '请求失败'
          ElMessage.error(defaultMsg)
      }
    } else {
      // 网络错误只在非401处理时显示
      if (!isHandling401) {
        ElMessage.error('网络错误，请检查网络连接')
      }
    }

    return Promise.reject(error)
  }
)

export default service
