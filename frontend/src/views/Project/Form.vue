<template>
  <div class="project-form-container">
    <PageHeader :title="isEdit ? '编辑项目' : '创建项目'">
      <template #extra>
        <div class="header-actions">
          <!-- 项目状态管理（仅编辑模式显示） -->
          <div v-if="isEdit" class="status-action-wrapper">
            <StatusTag :status="currentStatus" status-type="project" />
            <el-dropdown :disabled="actionLoading" @command="handleStatusCommand">
              <el-button :loading="actionLoading" size="default">
                操作
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-if="currentStatus === 0 || currentStatus === 5"
                    command="publish"
                    :disabled="actionLoading"
                  >
                    发布
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="currentStatus === 1 || currentStatus === 3 || currentStatus === 5"
                    command="stop"
                    :disabled="actionLoading"
                  >
                    停止
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="currentStatus !== 4 && currentStatus !== 5"
                    command="cancel"
                    :disabled="actionLoading"
                  >
                    取消
                  </el-dropdown-item>
                  <el-dropdown-item v-if="currentStatus === 4" disabled>
                    无可用操作
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <el-button @click="handleCancel">返回</el-button>
        </div>
      </template>
    </PageHeader>

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="form-container"
        :validate-on-rule-change="false"
      >
        <el-form-item label="项目名称" prop="project_name">
          <el-input 
            v-model="form.project_name" 
            placeholder="请输入项目名称（至少2个字符）"
            clearable
            show-word-limit
            maxlength="200"
          />
        </el-form-item>

        <el-form-item label="项目类别" prop="category_id">
          <el-select
            v-model="form.category_id"
            placeholder="请选择项目类别"
            clearable
            filterable
            class="w-full"
          >
            <el-option
              v-for="category in categoryList"
              :key="category.id"
              :label="category.category_name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关联品牌" prop="brand_id">
          <el-select
            v-model="selectedBrandId"
            placeholder="请选择品牌"
            clearable
            filterable
            class="w-full"
            @change="handleBrandChange"
          >
            <el-option
              v-for="brand in brandList"
              :key="brand.id"
              :label="brand.brand_name"
              :value="brand.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="所属公司" prop="company_id">
          <el-select
            v-model="form.company_id"
            :placeholder="selectedBrandId ? '请选择公司' : '请先选择品牌'"
            clearable
            filterable
            class="w-full"
            :disabled="!selectedBrandId"
          >
            <el-option
              v-for="company in companyList"
              :key="company.id"
              :label="company.company_name"
              :value="Number(company.id)"
            />
          </el-select>
          <div v-if="form.company_id && companyList.length === 0" class="warning-text">
            警告：选中的公司不在当前品牌的公司列表中
          </div>
        </el-form-item>

        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>

        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="datetime"
            placeholder="选择开始日期"
            class="w-full"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="datetime"
            placeholder="选择结束日期"
            class="w-full"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="time => form.start_date && time < new Date(form.start_date)"
          />
        </el-form-item>

        <el-form-item label="投标截止时间" prop="bidding_deadline">
          <el-date-picker
            v-model="form.bidding_deadline"
            type="datetime"
            placeholder="选择投标截止时间"
            class="w-full"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="附件">
          <div class="upload-controls">
            <el-upload
              ref="uploadRef"
              :action="uploadAction"
              :headers="uploadHeaders"
              :file-list="fileList"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :on-remove="handleRemoveFile"
              :before-upload="beforeUpload"
              :auto-upload="true"
              multiple
              :limit="10"
              class="custom-upload"
            >
              <el-button type="primary">选择文件</el-button>
            </el-upload>
            <div class="upload-tip">
              支持上传多个文件，单个文件不超过10MB；支持格式：{{ PROJECT_FILE_EXTENSIONS.join(', ') }}
            </div>
          </div>

          <!-- 已上传文件列表（显示在按钮下方） -->
          <div v-if="fileList.length > 0" class="uploaded-files-list">
            <div v-for="file in fileList" :key="file.uid || file.id" class="file-item">
              <span class="file-name">{{ file.name }}</span>
              <el-button
                type="danger"
                size="small"
                text
                circle
                class="delete-btn"
                @click="handleRemoveFile(file)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, ArrowDown } from '@element-plus/icons-vue'
import { PageHeader, StatusTag } from '@/components'
import { formatFileSize, formatDate } from '@/utils'
import {
  createProject,
  updateProject,
  getProjectDetail,
  publishProject,
  stopProject,
  cancelProject
} from '@/api/project'
import { getCompanyList } from '@/api/company'
import { getBrandList } from '@/api/brand'
import { getProjectCategoryList } from '@/api/projectCategory'
import { uploadFiles, getFiles } from '@/api/upload'
import { useUserStore } from '@/stores/user'
import { useFormValidation } from '@/composables'
import { PROJECT_FILE_EXTENSIONS, validateFileType } from '@/config/fileTypes'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const uploadRef = ref(null)
const loading = ref(false)
const actionLoading = ref(false)
const companyList = ref([])
const brandList = ref([])
const categoryList = ref([])
const fileList = ref([])
const uploadedFileIds = ref([])
const selectedBrandId = ref(null)
const currentStatus = ref(0)

const isEdit = computed(() => !!route.params.id)

// 计算是否有可用操作
const hasAvailableActions = computed(() => {
  // 已完成(4)和已取消(5)状态无可用操作
  if (currentStatus.value === 4 || currentStatus.value === 5) {
    return false
  }
  // 其他状态有可用操作
  return currentStatus.value === 0 || currentStatus.value === 1 || currentStatus.value === 3
})

const form = reactive({
  project_name: '',
  category_id: null,
  description: '',
  company_id: null,
  attachments: null,
  start_date: null,
  end_date: null,
  bidding_deadline: null
})

const rules = {
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 200, message: '项目名称长度在2到200个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择项目类别', trigger: 'change' }
  ],
  company_id: [
    { required: true, message: '请选择所属公司', trigger: 'change' }
  ]
}


const uploadAction = computed(() => {
  // 使用代理路径，vite会将/api代理到后端/api/v1
  return '/api/upload/'
})

const uploadHeaders = computed(() => {
  return {
    Authorization: `Bearer ${userStore.token}`
  }
})

const fetchBrandList = async () => {
  try {
    const data = await getBrandList({ page: 1, page_size: 100, is_active: true })
    // 确保返回的是纯数组，避免Vue Proxy对象导致的问题
    if (data && Array.isArray(data.items)) {
      brandList.value = JSON.parse(JSON.stringify(data.items))
    } else {
      brandList.value = []
    }
  } catch (error) {
    console.error('获取品牌列表失败:', error)
    brandList.value = []
  }
}

const fetchCategoryList = async () => {
  try {
    const data = await getProjectCategoryList({ page: 1, page_size: 100, is_active: true })
    // 确保返回的是纯数组，避免Vue Proxy对象导致的问题
    if (data && Array.isArray(data.items)) {
      categoryList.value = JSON.parse(JSON.stringify(data.items))
    } else {
      categoryList.value = []
    }
  } catch (error) {
    console.error('获取项目类别列表失败:', error)
    categoryList.value = []
  }
}

const fetchCompanyList = async brandId => {
  try {
    const params = { page: 1, page_size: 100, is_active: true }
    if (brandId) {
      params.brand_id = brandId
    }
    const data = await getCompanyList(params)
    // 确保返回的是纯数组，避免Vue Proxy对象导致的问题
    if (data && Array.isArray(data.items)) {
      companyList.value = JSON.parse(JSON.stringify(data.items))
    } else {
      companyList.value = []
    }
  } catch (error) {
    console.error('获取公司列表失败:', error)
    companyList.value = []
  }
}

const handleBrandChange = async brandId => {
  // 如果切换品牌，清空公司选择（因为不同品牌下的公司不同）
  const oldCompanyId = form.company_id
  form.company_id = null

  // 重新加载公司列表
  if (brandId) {
    await fetchCompanyList(brandId)
    // 如果新品牌下有相同的公司ID，保持选中（虽然这种情况很少见）
    // 否则保持清空状态
  } else {
    companyList.value = []
  }
}

const beforeUpload = file => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }

  // 检查文件格式（使用项目附件的文件类型配置）
  if (!validateFileType(file.name, PROJECT_FILE_EXTENSIONS)) {
    ElMessage.error(`不支持的文件格式。支持的格式：${PROJECT_FILE_EXTENSIONS.join(', ')}`)
    return false
  }

  return true
}

const handleUploadSuccess = (response, file) => {
  try {
    // Element Plus的el-upload组件，response已经是解析后的数据
    if (Array.isArray(response)) {
      // 批量上传返回数组
      response.forEach(item => {
        if (item.id && !uploadedFileIds.value.includes(item.id)) {
          uploadedFileIds.value.push(item.id)
        }
        // 更新fileList显示
        const fileItem = {
          uid: file.uid,
          name: item.file_name || file.name,
          size: item.file_size || file.size,
          status: 'success',
          response: item
        }
        const index = fileList.value.findIndex(f => f.uid === file.uid)
        if (index > -1) {
          fileList.value[index] = fileItem
        } else {
          fileList.value.push(fileItem)
        }
      })
    } else if (response && response.id) {
      // 单个文件上传返回对象
      if (!uploadedFileIds.value.includes(response.id)) {
        uploadedFileIds.value.push(response.id)
      }
      // 更新fileList显示
      const fileItem = {
        uid: file.uid,
        name: response.file_name || file.name,
        size: response.file_size || file.size,
        status: 'success',
        response: response
      }
      const index = fileList.value.findIndex(f => f.uid === file.uid)
      if (index > -1) {
        fileList.value[index] = fileItem
      } else {
        fileList.value.push(fileItem)
      }
    }
    ElMessage.success('文件上传成功')
  } catch (error) {
    console.error('处理上传成功响应失败:', error)
    ElMessage.success('文件上传成功')
  }
}

const handleUploadError = (error, file) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败')
}

const handleRemoveFile = file => {
  // 从已上传文件ID列表中移除
  if (file.response && file.response.id) {
    const index = uploadedFileIds.value.indexOf(file.response.id)
    if (index > -1) {
      uploadedFileIds.value.splice(index, 1)
    }
  }
  // 从fileList中移除
  const fileIndex = fileList.value.findIndex(f => f.uid === file.uid)
  if (fileIndex > -1) {
    fileList.value.splice(fileIndex, 1)
  }
}

// 根据文件ID列表加载文件详情
const loadFileList = async fileIds => {
  if (!fileIds || fileIds.length === 0) {
    fileList.value = []
    return
  }

  try {
    const data = await getFiles({ file_ids: fileIds.join(',') })
    if (Array.isArray(data)) {
      fileList.value = data.map(file => ({
        uid: file.id,
        name: file.file_name,
        size: file.file_size,
        status: 'success',
        response: file
      }))
    }
  } catch (error) {
    console.error('加载文件列表失败:', error)
    fileList.value = []
  }
}

const fetchData = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const data = await getProjectDetail(route.params.id)

    // 重置表单数据
    form.project_name = data.project_name || ''
    form.category_id = data.category_id || data.category?.id || null
    form.description = data.description || ''
    form.attachments = data.attachments || null
    form.start_date = data.start_date || null
    form.end_date = data.end_date || null
    form.bidding_deadline = data.bidding_deadline || null

    // 保存当前项目状态
    currentStatus.value = typeof data.status === 'number' ? data.status : 0

    // 保存公司ID，优先从company对象获取，其次从company_id字段获取
    // 注意：如果company对象存在，应该使用company.id，而不是company_id字段
    let savedCompanyId = null
    if (data.company && data.company.id) {
      savedCompanyId = Number(data.company.id)
    } else if (data.company_id) {
      savedCompanyId = Number(data.company_id)
    }

    // 重置附件列表
    uploadedFileIds.value = []

    // 处理公司和品牌的回显
    if (savedCompanyId && data.company && data.company.brand_id) {
      // 情况1：有完整的公司信息，包含品牌ID和公司ID
      const brandId = Number(data.company.brand_id)
      selectedBrandId.value = brandId

      // 加载对应的公司列表
      await fetchCompanyList(brandId)

      // 等待DOM更新
      await nextTick()

      // 验证公司是否在列表中
      const foundCompany = companyList.value.find(c => Number(c.id) === savedCompanyId)

      if (foundCompany) {
        // 设置公司ID（确保是数字类型）
        form.company_id = savedCompanyId
      } else {
        form.company_id = savedCompanyId
      }
    } else if (savedCompanyId) {
      // 情况2：有公司ID但没有品牌信息，需要查找品牌

      // 先加载所有公司查找对应的品牌
      await fetchCompanyList(null)

      // 查找公司对应的品牌
      const company = companyList.value.find(c => Number(c.id) === savedCompanyId)

      if (company && company.brand_id) {
        const brandId = Number(company.brand_id)
        selectedBrandId.value = brandId

        // 重新加载该品牌下的公司列表
        await fetchCompanyList(brandId)
        await nextTick()
      }

      // 设置公司ID
      form.company_id = savedCompanyId
    } else {
      // 情况3：没有公司信息
      selectedBrandId.value = null
      form.company_id = null
    }

    // 如果有附件，解析附件ID列表
    if (data.attachments) {
      try {
        const attachmentIds = JSON.parse(data.attachments)
        if (Array.isArray(attachmentIds)) {
          uploadedFileIds.value = attachmentIds
          // 加载文件详情
          await loadFileList(attachmentIds)
        }
      } catch (e) {
        console.error('解析附件失败:', e)
        uploadedFileIds.value = []
        fileList.value = []
      }
    } else {
      fileList.value = []
    }

  } catch (error) {
    console.error('获取项目信息失败:', error)
    ElMessage.error('获取项目信息失败')
    // 重置表单
    form.project_name = ''
    form.description = ''
    form.company_id = null
    form.attachments = null
    form.start_date = null
    form.end_date = null
    form.bidding_deadline = null
    selectedBrandId.value = null
    uploadedFileIds.value = []
  } finally {
    loading.value = false
  }
}

// 字段名映射：将后端字段名映射到前端表单项的 prop
const fieldNameMap = {
  'body.project_name': 'project_name',
  'body.category_id': 'category_id',
  'body.company_id': 'company_id',
  'body.description': 'description',
  'body.start_date': 'start_date',
  'body.end_date': 'end_date',
  'body.bidding_deadline': 'bidding_deadline',
  'body.items': 'items',
  'project_name': 'project_name',
  'category_id': 'category_id',
  'company_id': 'company_id',
  'description': 'description',
  'start_date': 'start_date',
  'end_date': 'end_date',
  'bidding_deadline': 'bidding_deadline',
  'items': 'items'
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form,
  {
    fieldNameMap,
    showTopMessage: true,
    topMessage: '表单验证失败，请检查下方红色标记的字段'
  }
)

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        const submitData = { ...form }

        // 添加必填的 items 字段（项目明细），如果没有明细，使用空数组
        submitData.items = []

        // 将附件ID列表转换为JSON字符串
        if (uploadedFileIds.value.length > 0) {
          submitData.attachments = JSON.stringify(uploadedFileIds.value)
        } else {
          submitData.attachments = null
        }

        if (isEdit.value) {
          await updateProject(route.params.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createProject(submitData)
          ElMessage.success('创建成功')
        }
        router.push('/projects')
      } catch (error) {
        console.error('创建/更新项目失败:', error)
        // 使用统一的错误处理
        handleSubmitError(error, form, isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
      }
    } else {
      // 前端验证失败，使用统一的处理
      handleFrontendValidationError()
    }
  })
}

const handleCancel = () => {
  router.push('/projects')
}

// 处理状态操作命令
const handleStatusCommand = async command => {
  if (!isEdit.value) return

  const projectId = route.params.id

  try {
    switch (command) {
      case 'publish':
        await ElMessageBox.confirm('确定要发布项目吗？发布后供应商将可以查看此项目。', '发布项目', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        })
        actionLoading.value = true
        await publishProject(projectId)
        ElMessage.success('发布成功')
        await fetchData()
        break

      case 'stop':
        await ElMessageBox.confirm('确定要停止项目吗？停止后供应商将无法查看此项目。', '停止项目', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        actionLoading.value = true
        await stopProject(projectId)
        ElMessage.success('停止成功')
        await fetchData()
        break

      case 'cancel':
        await ElMessageBox.confirm(
          '确定要取消项目吗？取消后项目将不能再进行任何操作。',
          '取消项目',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        actionLoading.value = true
        await cancelProject(projectId)
        ElMessage.success('取消成功')
        await fetchData()
        break
    }
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    console.error('操作失败:', error)
    const errorMsg =
      error.response?.data?.detail || error.response?.data?.message || error.message || '操作失败'
    ElMessage.error(errorMsg)
  } finally {
    actionLoading.value = false
  }
}

const initData = async () => {
  try {
    // 重置数据
    brandList.value = []
    companyList.value = []
    selectedBrandId.value = null
    fileList.value = []

    // 加载品牌列表
    await fetchBrandList()
    await fetchCategoryList()

    // 加载项目数据（如果是编辑模式）
    await fetchData()

    // 如果没有编辑模式，加载所有公司（用于显示）
    if (!isEdit.value) {
      await fetchCompanyList(null)
    }
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
}

onMounted(async () => {
  await initData()
})

onActivated(async () => {
  // 页面激活时重新加载数据
  await nextTick()
  await initData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/form-validation.scss';

.project-form-container {
  min-height: 100%;
}

// 隐藏el-upload组件默认的文件列表显示
:deep(.custom-upload) {
  .el-upload-list {
    display: none !important;
  }
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  width: 100%;

  .custom-upload {
    flex-shrink: 0;
  }

  .upload-tip {
    flex: 1;
    color: $text-secondary;
    font-size: 12px;
    line-height: 1.5;
  }
}

.uploaded-files-list {
  margin-top: $spacing-md;
  width: 100%;
  clear: both;

  .file-item {
    display: flex;
    align-items: center;
    padding: $spacing-sm $spacing-md;
    margin-bottom: $spacing-xs;
    color: $text-primary;
    font-size: 14px;
    line-height: 1.8;
    background-color: $bg-color-overlay;
    border-radius: $border-radius-base;
    transition: background-color 0.2s;

    &:hover {
      background-color: rgba(64, 158, 255, 0.08);
    }

    &:last-child {
      margin-bottom: 0;
    }

    .file-name {
      display: inline-block;
      margin-right: $spacing-sm;
      word-break: break-all;
    }

    .delete-btn {
      flex-shrink: 0;
      padding: $spacing-xxs $spacing-xs;
      margin-left: $spacing-sm;
      min-width: auto;
      width: auto;
      height: auto;
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.status-action-wrapper {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  .el-tag {
    margin: 0;
  }
}

</style>
