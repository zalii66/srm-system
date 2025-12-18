<template>
  <div class="brand-form-container">
    <PageHeader :title="isEdit ? '编辑品牌' : '新增品牌'">
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
        <el-form-item v-if="!isEdit" label="品牌编码" prop="brand_code">
          <el-input v-model="form.brand_code" placeholder="请输入品牌编码" />
        </el-form-item>

        <el-form-item label="品牌名称" prop="brand_name">
          <el-input v-model="form.brand_name" placeholder="请输入品牌名称" />
        </el-form-item>

        <el-form-item label="品牌描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入品牌描述"
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
import { createBrand, updateBrand, getBrandDetail } from '@/api/brand'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  brand_code: '',
  brand_name: '',
  description: '',
  sort_order: 0,
  is_active: true
})

const rules = {
  brand_code: [{ required: true, message: '请输入品牌编码', trigger: 'blur' }],
  brand_name: [{ required: true, message: '请输入品牌名称', trigger: 'blur' }]
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
    const data = await getBrandDetail(route.params.id)

    form.brand_name = data.brand_name || ''
    form.description = data.description || ''
    form.sort_order = data.sort_order || 0
    form.is_active = data.is_active !== undefined ? data.is_active : true
  } catch (error) {
    console.error('获取品牌信息失败:', error)
    ElMessage.error('获取品牌信息失败')
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
          await updateBrand(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createBrand(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/brands')
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
  router.push('/brands')
}

onMounted(async () => {
  await fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.brand-form-container {
  min-height: 100%;
}
</style>
