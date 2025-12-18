const TOKEN_KEY = 'srm_token'
const USER_INFO_KEY = 'srm_user_info'
const LAST_ACTIVITY_KEY = 'srm_last_activity'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
  updateLastActivity() // 设置token时更新活动时间（登录时）
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  clearLastActivity() // 清除token时也清除活动时间
}

export function getUserInfo() {
  const userInfo = localStorage.getItem(USER_INFO_KEY)
  return userInfo ? JSON.parse(userInfo) : null
}

export function setUserInfo(userInfo) {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
}

export function removeUserInfo() {
  localStorage.removeItem(USER_INFO_KEY)
}

/**
 * 解析JWT token，获取payload
 * @param {string} token JWT token
 * @returns {object|null} token payload 或 null
 */
export function decodeToken(token) {
  if (!token) return null
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payload = parts[1]
    const decoded = JSON.parse(atob(payload))
    return decoded
  } catch (error) {
    console.error('解析token失败:', error)
    return null
  }
}

/**
 * 检查token是否过期
 * @param {string} token JWT token
 * @returns {boolean} true表示已过期，false表示未过期
 */
export function isTokenExpired(token) {
  const payload = decodeToken(token)
  if (!payload || !payload.exp) return true
  const currentTime = Math.floor(Date.now() / 1000)
  return payload.exp < currentTime
}

/**
 * 检查token是否即将过期（剩余时间少于5分钟）
 * @param {string} token JWT token
 * @param {number} warnMinutes 提前警告的分钟数，默认5分钟
 * @returns {boolean} true表示即将过期，false表示还未过期
 */
export function isTokenExpiringSoon(token, warnMinutes = 5) {
  const payload = decodeToken(token)
  if (!payload || !payload.exp) return true
  const currentTime = Math.floor(Date.now() / 1000)
  const remainingSeconds = payload.exp - currentTime
  const warnSeconds = warnMinutes * 60
  return remainingSeconds > 0 && remainingSeconds < warnSeconds
}

/**
 * 获取token剩余有效时间（秒）
 * @param {string} token JWT token
 * @returns {number} 剩余秒数，如果已过期返回0
 */
export function getTokenRemainingTime(token) {
  const payload = decodeToken(token)
  if (!payload || !payload.exp) return 0
  const currentTime = Math.floor(Date.now() / 1000)
  const remaining = payload.exp - currentTime
  return remaining > 0 ? remaining : 0
}

/**
 * 更新用户最后活动时间
 */
export function updateLastActivity() {
  localStorage.setItem(LAST_ACTIVITY_KEY, Date.now().toString())
}

/**
 * 获取用户最后活动时间
 * @returns {number} 最后活动时间戳（毫秒），如果不存在返回0
 */
export function getLastActivity() {
  const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY)
  return lastActivity ? parseInt(lastActivity, 10) : 0
}

/**
 * 清除用户活动时间
 */
export function clearLastActivity() {
  localStorage.removeItem(LAST_ACTIVITY_KEY)
}

/**
 * 检查用户是否空闲（超过指定时间没有活动）
 * @param {number} idleMinutes 空闲时间（分钟），默认30分钟
 * @returns {boolean} true表示用户已空闲，false表示用户有活动
 */
export function isUserIdle(idleMinutes = 30) {
  const lastActivity = getLastActivity()
  if (!lastActivity) return false // 如果没有记录活动时间，不算空闲
  
  const idleTime = Date.now() - lastActivity
  const idleThreshold = idleMinutes * 60 * 1000 // 转换为毫秒
  return idleTime > idleThreshold
}

/**
 * 获取用户空闲时间（分钟）
 * @returns {number} 空闲时间（分钟）
 */
export function getIdleTime() {
  const lastActivity = getLastActivity()
  if (!lastActivity) return 0
  const idleTime = Date.now() - lastActivity
  return Math.floor(idleTime / (60 * 1000)) // 转换为分钟
}
