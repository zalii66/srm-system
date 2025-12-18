<template>
  <div class="company-form-container">
    <PageHeader :title="isEdit ? '编辑公司' : '新增公司'">
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
        <el-form-item v-if="!isEdit" label="公司编码" prop="company_code">
          <el-input v-model="form.company_code" placeholder="请输入公司编码" />
        </el-form-item>

        <el-form-item label="公司名称" prop="company_name">
          <el-input v-model="form.company_name" placeholder="请输入公司名称" />
        </el-form-item>

        <el-form-item label="所属品牌" prop="brand_id">
          <el-select
            v-model="form.brand_id"
            placeholder="请选择品牌"
            clearable
            filterable
            class="w-full"
          >
            <el-option
              v-for="brand in brandList"
              :key="brand.id"
              :label="brand.brand_name"
              :value="brand.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="详细地址" prop="address">
          <el-input v-model="form.address" type="textarea" :rows="3" placeholder="请输入详细地址" />
        </el-form-item>

        <el-form-item label="公司描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入公司描述"
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
import { createCompany, updateCompany, getCompanyDetail } from '@/api/company'
import { getBrandList } from '@/api/brand'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)
const brandList = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  company_code: '',
  company_name: '',
  brand_id: null,
  address: '',
  description: '',
  sort_order: 0,
  is_active: true
})

const rules = {
  company_code: [{ required: true, message: '请输入公司编码', trigger: 'blur' }],
  company_name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }]
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const fetchBrandList = async () => {
  try {
    const data = await getBrandList({ page: 1, page_size: 100, is_active: true })
    if (data && Array.isArray(data.items)) {
      brandList.value = data.items
    } else {
      brandList.value = []
    }
  } catch (error) {
    console.error('获取品牌列表失败:', error)
    brandList.value = []
  }
}

const fetchData = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getCompanyDetail(route.params.id)

    form.company_name = data.company_name || ''
    form.brand_id = data.brand_id || null
    form.address = data.address || ''
    form.description = data.description || ''
    form.sort_order = data.sort_order || 0
    form.is_active = data.is_active !== undefined ? data.is_active : true
  } catch (error) {
    console.error('获取公司信息失败:', error)
    ElMessage.error('获取公司信息失败')
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
          await updateCompany(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createCompany(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/companies')
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
  router.push('/companies')
}

onMounted(async () => {
  await fetchBrandList()
  await fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.company-form-container {
  min-height: 100%;
}
</style>
