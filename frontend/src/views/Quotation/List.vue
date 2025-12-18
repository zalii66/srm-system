<template>
  <div class="quotation-list-container">
    <PageHeader :title="isSupplier ? '我的报价' : '报价列表'" />

    <SearchForm v-model="searchForm" @search="fetchData" @reset="resetSearch">
      <el-form-item label="报价状态" class="status-select">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="草稿" value="draft" />
          <el-option label="已提交" value="submitted" />
          <el-option label="中标" value="selected" />
          <el-option label="未中标" value="rejected" />
          <el-option label="已取消" value="cancelled" />
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
      <el-table-column prop="project" label="项目名称" min-width="200">
        <template #default="{ row }">
          {{ row.project?.project_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="总金额" width="150">
        <template #default="{ row }">
          {{ formatCurrency(row.total_amount || 0) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag :status="row.status || 'draft'" status-type="quotation" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作"  fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleView(row.id)">查看</el-button>
        </template>
      </el-table-column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PageHeader, SearchForm, DataTable, StatusTag } from '@/components'
import { getQuotationList, getMyQuotations } from '@/api/quotation'
import { useUserStore } from '@/stores/user'
import { formatDate, formatCurrency } from '@/utils'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const tableData = ref([])

const isSupplier = computed(() => {
  return userStore.roles?.includes('supplier') || false
})

const searchForm = reactive({
  status: ''
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

    if (searchForm.status) {
      params.status = searchForm.status
    }

    // 供应商使用 /quotations/my 接口，其他用户使用 /quotations/ 接口
    let data
    if (isSupplier.value) {
      data = await getMyQuotations(params)
    } else {
      // 非供应商用户需要提供 project_id，如果没有则使用空列表
      data = await getQuotationList(params).catch(() => {
        return { items: [], total: 0 }
      })
    }

    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取报价列表失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取报价列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.status = ''
  pagination.page = 1
  fetchData()
}

const handleView = id => {
  router.push(`/quotation/detail/${id}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.quotation-list-container {
  min-height: 100%;
}
</style>
