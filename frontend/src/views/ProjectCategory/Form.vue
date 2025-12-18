<template>
  <div class="category-form-container">
    <PageHeader :title="isEdit ? '编辑项目类别' : '新增项目类别'" />

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="form-container"
      >
        <el-form-item v-if="!isEdit" label="类别编码" prop="category_code">
          <el-input v-model="form.category_code" placeholder="请输入类别编码" />
        </el-form-item>

        <el-form-item label="类别名称" prop="category_name">
          <el-input v-model="form.category_name" placeholder="请输入类别名称" />
        </el-form-item>

        <el-form-item label="类别描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入类别描述"
          />
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number
            v-model="form.sort_order"
            :min="0"
            placeholder="请输入排序值"
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
          <el-button @click="handleCancel">取消</el-button>
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
import {
  createProjectCategory,
  updateProjectCategory,
  getProjectCategoryDetail
} from '@/api/projectCategory'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  category_code: '',
  category_name: '',
  description: '',
  sort_order: 0,
  is_active: true
})

const rules = {
  category_code: [{ required: true, message: '请输入类别编码', trigger: 'blur' }],
  category_name: [{ required: true, message: '请输入类别名称', trigger: 'blur' }]
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const fetchData = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getProjectCategoryDetail(route.params.id)

    form.category_name = data.category_name || ''
    form.description = data.description || ''
    form.sort_order = data.sort_order || 0
    form.is_active = data.is_active !== undefined ? data.is_active : true
  } catch (error) {
    console.error('获取项目类别信息失败:', error)
    ElMessage.error('获取项目类别信息失败')
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
          await updateProjectCategory(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createProjectCategory(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/project-categories')
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
  router.push('/project-categories')
}

onMounted(async () => {
  await fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.category-form-container {
  min-height: 100%;
}
</style>

