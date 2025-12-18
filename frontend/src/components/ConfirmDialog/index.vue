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
  >
    <div class="confirm-content">
      <el-icon v-if="icon" :size="iconSize" :color="iconColor" class="confirm-icon">
        <component :is="icon" />
      </el-icon>
      <div class="confirm-message">
        <slot>
          <p v-if="message">{{ message }}</p>
        </slot>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button :disabled="loading" @click="handleCancel">
          {{ cancelText }}
        </el-button>
        <el-button :type="confirmType" :loading="loading" @click="handleConfirm">
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Warning, QuestionFilled, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '提示'
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'warning',
    validator: value => ['warning', 'question', 'info', 'success'].includes(value)
  },
  width: {
    type: String,
    default: '420px'
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  confirmType: {
    type: String,
    default: 'primary'
  },
  loading: {
    type: Boolean,
    default: false
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
  iconSize: {
    type: Number,
    default: 24
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel', 'close'])

const dialogVisible = ref(props.modelValue)

// 根据类型选择图标和颜色
const icon = computed(() => {
  const iconMap = {
    warning: Warning,
    question: QuestionFilled,
    info: InfoFilled,
    success: SuccessFilled
  }
  return iconMap[props.type] || Warning
})

const iconColor = computed(() => {
  const colorMap = {
    warning: '#e6a23c',
    question: '#409eff',
    info: '#909399',
    success: '#67c23a'
  }
  return colorMap[props.type] || '#e6a23c'
})

// 监听外部modelValue变化
watch(
  () => props.modelValue,
  newVal => {
    dialogVisible.value = newVal
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

const handleCancel = () => {
  dialogVisible.value = false
  emit('cancel')
}

const handleConfirm = () => {
  emit('confirm')
}

// 暴露方法供父组件调用
defineExpose({
  open: () => {
    dialogVisible.value = true
  },
  close: () => {
    dialogVisible.value = false
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.confirm-content {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;

  .confirm-icon {
    flex-shrink: 0;
    margin-top: 4px;
  }

  .confirm-message {
    flex: 1;
    color: $text-primary;
    line-height: 1.6;

    p {
      margin: 0;
      word-break: break-word;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: $spacing-sm;
}
</style>
