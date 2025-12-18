<template>
  <div class="supplier-profile-container">
    <PageHeader title="公司资料" subtitle="查看和编辑供应商信息" />

    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <!-- 公司信息 -->
        <div class="form-section">
          <div class="section-title">公司信息</div>

          <el-form-item label="公司名称" prop="company_name">
            <el-input v-model="form.company_name" placeholder="请输入公司名称" />
          </el-form-item>

          <el-form-item label="公司税号" prop="tax_number">
            <el-input v-model="form.tax_number" placeholder="请输入公司税号" />
          </el-form-item>

          <el-form-item label="注册地址" prop="company_address">
            <el-input v-model="form.company_address" placeholder="请输入注册地址" />
          </el-form-item>

          <el-form-item label="主营产品" prop="business_scope">
            <el-input
              v-model="form.business_scope"
              type="textarea"
              :rows="3"
              placeholder="请输入主营产品"
            />
          </el-form-item>
        </div>

        <!-- 联系信息 -->
        <div class="form-section">
          <div class="section-title">联系信息</div>

          <el-form-item label="联系人" prop="contact_person">
            <el-input v-model="form.contact_person" placeholder="请输入联系人" />
          </el-form-item>

          <el-form-item label="联系电话" prop="contact_phone">
            <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
          </el-form-item>
        </div>

        <!-- 银行信息 -->
        <div class="form-section">
          <div class="section-title">银行信息</div>

          <el-form-item label="账户名称" prop="bank_account_name">
            <el-input v-model="form.bank_account_name" placeholder="请输入账户名称" />
          </el-form-item>

          <el-form-item label="开户行" prop="bank_name">
            <el-input v-model="form.bank_name" placeholder="请输入开户行" />
          </el-form-item>

          <el-form-item label="银行账号" prop="bank_account">
            <el-input v-model="form.bank_account" placeholder="请输入银行账号" />
          </el-form-item>
        </div>

        <!-- 证件资质 -->
        <div class="form-section">
          <div class="section-title">证件资质</div>

          <el-form-item label="证件资质">
            <div class="qualification-wrapper">
              <!-- 上传组件 -->
              <div class="qualification-uploader">
                <el-upload
                  ref="uploadRef"
                  class="qualification-uploader-inner"
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  :multiple="true"
                  :accept="qualificationAccept"
                  :auto-upload="false"
                  @change="handleFileChange"
                >
                  <el-button type="primary" :icon="Upload" :loading="isUploading">
                    上传证件资质
                  </el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 {{ QUALIFICATION_FILE_EXTENSIONS.join('、') }} 格式，每个文件不超过 10MB，可上传多个文件
                    </div>
                  </template>
                </el-upload>
              </div>

              <!-- 文件列表 -->
              <div v-if="qualificationFiles.length > 0" class="qualification-files">
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
                      <el-icon class="file-icon">
                        <Document />
                      </el-icon>
                    </div>
                  </div>
                  <div class="file-content">
                    <div class="file-name" :title="getFileName(file)">{{ getFileName(file) }}</div>
                    <div class="file-actions">
                      <el-button
                        type="primary"
                        size="small"
                        link
                        class="file-view-btn"
                        @click.stop="handleViewFile(file, index)"
                      >
                        查看
                      </el-button>
                      <el-button
                        type="danger"
                        size="small"
                        link
                        class="file-delete-btn"
                        :icon="Delete"
                        @click.stop="handleRemoveFile(index)"
                      >
                        删除
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-form-item>
        </div>

        <!-- 审核状态（只在已提交过资料时显示，从未提交过不显示） -->
        <div v-if="hasSubmittedProfile" class="form-section">
          <div class="section-title">审核信息</div>

          <el-form-item label="审核状态">
            <StatusTag :status="form.status" status-type="supplier" />
          </el-form-item>

          <!-- 审核意见（只有未通过审核时才显示） -->
          <el-form-item
            v-if="
              (typeof form.status === 'number' ? form.status : Number(form.status)) === 0 &&
              form.audit_comment
            "
            label="审核意见"
          >
            <div class="comment-text">{{ form.audit_comment }}</div>
          </el-form-item>

          <!-- 已通过审核时的提示 -->
          <el-alert
            v-if="isApproved"
            type="success"
            :closable="false"
            show-icon
            class="status-alert"
          >
            <template #title>公司资料已通过审核。编辑后需要重新审核。</template>
          </el-alert>
        </div>

        <!-- 按钮区域 -->
        <el-form-item class="form-actions">
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Document, Delete } from '@element-plus/icons-vue'
import { PageHeader, StatusTag } from '@/components'
import {
  getCurrentSupplier,
  updateSupplier,
  uploadQualification,
  deleteQualificationFile
} from '@/api/supplier'
import { getToken } from '@/utils/auth'
import { getFileUrl as getApiFileUrl } from '@/utils/api'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import { useFormValidation } from '@/composables'
import { QUALIFICATION_FILE_EXTENSIONS, getAcceptString, validateFileType } from '@/config/fileTypes'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const uploadRef = ref(null)
const isUploading = ref(false)

const form = reactive({
  company_name: '',
  tax_number: '',
  company_address: '',
  business_scope: '',
  contact_person: '',
  contact_phone: '',
  bank_account_name: '',
  bank_name: '',
  bank_account: '',
  qualification_docs: '',
  status: null,
  audit_comment: ''
})

const rules = {
  company_name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const isApproved = computed(() => {
  const statusNum = typeof form.status === 'number' ? form.status : Number(form.status)
  return statusNum === 1
})

// 判断是否已提交过资料（只要status有值就认为已提交过）
const hasSubmittedProfile = computed(() => {
  // 如果 status 是 null、undefined、空字符串，则认为未提交过
  if (form.status === null || form.status === undefined || form.status === '') {
    return false
  }
  // 如果 status 是数字，检查是否为有效值（-1, 0, 1）
  const statusNum = typeof form.status === 'number' ? form.status : Number(form.status)
  return !isNaN(statusNum) && (statusNum === -1 || statusNum === 0 || statusNum === 1)
})

// 证件资质文件列表
const qualificationFiles = ref([])

// 图片URL缓存（用于需要认证的图片）
const imageUrlCache = ref({})
// 正在加载的图片集合，避免重复加载
const loadingImages = ref(new Set())

// 加载证件资质文件列表
const loadQualificationFiles = async () => {
  if (!form.qualification_docs) {
    qualificationFiles.value = []
    return
  }

  try {
    const files = JSON.parse(form.qualification_docs)
    const fileList = Array.isArray(files) ? files : []

    // 兼容旧格式（纯字符串数组）和新格式（对象数组）
    qualificationFiles.value = fileList.map(file => {
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

    // 预加载所有图片
    for (let i = 0; i < qualificationFiles.value.length; i++) {
      const file = qualificationFiles.value[i]
      const filePath = file.url || file
      if (isImageFile(file)) {
        await loadImageToCache(filePath, i)
      }
    }
  } catch {
    qualificationFiles.value = []
  }
}

// 加载图片到缓存
const loadImageToCache = async (filePath, index) => {
  if (!filePath || !isImageFile(filePath)) return

  const cacheKey = `${filePath}_${index}`
  // 如果已经在加载中或已缓存，直接返回
  if (imageUrlCache.value[cacheKey] || loadingImages.value.has(cacheKey)) return

  // 标记为加载中
  loadingImages.value.add(cacheKey)

  const fullUrl = getApiFileUrl(filePath)
  if (!fullUrl) {
    loadingImages.value.delete(cacheKey)
    return
  }

  try {
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

// 获取缓存键
const getCacheKey = (fileInfo, index) => {
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  return `${filePath}_${index}`
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

// 获取文件URL（支持对象或字符串）
const getFileUrl = (fileInfo, index) => {
  if (!fileInfo) return ''
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath) return ''

  // 如果是完整的 HTTP URL，直接返回
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath
  }

  // 如果是图片，优先使用缓存的 blob URL
  if (isImageFile(fileInfo)) {
    const cacheKey = `${filePath}_${index}`
    if (imageUrlCache.value[cacheKey]) {
      return imageUrlCache.value[cacheKey]
    }
    // 如果缓存中没有，异步加载到缓存
    loadImageToCache(filePath, index)
    // 返回占位符，等待异步加载完成
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIiBmaWxsPSIjOTk5Ij7lm77niYfliqDovb3lpLHotKU8L3RleHQ+PC9zdmc+'
  }

  // 非图片文件返回原始路径
  return filePath
}

// 获取图片预览列表（只返回已缓存的 blob URL）
const getImagePreviewList = () => {
  const imageFiles = []
  qualificationFiles.value.forEach((file, index) => {
    if (isImageFile(file)) {
      const filePath = typeof file === 'string' ? file : file.url || ''
      const cacheKey = `${filePath}_${index}`
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
  if (!filePath) {
    ElMessage.error('文件路径为空')
    return
  }

  try {
    loading.value = true

    // 检查缓存
    const cacheKey = `${filePath}_${index}`
    if (pdfUrlCache.value[cacheKey]) {
      window.open(pdfUrlCache.value[cacheKey], '_blank')
      ElMessage.success('PDF文件已打开')
      return
    }

    // 构建完整URL - 确保使用正确的路径格式
    let fullUrl = ''
    let normalizedPath = filePath
    
    // 标准化路径：移除 /api/v1 前缀（如果存在）
    if (normalizedPath.startsWith('/api/v1/uploads/')) {
      normalizedPath = normalizedPath.replace('/api/v1', '')
    }
    
    // 确保路径以 /uploads/ 开头
    if (!normalizedPath.startsWith('/uploads/')) {
      ElMessage.error('文件路径格式不正确')
      console.error('无效的文件路径:', filePath)
      return
    }
    
    fullUrl = getApiFileUrl(normalizedPath)
    
    // 调试信息

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

    if (response.status !== 200) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

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
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      filePath: filePath
    })
    
    let errorMsg = '预览PDF失败'
    if (error.response?.status === 401) {
      errorMsg = '认证失败，请重新登录'
    } else if (error.response?.status === 403) {
      errorMsg = '没有权限访问此文件'
    } else if (error.response?.status === 404) {
      errorMsg = `文件不存在: ${filePath}`
    } else if (error?.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error?.message) {
      errorMsg = error.message
    }
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

    // 构建完整URL（使用统一的工具函数）
    let fullUrl = ''
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
      fullUrl = filePath
    } else {
      // 使用统一的工具函数获取文件URL
      fullUrl = getApiFileUrl(filePath)
      if (!fullUrl) {
        ElMessage.error('文件路径无效')
        return
      }
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

// 处理图片加载成功
const handleImageLoad = (fileInfo, index) => {
  // 图片加载成功，检查是否需要更新缓存
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  if (!filePath) return
  
  const cacheKey = getCacheKey(fileInfo, index)
  // 如果占位符加载成功（不应该发生），尝试加载真实图片
  const currentSrc = getFileUrl(fileInfo, index)
  if (currentSrc.startsWith('data:image/svg+xml')) {
    // 占位符被加载，说明缓存还没有准备好，触发重新加载
    loadImageToCache(filePath, index)
  }
}

// 处理图片加载错误（占位符加载失败时）
const handleImageError = (fileInfo, index) => {
  // 静默处理，不输出错误日志（因为可能是占位符加载失败）
  const filePath = typeof fileInfo === 'string' ? fileInfo : fileInfo.url || ''
  // 尝试加载真实图片到缓存
  if (filePath && isImageFile(fileInfo)) {
    loadImageToCache(filePath, index)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getCurrentSupplier()
    if (data) {
      // 获取用户信息，优先使用用户的 full_name 作为联系人
      const userInfo = userStore.userInfo
      const contactPerson = userInfo?.full_name || data.contact_person || ''
      
      // 确保 status 字段正确处理（null、undefined、空字符串都视为未提交）
      Object.assign(form, {
        ...data,
        contact_person: contactPerson, // 优先使用用户的姓名
        status:
          data.status !== null && data.status !== undefined && data.status !== ''
            ? data.status
            : null
      })
      // 加载证件资质文件列表
      await loadQualificationFiles()
    }
  } catch (error) {
    // 403 错误表示当前用户不是供应商角色
    if (error.response?.status === 403) {
      ElMessage.warning('当前用户不是供应商角色')
      return
    }
    // 其他错误显示错误信息
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '获取信息失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 使用表单验证工具
const { handleSubmitError, handleFrontendValidationError } = useFormValidation(
  formRef,
  form
)

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        // 获取用户信息，优先使用用户的 full_name 作为联系人
        const userInfo = userStore.userInfo
        const contactPerson = userInfo?.full_name || form.contact_person || ''
        
        const updateData = {
          company_name: form.company_name,
          tax_number: form.tax_number,
          company_address: form.company_address,
          business_scope: form.business_scope,
          contact_person: contactPerson, // 优先使用用户的姓名
          contact_phone: form.contact_phone,
          bank_account_name: form.bank_account_name,
          bank_name: form.bank_name,
          bank_account: form.bank_account
        }
        await updateSupplier(updateData)

        // 保存成功后，只显示成功通知
        const successMessage = isApproved.value
          ? '公司资料已更新，需要重新审核。只有通过审核后才能参与项目报价。'
          : '公司资料已提交，等待审核。只有通过审核后才能参与项目报价。'

        ElMessage.success(successMessage)

        // 保存成功后，状态会变为pending（待审核），需要重新获取数据以显示状态
        await fetchData() // 重新获取数据
      } catch (error) {
        handleSubmitError(error, form, '保存失败')
      } finally {
        loading.value = false
      }
    } else {
      handleFrontendValidationError()
    }
  })
}

const handleReset = () => {
  fetchData()
}

// 证件资质文件类型配置
const qualificationAccept = computed(() => getAcceptString(QUALIFICATION_FILE_EXTENSIONS))

const beforeUpload = file => {
  // 使用配置文件中的证件资质文件类型
  if (!validateFileType(file.name, QUALIFICATION_FILE_EXTENSIONS)) {
    ElMessage.error(`不支持的文件格式！仅支持：${QUALIFICATION_FILE_EXTENSIONS.join('、')}`)
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！')
    return false
  }
  return true
}

// 处理文件选择变化（当 auto-upload 为 false 时）
const handleFileChange = (uploadFile, uploadFiles) => {
  // 过滤出状态为 'ready' 的文件
  const readyFiles = uploadFiles.filter(file => file.status === 'ready')
  // 如果有文件准备好且当前没有上传任务，则自动触发上传
  if (readyFiles.length > 0 && !isUploading.value) {
    uploadFilesManually(readyFiles)
  }
}

// 手动上传文件
const uploadFilesManually = async fileList => {
  if (!fileList || fileList.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  if (isUploading.value) {
    ElMessage.warning('文件正在上传中，请勿重复操作')
    return
  }

  isUploading.value = true
  try {
    // 提取原始文件对象
    const filesToUpload = fileList.map(file => file.raw || file)

    await uploadQualification(filesToUpload)

    const wasApproved = isApproved.value
    if (wasApproved) {
      ElMessage.success('证件资质上传成功，需要重新审核')
    } else {
      ElMessage.success('证件资质上传成功')
    }

    // 清空 el-upload 内部文件列表
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }

    // 重新获取数据以更新文件列表
    await fetchData()
  } catch (error) {
    console.error('文件上传失败:', error)
    const errorMsg =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      '上传失败'
    ElMessage.error(errorMsg)
  } finally {
    isUploading.value = false
  }
}

const handleRemoveFile = async index => {
  try {
    await ElMessageBox.confirm('确定要删除此文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteQualificationFile(index)

    if (isApproved.value) {
      ElMessage.success('文件已删除，需要重新审核')
    } else {
      ElMessage.success('文件已删除')
    }

    await fetchData()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    const errorMsg =
      error.response?.data?.detail || error.response?.data?.message || error.message || '删除失败'
    ElMessage.error(errorMsg)
  }
}

// 监听 qualification_docs 变化
watch(
  () => form.qualification_docs,
  () => {
    loadQualificationFiles()
  }
)

// 监听图片缓存变化，触发视图更新
watch(
  () => imageUrlCache.value,
  () => {
    // 缓存更新时，触发响应式更新
  },
  { deep: true }
)

// 监听用户信息变化，自动更新联系人
watch(
  () => userStore.userInfo?.full_name,
  (newName) => {
    if (newName && form.contact_person !== newName) {
      form.contact_person = newName
    }
  },
  { immediate: true }
)

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
@import '@/styles/mixins.scss';
@import '@/styles/form-validation.scss';

.supplier-profile-container {
  min-height: 100%;
}

.qualification-wrapper {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  width: 100%;
}

.qualification-uploader {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  width: 100%;
  margin-bottom: 0;

  .qualification-uploader-inner {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    width: 100%;

    :deep(.el-upload) {
      display: inline-block;
    }

    :deep(.el-upload__tip) {
      margin-top: 0;
      margin-left: $spacing-sm;
      color: $text-secondary;
      font-size: 12px;
      white-space: nowrap;
    }
  }
}

.qualification-files {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-md;
  width: 100%;
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
    @include flex-center;
    background: $bg-color-light;
    cursor: pointer;
    overflow: hidden;

    .file-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .file-icon-wrapper {
      @include flex-center;
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
      @include text-ellipsis(2);
      font-size: 12px;
      color: $text-primary;
      line-height: 1.4;
      min-height: 32px;
    }

    .file-actions {
      display: flex;
      gap: $spacing-xs;
      justify-content: center;
      margin-top: $spacing-xs;

      .file-view-btn,
      .file-delete-btn {
        flex: 1;
        text-align: center;
        padding: $spacing-xxs 0;
        font-size: 12px;
      }
    }
  }
}

.license-preview {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;

  .license-image {
    width: 200px;
    height: 150px;
    border: 1px solid $border-color;
    border-radius: $border-radius-base;
  }

  .preview-actions {
    margin-top: $spacing-xs;
  }
}

.comment-text {
  color: $text-secondary;
  line-height: 1.6;
  padding: $spacing-sm;
  background: $bg-color;
  border-radius: $border-radius-base;
}

.form-section {
  .el-form-item {
    margin-bottom: $spacing-md;

    :deep(.el-form-item__label) {
      font-weight: 500;
    }
  }

  .status-alert {
    margin-top: $spacing-md;
  }
}

.form-actions {
  margin-top: $spacing-xl;
  margin-bottom: 0;
  padding-top: $spacing-lg;
  border-top: 1px solid $border-color-light;
}
</style>
