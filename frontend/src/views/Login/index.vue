<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2 class="title">SRM供应商管理系统</h2>
        <p class="subtitle">登录您的账户</p>
      </div>

      <el-form ref="loginFormRef" :model="loginForm" :rules="rules" class="login-form">
        <el-form-item prop="phone">
          <el-input
            v-model="loginForm.phone"
            placeholder="请输入手机号"
            size="large"
            :prefix-icon="Phone"
            maxlength="11"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <router-link to="/register" class="register-link">还没有账号？立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Phone, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  phone: '',
  password: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        // 将手机号作为username传递给后端（后端支持手机号或用户名登录）
        await userStore.login({ username: loginForm.phone, password: loginForm.password })
        ElMessage.success('登录成功')

        // 检查用户信息是否完整（姓名和邮箱）
        const userInfo = userStore.userInfo
        const needsCompleteInfo = !userInfo?.full_name || !userInfo?.email
        if (needsCompleteInfo) {
          ElMessageBox.alert('请完善个人信息：姓名和邮箱为必填项，请前往个人资料页完善。', '提示', {
            confirmButtonText: '去完善信息',
            type: 'warning'
          })
            .then(() => {
              router.push('/profile')
            })
            .catch(() => {
              // 即使用户关闭对话框，也跳转到个人资料页
              router.push('/profile')
            })
          return
        }

        const redirect = router.currentRoute.value.query.redirect || '/dashboard'
        router.push(redirect)
      } catch (error) {
        // 提取后端返回的详细错误信息
        let errorMessage = '登录失败'
        if (error.response?.data?.detail) {
          // FastAPI 通常使用 detail 字段返回错误信息
          errorMessage = error.response.data.detail
        } else if (error.response?.data?.message) {
          // 某些情况下使用 message 字段
          errorMessage = error.response.data.message
        } else if (error.message && !error.message.includes('status code')) {
          // 使用 error.message，但排除通用的 "Request failed with status code 401" 消息
          errorMessage = error.message
        } else if (error.response?.status === 401) {
          // 如果是401但没有详细错误信息，显示通用提示
          errorMessage = '手机号或密码错误'
        }
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, $login-gradient-start 0%, $login-gradient-end 100%);
}

.login-box {
  width: 400px;
  padding: $spacing-xl;
  background: $bg-color;
  border-radius: $border-radius-base;
  box-shadow: $box-shadow-dark;
}

.login-header {
  text-align: center;
  margin-bottom: $spacing-xl;

  .title {
    font-size: 24px;
    font-weight: 500;
    color: $text-primary;
    margin: 0 0 $spacing-sm 0;
  }

  .subtitle {
    font-size: 14px;
    color: $text-secondary;
    margin: 0;
  }
}

.login-form {
  .login-button {
    width: 100%;
  }
}

.login-footer {
  text-align: center;
  margin-top: $spacing-lg;

  .register-link {
    font-size: 14px;
    color: $primary-color;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
