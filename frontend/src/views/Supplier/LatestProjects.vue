<template>
  <div class="latest-projects-container">
    <PageHeader title="最新项目" subtitle="查看可参与的最新项目" />

    <SearchForm v-model="searchForm" @search="fetchData" @reset="resetSearch">
      <el-form-item label="项目名称">
        <el-input v-model="searchForm.project_name" placeholder="请输入项目名称" clearable />
      </el-form-item>
    </SearchForm>

    <DataTable
      :data="tableData"
      :loading="loading"
      :page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      @update:page="
        val => {
          pagination.value.page = val
        }
      "
      @update:page-size="
        val => {
          pagination.value.pageSize = val
        }
      "
      @change="fetchData"
    >
      <el-table-column prop="project_no" label="项目编号" width="180" />
      <el-table-column prop="project_name" label="项目名称" min-width="200" />
      <el-table-column prop="category" label="项目类别" width="120">
        <template #default="{ row }">
          {{ row.category?.category_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="bidding_deadline" label="投标截止时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.bidding_deadline) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="发布时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleView(row.id)">查看详情</el-button>
          <el-button
            type="success"
            size="small"
            :disabled="!canQuote"
            @click="handleQuotation(row.id)"
          >
            参与报价
          </el-button>
        </template>
      </el-table-column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated, computed, toRaw, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PageHeader, SearchForm, DataTable } from '@/components'
import { getProjectList } from '@/api/project'
import { getCurrentSupplier } from '@/api/supplier'
import { useUserStore } from '@/stores/user'
import { SupplierStatus } from '@/utils/constants.js'
import { formatDate } from '@/utils'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const tableData = ref([])
const supplierInfo = ref(null)

const searchForm = reactive({
  project_name: ''
})

// 使用 ref 而不是 reactive，避免 v-model 绑定问题
const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const canQuote = computed(() => {
  if (!supplierInfo.value) return false
  // 支持数字和字符串格式的状态值
  const status = typeof supplierInfo.value.status === 'number' 
    ? supplierInfo.value.status 
    : Number(supplierInfo.value.status)
  return status === SupplierStatus.APPROVED // 1 = 审核通过
})

const fetchSupplierInfo = async () => {
  try {
    const data = await getCurrentSupplier()
    supplierInfo.value = data
  } catch (error) {
    console.error('获取供应商信息失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize
      // 供应商角色会自动获取已发布的项目，不需要传status参数
    }

    const data = await getProjectList(params)
    let projects = data.items || []

    // 确保 projects 是纯数组，移除任何可能的响应式代理
    // 使用 JSON 序列化/反序列化来彻底移除 Proxy
    projects = Array.isArray(projects) ? JSON.parse(JSON.stringify(projects)) : []

    // 前端过滤项目名称（如果后端不支持搜索）
    if (searchForm.project_name) {
      projects = projects.filter(p =>
        p.project_name?.toLowerCase().includes(searchForm.project_name.toLowerCase())
      )
      // 搜索时使用过滤后的数据
      pagination.value.total = projects.length
    } else {
      // 没有搜索条件时使用后端返回的总数
      pagination.value.total = data.total || 0
    }

    // 确保数据正确赋值，已经是纯对象数组，不需要再次map
    tableData.value = projects

    // 使用 nextTick 确保 DOM 更新完成
    await nextTick()
  } catch (error) {
    console.error('获取项目列表失败:', error)
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取项目列表失败'
    ElMessage.error(errorMsg)
    tableData.value = []
    pagination.value.total = 0
    if (!canQuote.value && error.response?.status !== 403) {
      ElMessage.warning('请先完成供应商资质审核后再参与报价')
    }
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.project_name = ''
  pagination.value.page = 1
  fetchData()
}

const handleView = id => {
  router.push(`/project/detail/${id}`)
}

const handleQuotation = id => {
  if (!canQuote.value) {
    ElMessage.warning('请先完成供应商资质审核后再参与报价')
    router.push('/supplier/profile')
    return
  }
  router.push(`/project/${id}/requirements`)
}

onMounted(() => {
  fetchSupplierInfo()
  fetchData()
})

// 页面激活时刷新数据（从其他页面返回时）
onActivated(() => {
  // 延迟执行，确保组件已完全激活
  nextTick(() => {
    // 如果数据为空或总数异常，重新获取
    if (tableData.value.length === 0 || pagination.value.total === 0) {
      fetchData()
    }
  })
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.latest-projects-container {
  min-height: 100%;
}
</style>
