<template>
  <el-card class="search-form-card">
    <el-form :model="formModel" :inline="inline" :label-width="labelWidth" class="search-form">
      <slot></slot>
      <el-form-item v-if="showButtons" class="search-buttons">
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  inline: {
    type: Boolean,
    default: true
  },
  labelWidth: {
    type: String,
    default: '100px'
  },
  showButtons: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const formModel = computed({
  get: () => props.modelValue,
  set: val => emit('update:modelValue', val)
})

const handleSearch = () => {
  emit('search')
}

const handleReset = () => {
  emit('reset')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.search-form-card {
  margin-bottom: $spacing-lg;
  background: $bg-color;
  border-radius: $border-radius-base;

  :deep(.el-card__body) {
    padding: $spacing-lg;
  }
}

.search-form {
  :deep(.el-form-item) {
    margin-bottom: 0;
    margin-right: $spacing-lg;
    vertical-align: middle;
    display: inline-flex;
    align-items: center;

    .el-form-item__label {
      color: $text-primary;
      font-weight: 500;
      line-height: 32px;
      padding-bottom: 0;
    }

    .el-form-item__content {
      line-height: 32px;
      display: flex;
      align-items: center;
    }

    // 统一输入框宽度和内边距
    .el-input {
      width: 200px;

      .el-input__wrapper {
        padding-top: 1px;
        padding-bottom: 1px;
        padding-left: 11px;
        padding-right: 11px;
        min-height: 32px;
        box-sizing: border-box;
      }

      .el-input__inner {
        height: 30px;
        line-height: 30px;
        padding: 0;
      }
    }

    // 下拉框内边距统一
    .el-select {
      width: 200px;

      .el-input__wrapper {
        padding-top: 1px;
        padding-bottom: 1px;
        padding-left: 11px;
        padding-right: 11px;
        min-height: 32px;
        box-sizing: border-box;
      }

      .el-input__inner {
        height: 30px;
        line-height: 30px;
        padding: 0;
      }
    }

    // 状态选择框宽度增加
    &.status-select {
      .el-select {
        width: 200px;
      }
    }
  }

  .search-buttons {
    margin-left: $spacing-md;
    margin-bottom: 0;
    vertical-align: middle;
    display: inline-flex;
    align-items: center;

    .el-button {
      margin-right: $spacing-sm;
      height: 32px;
      padding: 7px 15px;
      line-height: 1;
    }
  }
}
</style>
