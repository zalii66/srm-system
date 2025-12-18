<template>
  <div class="project-list-container">
    <PageHeader :title="isSupplier ? '我的项目' : '项目列表'" subtitle="查看和管理项目信息">
      <template #extra>
        <el-button v-if="!isSupplier" type="primary" @click="handleCreate">创建项目</el-button>
      </template>
    </PageHeader>

    <SearchForm v-model="searchForm" @search="fetchData" @reset="resetSearch">
      <el-form-item label="项目状态" class="status-select">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="已停止" :value="0" />
          <el-option label="进行中" :value="1" />
          <el-option label="竞标中" :value="3" />
          <el-option label="已完成" :value="4" />
          <el-option label="已取消" :value="5" />
        </el-select>
      </el-form-item>
      <el-form-item label="项目类别">
        <el-select
          v-model="searchForm.category_id"
          placeholder="全部"
          clearable
          filterable
          class="w-full"
        >
          <el-option
            v-for="category in categoryList"
            :key="category.id"
            :label="category.category_name"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
    </SearchForm>

    <DataTable
      :data="tableData"
      v-model:page="pagination.page"
      :loading="loading"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      @change="fetchData"
    >
      <el-table-column prop="project_no" label="项目编号" width="180" />
      <el-table-column prop="project_name" label="项目名称" min-width="200" />
      <el-table-column prop="category" label="项目类别" width="150">
        <template #default="{ row }">
          {{ row.category?.category_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag
            :status="typeof row.status === 'number' ? row.status : (row.status ?? 0)"
            status-type="project"
          />
        </template>
      </el-table-column>
      <el-table-column label="发布人" width="120">
        <template #default="{ row }">
          {{ row.creator?.full_name || row.creator?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="350" fixed="right">
        <template #default="{ row }">
          <ActionButtons :buttons="getActionButtons(row)" />
        </template>
      </el-table-column>
    </DataTable>

    <!-- 参与公司报价对话框 -->
    <el-dialog
      v-model="quotationDialogVisible"
      :title="`${currentProject?.project_name || ''} - 参与公司报价`"
      :width="DIALOG_WIDTH.XLARGE"
      :close-on-click-modal="false"
    >
      <el-table :data="quotationList" v-loading="quotationLoading" stripe border>
        <el-table-column prop="id" label="报价ID" width="80" />
        <el-table-column label="供应商" min-width="200">
          <template #default="{ row }">
            {{ row.supplier?.company_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="报价总金额" width="150">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="delivery_days" label="交货天数" width="100" />
        <el-table-column prop="payment_terms" label="付款条件" min-width="150" />
        <el-table-column prop="warranty_period" label="质保期" width="120" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <StatusTag :status="row.status || 'draft'" status-type="quotation" />
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.submitted_at || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <ActionButtons :buttons="getQuotationActionButtons(row)" />
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="quotationDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ElMessage,
  ElMessageBox,
  ElDialog,
  ElTable,
  ElTableColumn,
  ElButton,
  ElTag
} from 'element-plus'
import { PageHeader, SearchForm, DataTable, StatusTag, ActionButtons } from '@/components'
import { getProjectList, deleteProject } from '@/api/project'
import { getProjectQuotations } from '@/api/quotation'
import { getProjectCategoryList } from '@/api/projectCategory'
import { useUserStore } from '@/stores/user'
import { formatDate, formatCurrency, DIALOG_WIDTH } from '@/utils'

// getProjectQuotations 保留用于查看报价详情对话框

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const tableData = ref([])
const categoryList = ref([])
const quotationDialogVisible = ref(false)
const quotationLoading = ref(false)
const quotationList = ref([])
const currentProject = ref(null)

const isAdmin = computed(() => userStore.isSuperuser)
const isProjectManager = computed(() => {
  if (!userStore.roles || !Array.isArray(userStore.roles)) return false
  return userStore.roles.includes('project_manager')
})
const isSupplier = computed(() => {
  if (!userStore.roles || !Array.isArray(userStore.roles)) return false
  return userStore.roles.includes('supplier')
})

const searchForm = reactive({
  status: null,
  category_id: null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 监听搜索条件变化，自动搜索
watch(
  () => searchForm.status,
  () => {
    pagination.page = 1
    fetchData()
  }
)

// 监听项目类别变化，自动搜索
watch(
  () => searchForm.category_id,
  () => {
    pagination.page = 1
    fetchData()
  }
)

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (searchForm.status !== '' && searchForm.status !== null && searchForm.status !== undefined) {
      const statusNum = Number(searchForm.status)
      if (!isNaN(statusNum)) {
        params.status = statusNum
      }
    }

    if (
      searchForm.category_id !== null &&
      searchForm.category_id !== undefined &&
      searchForm.category_id !== ''
    ) {
      params.category_id = Number(searchForm.category_id)
    }

    const data = await getProjectList(params)
    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取项目列表失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取项目列表失败'
    ElMessage.error(errorMsg)
    // 如果是供应商且未审核通过，显示提示信息
    if (isSupplier.value && error.response?.status === 403) {
      ElMessage.warning('请先完成供应商资质审核后再查看项目')
    }
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.status = null
  searchForm.category_id = null
  pagination.page = 1
  fetchData()
}

const handleCreate = () => {
  router.push('/project/create')
}

const handleView = id => {
  router.push(`/project/detail/${id}`)
}

const handleEdit = id => {
  router.push(`/project/edit/${id}`)
}

const handleRequirements = id => {
  router.push(`/project/${id}/requirements`)
}

const handleViewQuotations = async project => {
  currentProject.value = project
  quotationDialogVisible.value = true
  quotationLoading.value = true
  quotationList.value = []

  try {
    const data = await getProjectQuotations(project.id, { page: 1, page_size: 100 })
    quotationList.value = data.items || []
  } catch (error) {
    console.error('获取报价列表失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取报价列表失败'
    ElMessage.error(errorMsg)
  } finally {
    quotationLoading.value = false
  }
}

const handleViewQuotationDetail = quotationId => {
  router.push(`/quotation/detail/${quotationId}`)
}

// 获取报价对话框中的操作按钮配置
const getQuotationActionButtons = row => [
  {
    key: 'view',
    label: '查看详情',
    type: 'primary',
    size: 'small',
    handler: () => handleViewQuotationDetail(row.id)
  }
]

// 获取操作按钮配置
const getActionButtons = row => {
  const buttons = [
    {
      key: 'view',
      label: '查看',
      type: 'primary',
      size: 'small',
      handler: () => handleView(row.id)
    }
  ]

  // 非供应商用户可以编辑和删除
  if (!isSupplier.value) {
    buttons.push({
      key: 'edit',
      label: '编辑',
      type: 'warning',
      size: 'small',
      handler: () => handleEdit(row.id)
    })

    buttons.push({
      key: 'delete',
      label: '删除',
      type: 'danger',
      size: 'small',
      handler: () => handleDelete(row)
    })
  }

  // 进行中或竞标中状态：显示需求报价和参与公司按钮
  if (row.status === 1 || row.status === 3) {
    buttons.push({
      key: 'requirements',
      label: '需求报价',
      type: 'success',
      size: 'small',
      handler: () => handleRequirements(row.id)
    })

    if (!isSupplier.value) {
      buttons.push({
        key: 'quotations',
        label: `参与公司(${row.quotation_count || 0})`,
        type: 'info',
        size: 'small',
        handler: () => handleViewQuotations(row)
      })
    }
  }

  return buttons
}

// 删除项目
const handleDelete = async row => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${row.project_name}"吗？此操作不可恢复！`,
      '删除项目',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteProject(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    console.error('删除项目失败:', error)
    const errorMsg =
      error.response?.data?.detail || error.response?.data?.message || error.message || '删除失败'
    ElMessage.error(errorMsg)
  }
}

const fetchCategoryList = async () => {
  try {
    const data = await getProjectCategoryList({ page: 1, page_size: 100, is_active: true })
    if (data && Array.isArray(data.items)) {
      categoryList.value = JSON.parse(JSON.stringify(data.items))
    } else {
      categoryList.value = []
    }
  } catch (error) {
    console.error('获取项目类别列表失败:', error)
    categoryList.value = []
  }
}

onMounted(() => {
  fetchCategoryList()
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.project-list-container {
  min-height: 100%;
}
</style>
