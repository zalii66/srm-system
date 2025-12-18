<template>
  <div class="quotation-detail-container">
    <PageHeader title="报价详情">
      <template #extra>
        <div class="action-buttons-wrapper">
          <ActionButtons v-if="quotation.status" :buttons="getActionButtons()" />
          <el-button @click="handleGoBack">返回</el-button>
        </div>
      </template>
    </PageHeader>

    <!-- 基本信息 -->
    <el-card v-loading="loading" class="info-card">
      <template #header>
        <span>基本信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="报价单号">
          {{ quotation.quotation_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目ID">
          {{ quotation.project_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="供应商">
          {{ quotation.supplier?.company_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="报价总金额">
          {{ formatCurrency(quotation.total_amount) }}
        </el-descriptions-item>
        <el-descriptions-item label="税率">
          {{ (quotation.tax_rate ? Number(quotation.tax_rate) * 100 : 0).toFixed(2) }}%
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <StatusTag :status="quotation.status || 'draft'" status-type="quotation" />
        </el-descriptions-item>
        <el-descriptions-item v-if="quotation.evaluation_comment" label="评审意见" :span="2">
          {{ quotation.evaluation_comment }}
        </el-descriptions-item>
        <el-descriptions-item label="交货天数">
          {{ quotation.delivery_days ? quotation.delivery_days + '天' : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="付款条件">
          {{ quotation.payment_terms || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="质保期">
          {{ quotation.warranty_period || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">
          {{ formatDate(quotation.submitted_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(quotation.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注说明" :span="2">
          {{ quotation.remarks || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 报价明细 -->
    <el-card v-loading="loading" class="items-card">
      <template #header>
        <span>报价明细</span>
      </template>
      <el-table
        v-if="quotation.items && quotation.items.length > 0"
        :data="quotation.items"
        stripe
        border
      >
        <el-table-column prop="project_item.item_no" label="需求编号" width="150" />
        <el-table-column prop="project_item.item_name" label="需求名称" min-width="200" />
        <el-table-column prop="project_item.specification" label="规格型号" min-width="150" />
        <el-table-column prop="project_item.unit" label="单位" width="80" />
        <el-table-column prop="project_item.quantity" label="需求数量" width="120">
          <template #default="{ row }">
            {{ formatNumber(row.project_item?.quantity) }}
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.unit_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="报价数量" width="120">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="brand" label="品牌" width="120" />
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="remarks" label="备注" min-width="150" />
      </el-table>
      <el-empty
        v-if="!loading && (!quotation.items || quotation.items.length === 0)"
        description="暂无报价明细"
      />
      
    </el-card>

    <!-- 评审对话框 -->
    <el-dialog
      v-model="evaluateDialogVisible"
      :title="getEvaluateDialogTitle()"
      :width="DIALOG_WIDTH.MEDIUM"
    >
      <el-form :model="evaluateForm" label-width="100px">
        <el-form-item label="评审状态">
          <el-tag :type="evaluateForm.status === 'selected' ? 'success' : 'warning'">
            {{ evaluateForm.status === 'selected' ? '中标' : '未中标' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="评审意见" required>
          <el-input
            v-model="evaluateForm.evaluation_comment"
            type="textarea"
            :rows="4"
            placeholder="请输入评审意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="evaluateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEvaluate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PageHeader, StatusTag, ActionButtons } from '@/components'
import {
  getQuotationDetail,
  submitQuotation,
  cancelQuotation,
  evaluateQuotation
} from '@/api/quotation'
import { formatDate, formatCurrency, formatNumber, DIALOG_WIDTH } from '@/utils'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const evaluateDialogVisible = ref(false)
const evaluateForm = reactive({
  status: '',
  evaluation_comment: ''
})

const isSupplier = computed(() => {
  return userStore.roles?.includes('supplier') || false
})

const isProjectManager = computed(() => {
  return userStore.isSuperuser || userStore.roles?.includes('project_manager') || false
})

const isAdmin = computed(() => {
  return userStore.isSuperuser || false
})

const quotation = reactive({
  id: '',
  quotation_no: '',
  project_id: '',
  supplier_id: '',
  supplier: null,
  total_amount: 0,
  tax_rate: 0.13,
  delivery_days: null,
  payment_terms: '',
  warranty_period: '',
  status: '',
  remarks: '',
  submitted_at: null,
  created_at: '',
  items: []
})

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getQuotationDetail(route.params.id)
    Object.assign(quotation, data)
  } catch (error) {
    console.error('获取报价详情失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取报价详情失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const handleGoBack = () => {
  router.back()
}

// 获取操作按钮配置
const getActionButtons = () => {
  const buttons = []
  const status = quotation.status || ''

  // 供应商操作
  if (isSupplier.value) {
    if (status === 'draft') {
      buttons.push({
        key: 'submit',
        label: '提交报价',
        type: 'primary',
        handler: handleSubmit
      })
      buttons.push({
        key: 'edit',
        label: '编辑报价',
        type: 'default',
        handler: () => router.push(`/quotation/edit/${quotation.id}`)
      })
      buttons.push({
        key: 'cancel',
        label: '取消报价',
        type: 'danger',
        handler: handleCancel
      })
    } else if (status === 'submitted') {
      buttons.push({
        key: 'cancel',
        label: '取消报价',
        type: 'danger',
        handler: handleCancel
      })
    } else if (status === 'cancelled') {
      // 已取消的报价可以重新报价
      buttons.push({
        key: 're-quote',
        label: '重新报价',
        type: 'primary',
        handler: () => router.push(`/quotation/edit/${quotation.id}`)
      })
    }
  }

  // 项目经理/管理员操作
  if (isProjectManager.value || isAdmin.value) {
    // 已提交的报价可以评审
    if (status === 'submitted') {
      buttons.push({
        key: 'approve',
        label: '批准（中标）',
        type: 'success',
        handler: () => handleEvaluate('selected')
      })
      buttons.push({
        key: 'reject',
        label: '拒绝（未中标）',
        type: 'warning',
        handler: () => handleEvaluate('rejected')
      })
    }
    // 已中标或已拒绝的报价可以重新评审
    if (status === 'selected' || status === 'rejected') {
      buttons.push({
        key: 're-evaluate',
        label: '重新评审',
        type: 'primary',
        handler: () => {
          // 如果已中标，显示重新评审为未中标；如果已拒绝，显示重新评审为中标
          const newStatus = status === 'selected' ? 'rejected' : 'selected'
          handleEvaluate(newStatus)
        }
      })
    }
    // 管理员可以取消任何状态的报价
    if (isAdmin.value && status !== 'cancelled') {
      buttons.push({
        key: 'admin-cancel',
        label: '取消报价',
        type: 'danger',
        handler: handleCancel
      })
    }
  }

  return buttons
}

// 提交报价
const handleSubmit = async () => {
  try {
    await ElMessageBox.confirm('确定要提交此报价吗？提交后将无法修改。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await submitQuotation(quotation.id)
    ElMessage.success('提交报价成功')
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        '提交报价失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 取消报价
const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消此报价吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await cancelQuotation(quotation.id)
    ElMessage.success('取消报价成功')
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        '取消报价失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 获取评审对话框标题
const getEvaluateDialogTitle = () => {
  const status = evaluateForm.status
  const currentStatus = quotation.status || ''
  if (status === 'selected') {
    return currentStatus === 'selected' ? '重新评审：批准报价（中标）' : '批准报价（中标）'
  } else {
    return currentStatus === 'rejected' ? '重新评审：拒绝报价（未中标）' : '拒绝报价（未中标）'
  }
}

// 评审报价
const handleEvaluate = (status) => {
  evaluateForm.status = status
  // 如果是重新评审，保留原有评审意见作为默认值
  evaluateForm.evaluation_comment = (quotation.evaluation_comment || '').trim()
  evaluateDialogVisible.value = true
}

// 确认评审
const confirmEvaluate = async () => {
  if (!evaluateForm.evaluation_comment.trim()) {
    ElMessage.warning('请输入评审意见')
    return
  }

  try {
    await evaluateQuotation(quotation.id, {
      status: evaluateForm.status,
      evaluation_comment: evaluateForm.evaluation_comment.trim()
    })
    ElMessage.success('评审成功')
    evaluateDialogVisible.value = false
    await fetchData()
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '评审失败'
    ElMessage.error(errorMsg)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.quotation-detail-container {
  min-height: 100%;
}

.info-card,
.items-card {
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

.action-buttons-wrapper {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.evaluate-actions {
  margin-top: $spacing-lg;
  padding-top: $spacing-lg;
  border-top: 1px solid $border-color-lighter;
  display: flex;
  justify-content: flex-end;
  gap: $spacing-md;
}
</style>
