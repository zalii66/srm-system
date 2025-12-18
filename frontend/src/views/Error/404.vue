<template>
  <div class="error-container">
    <div class="error-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: $bg-color-page;
}

.error-content {
  text-align: center;

  .error-code {
    font-size: 120px;
    font-weight: bold;
    color: $primary-color;
    margin-bottom: $spacing-md;
  }

  .error-message {
    font-size: 20px;
    color: $text-secondary;
    margin-bottom: $spacing-xl;
  }
}
</style>
