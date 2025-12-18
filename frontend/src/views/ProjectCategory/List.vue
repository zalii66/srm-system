<template>
  <div class="category-list-container">
    <PageHeader title="项目类别列表" subtitle="管理项目类别信息">
      <template #extra>
        <el-button type="primary" @click="handleCreate">新增类别</el-button>
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
      <el-table-column prop="category_code" label="类别编码" width="150" />
      <el-table-column prop="category_name" label="类别名称" min-width="200" />
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
import { getProjectCategoryList, deleteProjectCategory } from '@/api/projectCategory'
import { useListPage } from '@/composables/useListPage'

const { loading, tableData, pagination, fetchData, handleCreate, handleEdit, handleDelete } =
  useListPage({
    fetchApi: getProjectCategoryList,
    deleteApi: deleteProjectCategory,
    createRoute: '/project-category/create',
    editRoute: id => `/project-category/edit/${id}`,
    deleteConfirmText: '确定要删除该项目类别吗？删除前请确保没有项目使用此类别。'
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

.category-list-container {
  min-height: 100%;
}
</style>

