<template>
  <el-tag :type="tagType" :effect="effect">
    <slot>{{ statusText }}</slot>
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: [String, Number],
    default: null
  },
  effect: {
    type: String,
    default: 'light'
  },
  statusType: {
    type: String,
    default: 'auto', // 'auto' | 'project' | 'supplier' | 'milestone' | 'quotation'
    validator: value => ['auto', 'project', 'supplier', 'milestone', 'quotation'].includes(value)
  }
})

// 项目状态映射（int类型：0已停止/1进行中/3竞标中/4已完成/5已取消）
const projectStatusMap = {
  0: { text: '已停止', type: 'info' },
  1: { text: '进行中', type: 'success' },
  3: { text: '竞标中', type: 'primary' },
  4: { text: '已完成', type: 'success' },
  5: { text: '已取消', type: 'danger' }
}

// 供应商审核状态映射（int类型：-1待审核/0审核失败/1审核通过）
const supplierStatusMap = {
  [-1]: { text: '待审核', type: 'warning' },
  0: { text: '审核失败', type: 'danger' },
  1: { text: '审核通过', type: 'success' }
}

// 里程碑状态映射（int类型：0待开始/1进行中/2已完成/3已延期/4已取消）
const milestoneStatusMap = {
  0: { text: '待开始', type: 'info' },
  1: { text: '进行中', type: 'primary' },
  2: { text: '已完成', type: 'success' },
  3: { text: '已延期', type: 'warning' },
  4: { text: '已取消', type: 'danger' }
}

// 报价状态映射（字符串类型：draft草稿/submitted已提交/selected中标/rejected未中标/cancelled已取消）
const quotationStatusMap = {
  draft: { text: '草稿', type: 'info' },
  submitted: { text: '已提交', type: 'primary' },
  selected: { text: '中标', type: 'success' },
  rejected: { text: '未中标', type: 'warning' },
  cancelled: { text: '已取消', type: 'danger' }
}

// 其他状态映射（字符串类型，用于供应商、报价等）
// 注意：报价状态已在 quotationStatusMap 中定义，这里避免重复定义
const statusMap = {
  pending: { text: '待审核', type: 'warning' },
  approved: { text: '已通过审核', type: 'success' },
  draft: { text: '草稿', type: 'info' },
  published: { text: '已发布', type: 'success' },
  bidding: { text: '进行中', type: 'primary' },
  evaluation: { text: '评标中', type: 'warning' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'danger' },
  closed: { text: '已关闭', type: 'info' },
  submitted: { text: '已提交', type: 'warning' },
  active: { text: '启用', type: 'success' },
  inactive: { text: '禁用', type: 'info' }
  // 注意：rejected 和 selected 已在 quotationStatusMap 中定义，避免冲突
}

const statusConfig = computed(() => {
  // 处理null、undefined或空字符串
  const statusValue = props.status
  if (statusValue === null || statusValue === undefined || statusValue === '') {
    return { text: '未知', type: 'info' }
  }

  // 如果是报价状态（字符串类型），优先使用报价状态映射
  if (props.statusType === 'quotation') {
    // 确保 statusValue 是字符串类型
    const statusStr = String(statusValue).toLowerCase()
    const quotationStatus = quotationStatusMap[statusStr]
    if (quotationStatus !== undefined) {
      return quotationStatus
    }
    // 如果报价状态映射中没有找到，返回默认值
    return { text: String(statusValue) || '未知', type: 'info' }
  }

  // 转换为数字类型
  const statusNum = typeof statusValue === 'number' ? statusValue : Number(statusValue)

  // 如果是有效的数字
  if (!isNaN(statusNum) && isFinite(statusNum)) {
    // 根据 statusType 决定优先检查哪个状态映射
    if (props.statusType === 'milestone') {
      // 明确指定为里程碑状态
      const milestoneStatus = milestoneStatusMap[statusNum]
      if (milestoneStatus !== undefined) {
        return milestoneStatus
      }
    } else if (props.statusType === 'project') {
      // 明确指定为项目状态，优先检查项目状态
      const projectStatus = projectStatusMap[statusNum]
      if (projectStatus !== undefined) {
        return projectStatus
      }
      // 如果项目状态不存在，再检查供应商状态
      const supplierStatus = supplierStatusMap[statusNum]
      if (supplierStatus !== undefined) {
        return supplierStatus
      }
    } else if (props.statusType === 'supplier') {
      // 明确指定为供应商状态，优先检查供应商状态
      const supplierStatus = supplierStatusMap[statusNum]
      if (supplierStatus !== undefined) {
        return supplierStatus
      }
      // 如果供应商状态不存在，再检查项目状态
      const projectStatus = projectStatusMap[statusNum]
      if (projectStatus !== undefined) {
        return projectStatus
      }
    } else {
      // auto 模式：根据状态值范围智能判断
      // 供应商状态：0-1
      // 项目状态：0, 1, 3, 4, 5
      // 如果状态值在 0-1 范围内，且项目状态和供应商状态都存在，优先使用供应商状态
      // 如果状态值不在 0-1 范围内（如 3, 4, 5），则使用项目状态
      if (statusNum >= 0 && statusNum <= 1) {
        // 0 和 1 两个值在两种状态中都有，优先检查供应商状态
        const supplierStatus = supplierStatusMap[statusNum]
        if (supplierStatus !== undefined) {
          return supplierStatus
        }
        // 如果供应商状态不存在，使用项目状态
        const projectStatus = projectStatusMap[statusNum]
        if (projectStatus !== undefined) {
          return projectStatus
        }
      } else {
        // 状态值 3, 4, 5 等，只可能是项目状态
        const projectStatus = projectStatusMap[statusNum]
        if (projectStatus !== undefined) {
          return projectStatus
        }
      }
    }

    // 如果都不匹配，返回默认显示
    return { text: `状态${statusNum}`, type: 'info' }
  }

  // 如果是字符串类型，使用原有映射
  const stringStatus = statusMap[statusValue]
  if (stringStatus !== undefined) {
    return stringStatus
  }

  return { text: String(statusValue) || '未知', type: 'info' }
})

const statusText = computed(() => {
  return statusConfig.value.text
})

const tagType = computed(() => {
  return statusConfig.value.type
})
</script>

<style scoped lang="scss">
.el-tag {
  border-radius: 4px;
}
</style>
