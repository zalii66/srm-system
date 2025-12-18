<template>
  <div class="role-list-container">
    <PageHeader title="角色管理" subtitle="管理系统角色信息">
      <template #extra>
        <el-button type="primary" @click="handleCreate">新增角色</el-button>
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
      <el-table-column prop="name" label="角色名称" width="150" />
      <el-table-column prop="code" label="角色编码" width="150" />
      <el-table-column prop="description" label="描述" min-width="200" />
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
import { getRoleList, deleteRole } from '@/api/role'
import { formatDate } from '@/utils'
import { useListPage } from '@/composables/useListPage'

const { loading, tableData, pagination, fetchData, handleCreate, handleEdit, handleDelete } =
  useListPage({
    fetchApi: getRoleList,
    deleteApi: deleteRole,
    createRoute: '/role/create',
    editRoute: id => `/role/edit/${id}`,
    deleteConfirmText: '确定要删除该角色吗？'
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

.role-list-container {
  min-height: 100%;
}
</style>
