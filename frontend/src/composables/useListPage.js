/**
 * 列表页面通用逻辑 Composable
 * 提供统一的数据获取、分页、删除等功能
 *
 * @param {Object} config - 配置对象
 * @param {Function} config.fetchApi - 获取列表数据的API函数
 * @param {Function} config.deleteApi - 删除数据的API函数
 * @param {string} config.createRoute - 创建页面的路由路径
 * @param {Function|string} config.editRoute - 编辑页面的路由路径或函数，函数接收id参数
 * @param {string} config.deleteConfirmText - 删除确认提示文本
 * @param {boolean} config.showErrorMessage - 是否显示错误消息，默认true
 * @returns {Object} 返回列表页所需的响应式数据和方法
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useConfirm } from './useConfirm'
import { useErrorHandler } from './useErrorHandler'

export function useListPage(config) {
  const {
    fetchApi,
    deleteApi,
    createRoute,
    editRoute,
    deleteConfirmText = '确定要删除该项吗？',
    showErrorMessage = true
  } = config

  const router = useRouter()
  const { confirmDelete } = useConfirm()
  const { handleApiError } = useErrorHandler()
  const loading = ref(false)
  const tableData = ref([])

  const pagination = reactive({
    page: 1,
    pageSize: 10,
    total: 0
  })

  /**
   * 获取列表数据
   * @param {Object} params - 额外的查询参数
   */
  const fetchData = async (params = {}) => {
    loading.value = true
    try {
      const data = await fetchApi({
        page: pagination.page,
        page_size: pagination.pageSize,
        ...params
      })
      tableData.value = data.items || []
      pagination.total = data.total || 0
    } catch (error) {
      if (showErrorMessage) {
        handleApiError(error, '获取数据失败')
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 跳转到创建页面
   */
  const handleCreate = () => {
    router.push(createRoute)
  }

  /**
   * 跳转到编辑页面
   * @param {number|string} id - 记录ID
   */
  const handleEdit = id => {
    const route = typeof editRoute === 'function' ? editRoute(id) : `${editRoute}/${id}`
    router.push(route)
  }

  /**
   * 删除记录
   * @param {number|string} id - 记录ID
   * @param {Object} options - 选项
   * @param {string} options.confirmText - 自定义确认文本
   * @param {Function} options.onSuccess - 删除成功回调
   * @param {Function} options.onError - 删除失败回调
   */
  const handleDelete = async (id, options = {}) => {
    const { confirmText = deleteConfirmText, onSuccess, onError } = options

    try {
      await confirmDelete(confirmText)

      await deleteApi(id)
      ElMessage.success('删除成功')

      // 删除成功后刷新数据
      await fetchData()

      // 执行成功回调
      if (onSuccess) {
        onSuccess(id)
      }
    } catch (error) {
      if (error !== 'cancel') {
        handleApiError(error, '删除失败')

        // 执行失败回调
        if (onError) {
          onError(error, id)
        }
      }
    }
  }

  /**
   * 重置分页并刷新数据
   * @param {Object} params - 额外的查询参数
   */
  const resetAndFetch = async (params = {}) => {
    pagination.page = 1
    await fetchData(params)
  }

  return {
    loading,
    tableData,
    pagination,
    fetchData,
    handleCreate,
    handleEdit,
    handleDelete,
    resetAndFetch
  }
}
