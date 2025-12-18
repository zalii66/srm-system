<template>
  <div class="role-form-container">
    <PageHeader :title="isEdit ? '编辑角色' : '新增角色'">
      <template #extra>
        <el-button @click="handleCancel">返回</el-button>
      </template>
    </PageHeader>

    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>

        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" placeholder="请输入角色编码" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入角色描述"
          />
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>

        <el-form-item label="权限分配" prop="permission_ids">
          <div class="permission-assignment">
            <!-- 权限分组 -->
            <div v-if="permissionsLoading" class="loading-container">
              <el-skeleton :rows="5" animated />
            </div>
            <div v-else-if="groupedPermissions.length === 0" class="empty-container">
              <el-empty description="暂无权限数据" />
            </div>
            <div v-else class="permission-groups">
              <!-- 全选控制 -->
              <div class="permission-header">
                <el-checkbox
                  :model-value="isAllSelected"
                  :indeterminate="isIndeterminate"
                  @change="handleSelectAll"
                >
                  <span class="header-text">全选</span>
                </el-checkbox>
                <span class="selected-count">
                  已选择 {{ form.permission_ids.length }} / {{ totalPermissions }} 项权限
                </span>
              </div>

              <!-- 分组列表 -->
              <div class="permission-groups-list">
                <div
                  v-for="group in groupedPermissions"
                  :key="group.resource"
                  class="permission-group"
                >
                  <div class="group-header">
                    <el-checkbox
                      :model-value="isGroupSelected(group.resource)"
                      :indeterminate="isGroupIndeterminate(group.resource)"
                      @change="handleGroupSelect(group.resource, $event)"
                    >
                      <span class="group-title">{{ getResourceName(group.resource) }}</span>
                    </el-checkbox>
                    <span class="group-count">
                      {{ getSelectedCountInGroup(group.resource) }} / {{ group.permissions.length }}
                    </span>
                  </div>
                  <div class="group-content">
                    <el-checkbox-group v-model="form.permission_ids" class="permission-checkboxes">
                      <el-checkbox
                        v-for="permission in group.permissions"
                        :key="permission.id"
                        :label="permission.id"
                        class="permission-checkbox"
                      >
                        <span class="permission-name">{{ permission.name }}</span>
                        <span class="permission-code">({{ permission.code }})</span>
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="form-tip">可多选，为空表示该角色无任何权限</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PageHeader } from '@/components'
import { createRole, updateRole, getRoleDetail } from '@/api/role'
import { getAllPermissions } from '@/api/permission'
import { useFormValidation } from '@/composables'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true,
  permission_ids: []
})

const permissionList = ref([])
const permissionsLoading = ref(false)

// 资源名称映射（可扩展）
const resourceNameMap = {
  project: '项目管理',
  quotation: '报价管理',
  supplier: '供应商管理',
  user: '用户管理',
  role: '角色管理',
  permission: '权限管理',
  company: '公司管理',
  brand: '品牌管理',
  dashboard: '仪表盘',
  project_category: '项目类别',
  product_library: '产品库',
  operation_log: '操作日志'
}

// 获取资源显示名称
const getResourceName = resource => {
  return resourceNameMap[resource] || resource
}

// 按资源分组权限
const groupedPermissions = computed(() => {
  if (!permissionList.value || permissionList.value.length === 0) {
    return []
  }

  const groups = {}
  permissionList.value.forEach(permission => {
    const resource = permission.resource || 'other'
    if (!groups[resource]) {
      groups[resource] = {
        resource,
        permissions: []
      }
    }
    groups[resource].permissions.push(permission)
  })

  // 转换为数组并排序
  return Object.values(groups).sort((a, b) => {
    // 按资源名称排序
    const nameA = getResourceName(a.resource)
    const nameB = getResourceName(b.resource)
    return nameA.localeCompare(nameB, 'zh-CN')
  })
})

// 总权限数
const totalPermissions = computed(() => {
  return permissionList.value.length
})

// 是否全选
const isAllSelected = computed(() => {
  return (
    totalPermissions.value > 0 &&
    form.permission_ids.length === totalPermissions.value
  )
})

// 是否部分选中（全选的不确定状态）
const isIndeterminate = computed(() => {
  return (
    form.permission_ids.length > 0 &&
    form.permission_ids.length < totalPermissions.value
  )
})

// 处理全选
const handleSelectAll = checked => {
  if (checked) {
    form.permission_ids = permissionList.value.map(p => p.id)
  } else {
    form.permission_ids = []
  }
}

// 检查组是否全选
const isGroupSelected = resource => {
  const group = groupedPermissions.value.find(g => g.resource === resource)
  if (!group) return false
  const groupPermissionIds = group.permissions.map(p => p.id)
  return (
    groupPermissionIds.length > 0 &&
    groupPermissionIds.every(id => form.permission_ids.includes(id))
  )
}

// 检查组是否部分选中
const isGroupIndeterminate = resource => {
  const group = groupedPermissions.value.find(g => g.resource === resource)
  if (!group) return false
  const groupPermissionIds = group.permissions.map(p => p.id)
  const selectedCount = groupPermissionIds.filter(id =>
    form.permission_ids.includes(id)
  ).length
  return selectedCount > 0 && selectedCount < groupPermissionIds.length
}

// 处理组选择
const handleGroupSelect = (resource, checked) => {
  const group = groupedPermissions.value.find(g => g.resource === resource)
  if (!group) return

  const groupPermissionIds = group.permissions.map(p => p.id)
  if (checked) {
    // 添加该组所有权限
    groupPermissionIds.forEach(id => {
      if (!form.permission_ids.includes(id)) {
        form.permission_ids.push(id)
      }
    })
  } else {
    // 移除该组所有权限
    form.permission_ids = form.permission_ids.filter(
      id => !groupPermissionIds.includes(id)
    )
  }
}

// 获取组内已选中的数量
const getSelectedCountInGroup = resource => {
  const group = groupedPermissions.value.find(g => g.resource === resource)
  if (!group) return 0
  const groupPermissionIds = group.permissions.map(p => p.id)
  return groupPermissionIds.filter(id => form.permission_ids.includes(id)).length
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在2到50个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 2, max: 50, message: '角色编码长度在2到50个字符', trigger: 'blur' }
  ]
}

const fetchPermissions = async () => {
  permissionsLoading.value = true
  try {
    const data = await getAllPermissions()
    permissionList.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取权限列表失败:', error)
    ElMessage.error('获取权限列表失败')
    permissionList.value = []
  } finally {
    permissionsLoading.value = false
  }
}

const fetchData = async () => {
  if (!isEdit.value) {
    // 新增时也要加载权限列表
    await fetchPermissions()
    return
  }

  loading.value = true
  try {
    const data = await getRoleDetail(route.params.id)
    if (data && typeof data === 'object') {
      form.name = data.name || ''
      form.code = data.code || ''
      form.description = data.description || ''
      form.is_active = data.is_active !== false
      // 设置权限ID列表
      if (data.permissions && Array.isArray(data.permissions)) {
        form.permission_ids = data.permissions.map(p => p.id)
      } else {
        form.permission_ids = []
      }
    } else {
      ElMessage.error('获取的角色数据格式不正确')
    }
  } catch (error) {
    console.error('获取角色信息失败:', error)
    // 从错误对象中提取详细信息
    let errorMsg = '获取角色信息失败'
    if (error.response) {
      errorMsg = error.response.data?.detail || error.response.data?.message || errorMsg
    } else if (error.message) {
      errorMsg = error.message
    }
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        // 构建提交数据，包含权限ID列表
        const submitData = {
          name: form.name,
          code: form.code,
          description: form.description,
          is_active: form.is_active,
          permission_ids: form.permission_ids || []
        }

        if (isEdit.value) {
          await updateRole(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createRole(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/roles')
      } catch (error) {
        handleSubmitError(error, form, isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
      }
    } else {
      handleFrontendValidationError()
    }
  })
}

const handleCancel = () => {
  router.push('/roles')
}

onMounted(async () => {
  await fetchPermissions()
  await fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.role-form-container {
  min-height: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.permission-assignment {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;

  .loading-container,
  .empty-container {
    padding: 40px 0;
    text-align: center;
  }

  .permission-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;
    margin-bottom: 16px;

    .header-text {
      font-weight: 600;
      font-size: 14px;
      color: #303133;
    }

    .selected-count {
      font-size: 12px;
      color: #909399;
    }
  }

  .permission-groups-list {
    .permission-group {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .group-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 12px;
        background-color: #f5f7fa;
        border-radius: 4px;
        margin-bottom: 12px;

        .group-title {
          font-weight: 500;
          font-size: 14px;
          color: #303133;
          margin-left: 8px;
        }

        .group-count {
          font-size: 12px;
          color: #909399;
        }
      }

      .group-content {
        padding: 0 12px;

        .permission-checkboxes {
          display: flex;
          flex-direction: column;
          gap: 12px;

          .permission-checkbox {
            display: flex;
            align-items: center;
            padding: 8px;
            border-radius: 4px;
            transition: background-color 0.2s;

            &:hover {
              background-color: #f5f7fa;
            }

            .permission-name {
              font-size: 14px;
              color: #606266;
              margin-right: 8px;
            }

            .permission-code {
              font-size: 12px;
              color: #909399;
            }
          }
        }
      }
    }
  }
}

// 滚动条样式
.permission-assignment::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.permission-assignment::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;

  &:hover {
    background-color: #a8a8a8;
  }
}

.permission-assignment::-webkit-scrollbar-track {
  background-color: #f1f1f1;
  border-radius: 3px;
}
</style>
