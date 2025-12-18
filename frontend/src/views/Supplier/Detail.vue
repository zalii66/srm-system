<template>
  <div class="supplier-detail-container">
    <PageHeader :title="supplierData.company_name || '供应商详情'" subtitle="查看供应商详细信息">
      <template #extra>
        <el-button @click="handleGoBack">返回</el-button>
      </template>
    </PageHeader>

    <el-card v-loading="loading" class="info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <StatusTag :status="supplierData.status ?? 0" status-type="supplier" />
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="公司名称" :span="1">
          {{ supplierData.company_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="公司税号" :span="1">
          {{ supplierData.tax_number || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="注册地址" :span="2">
          {{ supplierData.company_address || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="主营产品" :span="2">
          {{ supplierData.business_scope || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="联系人" :span="1">
          {{ supplierData.contact_person || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="联系电话" :span="1">
          {{ supplierData.contact_phone || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="审核状态" :span="2">
          <div class="audit-status-wrapper">
            <StatusTag :status="supplierData.status ?? 0" status-type="supplier" />
            <template v-if="isAdmin && (supplierData.status === -1 || supplierData.status === 0)">
              <div class="audit-buttons">
                <el-button type="success" size="small" @click="handleAudit('approved')">通过</el-button>
                <el-button type="danger" size="small" @click="handleAudit('rejected')">拒绝</el-button>
              </div>
              <span v-if="supplierData.audit_comment" class="audit-comment-text">
                {{ supplierData.audit_comment }}
              </span>
            </template>
            <span v-else-if="supplierData.audit_comment" class="audit-comment-text">
              {{ supplierData.audit_comment }}
            </span>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间" :span="2">
          {{ formatDate(supplierData.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card v-if="qualificationFiles.length > 0" class="qualification-card">
      <template #header>
        <span>资质文件</span>
      </template>

      <div class="file-list">
        <div v-for="(file, index) in qualificationFiles" :key="index" class="file-card">
          <div class="file-preview">
            <el-image
              v-if="isImageFile(file)"
              :key="`image-${index}-${imageUrlCache[getCacheKey(file, index)] ? 'cached' : 'placeholder'}`"
              :src="getFileUrl(file, index)"
              :preview-src-list="getImagePreviewList()"
              :initial-index="getImageIndex(index)"
              fit="cover"
              class="file-image"
              :lazy="true"
              preview-teleported
              @load="handleImageLoad(file, index)"
            />
            <div v-else class="file-icon-wrapper">
              <el-icon class="file-icon"><Document /></el-icon>
            </div>
          </div>
          <div class="file-content">
            <div class="file-name" :title="getFileName(file)">{{ getFileName(file) }}</div>
            <el-button
              type="primary"
              size="small"
              link
              class="file-view-btn"
              @click.stop="handleViewFile(file, index)"
            >
              查看
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <el-card v-loading="projectsLoading" class="projects-card">
      <template #header>
        <div class="card-header">
          <span>关联的项目</span>
          <span class="project-count">共 {{ projectsPagination.total }} 个项目</span>
        </div>
      </template>

      <el-table :data="projectsData" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="project_no" label="项目编号" width="180" />
        <el-table-column prop="project_name" label="项目名称" min-width="200" />
        <el-table-column prop="company_name" label="所属公司" width="150" />
        <el-table-column prop="contract_amount" label="合同金额" width="150">
          <template #default="{ row }">
            <span v-if="row.contract_amount">
              {{ formatCurrency(row.contract_amount) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_winner" label="是否中标" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_winner ? 'success' : 'info'">
              {{ row.is_winner ? '中标' : '未中标' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="participated_at" label="参与时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.participated_at || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleViewProject(row.project_id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="projectsPagination.total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="projectsPagination.page"
          v-model:page-size="projectsPagination.pageSize"
          :total="projectsPagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchProjects"
          @current-change="fetchProjects"
        />
      </div>

      <el-empty v-if="!projectsLoading && projectsData.length === 0" description="暂无参与项目" />
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="auditDialogVisible"
      :title="`审核供应商 - ${supplierData.company_name || ''}`"
      :width="DIALOG_WIDTH.SMALL"
    >
      <el-form>
        <el-form-item label="审核操作">
          <el-tag :type="auditStatus === 'approved' ? 'success' : 'danger'">
            {{ auditStatus === 'approved' ? '通过' : '拒绝' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="审核理由" required>
          <el-input v-model="auditComment" type="textarea" :rows="4" placeholder="请输入审核理由" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAudit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { PageHeader, StatusTag } from '@/components'
import { getSupplierDetail, getSupplierProjects, auditSupplier } from '@/api/supplier'
import { formatDate, formatCurrency, DIALOG_WIDTH } from '@/utils'
import { getToken } from '@/utils/auth'
import { getFileUrl as getApiFileUrl } from '@/utils/api'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const projectsLoading = ref(false)

const isAdmin = computed(() => {
  return userStore.userInfo?.is_superuser
})

const auditDialogVisible = ref(false)
const auditStatus = ref(null)
const auditComment = ref('')

const supplierData = reactive({
  id: null,
  company_name: '',
  tax_number: '',
  company_address: '',
  business_scope: '',
  contact_person: '',
  contact_phone: '',
  qualification_docs: '',
  status: '',
  audit_comment: '',
  created_at: ''
})

const projectsData = ref([])
const projectsPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const qualificationFiles = computed(() => {
  if (!supplierData.qualification_docs) return []
  try {
    const files = JSON.parse(supplierData.qualification_docs)
    const fileList = Array.isArray(files) ? files : []

    // 兼容旧格式（纯字符串数组）和新格式（对象数组）
    return fileList.map(file => {
      if (typeof file === 'string') {
        // 旧格式：纯字符串路径
        return {
          url: file,
          name: file.split('/').pop() || file
        }
      } else {
        // 新格式：{url, name} 对象
        return {
          url: file.url || file,
          name: file.name || (file.url ? file.url.split('/').pop() : '未知文件')
        }
      }
    })
  } catch {
    return []
  }
})

// 图片 URL 缓存
const imageUrlCache = ref({})
// 正在加载的图片集合，避免重复加载
const loadingImages = ref(new Set())

const fetchData = async () => {
  loading.value = true
  try {
    const supplierId = route.params.id
    const data = await getSupplierDetail(supplierId)
    Object.assign(supplierData, data)

    // 预加载图片
    if (qualificationFiles.value.length > 0) {
      for (let i = 0; i < qualificationFiles.value.length; i++) {
        const file = qualificationFiles.value[i]
        if (isImageFile(file)) {
          const filePath = file.url || file
          await loadImageToCache(filePath, i)
        }
      }
    }
  } catch (error) {
    console.error('获取供应商详情失败:', error)
    ElMessage.error('获取供应商详情失败')
  } finally {
    loading.value = false
  }
}

// 处理图片加载成功
const handleImageLoad = (fileInfo, index) => {
  // 图片加载成功，无需处理
}

// 处理图片加载错误（占位符加载失败时）
const handleImageError = async (fileInfo, index = 0) => {
  // 如果图片加载失败，尝试重新加载
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || fileInfo
  const cacheKey = `${filePath}_${index}`
  if (!imageUrlCache.value[cacheKey]) {
    await loadImageToCache(filePath, index)
  }
}

const fetchProjects = async () => {
  projectsLoading.value = true
  try {
    const supplierId = route.params.id
    const data = await getSupplierProjects(supplierId, {
      page: projectsPagination.page,
      page_size: projectsPagination.pageSize
    })
    projectsData.value = data.items || []
    projectsPagination.total = data.total || 0
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  } finally {
    projectsLoading.value = false
  }
}

// 获取文件名（支持对象或字符串）
const getFileName = fileInfo => {
  if (!fileInfo) return ''
  // 如果是对象格式，返回name字段（原始文件名）
  if (typeof fileInfo === 'object' && fileInfo.name) {
    return fileInfo.name
  }
  // 兼容旧格式：从路径中提取文件名
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  const parts = filePath.split('/')
  return parts[parts.length - 1] || filePath
}

// 加载图片到缓存
const loadImageToCache = async (filePath, index = 0) => {
  // 确保 filePath 是字符串
  if (!filePath || typeof filePath !== 'string') return
  // 检查是否为图片文件
  const filePathStr = filePath
  const ext = filePathStr.split('.').pop()?.toLowerCase()
  if (!['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) return

  const cacheKey = `${filePath}_${index}`
  // 如果已经在缓存中或正在加载，跳过
  if (imageUrlCache.value[cacheKey] || loadingImages.value.has(cacheKey)) return

  // 标记为加载中
  loadingImages.value.add(cacheKey)

  // 构建完整URL
  let normalizedPath = filePath
  
  // 标准化路径：移除 /api/v1 前缀（如果存在）
  if (normalizedPath.startsWith('/api/v1/uploads/')) {
    normalizedPath = normalizedPath.replace('/api/v1', '')
  }
  
  const fullUrl = getApiFileUrl(normalizedPath)
  if (!fullUrl) {
    loadingImages.value.delete(cacheKey)
    return
  }

  try {
    // 使用 axios 直接请求图片，携带认证信息
    const token = getToken()
    if (!token) {
      loadingImages.value.delete(cacheKey)
      return
    }
    const response = await axios.get(fullUrl, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${token}` },
      // 静默处理错误，不输出到控制台
      validateStatus: () => true
    })
    
    if (response.status === 200) {
      // 转换为 blob URL
      const blobUrl = URL.createObjectURL(response.data)
      // 使用对象展开触发响应式更新
      imageUrlCache.value = {
        ...imageUrlCache.value,
        [cacheKey]: blobUrl
      }
    }
  } catch (error) {
    // 错误已通过其他方式处理，不需要额外操作
  } finally {
    loadingImages.value.delete(cacheKey)
  }
}

// 获取文件URL（支持对象或字符串）
const getFileUrl = (fileInfo, index = 0) => {
  if (!fileInfo) return ''
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath) return ''

  // 如果已经是完整URL，直接返回
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath
  }

  // 如果是图片文件，优先使用缓存的 blob URL
  if (isImageFile(fileInfo)) {
    const cacheKey = `${filePath}_${index}`
    // 如果缓存中有，返回缓存
    if (imageUrlCache.value[cacheKey]) {
      return imageUrlCache.value[cacheKey]
    }
    // 如果缓存中没有，异步加载到缓存
    loadImageToCache(filePath, index)
    // 返回占位符，等待异步加载完成
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIiBmaWxsPSIjOTk5Ij7lm77niYfliqDovb3lpLHotKU8L3RleHQ+PC9zdmc+'
  }

  // 非图片文件，直接返回完整URL
  return getApiFileUrl(filePath) || filePath
}

// 判断是否为图片文件（支持对象或字符串）
const isImageFile = fileInfo => {
  if (!fileInfo) return false
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath || typeof filePath !== 'string') return false
  const ext = filePath.split('.').pop()?.toLowerCase()
  // 支持所有常见图片格式，以便显示预览（包括旧文件如PNG）
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
}

// 获取缓存键
const getCacheKey = (fileInfo, index) => {
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  return `${filePath}_${index}`
}

// 获取图片预览列表（只返回已缓存的 blob URL）
const getImagePreviewList = () => {
  const imageFiles = []
  qualificationFiles.value.forEach((file, index) => {
    if (isImageFile(file)) {
      const filePath = typeof file === 'string' ? file : file.url || ''
      const cacheKey = getCacheKey(file, index)
      // 只使用已缓存的 blob URL，避免使用占位符
      if (imageUrlCache.value[cacheKey]) {
        imageFiles.push(imageUrlCache.value[cacheKey])
      }
    }
  })
  return imageFiles
}

// 获取当前图片在预览列表中的索引
const getImageIndex = currentIndex => {
  let imageIndex = 0
  for (let i = 0; i < currentIndex; i++) {
    if (isImageFile(qualificationFiles.value[i])) {
      imageIndex++
    }
  }
  return imageIndex
}

// 判断是否为PDF文件
const isPdfFile = fileInfo => {
  if (!fileInfo) return false
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath || typeof filePath !== 'string') return false
  const ext = filePath.split('.').pop()?.toLowerCase()
  return ext === 'pdf'
}

// PDF文件URL缓存（用于需要认证的PDF）
const pdfUrlCache = ref({})

// 预览PDF文件
const handlePreviewPdf = async (fileInfo, index) => {
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath) return

  try {
    loading.value = true

    // 检查缓存
    const cacheKey = `${filePath}_${index}`
    if (pdfUrlCache.value[cacheKey]) {
      window.open(pdfUrlCache.value[cacheKey], '_blank')
      return
    }

    // 构建完整URL
    const fullUrl = getApiFileUrl(filePath)
    if (!fullUrl) {
      ElMessage.error('文件路径无效')
      return
    }

    // 使用 axios 获取PDF文件（携带认证信息）
    const token = getToken()
    if (!token) {
      ElMessage.error('未找到认证信息，无法访问文件')
      return
    }
    const response = await axios.get(fullUrl, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${token}` }
    })

    // 创建 Blob URL
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const blobUrl = URL.createObjectURL(blob)

    // 缓存 Blob URL
    pdfUrlCache.value[cacheKey] = blobUrl

    // 在新窗口中打开PDF
    window.open(blobUrl, '_blank')

    ElMessage.success('PDF文件已打开')
  } catch (error) {
    console.error('预览PDF失败:', error)
    const errorMsg =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      '预览PDF失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 预览图片文件
const handlePreviewImage = async (fileInfo, index) => {
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath) return

  try {
    loading.value = true

    // 检查缓存
    const cacheKey = `${filePath}_${index}`
    if (imageUrlCache.value[cacheKey]) {
      window.open(imageUrlCache.value[cacheKey], '_blank')
      return
    }

    // 构建完整URL
    const fullUrl = getApiFileUrl(filePath)
    if (!fullUrl) {
      ElMessage.error('文件路径无效')
      return
    }

    // 使用 axios 获取图片文件（携带认证信息）
    const token = getToken()
    if (!token) {
      ElMessage.error('未找到认证信息，无法访问文件')
      return
    }
    const response = await axios.get(fullUrl, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${token}` }
    })

    // 创建 Blob URL
    const blobUrl = URL.createObjectURL(response.data)

    // 缓存 Blob URL
    imageUrlCache.value[cacheKey] = blobUrl

    // 在新窗口中打开图片
    window.open(blobUrl, '_blank')

    ElMessage.success('图片已打开')
  } catch (error) {
    console.error('预览图片失败:', error)
    const errorMsg =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      '预览图片失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 统一处理文件查看
const handleViewFile = (fileInfo, index) => {
  if (isPdfFile(fileInfo)) {
    handlePreviewPdf(fileInfo, index)
  } else if (isImageFile(fileInfo)) {
    handlePreviewImage(fileInfo, index)
  } else {
    // 其他文件类型，直接打开
    const fileUrl = getFileUrl(fileInfo, index)
    if (fileUrl) {
      window.open(fileUrl, '_blank')
    }
  }
}

const handlePreviewFile = fileInfo => {
  // 兼容旧的调用方式
  handleViewFile(fileInfo, 0)
}

const handleViewProject = projectId => {
  router.push(`/project/detail/${projectId}`)
}

const handleGoBack = () => {
  router.back()
}

const handleAudit = (status) => {
  auditStatus.value = status
  auditComment.value = ''
  auditDialogVisible.value = true
}

const confirmAudit = async () => {
  if (!auditComment.value.trim()) {
    ElMessage.warning('请输入审核理由')
    return
  }

  try {
    const statusValue = auditStatus.value === 'approved' ? 1 : 0
    await auditSupplier(supplierData.id, {
      status: statusValue,
      audit_comment: auditComment.value.trim()
    })
    ElMessage.success('审核成功')
    auditDialogVisible.value = false
    fetchData()
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail || error.response?.data?.message || error.message || '审核失败'
    ElMessage.error(errorMsg)
  }
}

// 监听图片缓存变化，触发视图更新
watch(
  () => imageUrlCache.value,
  () => {
    // 缓存更新时，触发响应式更新
  },
  { deep: true }
)

onMounted(() => {
  fetchData()
  fetchProjects()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.supplier-detail-container {
  min-height: 100%;
}

.info-card,
.qualification-card,
.projects-card {
  margin-bottom: $spacing-lg;

  :deep(.el-card__header) {
    padding: $spacing-lg;
    border-bottom: 1px solid $border-color-lighter;
  }

  :deep(.el-card__body) {
    padding: $spacing-lg;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .project-count {
    color: $text-secondary;
    font-size: 14px;
  }
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-md;
}

.file-card {
  display: flex;
  flex-direction: column;
  width: 140px;
  background: $bg-color;
  border-radius: $border-radius-base;
  border: 1px solid $border-color-lighter;
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    border-color: $primary-color;
    box-shadow: $box-shadow-light;
    transform: translateY(-2px);
  }

  .file-preview {
    width: 100%;
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: $bg-color-light;
    cursor: pointer;
    overflow: hidden;

    .file-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .file-icon-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;

      .file-icon {
        font-size: 48px;
        color: $text-secondary;
      }
    }
  }

  .file-content {
    padding: $spacing-sm $spacing-md;
    display: flex;
    flex-direction: column;
    gap: $spacing-xs;
    flex: 1;

    .file-name {
      font-size: 12px;
      color: $text-primary;
      line-height: 1.4;
      word-break: break-all;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      min-height: 32px;
    }

    .file-view-btn {
      width: 100%;
      text-align: center;
      padding: $spacing-xxs 0;
      font-size: 12px;
    }
  }
}

.pagination-container {
  margin-top: $spacing-lg;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
  width: 120px;
  text-align: center;
}

.audit-status-wrapper {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  flex-wrap: nowrap;

  .audit-buttons {
    display: flex;
    gap: $spacing-sm;
    flex-shrink: 0;
  }

  .audit-comment-text {
    color: $text-secondary;
    font-size: 14px;
    flex: 1;
    min-width: 0;
    word-break: break-word;
  }
}
</style>
