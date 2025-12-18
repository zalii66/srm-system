<template>
  <div class="operation-log-list-container">
    <PageHeader title="操作日志" subtitle="查看系统操作记录">
      <template #extra>
        <el-button type="warning" @click="handleCleanup">清理旧日志</el-button>
      </template>
    </PageHeader>

    <SearchForm v-model="searchForm" @search="handleSearch" @reset="handleReset">
      <el-form-item label="操作类型">
        <el-select v-model="searchForm.action" placeholder="全部" clearable>
          <el-option label="创建" value="create" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="审核" value="audit" />
          <el-option label="评审" value="evaluate" />
          <el-option label="提交" value="submit" />
          <el-option label="取消" value="cancel" />
        </el-select>
      </el-form-item>
      <el-form-item label="时间范围">
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          @change="handleDateRangeChange"
        />
      </el-form-item>
    </SearchForm>

    <DataTable
      v-model:page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      @change="handlePageChange"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="操作用户" width="120" />
      <el-table-column prop="action" label="操作类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getActionTagType(row.action)" size="small">
            {{ getActionText(row.action) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="resource_type" label="资源类型" width="100">
        <template #default="{ row }">
          {{ getResourceTypeText(row.resource_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="resource_name" label="资源名称" width="200" show-overflow-tooltip />
      <el-table-column prop="description" label="操作描述" min-width="250" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP地址" width="140" />
      <el-table-column prop="created_at" label="操作时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="80">
        <template #default="{ row }">
          <ActionButtons :buttons="getActionButtons(row)" />
        </template>
      </el-table-column>
    </DataTable>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="操作日志详情" :width="DIALOG_WIDTH.LARGE">
      <el-descriptions :column="2" border v-if="detailData">
        <el-descriptions-item label="操作ID">{{ detailData.id }}</el-descriptions-item>
        <el-descriptions-item label="操作用户">{{ detailData.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">{{ getActionText(detailData.action) }}</el-descriptions-item>
        <el-descriptions-item label="资源类型">{{ getResourceTypeText(detailData.resource_type) }}</el-descriptions-item>
        <el-descriptions-item label="资源ID">{{ detailData.resource_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="资源名称">{{ detailData.resource_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作描述" :span="2">{{ detailData.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ detailData.ip_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ detailData.request_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="请求路径" :span="2">{{ detailData.request_path || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作时间" :span="2">{{ formatDate(detailData.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="旧值" :span="2" v-if="detailData.old_value">
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">{{ formatJson(detailData.old_value) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="新值" :span="2" v-if="detailData.new_value">
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">{{ formatJson(detailData.new_value) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 清理日志对话框 -->
    <el-dialog v-model="cleanupDialogVisible" title="清理旧日志" :width="DIALOG_WIDTH.SMALL">
      <el-form :model="cleanupForm" label-width="100px">
        <el-form-item label="保留天数">
          <el-input-number v-model="cleanupForm.days" :min="1" :max="365" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">将删除指定天数之前的所有日志</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cleanupDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="confirmCleanup">确定清理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { PageHeader, DataTable, SearchForm, ActionButtons } from '@/components'
import { getOperationLogs, getOperationLog, cleanupOldLogs } from '@/api/operationLog'
import { formatDate, DIALOG_WIDTH, debounce } from '@/utils'
import { ElMessage } from 'element-plus'
import { useListPage } from '@/composables/useListPage'

// 搜索表单
const searchForm = reactive({
  action: '',
  start_date: '',
  end_date: ''
})

const dateRange = ref(null)

// 处理搜索参数的函数
const buildSearchParams = () => {
  const params = {
    ...searchForm
  }
  // 移除空值
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === null || params[key] === undefined) {
      delete params[key]
    }
  })
  return params
}

// 使用统一的列表页面工具类
const { loading, tableData, pagination, fetchData, resetAndFetch } = useListPage({
  fetchApi: async (params) => {
    // 合并搜索参数
    const queryParams = {
      ...params,
      ...buildSearchParams()
    }
    return await getOperationLogs(queryParams)
  },
  deleteApi: null, // 操作日志不需要删除功能
  createRoute: null, // 操作日志不需要创建功能
  editRoute: null, // 操作日志不需要编辑功能
  showErrorMessage: true
})

const detailDialogVisible = ref(false)
const detailData = ref(null)

const cleanupDialogVisible = ref(false)
const cleanupForm = reactive({
  days: 90
})

// 搜索处理 - 使用统一的工具方法
const handleSearch = () => {
  resetAndFetch()
}

// 重置搜索 - 使用统一的工具方法
const handleReset = () => {
  searchForm.action = ''
  searchForm.start_date = ''
  searchForm.end_date = ''
  dateRange.value = null
  resetAndFetch()
}

// 分页变化处理
const handlePageChange = () => {
  fetchData(buildSearchParams())
}

// 获取操作按钮配置
const getActionButtons = row => [
  {
    key: 'view',
    label: '查看详情',
    type: 'primary',
    size: 'small',
    handler: () => handleViewDetail(row)
  }
]

// 处理日期范围变化（同步到 searchForm）
const handleDateRangeChange = (value) => {
  if (value && value.length === 2) {
    searchForm.start_date = value[0]
    searchForm.end_date = value[1]
  } else {
    searchForm.start_date = ''
    searchForm.end_date = ''
  }
}

const handleViewDetail = async (row) => {
  try {
    const response = await getOperationLog(row.id)
    detailData.value = response
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取日志详情失败:', error)
    ElMessage.error('获取日志详情失败')
  }
}

const handleCleanup = () => {
  cleanupDialogVisible.value = true
}

const confirmCleanup = async () => {
  try {
    await cleanupOldLogs(cleanupForm.days)
    ElMessage.success('清理完成')
    cleanupDialogVisible.value = false
    resetAndFetch()
  } catch (error) {
    console.error('清理日志失败:', error)
    ElMessage.error('清理日志失败')
  }
}

const getActionText = (action) => {
  const map = {
    create: '创建',
    update: '更新',
    delete: '删除',
    audit: '审核',
    evaluate: '评审',
    submit: '提交',
    cancel: '取消'
  }
  return map[action] || action
}

const getActionTagType = (action) => {
  const map = {
    create: 'success',
    update: 'primary',
    delete: 'danger',
    audit: 'warning',
    evaluate: 'info',
    submit: 'success',
    cancel: 'info'
  }
  return map[action] || ''
}

const getResourceTypeText = (resourceType) => {
  const map = {
    project: '项目',
    quotation: '报价',
    supplier: '供应商',
    user: '用户',
    role: '角色',
    permission: '权限'
  }
  return map[resourceType] || resourceType
}

const formatJson = (value) => {
  if (typeof value === 'string') {
    try {
      return JSON.stringify(JSON.parse(value), null, 2)
    } catch {
      return value
    }
  }
  return JSON.stringify(value, null, 2)
}

// 监听日期范围变化，同步到 searchForm
watch(
  dateRange,
  (newValue) => {
    handleDateRangeChange(newValue)
  },
  { deep: true }
)

// 防抖搜索函数 - 统一使用工具函数
const debouncedSearch = debounce(() => {
  pagination.page = 1
  fetchData(buildSearchParams())
}, 300)

// 监听操作类型变化，自动搜索（下拉框选择后立即搜索）
watch(
  () => searchForm.action,
  () => {
    pagination.page = 1
    fetchData(buildSearchParams())
  }
)

// 监听时间范围变化，自动搜索（防抖处理，避免频繁请求）
watch(
  () => [searchForm.start_date, searchForm.end_date],
  () => {
    debouncedSearch()
  },
  { deep: true }
)

onMounted(() => {
  // 页面加载时自动获取数据
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.operation-log-list-container {
  min-height: 100%;
}
</style>

