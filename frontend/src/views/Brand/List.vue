<template>
  <div class="brand-list-container">
    <PageHeader title="品牌列表" subtitle="管理品牌信息">
      <template #extra>
        <el-button type="primary" @click="handleCreate">新增品牌</el-button>
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
      <el-table-column prop="brand_code" label="品牌编码" width="150" />
      <el-table-column prop="brand_name" label="品牌名称" min-width="200" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag :status="row.is_active ? 'active' : 'inactive'" />
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="150">
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
import { getBrandList, deleteBrand } from '@/api/brand'
import { useListPage } from '@/composables/useListPage'

const { loading, tableData, pagination, fetchData, handleCreate, handleEdit, handleDelete } =
  useListPage({
    fetchApi: getBrandList,
    deleteApi: deleteBrand,
    createRoute: '/brand/create',
    editRoute: id => `/brand/edit/${id}`,
    deleteConfirmText: '确定要删除该品牌吗？',
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

.brand-list-container {
  min-height: 100%;
}
</style>
