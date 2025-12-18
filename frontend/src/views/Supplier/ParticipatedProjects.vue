<template>
  <div class="participated-projects-container">
    <PageHeader title="参与项目" subtitle="查看我已参与的项目" />

    <SearchForm v-model="searchForm" @search="fetchData" @reset="resetSearch">
      <el-form-item label="项目名称">
        <el-input v-model="searchForm.project_name" placeholder="请输入项目名称" clearable />
      </el-form-item>
      <el-form-item label="报价状态" class="status-select">
        <el-select v-model="searchForm.quotation_status" placeholder="全部" clearable>
          <el-option label="草稿" value="draft" />
          <el-option label="已提交" value="submitted" />
          <el-option label="已中标" value="selected" />
          <el-option label="未中标" value="rejected" />
        </el-select>
      </el-form-item>
    </SearchForm>

    <el-card class="table-card">
      <DataTable
        v-model:page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :data="tableData"
        :loading="loading"
        :total="pagination.total"
        @change="fetchData"
      >
        <el-table-column prop="project_no" label="项目编号" width="180" />
        <el-table-column prop="project_name" label="项目名称" min-width="200" />
        <el-table-column prop="company_name" label="所属公司" width="150" />
        <el-table-column prop="quotation_amount" label="报价金额" width="150">
          <template #default="{ row }">
            <span v-if="row.quotation_amount">
              {{ formatCurrency(row.quotation_amount) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="quotation_status" label="报价状态" width="120">
          <template #default="{ row }">
            <StatusTag :status="row.quotation_status || 'draft'" status-type="quotation" />
          </template>
        </el-table-column>
        <el-table-column prop="is_winner" label="是否中标" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_winner ? 'success' : 'info'">
              {{ row.is_winner ? '中标' : '未中标' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="participated_at" label="参与时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.participated_at || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewProject(row.project_id)">
              查看项目
            </el-button>
            <el-button
              v-if="row.quotation_id"
              type="success"
              size="small"
              @click="handleViewQuotation(row.quotation_id)"
            >
              查看报价
            </el-button>
          </template>
        </el-table-column>
      </DataTable>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PageHeader, SearchForm, DataTable, StatusTag } from '@/components'
import { getSupplierProjects } from '@/api/supplier'
import { formatDate, formatCurrency } from '@/utils'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  project_name: '',
  quotation_status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    // 先获取当前供应商ID（从用户信息中获取）
    const supplierId = await getSupplierId()
    if (!supplierId) {
      ElMessage.error('无法获取供应商信息')
      return
    }

    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const data = await getSupplierProjects(supplierId, params)
    let projects = data.items || []

    // 前端过滤
    if (searchForm.project_name) {
      projects = projects.filter(p =>
        p.project_name?.toLowerCase().includes(searchForm.project_name.toLowerCase())
      )
    }

    if (searchForm.quotation_status) {
      // 这里需要根据报价状态过滤，但需要从报价表中获取状态
      // 暂时不过滤，后续可以优化
    }

    // 获取报价信息并合并
    const projectsWithQuotation = await enrichProjectsWithQuotation(projects)

    tableData.value = projectsWithQuotation
    pagination.total = searchForm.project_name ? projectsWithQuotation.length : data.total || 0
  } catch (error) {
    console.error('获取参与项目失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取参与项目失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const getSupplierId = async () => {
  // 从当前用户信息中获取供应商ID
  try {
    const { getCurrentSupplier } = await import('@/api/supplier')
    const data = await getCurrentSupplier()
    return data?.id
  } catch (error) {
    console.error('获取供应商ID失败:', error)
    return null
  }
}

const enrichProjectsWithQuotation = async projects => {
  // 获取报价信息并合并到项目数据中
  try {
    const { getMyQuotations } = await import('@/api/quotation')
    // 后端限制最大page_size为100，需要分页获取
    const quotationData = await getMyQuotations({ page: 1, page_size: 100 })
    const quotations = quotationData.items || []

    return projects.map(project => {
      const quotation = quotations.find(q => q.project_id === project.project_id)
      return {
        ...project,
        quotation_id: quotation?.id,
        quotation_amount: quotation?.total_amount,
        quotation_status: quotation?.status,
        is_winner: quotation?.status === 'selected' || project.is_winner === 1
      }
    })
  } catch {
    return projects
  }
}

const resetSearch = () => {
  searchForm.project_name = ''
  searchForm.quotation_status = ''
  pagination.page = 1
  fetchData()
}

const handleViewProject = projectId => {
  router.push(`/project/detail/${projectId}`)
}

const handleViewQuotation = quotationId => {
  router.push(`/quotation/detail/${quotationId}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.participated-projects-container {
  min-height: 100%;
}
</style>
