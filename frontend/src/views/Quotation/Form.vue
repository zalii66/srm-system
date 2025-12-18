<template>
  <div class="quotation-form-container">
    <PageHeader :title="isEdit ? '编辑报价' : '创建报价'">
      <template #extra>
        <el-button @click="handleCancel">返回</el-button>
      </template>
    </PageHeader>

    <!-- 项目信息 -->
    <el-card v-loading="projectLoading" class="project-info-card">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="项目编号">
          {{ projectInfo.project_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目名称">
          {{ projectInfo.project_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目状态">
          <StatusTag :status="projectInfo.status ?? 0" status-type="project" />
        </el-descriptions-item>
        <el-descriptions-item label="投标截止时间">
          {{ formatDate(projectInfo.bidding_deadline) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 报价明细表格 -->
    <el-card class="items-card">
      <template #header>
        <span>报价明细</span>
      </template>
      <el-table v-if="quotationItems.length > 0" :data="quotationItems" border class="mb-lg">
        <el-table-column prop="item_name" label="需求名称" min-width="150" />
        <el-table-column prop="specification" label="规格型号" min-width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="quantity" label="数量" width="100">
          <template #default="{ row }">
            {{ formatNumber(normalizeQuantity(row.quantity)) }}
          </template>
        </el-table-column>
        <el-table-column label="单价" width="150">
          <template #default="{ row }">
            <el-input-number
              v-model="row.unit_price"
              :min="0"
              :precision="2"
              :step="0.01"
              placeholder="请输入单价"
              class="w-full"
              @change="(val) => {
                if (val !== null && val !== undefined) {
                  row.unit_price = normalizePrice(val)
                }
                calculateTotalAmount()
              }"
            />
          </template>
        </el-table-column>
        <el-table-column label="金额" width="150">
          <template #default="{ row }">
            <span v-if="row.unit_price && row.quantity">
              {{ formatCurrency(calculateAmount(row.unit_price, row.quantity)) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="品牌" width="120">
          <template #default="{ row }">
            <el-input
              v-model="row.brand"
              placeholder="请输入品牌"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column label="型号" width="120">
          <template #default="{ row }">
            <el-input
              v-model="row.model"
              placeholder="请输入型号"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150">
          <template #default="{ row }">
            <el-input
              v-model="row.remarks"
              placeholder="请输入备注"
              size="small"
            />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无报价明细" />
    </el-card>

    <!-- 报价表单 -->
    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :label-width="FORM_LABEL_WIDTH.DEFAULT"
        class="form-container"
      >
        <el-form-item label="报价总金额">
          <span class="total-amount-text">
            {{ formatCurrency(totalAmount) }}
          </span>
        </el-form-item>

        <el-form-item label="交货天数" prop="delivery_days">
          <el-input-number
            v-model="form.delivery_days"
            :min="1"
            placeholder="请输入交货天数"
          />
        </el-form-item>

        <el-form-item label="付款条件" prop="payment_terms">
          <el-input v-model="form.payment_terms" placeholder="请输入付款条件" />
        </el-form-item>

        <el-form-item label="质保期" prop="warranty_period">
          <el-input v-model="form.warranty_period" placeholder="请输入质保期，如：1年" />
        </el-form-item>

        <el-form-item label="备注说明" prop="remarks">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="4"
            placeholder="请输入备注说明"
          />
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
import { PageHeader, StatusTag } from '@/components'
import { createQuotation, updateQuotation, getQuotationDetail } from '@/api/quotation'
import { getProjectDetail, getProjectItems } from '@/api/project'
import { formatDate, formatCurrency, formatNumber, calculateAmount, normalizePrice, normalizeQuantity, FORM_LABEL_WIDTH } from '@/utils'
import { useFormValidation } from '@/composables'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const projectLoading = ref(false)
const projectInfo = reactive({
  id: null,
  project_no: '',
  project_name: '',
  status: '',
  bidding_deadline: ''
})

const quotationItems = ref([])
const totalAmount = ref(0)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  delivery_days: null,
  payment_terms: '',
  warranty_period: '',
  remarks: ''
})

const rules = {
  delivery_days: [{ required: true, message: '请输入交货天数', trigger: 'blur' }]
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const calculateTotalAmount = () => {
  totalAmount.value = quotationItems.value.reduce((sum, item) => {
    if (item.unit_price && item.quantity) {
      return sum + calculateAmount(item.unit_price, item.quantity)
    }
    return sum
  }, 0)
}

// 获取项目信息
const fetchProjectInfo = async (projectId) => {
  projectLoading.value = true
  try {
    const data = await getProjectDetail(projectId)
    Object.assign(projectInfo, data)
  } catch (error) {
    console.error('获取项目信息失败:', error)
    ElMessage.error('获取项目信息失败')
  } finally {
    projectLoading.value = false
  }
}

// 获取报价数据
const fetchData = async () => {
  if (!isEdit.value) {
    ElMessage.error('请从项目需求页面创建报价')
    router.push('/projects')
    return
  }

  loading.value = true
  try {
    const data = await getQuotationDetail(route.params.id)
    
    // 填充表单
    form.delivery_days = data.delivery_days
    form.payment_terms = data.payment_terms || ''
    form.warranty_period = data.warranty_period || ''
    form.remarks = data.remarks || ''
    
    // 获取项目信息
    await fetchProjectInfo(data.project_id)
    
    // 获取项目需求项
    const itemsData = await getProjectItems(data.project_id)
    const items = itemsData.items || []
    
    // 初始化报价明细（如果有已存在的报价明细，使用它；否则从项目需求项创建）
    if (data.items && data.items.length > 0) {
      quotationItems.value = data.items.map(quotationItem => {
        const projectItem = items.find(item => item.id === quotationItem.project_item_id)
        const rawQuantity = projectItem?.quantity || quotationItem.quantity
        
        return {
          project_item_id: quotationItem.project_item_id,
          item_name: projectItem?.item_name || '',
          specification: projectItem?.specification || '',
          unit: projectItem?.unit || '',
          quantity: normalizeQuantity(rawQuantity),
          unit_price: normalizePrice(quotationItem.unit_price),
          brand: quotationItem.brand || null,
          model: quotationItem.model || null,
          remarks: quotationItem.remarks || null
        }
      })
    } else {
      quotationItems.value = items.map(item => ({
        project_item_id: item.id,
        item_name: item.item_name,
        specification: item.specification || '',
        unit: item.unit || '',
        quantity: normalizeQuantity(item.quantity),
        unit_price: 0,
        brand: null,
        model: null,
        remarks: null
      }))
    }
    
    calculateTotalAmount()
  } catch (error) {
    console.error('获取报价信息失败:', error)
    ElMessage.error('获取报价信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  // 验证是否填写了所有单价
  const hasEmptyPrice = quotationItems.value.some(
    item => !item.unit_price || Number(item.unit_price) <= 0
  )
  if (hasEmptyPrice) {
    ElMessage.warning('请为所有需求项填写单价')
    return
  }

  await formRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        // 准备报价明细数据
        const itemsData = quotationItems.value.map(item => ({
          project_item_id: item.project_item_id,
          unit_price: Number(item.unit_price),
          quantity: item.quantity,
          brand: item.brand || null,
          model: item.model || null,
          remarks: item.remarks || null
        }))

        const quotationData = {
          tax_rate: 0.13, // 默认税率13%
          delivery_days: form.delivery_days,
          payment_terms: form.payment_terms,
          warranty_period: form.warranty_period,
          remarks: form.remarks,
          items: itemsData
        }

        if (isEdit.value) {
          await updateQuotation(route.params.id, quotationData)
          ElMessage.success('更新报价成功')
        } else {
          await createQuotation(quotationData)
          ElMessage.success('创建报价成功')
        }
        
        router.push(`/quotation/detail/${route.params.id}`)
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
  router.back()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.quotation-form-container {
  min-height: 100%;

  .project-info-card,
  .items-card {
    margin-bottom: $spacing-lg;
  }

  .total-amount-text {
    font-size: 18px;
    font-weight: bold;
    color: $primary-color;
  }

  .w-full {
    width: 100%;
  }
}
</style>
