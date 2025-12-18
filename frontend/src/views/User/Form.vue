<template>
  <div class="user-form-container">
    <PageHeader :title="isEdit ? '编辑用户' : '新增用户'">
      <template #extra>
        <el-button @click="handleCancel">返回</el-button>
      </template>
    </PageHeader>

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="form-container"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" :prop="isEdit ? 'passwordOptional' : 'password'">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="isEdit ? '留空则不修改密码' : '请输入密码'"
            show-password
          />
        </el-form-item>

        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="角色" prop="role_ids">
          <el-select v-model="form.role_ids" multiple placeholder="请选择角色" class="w-full">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PageHeader } from '@/components'
import { createUser, updateUser, getUserDetail } from '@/api/user'
import { getRoleList } from '@/api/role'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)
const roles = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  username: '',
  password: '',
  full_name: '',
  email: '',
  phone: '',
  role_ids: [],
  is_active: true
})

const validatePasswordOptional = (rule, value, callback) => {
  if (!isEdit.value || value) {
    if (value && value.length < 6) {
      callback(new Error('密码长度至少6位'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3到50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6到50个字符', trigger: 'blur' }
  ],
  passwordOptional: [{ validator: validatePasswordOptional, trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
}

const fetchRoles = async () => {
  try {
    const data = await getRoleList({ page: 1, page_size: 100 })
    roles.value = data.items || []
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const fetchData = async () => {
  if (!isEdit.value) {
    fetchRoles()
    return
  }

  loading.value = true
  try {
    const data = await getUserDetail(route.params.id)
    form.username = data.username
    form.full_name = data.full_name || ''
    form.email = data.email || ''
    form.phone = data.phone || ''
    form.role_ids = data.roles ? data.roles.map(r => r.id) : []
    form.is_active = data.is_active !== false
    form.password = ''
    await fetchRoles()
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        const submitData = { ...form }
        if (isEdit.value && !submitData.password) {
          delete submitData.password
        }

        if (isEdit.value) {
          await updateUser(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createUser(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/users')
      } catch (error) {
        handleSubmitError(error, form, isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
      }
    } else {
      handleFrontendValidationError()
    }
  })
}

const handleCancel = () => {
  router.push('/users')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.user-form-container {
  min-height: 100%;
}
</style>
