<template>
  <div class="supplier-list-container">
    <PageHeader title="供应商列表" subtitle="审核和管理供应商信息" />

    <SearchForm v-model="searchForm" @search="fetchData" @reset="resetSearch">
      <el-form-item label="搜索关键词">
        <el-input
          v-model="searchForm.keyword"
          placeholder="请输入手机号、公司名称或联系人"
          clearable
          class="keyword-input"
        />
      </el-form-item>
      <el-form-item label="审核状态" class="status-select">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="待审核" :value="-1" />
          <el-option label="审核失败" :value="0" />
          <el-option label="审核通过" :value="1" />
        </el-select>
      </el-form-item>
    </SearchForm>

    <DataTable
      v-model:page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      @change="fetchData"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="company_name" label="公司名称" min-width="200" />
      <el-table-column prop="contact_person" label="联系人" width="120" />
      <el-table-column prop="contact_phone" label="联系电话" width="130" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag
            :status="typeof row.status === 'number' ? row.status : (row.status ?? 0)"
            status-type="supplier"
          />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作"  fixed="right">
        <template #default="{ row }">
          <ActionButtons :buttons="getActionButtons(row)" />
        </template>
      </el-table-column>
    </DataTable>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="auditDialogVisible"
      :title="`审核供应商 - ${currentAuditRow?.company_name || ''}`"
      :width="DIALOG_WIDTH.SMALL"
    >
      <el-form>
        <el-form-item label="审核操作">
          <el-tag :type="auditStatus === 'approved' ? 'success' : 'danger'">
            {{ auditStatus === 'approved' ? '通过' : '拒绝' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="审核理由" required>
          <el-input v-model="auditComment" type="textarea" :rows="4" placeholder="请输入审核理由" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAudit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  PageHeader,
  SearchForm,
  DataTable,
  StatusTag,
  ActionButtons,
  ConfirmDialog
} from '@/components'
import { getSupplierList, auditSupplier, deleteSupplier } from '@/api/supplier'
import { useConfirm } from '@/composables'
import { debounce, formatDate, DIALOG_WIDTH } from '@/utils'

const router = useRouter()
const { confirmDelete } = useConfirm()

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  keyword: '',
  status: null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (searchForm.keyword) {
      params.keyword = searchForm.keyword.trim()
    }

    if (searchForm.status !== '' && searchForm.status !== null && searchForm.status !== undefined) {
      const statusNum = Number(searchForm.status)
      if (!isNaN(statusNum)) {
        params.status = statusNum
      }
    }

    const data = await getSupplierList(params)
    // 确保status字段是数字类型
    const items = (data.items || []).map(item => ({
      ...item,
      status: typeof item.status === 'number' ? item.status : Number(item.status) || 0
    }))
    tableData.value = items
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取供应商列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 防抖搜索函数
const debouncedSearch = debounce(() => {
  pagination.page = 1
  fetchData()
}, 500)

// 监听关键词变化，自动搜索
watch(
  () => searchForm.keyword,
  () => {
    debouncedSearch()
  }
)

// 监听状态变化，自动搜索
watch(
  () => searchForm.status,
  () => {
    pagination.page = 1
    fetchData()
  }
)

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.status = null
  pagination.page = 1
  fetchData()
}

const handleViewDetail = id => {
  router.push(`/supplier/detail/${id}`)
}

const currentAuditRow = ref(null)
const auditDialogVisible = ref(false)
const auditStatus = ref(null)
const auditComment = ref('')

const handleAudit = (row, status) => {
  currentAuditRow.value = row
  auditStatus.value = status
  auditComment.value = ''
  auditDialogVisible.value = true
}

const confirmAudit = async () => {
  if (!auditComment.value.trim()) {
    ElMessage.warning('请输入审核理由')
    return
  }

  try {
    const statusValue = auditStatus.value === 'approved' ? 1 : 0
    await auditSupplier(currentAuditRow.value.id, {
      status: statusValue,
      audit_comment: auditComment.value.trim()
    })
    ElMessage.success('审核成功')
    auditDialogVisible.value = false
    fetchData()
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail || error.response?.data?.message || error.message || '审核失败'
    ElMessage.error(errorMsg)
  }
}

// 删除供应商
const handleDelete = async id => {
  try {
    await confirmDelete('确定要删除该供应商吗？删除前请确保该供应商没有报价记录。')
    
    await deleteSupplier(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg =
        error?.response?.data?.detail || error?.response?.data?.message || error?.message || '删除失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 获取操作按钮配置
const getActionButtons = row => {
  const buttons = [
    {
      key: 'view',
      label: '查看详情',
      type: 'primary',
      size: 'small',
      handler: () => handleViewDetail(row.id)
    },
    {
      key: 'delete',
      label: '删除',
      type: 'danger',
      size: 'small',
      handler: () => handleDelete(row.id)
    }
  ]
  return buttons
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.supplier-list-container {
  min-height: 100%;
}

.keyword-input {
  width: 280px;
}
</style>
