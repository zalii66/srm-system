<template>
  <div class="file-upload-wrapper">
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
        :auto-upload="autoUpload"
        :multiple="multiple"
        :limit="limit"
        :accept="computedAccept"
        class="custom-upload"
      >
        <el-button type="primary">
          <el-icon><Upload /></el-icon>
          选择文件
        </el-button>
      </el-upload>
      <div class="upload-tip">
        {{ computedTip }}
      </div>
    </div>

    <!-- 已上传文件列表 -->
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
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Delete } from '@element-plus/icons-vue'
import { getToken } from '@/utils/auth'
import {
  PROJECT_FILE_EXTENSIONS,
  QUALIFICATION_FILE_EXTENSIONS,
  getAcceptString,
  getFileTypeTip,
  validateFileType
} from '@/config/fileTypes'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  action: {
    type: String,
    default: '/api/upload'
  },
  category: {
    type: String,
    default: 'project'
  },
  tip: {
    type: String,
    default: null // 如果为null，将根据category自动生成
  },
  limit: {
    type: Number,
    default: 10
  },
  accept: {
    type: String,
    default: null // 如果为null，将根据category自动生成
  },
  multiple: {
    type: Boolean,
    default: true
  },
  autoUpload: {
    type: Boolean,
    default: true
  },
  maxSize: {
    type: Number,
    default: 10 // MB
  }
})

// 根据category获取允许的文件类型
const getAllowedExtensions = () => {
  if (props.category === 'qualification') {
    return QUALIFICATION_FILE_EXTENSIONS
  }
  // 默认使用项目附件的文件类型
  return PROJECT_FILE_EXTENSIONS
}

// 计算accept属性
const computedAccept = computed(() => {
  if (props.accept) {
    return props.accept
  }
  return getAcceptString(getAllowedExtensions())
})

// 计算提示文本
const computedTip = computed(() => {
  if (props.tip) {
    return props.tip
  }
  return getFileTypeTip(getAllowedExtensions(), props.maxSize)
})

const emit = defineEmits(['update:modelValue', 'success', 'error', 'remove'])

const uploadRef = ref(null)
const fileList = ref([...props.modelValue])

const uploadAction = computed(() => props.action)
const uploadHeaders = computed(() => {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
})

// 监听modelValue变化
watch(
  () => props.modelValue,
  newVal => {
    if (JSON.stringify(newVal) !== JSON.stringify(fileList.value)) {
      fileList.value = [...newVal]
    }
  },
  { deep: true }
)

// 监听fileList变化，同步到modelValue
watch(
  fileList,
  newVal => {
    emit('update:modelValue', [...newVal])
  },
  { deep: true }
)

const beforeUpload = file => {
  const maxSize = props.maxSize * 1024 * 1024 // 转换为字节
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过${props.maxSize}MB`)
    return false
  }
  
  // 验证文件类型
  const allowedExtensions = getAllowedExtensions()
  if (!validateFileType(file.name, allowedExtensions)) {
    ElMessage.error(`不支持的文件格式。支持的格式：${allowedExtensions.join(', ')}`)
    return false
  }
  
  return true
}

const handleUploadSuccess = (response, file) => {
  // 更新文件列表
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    fileList.value[index] = {
      ...fileList.value[index],
      ...file,
      url: response.url || response.file_url || response.path,
      id: response.id || response.file_id
    }
  }
  emit('success', response, file)
}

const handleUploadError = (error, file) => {
  const errorMsg = error?.response?.data?.detail || error?.message || '上传失败'
  ElMessage.error(errorMsg)

  // 移除失败的文件
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }

  emit('error', error, file)
}

const handleRemoveFile = file => {
  const index = fileList.value.findIndex(f => f.uid === file.uid || f.id === file.id)
  if (index > -1) {
    fileList.value.splice(index, 1)
    emit('remove', file)
  }
}

// 暴露方法供父组件调用
defineExpose({
  clearFiles: () => {
    fileList.value = []
    uploadRef.value?.clearFiles()
  },
  submit: () => {
    uploadRef.value?.submit()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.file-upload-wrapper {
  width: 100%;
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  width: 100%;

  .custom-upload {
    flex-shrink: 0;

    :deep(.el-upload-list) {
      display: none !important;
    }
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
      flex: 1;
    }

    .delete-btn {
      flex-shrink: 0;
      padding: 2px 4px;
      margin-left: $spacing-sm;
      min-width: auto;
      width: auto;
      height: auto;
    }
  }
}
</style>
