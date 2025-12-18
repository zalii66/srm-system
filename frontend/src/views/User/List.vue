<template>
  <div class="user-list-container">
    <PageHeader title="用户管理" subtitle="管理系统用户信息">
      <template #extra>
        <el-button type="primary" @click="handleCreate">新增用户</el-button>
      </template>
    </PageHeader>

    <SearchForm v-model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="搜索关键词">
        <el-input
          v-model="searchForm.keyword"
          placeholder="请输入姓名、手机号、邮箱或用户名"
          clearable
          class="keyword-input"
        />
      </el-form-item>
      <el-form-item label="状态" class="status-select">
        <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
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
      <el-table-column prop="full_name" label="姓名" width="260" />
      <el-table-column prop="email" label="邮箱" width="220" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="is_superuser" label="管理员" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_superuser ? 'danger' : 'info'">
            {{ row.is_superuser ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="roles" label="角色" width="120">
        <template #default="{ row }">
          <el-tag v-for="role in row.roles" :key="role.id" class="role-tag" size="small">
            {{ role.name }}
          </el-tag>
          <span v-if="!row.roles || row.roles.length === 0" class="text-secondary">无</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="90">
        <template #default="{ row }">
          <StatusTag :status="row.is_active ? 'active' : 'inactive'" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <ActionButtons :buttons="getActionButtons(row)" />
        </template>
      </el-table-column>
    </DataTable>
  </div>
</template>

<script setup>
import { reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { PageHeader, DataTable, StatusTag, ActionButtons, SearchForm } from '@/components'
import { getUserList, deleteUser } from '@/api/user'
import { formatDate, debounce } from '@/utils'
import { useListPage } from '@/composables/useListPage'
import { useConfirm } from '@/composables'
import { useErrorHandler } from '@/composables'

const { loading, tableData, pagination, fetchData: baseFetchData, handleCreate, handleEdit } =
  useListPage({
    fetchApi: getUserList,
    deleteApi: deleteUser,
    createRoute: '/user/create',
    editRoute: id => `/user/edit/${id}`,
    deleteConfirmText: '确定要删除该用户吗？',
    showErrorMessage: false // 禁用自动错误处理，我们自己处理
  })

const { confirmDelete } = useConfirm()
const { handleApiError } = useErrorHandler()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  is_active: null
})

// 获取数据（包含搜索条件）
const fetchData = async () => {
  const params = {}
  
  if (searchForm.keyword) {
    params.keyword = searchForm.keyword.trim()
  }
  
  if (searchForm.is_active !== null && searchForm.is_active !== undefined) {
    params.is_active = searchForm.is_active
  }
  
  await baseFetchData(params)
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.is_active = null
  pagination.page = 1
  fetchData()
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
  () => searchForm.is_active,
  () => {
    pagination.page = 1
    fetchData()
  }
)

// 删除用户（使用带搜索条件的刷新）
const handleDeleteUser = async id => {
  try {
    await confirmDelete('确定要删除该用户吗？')
    await deleteUser(id)
    ElMessage.success('删除成功')
    // 使用带搜索条件的fetchData刷新
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      handleApiError(error, '删除失败')
    }
  }
}

const getActionButtons = row => [
  {
    key: 'edit',
    label: '编辑',
    type: 'primary',
    size: 'small',
    handler: () => handleEdit(row.id)
  },
  {
    key: 'delete',
    label: '删除',
    type: 'danger',
    size: 'small',
    handler: () => handleDeleteUser(row.id)
  }
]

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.user-list-container {
  min-height: 100%;
}

.role-tag {
  margin-right: $spacing-xs;
}
</style>
