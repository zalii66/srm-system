<template>
  <div class="permission-form-container">
    <PageHeader :title="isEdit ? '编辑权限' : '新增权限'">
      <template #extra>
        <el-button @click="handleCancel">返回</el-button>
      </template>
    </PageHeader>

    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入权限名称" />
        </el-form-item>

        <el-form-item label="权限编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" placeholder="请输入权限编码，如：user:manage" />
          <div class="form-tip">格式：资源:操作，如 user:manage、project:create</div>
        </el-form-item>

        <el-form-item label="资源" prop="resource">
          <el-input v-model="form.resource" placeholder="请输入资源名称，如：user" />
        </el-form-item>

        <el-form-item label="操作" prop="action">
          <el-input v-model="form.action" placeholder="请输入操作名称，如：manage" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入权限描述"
          />
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
import { createPermission, updatePermission, getPermissionDetail } from '@/api/permission'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  code: '',
  resource: '',
  action: '',
  description: '',
  is_active: true
})

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const rules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度在2到50个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限编码', trigger: 'blur' },
    { min: 2, max: 100, message: '权限编码长度在2到100个字符', trigger: 'blur' },
    {
      pattern: /^[a-z_]+:[a-z_]+$/,
      message: '权限编码格式不正确，应为：资源:操作，如 user:manage',
      trigger: 'blur'
    }
  ],
  resource: [
    { required: true, message: '请输入资源名称', trigger: 'blur' },
    { min: 2, max: 50, message: '资源名称长度在2到50个字符', trigger: 'blur' }
  ],
  action: [
    { required: true, message: '请输入操作名称', trigger: 'blur' },
    { min: 2, max: 50, message: '操作名称长度在2到50个字符', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getPermissionDetail(route.params.id)

    form.name = data.name || ''
    form.code = data.code || ''
    form.resource = data.resource || ''
    form.action = data.action || ''
    form.description = data.description || ''
    form.is_active = data.is_active !== undefined ? data.is_active : true
  } catch (error) {
    console.error('获取权限信息失败:', error)
    ElMessage.error('获取权限信息失败')
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

        if (isEdit.value) {
          await updatePermission(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createPermission(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/permissions')
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
  router.push('/permissions')
}

onMounted(async () => {
  await fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.permission-form-container {
  min-height: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>

