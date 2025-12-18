<template>
  <div class="milestone-timeline">
    <div v-if="milestones.length === 0" class="empty-state">
      <el-empty description="暂无时间节点" :image-size="100" />
    </div>

    <div v-else class="timeline-container">
      <div
        v-for="(milestone, index) in milestones"
        :key="milestone.id"
        class="milestone-item"
        :class="getMilestoneClass(milestone)"
      >
        <div class="milestone-icon">
          <el-icon v-if="milestone.status === 2" class="icon-completed">
            <Check />
          </el-icon>
          <el-icon v-else-if="milestone.status === 1" class="icon-in-progress">
            <Loading />
          </el-icon>
          <el-icon v-else-if="milestone.status === 3" class="icon-delayed">
            <Warning />
          </el-icon>
          <el-icon v-else class="icon-pending">
            <CircleCheck />
          </el-icon>
        </div>

        <div class="milestone-content">
          <div class="milestone-header">
            <span class="milestone-name">{{ milestone.milestone_name }}</span>
            <span v-if="milestone.is_critical" class="critical-badge">关键</span>
            <StatusTag
              :status="milestone.status"
              status-type="milestone"
              class="status-tag"
            />
          </div>

          <div v-if="milestone.description" class="milestone-description">
            {{ milestone.description }}
          </div>

          <div class="milestone-dates">
            <div v-if="milestone.planned_date" class="date-item">
              <span class="date-label">计划时间：</span>
              <span class="date-value">{{ formatDate(milestone.planned_date) }}</span>
            </div>
            <div v-if="milestone.actual_date" class="date-item">
              <span class="date-label">实际完成：</span>
              <span class="date-value completed">{{ formatDate(milestone.actual_date) }}</span>
            </div>
            <div v-if="milestone.status === 1 && milestone.planned_date" class="date-item">
              <span class="date-label">剩余时间：</span>
              <span class="date-value remaining">{{ getRemainingTime(milestone.planned_date) }}</span>
            </div>
          </div>

          <div v-if="milestone.progress > 0" class="milestone-progress">
            <el-progress
              :percentage="milestone.progress"
              :stroke-width="6"
              :color="getProgressColor(milestone.progress)"
            />
          </div>

          <!-- 操作按钮（仅管理人员可见） -->
          <div v-if="!readonly && isProjectManager" class="milestone-actions">
            <el-button
              v-if="milestone.status !== 2"
              type="primary"
              size="small"
              link
              @click="handleComplete(milestone)"
            >
              标记完成
            </el-button>
            <el-button
              type="warning"
              size="small"
              link
              @click="handleEdit(milestone)"
            >
              编辑
            </el-button>
            <el-button
              v-if="milestone.status === 0 || milestone.status === 4"
              type="danger"
              size="small"
              link
              @click="handleDelete(milestone)"
            >
              删除
            </el-button>
          </div>
        </div>

        <!-- 连接线 -->
        <div v-if="index < milestones.length - 1" class="timeline-line" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Loading, Warning, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StatusTag } from '@/components'
import { formatDate } from '@/utils'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  milestones: {
    type: Array,
    default: () => []
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['complete', 'edit', 'delete'])

const userStore = useUserStore()

const isProjectManager = computed(() => {
  return userStore.isSuperuser || userStore.roles?.includes('project_manager')
})

const getMilestoneClass = milestone => {
  return {
    'milestone-completed': milestone.status === 2,
    'milestone-in-progress': milestone.status === 1,
    'milestone-delayed': milestone.status === 3,
    'milestone-pending': milestone.status === 0,
    'milestone-cancelled': milestone.status === 4
  }
}

const getProgressColor = percentage => {
  if (percentage < 30) return '#909399'
  if (percentage < 60) return '#E6A23C'
  if (percentage < 100) return '#409EFF'
  return '#67C23A'
}

const getRemainingTime = plannedDate => {
  const now = new Date()
  const planned = new Date(plannedDate)
  const diff = planned - now

  if (diff <= 0) return '已过期'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  if (days > 0) return `${days}天${hours}小时`
  if (hours > 0) return `${hours}小时${minutes}分钟`
  return `${minutes}分钟`
}

const handleComplete = milestone => {
  emit('complete', milestone)
}

const handleEdit = milestone => {
  emit('edit', milestone)
}

const handleDelete = async milestone => {
  try {
    await ElMessageBox.confirm(
      `确定要删除节点"${milestone.milestone_name}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete', milestone)
  } catch {
    // 用户取消
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.milestone-timeline {
  .empty-state {
    padding: $spacing-xl;
    text-align: center;
  }

  .timeline-container {
    position: relative;
    padding-left: $spacing-lg;
  }

  .milestone-item {
    position: relative;
    padding-bottom: $spacing-xl;
    display: flex;
    align-items: flex-start;
    gap: $spacing-md;

    .milestone-icon {
      position: absolute;
      left: -$spacing-lg;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #fff;
      border: 2px solid $border-color;
      z-index: 1;

      .el-icon {
        font-size: 18px;
      }

      .icon-completed {
        color: $success-color;
      }

      .icon-in-progress {
        color: $primary-color;
        animation: rotate 2s linear infinite;
      }

      .icon-delayed {
        color: $warning-color;
      }

      .icon-pending {
        color: $text-secondary;
      }
    }

    &.milestone-completed .milestone-icon {
      border-color: $success-color;
      background: $success-color;
      color: #fff;
    }

    &.milestone-in-progress .milestone-icon {
      border-color: $primary-color;
      background: $primary-color;
      color: #fff;
    }

    &.milestone-delayed .milestone-icon {
      border-color: $warning-color;
      background: $warning-color;
      color: #fff;
    }

    .milestone-content {
      flex: 1;
      padding: $spacing-md;
      background: #fff;
      border-radius: $border-radius-base;
      border: 1px solid $border-color-lighter;

      .milestone-header {
        display: flex;
        align-items: center;
        gap: $spacing-sm;
        margin-bottom: $spacing-xs;

        .milestone-name {
          font-size: 16px;
          font-weight: 500;
          color: $text-primary;
        }

        .critical-badge {
          padding: 2px $spacing-xs;
          background: $warning-color;
          color: #fff;
          border-radius: $border-radius-small;
          font-size: 12px;
        }

        .status-tag {
          margin-left: auto;
        }
      }

      .milestone-description {
        margin-bottom: $spacing-sm;
        color: $text-secondary;
        font-size: 14px;
      }

      .milestone-dates {
        margin-bottom: $spacing-sm;
        font-size: 14px;

        .date-item {
          margin-bottom: $spacing-xs;

          .date-label {
            color: $text-secondary;
          }

          .date-value {
            color: $text-primary;

            &.completed {
              color: $success-color;
            }

            &.remaining {
              color: $warning-color;
              font-weight: 500;
            }
          }
        }
      }

      .milestone-progress {
        margin-bottom: $spacing-sm;
      }

      .milestone-actions {
        display: flex;
        gap: $spacing-sm;
        padding-top: $spacing-sm;
        border-top: 1px solid $border-color-lighter;
      }
    }

    .timeline-line {
      position: absolute;
      left: -$spacing-lg + 15px;
      top: 32px;
      bottom: 0;
      width: 2px;
      background: $border-color;
      z-index: 0;
    }

    &:last-child .timeline-line {
      display: none;
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

