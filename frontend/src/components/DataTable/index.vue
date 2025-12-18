<template>
  <el-card class="data-table-card">
    <el-table v-loading="loading" :data="data" :stripe="stripe" :border="border">
      <slot></slot>
    </el-table>

    <div v-if="showPagination" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="currentPageSize"
        :total="total"
        :page-sizes="pageSizes"
        :layout="layout"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  stripe: {
    type: Boolean,
    default: true
  },
  border: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    default: 0
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

defineOptions({
  inheritAttrs: false
})

const emit = defineEmits(['update:page', 'update:pageSize', 'change'])

const currentPage = computed({
  get: () => props.page,
  set: val => emit('update:page', val)
})

const currentPageSize = computed({
  get: () => props.pageSize,
  set: val => emit('update:pageSize', val)
})

const handleSizeChange = () => {
  emit('change')
}

const handleCurrentChange = () => {
  emit('change')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.data-table-card {
  .pagination-container {
    margin-top: $spacing-lg;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
