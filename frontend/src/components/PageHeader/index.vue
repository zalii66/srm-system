<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-title">
        <h2 class="title">{{ title }}</h2>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.extra" class="header-extra">
        <slot name="extra"></slot>
      </div>
    </div>
    <el-breadcrumb v-if="breadcrumbs && breadcrumbs.length > 0" class="breadcrumb">
      <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
        {{ item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.page-header {
  margin-bottom: $spacing-lg;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: $spacing-md;
  }

  .header-title {
    .title {
      font-size: 20px;
      font-weight: 500;
      color: $text-primary;
      margin: 0 0 $spacing-xs 0;
    }

    .subtitle {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
    }
  }

  .header-extra {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }

  .breadcrumb {
    font-size: 14px;
  }
}
</style>
