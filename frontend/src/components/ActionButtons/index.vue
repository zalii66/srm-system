<template>
  <div class="action-buttons">
    <el-button
      v-for="button in visibleButtons"
      :key="button.key"
      :type="button.type || 'default'"
      :size="button.size || 'small'"
      :disabled="button.disabled"
      :loading="button.loading"
      :icon="button.icon"
      :link="button.link"
      @click="handleClick(button)"
    >
      {{ button.label }}
    </el-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  buttons: {
    type: Array,
    required: true,
    default: () => [],
    validator: value => {
      if (!Array.isArray(value)) return false
      return value.every(
        btn =>
          btn &&
          typeof btn === 'object' &&
          btn.key &&
          btn.label &&
          typeof btn.handler === 'function'
      )
    }
  },
  // 权限控制：传入需要检查的权限列表，只有有权限的按钮才显示
  permissions: {
    type: Array,
    default: () => []
  },
  // 权限映射：按钮key到权限的映射，如 { 'edit': 'project:edit' }
  permissionMap: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['action'])

// 过滤出有权限的按钮
const visibleButtons = computed(() => {
  return props.buttons.filter(button => {
    // 如果没有设置权限，显示所有按钮
    if (!props.permissions || props.permissions.length === 0) {
      return true
    }

    // 如果按钮没有设置权限要求，显示
    const requiredPermission = props.permissionMap[button.key]
    if (!requiredPermission) {
      return true
    }

    // 检查用户是否有权限
    return props.permissions.includes(requiredPermission)
  })
})

const handleClick = button => {
  if (button.handler) {
    button.handler()
  }
  emit('action', button.key, button)
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.action-buttons {
  display: flex;
  gap: $spacing-xxs;
  flex-wrap: nowrap;
  align-items: center;

  .el-button {
    margin-right: 0;
    white-space: nowrap;
    min-width: auto;

    // 统一 small 按钮样式，确保按钮紧凑显示，复用系统风格
    &.el-button--small {
      padding: 3px $spacing-sm;
      font-size: 12px;
      height: auto;
      line-height: 1.5;
      border-radius: $border-radius-base;
    }
  }
}
</style>
