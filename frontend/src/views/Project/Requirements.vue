<template>
  <div class="requirements-container">
    <PageHeader :title="projectInfo.project_name || '项目需求'" subtitle="查看和管理项目需求项">
      <template #extra>
        <el-button @click="handleGoBack">返回</el-button>
        <el-button
          v-if="canManage && projectInfo.status !== 1 && projectInfo.status !== 3"
          type="success"
          :loading="publishLoading"
          @click="handlePublishProject"
        >
          发布项目
        </el-button>
        <el-button v-if="canManage" type="primary" @click="handleAddItem">添加需求项</el-button>
      </template>
    </PageHeader>

    <!-- 项目信息卡片 -->
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

    <!-- 需求项列表（管理员/项目经理可见，供应商在报价区域已能看到，无需重复显示） -->
    <el-card v-if="canManage" v-loading="itemsLoading" class="items-card">
      <template #header>
        <div class="card-header">
          <span>需求项列表</span>
          <span class="item-count">共 {{ items.length }} 项</span>
        </div>
      </template>

      <el-table v-if="items.length > 0" :data="items" stripe>
        <el-table-column prop="item_no" label="需求编号" width="120" />
        <el-table-column prop="item_name" label="需求名称" min-width="200" />
        <el-table-column prop="specification" label="规格型号" min-width="150" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="quantity" label="数量" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }}
          </template>
        </el-table-column>
        <!-- 单价和金额由供应商在报价时填写，需求清单中不显示 -->
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <ActionButtons :buttons="getActionButtons(row)" />
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!itemsLoading && items.length === 0" description="暂无需求项" />
    </el-card>

    <!-- 供应商报价区域 -->
    <el-card
      v-if="isSupplier && (projectInfo.status === 1 || projectInfo.status === 3)"
      class="quotation-card"
    >
      <template #header>
        <span>填写报价</span>
      </template>

      <el-alert v-if="existingQuotation" type="info" :closable="false" class="mb-lg">
        <template #title>
          <span>
            您已为此项目提交过报价，总金额：{{ formatCurrency(existingQuotation.total_amount) }}
          </span>
          <el-button type="primary" size="small" class="ml-sm" @click="handleViewQuotation">
            查看报价详情
          </el-button>
        </template>
      </el-alert>

      <!-- 报价明细表格 -->
      <el-table v-if="items.length > 0" :data="quotationItems" border class="mb-lg">
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

      <el-form
        ref="quotationFormRef"
        :model="quotationForm"
        :rules="quotationRules"
        :label-width="FORM_LABEL_WIDTH.DEFAULT"
        class="form-container"
      >
        <el-form-item label="报价总金额">
          <span class="total-amount-text">
            {{ formatCurrency(totalQuotationAmount) }}
          </span>
        </el-form-item>

        <el-form-item label="交货天数" prop="delivery_days">
          <el-input-number
            v-model="quotationForm.delivery_days"
            :min="1"
            placeholder="请输入交货天数"
          />
        </el-form-item>

        <el-form-item label="付款条件" prop="payment_terms">
          <el-input v-model="quotationForm.payment_terms" placeholder="请输入付款条件" />
        </el-form-item>

        <el-form-item label="质保期" prop="warranty_period">
          <el-input v-model="quotationForm.warranty_period" placeholder="请输入质保期，如：1年" />
        </el-form-item>

        <el-form-item label="备注说明" prop="remarks">
          <el-input
            v-model="quotationForm.remarks"
            type="textarea"
            :rows="4"
            placeholder="请输入备注说明"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="quotationLoading" @click="handleSubmitQuotation">
            {{ existingQuotation ? '更新报价' : '提交报价' }}
          </el-button>
          <el-button @click="handleResetQuotation">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 添加/编辑需求项对话框 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="isEditItem ? '编辑需求项' : '添加需求项'"
      :width="DIALOG_WIDTH.MEDIUM"
      @close="handleCloseItemDialog"
    >
      <el-form
        ref="itemFormRef"
        :model="itemForm"
        :rules="itemRules"
        :label-width="FORM_LABEL_WIDTH.DEFAULT"
        class="form-container"
      >
        <!-- 需求编号自动生成，不需要手动输入 -->

        <el-form-item label="需求名称" prop="item_name">
          <el-input v-model="itemForm.item_name" placeholder="请输入需求名称" />
        </el-form-item>

        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="itemForm.specification" placeholder="请输入规格型号" />
        </el-form-item>

        <el-form-item label="单位" prop="unit">
          <el-input v-model="itemForm.unit" placeholder="请输入单位，如：台、套、件" />
        </el-form-item>

        <el-form-item label="数量" prop="quantity">
          <el-input-number
            v-model="itemForm.quantity"
            :min="0.01"
            :precision="2"
            placeholder="请输入数量"
            class="w-full"
          />
        </el-form-item>

        <!-- 预估单价由供应商在报价时填写，项目经理不需要填写 -->

        <el-form-item label="说明" prop="description">
          <el-input
            v-model="itemForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入说明"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCloseItemDialog">取消</el-button>
        <el-button type="primary" :loading="itemLoading" @click="handleSubmitItem">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PageHeader, StatusTag, ActionButtons } from '@/components'
import { formatDate, formatCurrency, formatNumber, calculateAmount, normalizePrice, normalizeQuantity, DIALOG_WIDTH, FORM_LABEL_WIDTH, SupplierStatus } from '@/utils'
import {
  getProjectDetail,
  getProjectItems,
  createProjectItem,
  updateProjectItem,
  deleteProjectItem,
  publishProject as publishProjectApi
} from '@/api/project'
import { createQuotation, getMyQuotations, getQuotationDetail, submitQuotation } from '@/api/quotation'
import { useUserStore } from '@/stores/user'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const projectLoading = ref(false)
const itemsLoading = ref(false)
const quotationLoading = ref(false)
const publishLoading = ref(false)
const itemLoading = ref(false)
const itemDialogVisible = ref(false)
const isEditItem = ref(false)
const currentItemId = ref(null)

const projectInfo = reactive({
  id: null,
  project_no: '',
  project_name: '',
  status: '',
  bidding_deadline: ''
})

const items = ref([])
const existingQuotation = ref(null)
const quotationItems = ref([])
const totalQuotationAmount = ref(0)

const canManage = computed(() => {
  if (!userStore.roles || !Array.isArray(userStore.roles)) return false
  return userStore.isSuperuser || userStore.roles.includes('project_manager')
})

const isSupplier = computed(() => {
  if (!userStore.roles || !Array.isArray(userStore.roles)) return false
  return userStore.roles.includes('supplier')
})

const quotationFormRef = ref(null)
const quotationForm = reactive({
  delivery_days: null,
  payment_terms: '',
  warranty_period: '',
  remarks: ''
})

const quotationRules = {
  delivery_days: [{ required: true, message: '请输入交货天数', trigger: 'blur' }]
}

const itemFormRef = ref(null)
// 注意：
// - item_no 由系统根据项目编号自动生成，不需要填写
// - estimated_price 由供应商在报价时填写，项目经理不填写
const itemForm = reactive({
  item_name: '',
  specification: '',
  unit: '',
  quantity: null,
  description: ''
})

const itemRules = {
  item_name: [{ required: true, message: '请输入需求名称', trigger: 'blur' }],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '数量必须大于0', trigger: 'blur' }
  ]
}

// 使用表单验证工具（需求项表单）
const { handleSubmitError: handleItemSubmitError, handleFrontendValidationError: handleItemFrontendValidationError } = useFormValidation(
  itemFormRef,
  itemForm
)

// 使用表单验证工具（报价表单）
const { handleSubmitError: handleQuotationSubmitError, handleFrontendValidationError: handleQuotationFrontendValidationError } = useFormValidation(
  quotationFormRef,
  quotationForm
)

const fetchProjectInfo = async () => {
  projectLoading.value = true
  try {
    const projectId = route.params.id
    const data = await getProjectDetail(projectId)
    Object.assign(projectInfo, data)
  } catch (error) {
    console.error('获取项目信息失败:', error)
    ElMessage.error('获取项目信息失败')
  } finally {
    projectLoading.value = false
  }
}

const fetchItems = async () => {
  itemsLoading.value = true
  try {
    const projectId = route.params.id
    const data = await getProjectItems(projectId)
    items.value = data.items || []

    // 如果是供应商，初始化报价明细项
    if (isSupplier.value && items.value.length > 0) {
      initializeQuotationItems()
    }
  } catch (error) {
    console.error('获取需求项列表失败:', error)
    ElMessage.error('获取需求项列表失败')
  } finally {
    itemsLoading.value = false
  }
}

const initializeQuotationItems = () => {
  quotationItems.value = items.value.map(item => ({
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
  calculateTotalAmount()
}

const calculateTotalAmount = () => {
  totalQuotationAmount.value = quotationItems.value.reduce((sum, item) => {
    if (item.unit_price && item.quantity) {
      return sum + calculateAmount(item.unit_price, item.quantity)
    }
    return sum
  }, 0)
}

const fetchExistingQuotation = async () => {
  if (!isSupplier.value) return

  try {
    const data = await getMyQuotations({ page: 1, page_size: 100 })
    const quotations = data.items || []
    const quotation = quotations.find(q => q.project_id === Number(route.params.id))
    if (quotation) {
      existingQuotation.value = quotation
      
      // 获取完整的报价详情（包含明细项）
      try {
        const quotationDetail = await getQuotationDetail(quotation.id)
        // 填充表单
        quotationForm.delivery_days = quotationDetail.delivery_days
        quotationForm.payment_terms = quotationDetail.payment_terms || ''
        quotationForm.warranty_period = quotationDetail.warranty_period || ''
        quotationForm.remarks = quotationDetail.remarks || ''
        
        // 如果已有报价明细，填充到报价明细表格中
        if (quotationDetail.items && quotationDetail.items.length > 0 && quotationItems.value.length > 0) {
          quotationDetail.items.forEach(quotationItem => {
            const itemIndex = quotationItems.value.findIndex(
              item => item.project_item_id === quotationItem.project_item_id
            )
            if (itemIndex !== -1) {
              quotationItems.value[itemIndex].unit_price = normalizePrice(quotationItem.unit_price)
              quotationItems.value[itemIndex].brand = quotationItem.brand || null
              quotationItems.value[itemIndex].model = quotationItem.model || null
              quotationItems.value[itemIndex].remarks = quotationItem.remarks || null
            }
          })
          calculateTotalAmount()
        }
      } catch (error) {
        console.error('获取报价详情失败:', error)
        // 如果获取详情失败，至少填充基本信息
        quotationForm.delivery_days = quotation.delivery_days
        quotationForm.payment_terms = quotation.payment_terms || ''
        quotationForm.warranty_period = quotation.warranty_period || ''
        quotationForm.remarks = quotation.remarks || ''
      }
    }
  } catch (error) {
    console.error('获取已有报价失败:', error)
  }
}

const handleGoBack = () => {
  router.back()
}

const handleAddItem = () => {
  isEditItem.value = false
  currentItemId.value = null
  itemForm.item_name = ''
  itemForm.specification = ''
  itemForm.unit = ''
  itemForm.quantity = null
  itemForm.description = ''
  itemDialogVisible.value = true
}

const handleEditItem = row => {
  isEditItem.value = true
  currentItemId.value = row.id
  itemForm.item_name = row.item_name
  itemForm.specification = row.specification || ''
  itemForm.unit = row.unit || ''
  itemForm.quantity = Number(row.quantity)
  itemForm.description = row.description || ''
  itemDialogVisible.value = true
}

const handleCloseItemDialog = () => {
  itemDialogVisible.value = false
  if (itemFormRef.value) {
    itemFormRef.value.clearValidate()
  }
}

const handleSubmitItem = async () => {
  if (!itemFormRef.value) return

  await itemFormRef.value.validate(async valid => {
    if (valid) {
      itemLoading.value = true
      try {
        const projectId = Number(route.params.id)
        const itemData = {
          item_name: itemForm.item_name,
          specification: itemForm.specification || null,
          unit: itemForm.unit || null,
          quantity: itemForm.quantity,
          estimated_price: null, // 单价由供应商在报价时填写
          description: itemForm.description || null
          // 注意：item_no 由后端根据项目编号自动生成，不需要传递
        }

        if (isEditItem.value) {
          await updateProjectItem(projectId, currentItemId.value, itemData)
          ElMessage.success('更新需求项成功')
        } else {
          await createProjectItem(projectId, itemData)
          ElMessage.success('添加需求项成功')
        }

        handleCloseItemDialog()
        await fetchItems()
      } catch (error) {
        handleItemSubmitError(error, itemForm, isEditItem.value ? '更新需求项失败' : '添加需求项失败')
      } finally {
        itemLoading.value = false
      }
    } else {
      handleItemFrontendValidationError()
    }
  })
}

const handleDeleteItem = row => {
  ElMessageBox.confirm(`确定要删除需求项"${row.item_name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        const projectId = Number(route.params.id)
        await deleteProjectItem(projectId, row.id)
        ElMessage.success('删除成功')
        await fetchItems()
      } catch (error) {
        const errorMsg =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          '删除失败'
        ElMessage.error(errorMsg)
      }
    })
    .catch(() => {})
}

const handlePublishProject = () => {
  ElMessageBox.confirm('发布后，供应商将可以查看此项目并提交报价。确定要发布吗？', '发布项目', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      publishLoading.value = true
      try {
        await publishProjectApi(Number(route.params.id))
        ElMessage.success('发布成功')
        await fetchProjectInfo()
      } catch (error) {
        const errorMsg =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          '发布失败'
        ElMessage.error(errorMsg)
      } finally {
        publishLoading.value = false
      }
    })
    .catch(() => {})
}

const handleSubmitQuotation = async () => {
  if (!quotationFormRef.value) return

  await quotationFormRef.value.validate(async valid => {
    if (valid) {
      if (items.value.length === 0) {
        ElMessage.warning('项目暂无需求项，无法提交报价')
        return
      }

      // 检查供应商审核状态
      try {
        const { getCurrentSupplier } = await import('@/api/supplier')
        const supplierData = await getCurrentSupplier()
        // 状态是整数：-1待审核/0审核失败/1审核通过
        const status = supplierData?.status
        if (!supplierData || status !== SupplierStatus.APPROVED) {
          await ElMessageBox.alert(
            '只有通过审核的公司才能参与项目报价。请先完善公司资料并等待审核通过。',
            '无法报价',
            {
              confirmButtonText: '前往公司资料',
              type: 'warning'
            }
          )
          router.push('/supplier/profile')
          return
        }
      } catch (error) {
        // 如果获取供应商信息失败，提示用户
        if (error.response?.status === 404) {
          await ElMessageBox.alert(
            '请先完善公司资料并等待审核通过后才能参与项目报价。',
            '无法报价',
            {
              confirmButtonText: '前往公司资料',
              type: 'warning'
            }
          )
          router.push('/supplier/profile')
          return
        }
        // 其他错误也阻止报价
        ElMessage.error('无法获取供应商信息，请稍后重试')
        return
      }

      // 验证是否填写了所有单价
      const hasEmptyPrice = quotationItems.value.some(
        item => !item.unit_price || Number(item.unit_price) <= 0
      )
      if (hasEmptyPrice) {
        ElMessage.warning('请为所有需求项填写单价')
        return
      }

      quotationLoading.value = true
      try {
        // 使用供应商填写的报价明细
        const quotationItemsData = quotationItems.value.map(item => ({
          project_item_id: item.project_item_id,
          unit_price: Number(item.unit_price),
          quantity: item.quantity,
          brand: item.brand || null,
          model: item.model || null,
          remarks: item.remarks || null
        }))

        const quotationData = {
          project_id: Number(route.params.id),
          tax_rate: 0.13, // 默认税率13%
          delivery_days: quotationForm.delivery_days,
          payment_terms: quotationForm.payment_terms,
          warranty_period: quotationForm.warranty_period,
          remarks: quotationForm.remarks,
          items: quotationItemsData
        }

        let quotation
        if (existingQuotation.value) {
          // 如果已存在报价，先删除再创建（因为后端不支持更新报价明细）
          ElMessage.warning('已存在报价，请前往报价详情页面进行修改')
          router.push(`/quotation/detail/${existingQuotation.value.id}`)
          quotationLoading.value = false
          return
        } else {
          quotation = await createQuotation(quotationData)
          // 创建报价后自动提交
          if (quotation && quotation.id) {
            await submitQuotation(quotation.id)
          }
        }
        ElMessage.success('提交报价成功')
        await fetchExistingQuotation()
      } catch (error) {
        const errorMsg =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          '提交报价失败'
        // 如果是审核状态错误，使用弹窗提示
        if (errorMsg.includes('审核') || errorMsg.includes('资质')) {
          ElMessageBox.alert(errorMsg + '请先完善公司资料并等待审核通过。', '无法报价', {
            confirmButtonText: '前往公司资料',
            type: 'warning'
          })
            .then(() => {
              router.push('/supplier/profile')
            })
            .catch(() => {})
        } else {
          // 使用统一的错误处理
          handleQuotationSubmitError(error, quotationForm, '提交报价失败')
        }
      } finally {
        quotationLoading.value = false
      }
    } else {
      handleQuotationFrontendValidationError()
    }
  })
}

const handleResetQuotation = () => {
  quotationForm.delivery_days = null
  quotationForm.payment_terms = ''
  quotationForm.warranty_period = ''
  quotationForm.remarks = ''
  // 重置报价明细
  initializeQuotationItems()
  if (quotationFormRef.value) {
    quotationFormRef.value.clearValidate()
  }
}

const handleViewQuotation = () => {
  router.push(`/quotation/detail/${existingQuotation.value.id}`)
}

// 获取操作按钮配置
const getActionButtons = row => {
  return [
    {
      key: 'edit',
      label: '编辑',
      type: 'primary',
      size: 'small',
      handler: () => handleEditItem(row)
    },
    {
      key: 'delete',
      label: '删除',
      type: 'danger',
      size: 'small',
      handler: () => handleDeleteItem(row)
    }
  ]
}

onMounted(() => {
  fetchProjectInfo()
  fetchItems()
  if (isSupplier.value) {
    fetchExistingQuotation()
  }
})

// 监听items变化，如果是供应商且items有数据，初始化报价明细
watch(
  () => items.value,
  newItems => {
    if (isSupplier.value && newItems && newItems.length > 0 && quotationItems.value.length === 0) {
      initializeQuotationItems()
    }
  }
)
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.requirements-container {
  min-height: 100%;
}

.project-info-card,
.items-card,
.quotation-card {
  margin-bottom: $spacing-lg;
  border-radius: $border-radius-base;

  :deep(.el-card__header) {
    padding: $spacing-lg;
    border-bottom: 1px solid $border-color-lighter;
  }

  :deep(.el-card__body) {
    padding: $spacing-lg;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .item-count {
    color: $text-secondary;
    font-size: 14px;
  }
}

.total-amount-text {
  font-size: 18px;
  color: $primary-color;
  font-weight: bold;
}
</style>
