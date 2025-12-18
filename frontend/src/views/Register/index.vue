<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2 class="title">供应商注册</h2>
        <p class="subtitle">填写信息完成注册</p>
      </div>

      <el-form ref="registerFormRef" :model="registerForm" :rules="rules" class="register-form">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>

        <el-form-item label="验证码" prop="verification_code">
          <el-input
            v-model="registerForm.verification_code"
            placeholder="请输入验证码（手机号后4位）"
            maxlength="4"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
          />
        </el-form-item>

        <el-form-item label="公司名称" prop="company_name">
          <el-input v-model="registerForm.company_name" placeholder="请输入公司名称" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleRegister">注册</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>

        <div class="register-footer">
          <router-link to="/login" class="login-link">已有账号？立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { registerSupplier } from '@/api/supplier'

const router = useRouter()

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  phone: '',
  verification_code: '',
  password: '',
  confirmPassword: '',
  company_name: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const validateVerificationCode = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入验证码'))
  } else if (registerForm.phone && value !== registerForm.phone.slice(-4)) {
    callback(new Error('验证码错误，请输入手机号后4位'))
  } else {
    callback()
  }
}

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  verification_code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { validator: validateVerificationCode, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6到50个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  company_name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        const { confirmPassword, ...data } = registerForm
        await registerSupplier(data)
        ElMessage.success('注册成功，请等待管理员审核')
        router.push('/login')
      } catch (error) {
        ElMessage.error(error.message || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleCancel = () => {
  router.push('/login')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: $spacing-lg;
}

.register-box {
  width: 600px;
  max-width: 100%;
  padding: $spacing-xl;
  background: $bg-color;
  border-radius: $border-radius-base;
  box-shadow: $box-shadow-dark;
}

.register-header {
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

.register-footer {
  text-align: center;
  margin-top: $spacing-lg;

  .login-link {
    font-size: 14px;
    color: $primary-color;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
