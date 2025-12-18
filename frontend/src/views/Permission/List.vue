<template>
  <div class="permission-list-container">
    <PageHeader title="权限管理" subtitle="管理系统权限信息">
      <template #extra>
        <el-button type="primary" @click="handleCreate">新增权限</el-button>
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
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="权限名称" width="150" />
      <el-table-column prop="code" label="权限编码" width="150" />
      <el-table-column prop="resource" label="资源" width="100" />
      <el-table-column prop="action" label="操作" width="100" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag :status="row.is_active ? 'active' : 'inactive'" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
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
import { getPermissionList, deletePermission } from '@/api/permission'
import { formatDate } from '@/utils'
import { useListPage } from '@/composables/useListPage'

const { loading, tableData, pagination, fetchData, handleCreate, handleEdit, handleDelete } =
  useListPage({
    fetchApi: getPermissionList,
    deleteApi: deletePermission,
    createRoute: '/permission/create',
    editRoute: id => `/permission/edit/${id}`,
    deleteConfirmText: '确定要删除该权限吗？删除前请确保没有角色使用此权限。'
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

.permission-list-container {
  min-height: 100%;
}
</style>

