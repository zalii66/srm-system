<template>
  <div class="company-list-container">
    <PageHeader title="公司列表" subtitle="管理公司信息">
      <template #extra>
        <el-button type="primary" @click="handleCreate">新增公司</el-button>
      </template>
    </PageHeader>

    <DataTable
      v-model:page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      @change="fetchData"
    >
      <el-table-column prop="company_code" label="公司编码" width="150" />
      <el-table-column prop="company_name" label="公司名称" min-width="200" />
      <el-table-column label="所属品牌" width="150">
        <template #default="{ row }">
          {{ row.brand?.brand_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag :status="row.is_active ? 'active' : 'inactive'" />
        </template>
      </el-table-column>
      <el-table-column label="操作"  fixed="right">
        <template #default="{ row }">
          <ActionButtons :buttons="getActionButtons(row)" />
        </template>
      </el-table-column>
    </DataTable>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { PageHeader, DataTable, StatusTag, ActionButtons } from '@/components'
import { getCompanyList, deleteCompany } from '@/api/company'
import { useListPage } from '@/composables/useListPage'

const { loading, tableData, pagination, fetchData, handleCreate, handleEdit, handleDelete } =
  useListPage({
    fetchApi: getCompanyList,
    deleteApi: deleteCompany,
    createRoute: '/company/create',
    editRoute: id => `/company/edit/${id}`,
    deleteConfirmText: '确定要删除该公司吗？',
    showErrorMessage: false
  })

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
    handler: () => handleDelete(row.id)
  }
]

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.company-list-container {
  min-height: 100%;
}
</style>
