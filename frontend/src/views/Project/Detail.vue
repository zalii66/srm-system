<template>
  <div class="project-detail-container">
    <PageHeader title="项目详情">
      <template #extra>
        <el-button @click="handleBack">返回</el-button>
        <el-button v-if="isSupplier" type="primary" @click="handleParticipateQuotation">参与报价</el-button>
        <el-button v-if="!isSupplier" type="primary" @click="handleManageMilestones">管理时间节点</el-button>
        <el-button v-if="!isSupplier" type="warning" @click="handleEdit">编辑</el-button>
      </template>
    </PageHeader>

    <el-card v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="项目编号">
          {{ project.project_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目名称">
          {{ project.project_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目类别">
          {{ project.category?.category_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <StatusTag :status="project.status ?? 0" status-type="project" />
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(project.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="项目描述" :span="2">
          {{ project.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 附件列表 -->
    <el-card v-if="attachments.length > 0" class="attachments-card">
      <template #header>
        <span>项目附件</span>
      </template>

      <div class="attachments-list">
        <div v-for="file in attachments" :key="file.id" class="attachment-item">
          <div class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ file.file_name }}</span>
            <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
          </div>
          <div class="file-actions">
            <!-- 图片文件可以预览 -->
            <el-button
              v-if="isImageFile(file.file_type)"
              type="primary"
              link
              size="small"
              @click="previewFile(file)"
            >
              预览
            </el-button>
            <el-button type="primary" link size="small" @click="downloadAttachment(file)">
              下载
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 项目进度（时间节点） -->
    <el-card v-loading="milestonesLoading" class="milestones-card">
      <template #header>
        <div class="card-header">
          <span>项目进度</span>
          <div v-if="!isSupplier && projectProgress" class="progress-info">
            <span class="progress-label">总进度：</span>
            <span class="progress-value">{{ projectProgress.total_progress }}%</span>
          </div>
        </div>
      </template>

      <MilestoneTimeline :milestones="milestones" :readonly="true" />
    </el-card>

    <!-- 需求列表 -->
    <el-card v-loading="requirementsLoading" class="requirements-card">
      <template #header>
        <div class="card-header">
          <span>项目需求</span>
          <el-button
            v-if="!isSupplier"
            type="primary"
            size="small"
            link
            @click="handleManageRequirements"
          >
            管理需求
          </el-button>
        </div>
      </template>

      <DataTable
        v-if="requirements.length > 0"
        :data="requirements"
        :loading="false"
        :show-pagination="false"
        stripe
      >
        <el-table-column prop="item_no" label="需求编号" width="120" />
        <el-table-column prop="item_name" label="需求名称" min-width="200" />
        <el-table-column
          prop="specification"
          label="规格型号"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="quantity" label="数量" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
      </DataTable>

      <el-empty v-if="!requirementsLoading && requirements.length === 0" description="暂无需求项" />
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewVisible" title="图片预览" :width="DIALOG_WIDTH.XLARGE">
      <div class="image-preview" v-loading="previewLoading">
        <img v-if="previewImageUrl" :src="previewImageUrl" alt="预览图片" @load="handleImageLoad" @error="handleImageError" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { PageHeader, StatusTag, DataTable, MilestoneTimeline } from '@/components'
import { getProjectDetail, getProjectItems } from '@/api/project'
import { getFiles, downloadFile } from '@/api/upload'
import { getMilestones, getProjectProgress } from '@/api/milestone'
import { useUserStore } from '@/stores/user'
import { formatDate, formatFileSize, formatNumber, DIALOG_WIDTH } from '@/utils'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const attachments = ref([])
const previewVisible = ref(false)
const previewImageUrl = ref('')
const previewBlobUrl = ref(null) // 用于存储 Blob URL，以便清理
const previewLoading = ref(false)
const requirements = ref([])
const requirementsLoading = ref(false)
const milestones = ref([])
const milestonesLoading = ref(false)
const projectProgress = ref(null)

const isSupplier = computed(() => {
  if (!userStore.roles || !Array.isArray(userStore.roles)) return false
  return userStore.roles.includes('supplier')
})

const project = reactive({
  project_no: '',
  project_name: '',
  status: 0,
  description: '',
  created_at: '',
  attachments: null
})

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getProjectDetail(route.params.id)
    Object.assign(project, data)

    // 加载附件列表
    if (data.attachments) {
      try {
        const attachmentIds = JSON.parse(data.attachments)
        if (Array.isArray(attachmentIds) && attachmentIds.length > 0) {
          await loadAttachments(attachmentIds)
        }
      } catch (e) {
        console.error('解析附件失败:', e)
        attachments.value = []
      }
    } else {
      attachments.value = []
    }

    // 加载需求列表
    await fetchRequirements()

    // 加载时间节点和进度
    await fetchMilestones()
    await fetchProjectProgress()
  } catch (error) {
    ElMessage.error('获取项目详情失败')
  } finally {
    loading.value = false
  }
}

const fetchRequirements = async () => {
  requirementsLoading.value = true
  try {
    const data = await getProjectItems(route.params.id)
    // API返回的是对象，包含items数组
    requirements.value = data.items || []
  } catch (error) {
    console.error('获取需求列表失败:', error)
    requirements.value = []
  } finally {
    requirementsLoading.value = false
  }
}

const loadAttachments = async fileIds => {
  try {
    // 传递项目ID，用于后端验证权限（供应商可以查看已发布项目的附件）
    const projectId = Number(route.params.id)
    const data = await getFiles({ 
      file_ids: fileIds.join(','), 
      category: 'project',
      project_id: projectId 
    })
    if (Array.isArray(data)) {
      attachments.value = data
    } else {
      attachments.value = []
    }
  } catch (error) {
    console.error('加载附件列表失败:', error)
    // 如果是权限错误，显示错误提示
    if (error.response?.status === 403) {
      ElMessage.warning(error.response?.data?.detail || '无权查看项目附件')
    }
    attachments.value = []
  }
}

const isImageFile = fileType => {
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  return imageTypes.includes(fileType?.toLowerCase())
}

const previewFile = async file => {
  if (!isImageFile(file.file_type)) {
    ElMessage.warning('只能预览图片文件')
    return
  }

  try {
    // 如果已有 Blob URL，先释放
    if (previewBlobUrl.value) {
      URL.revokeObjectURL(previewBlobUrl.value)
      previewBlobUrl.value = null
    }

    previewLoading.value = true
    previewImageUrl.value = '' // 清空之前的图片
    previewVisible.value = true // 先打开对话框，显示加载状态

    // 使用 downloadFile API 获取图片文件（携带认证信息和项目ID）
    const projectId = Number(route.params.id)
    const blob = await downloadFile(file.id, projectId)
    
    // 创建 Blob URL 用于预览
    const blobUrl = URL.createObjectURL(blob)
    previewBlobUrl.value = blobUrl
    previewImageUrl.value = blobUrl
    // 图片加载事件会控制 loading 状态
  } catch (error) {
    console.error('预览文件失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '预览文件失败'
    ElMessage.error(errorMsg)
    previewVisible.value = false
    previewLoading.value = false
  }
}

const handleImageLoad = () => {
  // 图片加载成功，隐藏加载状态
  previewLoading.value = false
}

const handleImageError = () => {
  // 图片加载失败
  previewLoading.value = false
  ElMessage.error('图片加载失败')
  previewVisible.value = false
}

// 监听预览对话框关闭，释放 Blob URL
watch(previewVisible, (newVal) => {
  if (!newVal) {
    // 对话框关闭时释放 Blob URL
    if (previewBlobUrl.value) {
      URL.revokeObjectURL(previewBlobUrl.value)
      previewBlobUrl.value = null
    }
    previewImageUrl.value = ''
    previewLoading.value = false
  }
})

const downloadAttachment = async file => {
  try {
    // 传递项目ID，用于后端验证权限（供应商可以下载已发布项目的附件）
    const projectId = Number(route.params.id)
    const blob = await downloadFile(file.id, projectId)

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = file.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('文件下载成功')
  } catch (error) {
    console.error('下载文件失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '下载文件失败'
    ElMessage.error(errorMsg)
  }
}

// 返回
const handleBack = () => {
  router.push('/projects')
}

// 编辑项目
const handleEdit = () => {
  router.push(`/project/edit/${route.params.id}`)
}

// 管理时间节点
const handleManageMilestones = () => {
  router.push(`/project/${route.params.id}/milestones`)
}

// 管理需求
const handleManageRequirements = () => {
  router.push(`/project/${route.params.id}/requirements`)
}

// 参与报价（供应商用户）
const handleParticipateQuotation = () => {
  router.push(`/project/${route.params.id}/requirements`)
}

// 加载时间节点
const fetchMilestones = async () => {
  milestonesLoading.value = true
  try {
    const data = await getMilestones(route.params.id, !isSupplier.value)
    milestones.value = data || []
  } catch (error) {
    console.error('获取时间节点失败:', error)
    milestones.value = []
  } finally {
    milestonesLoading.value = false
  }
}

// 加载项目进度
const fetchProjectProgress = async () => {
  try {
    const data = await getProjectProgress(route.params.id)
    projectProgress.value = data
    // 更新里程碑列表（使用进度接口返回的里程碑，因为可能包含更完整的信息）
    if (data.milestones) {
      milestones.value = data.milestones
    }
  } catch (error) {
    console.error('获取项目进度失败:', error)
  }
}


onMounted(() => {
  fetchData()
})

// 组件卸载时清理 Blob URL
onBeforeUnmount(() => {
  if (previewBlobUrl.value) {
    URL.revokeObjectURL(previewBlobUrl.value)
    previewBlobUrl.value = null
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.project-detail-container {
  min-height: 100%;

  .requirements-card,
  .attachments-card,
  .milestones-card {
    margin-top: $spacing-md;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .progress-info {
        display: flex;
        align-items: center;
        gap: $spacing-xs;

        .progress-label {
          color: $text-secondary;
          font-size: 14px;
        }

        .progress-value {
          color: $primary-color;
          font-size: 16px;
          font-weight: 500;
        }
      }
    }
  }

  .attachments-list {
    .attachment-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-md;
      border-bottom: 1px solid $border-color-lighter;

      &:last-child {
        border-bottom: none;
      }

      .file-info {
        display: flex;
        align-items: center;
        flex: 1;

        .file-icon {
          margin-right: $spacing-sm;
          color: $text-secondary;
          font-size: 20px;
        }

        .file-name {
          flex: 1;
          margin-right: $spacing-sm;
          color: $text-primary;
        }

        .file-size {
          color: $text-secondary;
          font-size: 12px;
        }
      }

      .file-actions {
        display: flex;
        gap: $spacing-sm;
      }
    }
  }

  .image-preview {
    display: flex;
    justify-content: center;
    align-items: center;

    img {
      max-width: 100%;
      max-height: 70vh;
      object-fit: contain;
    }
  }
}
</style>

