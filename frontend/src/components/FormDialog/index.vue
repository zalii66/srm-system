<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :draggable="draggable"
    @close="handleClose"
    @opened="handleOpened"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      class="form-container"
    >
      <slot :form-data="formData" :form-ref="formRef"></slot>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button :disabled="loading" @click="handleCancel">
          {{ cancelText }}
        </el-button>
        <el-button type="primary" :loading="loading" @click="handleConfirm">
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '表单'
  },
  width: {
    type: String,
    default: '600px'
  },
  formData: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    default: () => ({})
  },
  labelWidth: {
    type: String,
    default: '120px'
  },
  labelPosition: {
    type: String,
    default: 'right',
    validator: value => ['left', 'right', 'top'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  closeOnClickModal: {
    type: Boolean,
    default: false
  },
  closeOnPressEscape: {
    type: Boolean,
    default: true
  },
  showClose: {
    type: Boolean,
    default: true
  },
  draggable: {
    type: Boolean,
    default: false
  },
  // 是否在提交前验证表单
  validateOnSubmit: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel', 'close', 'opened', 'closed'])

const formRef = ref(null)
const dialogVisible = ref(props.modelValue)

// 监听外部modelValue变化
watch(
  () => props.modelValue,
  newVal => {
    dialogVisible.value = newVal
    if (newVal) {
      nextTick(() => {
        // 打开对话框时，如果有表单引用，清除验证
        if (formRef.value) {
          formRef.value.clearValidate()
        }
      })
    }
  }
)

// 监听内部dialogVisible变化，同步到外部
watch(dialogVisible, newVal => {
  emit('update:modelValue', newVal)
})

const handleClose = () => {
  dialogVisible.value = false
  emit('close')
}

const handleOpened = () => {
  emit('opened')
}

const handleClosed = () => {
  // 清除表单验证
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  emit('closed')
}

const handleCancel = () => {
  dialogVisible.value = false
  emit('cancel')
}

const handleConfirm = async () => {
  // 如果启用验证，先验证表单
  if (props.validateOnSubmit && formRef.value) {
    try {
      await formRef.value.validate()
      emit('confirm', props.formData)
    } catch (error) {
      // 验证失败，不提交
    }
  } else {
    emit('confirm', props.formData)
  }
}

// 暴露方法供父组件调用
defineExpose({
  validate: () => {
    return formRef.value?.validate()
  },
  clearValidate: () => {
    formRef.value?.clearValidate()
  },
  resetFields: () => {
    formRef.value?.resetFields()
  },
  validateField: props => {
    return formRef.value?.validateField(props)
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: $spacing-sm;
}
</style>
