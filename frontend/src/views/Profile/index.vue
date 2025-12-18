<template>
  <div class="profile-container">
    <PageHeader title="个人资料" subtitle="查看和编辑您的个人信息">
      <template #extra>
        <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
      </template>
    </PageHeader>

    <el-card class="profile-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :label-width="FORM_LABEL_WIDTH.DEFAULT"
        class="form-container"
      >
        <!-- 账户信息 -->
        <div class="form-section">
          <div class="section-title">账户信息</div>
          
          <el-form-item label="手机号">
            <span class="text-secondary">{{ form.phone || '-' }}</span>
          </el-form-item>

          <el-form-item label="角色">
            <div class="role-tags">
              <el-tag v-for="role in userRoles" :key="role.id" type="primary">
                {{ role.name }}
              </el-tag>
              <span v-if="userRoles.length === 0" class="text-secondary">无</span>
            </div>
          </el-form-item>

          <el-form-item label="账户状态">
            <StatusTag :status="form.is_active ? 'active' : 'inactive'" />
          </el-form-item>

          <el-form-item label="创建时间">
            <span class="text-secondary">{{ formatDate(form.created_at) }}</span>
          </el-form-item>

          <el-form-item label="最后登录时间">
            <span class="text-secondary">
              {{ form.last_login ? formatDate(form.last_login) : '从未登录' }}
            </span>
          </el-form-item>
        </div>

        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-title">基本信息</div>

          <el-form-item v-if="isSupplier" label="公司名称">
            <span class="text-secondary">{{ supplierInfo.company_name || '-' }}</span>
          </el-form-item>

          <el-form-item label="姓名" prop="full_name">
            <el-input v-if="isEditing" v-model="form.full_name" placeholder="请输入姓名" />
            <span v-else class="text-secondary">{{ form.full_name || '-' }}</span>
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input v-if="isEditing" v-model="form.email" placeholder="请输入邮箱" />
            <span v-else class="text-secondary">{{ form.email || '-' }}</span>
          </el-form-item>
        </div>

        <!-- 按钮区域 -->
        <el-form-item class="form-actions">
          <el-button v-if="!isEditing" type="primary" @click="handleEdit">编辑资料</el-button>
          <template v-else>
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
          </template>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      :width="DIALOG_WIDTH.SMALL"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        :label-width="FORM_LABEL_WIDTH.SMALL"
      >
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSubmitting" @click="handleSubmitPassword">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ElDialog, ElForm, ElFormItem, ElInput, ElButton } from 'element-plus'
import { PageHeader, StatusTag } from '@/components'
import { getUserDetail, updateUser } from '@/api/user'
import { getCurrentSupplier } from '@/api/supplier'
import { useUserStore } from '@/stores/user'
import { formatDate, DIALOG_WIDTH, FORM_LABEL_WIDTH } from '@/utils'
import { useFormValidation } from '@/composables'

const userStore = useUserStore()
const formRef = ref(null)
const passwordFormRef = ref(null)
const isEditing = ref(false)
const submitting = ref(false)
const passwordDialogVisible = ref(false)
const passwordSubmitting = ref(false)
const supplierInfo = ref({})

const form = reactive({
  id: null,
  username: '',
  email: '',
  full_name: '',
  phone: '',
  is_active: true,
  created_at: null,
  last_login: null
})

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

const userRoles = computed(() => {
  return userStore.userInfo?.roles || []
})

const isSupplier = computed(() => {
  return userStore.roles?.includes('supplier') || false
})

// 验证规则
const rules = {
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号',
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (!value || /^1[3-9]\d{9}$/.test(value)) {
          callback()
        } else {
          callback(new Error('请输入正确的手机号'))
        }
      }
    }
  ]
}

// 密码修改验证规则
const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

// 使用表单验证工具（个人资料表单）
const { handleSubmitError: handleProfileSubmitError, handleFrontendValidationError: handleProfileFrontendValidationError } = useFormValidation(
  formRef,
  form
)

// 使用表单验证工具（密码修改表单）
const { handleSubmitError: handlePasswordSubmitError, handleFrontendValidationError: handlePasswordFrontendValidationError } = useFormValidation(
  passwordFormRef,
  passwordForm
)

// 获取用户信息
const fetchData = async () => {
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.error('用户信息不存在')
      return
    }

    const data = await getUserDetail(userId)
    Object.assign(form, {
      id: data.id,
      username: data.username,
      email: data.email || '',
      full_name: data.full_name || '',
      phone: data.phone || '',
      is_active: data.is_active,
      created_at: data.created_at,
      last_login: data.last_login
    })

    // 如果是供应商，获取供应商信息（公司名称）
    if (isSupplier.value) {
      try {
        const supplierData = await getCurrentSupplier()
        supplierInfo.value = supplierData || {}
      } catch (error) {
        // 如果获取失败，可能是403错误（不是供应商角色），忽略
        console.error('获取供应商信息失败:', error)
        supplierInfo.value = {}
      }
    }

    // 如果缺少姓名或邮箱，自动进入编辑模式
    if (!data.full_name || !data.email) {
      isEditing.value = true
      ElMessage.warning('请完善个人信息：姓名和邮箱为必填项')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取用户信息失败')
  }
}

// 编辑
const handleEdit = () => {
  isEditing.value = true
}

// 取消
const handleCancel = () => {
  isEditing.value = false
  fetchData() // 重新获取数据，重置表单
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitting.value = true

    const updateData = {
      email: form.email,
      full_name: form.full_name,
      phone: form.phone
    }

    await updateUser(form.id, updateData)

    // 更新用户store中的信息
    await userStore.fetchUserInfo()

    // 如果是供应商，重新获取供应商信息
    if (isSupplier.value) {
      try {
        const supplierData = await getCurrentSupplier()
        supplierInfo.value = supplierData || {}
      } catch (error) {
        console.error('获取供应商信息失败:', error)
      }
    }

    ElMessage.success('更新成功')
    isEditing.value = false
  } catch (error) {
    if (error.errors) {
      // 前端验证失败
      handleProfileFrontendValidationError()
      return
    }
    handleProfileSubmitError(error, form, '更新用户信息失败')
  } finally {
    submitting.value = false
  }
}

// 修改密码
const handleChangePassword = () => {
  passwordDialogVisible.value = true
  // 重置表单
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

// 提交密码修改
const handleSubmitPassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()

    passwordSubmitting.value = true

    const updateData = {
      password: passwordForm.newPassword
    }

    await updateUser(form.id, updateData)

    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false

    // 重置表单
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    if (error.errors) {
      // 前端验证失败
      handlePasswordFrontendValidationError()
      return
    }
    handlePasswordSubmitError(error, passwordForm, '修改密码失败')
  } finally {
    passwordSubmitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form.scss';
@import '@/styles/form-validation.scss';

.profile-container {
  .profile-card {
    :deep(.el-card__body) {
      padding: $spacing-xl;
    }
  }

  .form-section {
    .el-form-item {
      margin-bottom: $spacing-md;

      :deep(.el-form-item__label) {
        font-weight: 500;
      }
    }
  }

  .role-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: $spacing-sm;
  }

  .form-actions {
    margin-top: $spacing-xl;
    margin-bottom: 0;
    padding-top: $spacing-lg;
    border-top: 1px solid $border-color-light;
  }
}
</style>
