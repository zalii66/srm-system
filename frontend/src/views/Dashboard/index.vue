<template>
  <div class="dashboard-container" v-loading="loading">
    <PageHeader title="仪表盘" subtitle="系统概览和统计信息" />

    <!-- 管理员/项目经理视图 -->
    <template v-if="!isSupplier">
      <!-- 第一行：核心指标卡片（6个） -->
      <div class="stats-cards">
        <el-card 
          class="stat-card" 
          @click="handleCardClick('/projects')"
          v-if="hasPermission('project:view')"
        >
          <div class="stat-content">
            <div class="stat-icon primary">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.projects_count || 0 }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>

        <el-card 
          class="stat-card" 
          @click="handleCardClick('/projects', { status: '1' })"
          v-if="hasPermission('project:view')"
        >
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon><Promotion /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.ongoing_projects_count || 0 }}</div>
              <div class="stat-label">进行中的项目</div>
            </div>
          </div>
        </el-card>

        <el-card 
          class="stat-card" 
          @click="handleCardClick('/suppliers', { status: '-1' })"
          v-if="hasPermission('supplier:audit')"
        >
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_suppliers_count || 0 }}</div>
              <div class="stat-label">待审核供应商</div>
            </div>
          </div>
        </el-card>

        <el-card 
          class="stat-card" 
          @click="handleCardClick('/quotations')"
          v-if="hasPermission('quotation:view')"
        >
          <div class="stat-content">
            <div class="stat-icon info">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.quotations_count || 0 }}</div>
              <div class="stat-label">报价总数</div>
            </div>
          </div>
        </el-card>
        
        <!-- 添加供应商总数卡片，仅管理员可见 -->
        <el-card 
          class="stat-card" 
          @click="handleCardClick('/suppliers')"
          v-if="hasPermission('supplier:view')"
        >
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.suppliers_count || 0 }}</div>
              <div class="stat-label">供应商总数</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 第二行：图表区域 -->
      <div class="charts-row">
        <!-- 项目状态分布（饼状图） -->
        <el-card 
          class="chart-card" 
          v-if="Object.keys(stats.project_status_stats || {}).length > 0 && hasPermission('project:view')"
        >
          <template #header>
            <span>项目状态分布</span>
          </template>
          <PieChart 
            :data="projectStatusChartData" 
            :height="'300px'"
            v-if="projectStatusChartData.length > 0"
          />
        </el-card>

        <!-- 报价状态统计（饼状图） -->
        <el-card 
          class="chart-card" 
          v-if="Object.keys(stats.quotation_status_stats || {}).length > 0 && hasPermission('quotation:view')"
        >
          <template #header>
            <span>报价状态统计</span>
          </template>
          <PieChart 
            :data="quotationStatusChartData" 
            :height="'300px'"
            v-if="quotationStatusChartData.length > 0"
          />
        </el-card>
      </div>

      <!-- 第三行：待办事项和最近活动 -->
      <div class="tasks-row">
        <!-- 待办事项 -->
        <el-card class="tasks-card">
          <template #header>
            <span>待办事项</span>
          </template>
          
          <!-- 待审核供应商 -->
          <div 
            class="task-section" 
            v-if="stats.pending_tasks?.pending_suppliers?.length > 0 && hasPermission('supplier:audit')"
          >
            <div class="task-section-title">
              <el-icon><User /></el-icon>
              <span>待审核供应商（{{ stats.pending_tasks.pending_suppliers.length }}）</span>
            </div>
            <div class="task-list">
              <div
                v-for="supplier in stats.pending_tasks.pending_suppliers"
                :key="supplier.id"
                class="task-item"
                @click="handleViewSupplier(supplier.id)"
              >
                <div class="task-item-content">
                  <div class="task-item-title">{{ supplier.company_name }}</div>
                  <div class="task-item-meta">
                    <span>联系人：{{ supplier.contact_person }}</span>
                    <span>提交时间：{{ formatDate(supplier.created_at) }}</span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click.stop="handleAuditSupplier(supplier.id)">
                  审核
                </el-button>
              </div>
            </div>
          </div>

          <!-- 即将截止的项目 -->
          <div 
            class="task-section" 
            v-if="stats.pending_tasks?.upcoming_deadlines?.length > 0 && hasPermission('project:view')"
          >
            <div class="task-section-title">
              <el-icon><Clock /></el-icon>
              <span>即将截止的项目（{{ stats.pending_tasks.upcoming_deadlines.length }}）</span>
            </div>
            <div class="task-list">
              <div
                v-for="project in stats.pending_tasks.upcoming_deadlines"
                :key="project.id"
                class="task-item"
                :class="{ 'urgent': project.remaining_hours < 24 }"
                @click="handleViewProject(project.id)"
              >
                <div class="task-item-content">
                  <div class="task-item-title">{{ project.project_name }}</div>
                  <div class="task-item-meta">
                    <span>截止时间：{{ formatDateTime(project.bidding_deadline) }}</span>
                    <span class="remaining-time" :class="{ 'urgent': project.remaining_hours < 24 }">
                      剩余：{{ formatRemainingTime(project.remaining_hours) }}
                    </span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click.stop="handleViewProject(project.id)">
                  查看
                </el-button>
              </div>
            </div>
          </div>

          <!-- 待评审报价 -->
          <div 
            class="task-section" 
            v-if="stats.pending_tasks?.pending_quotations?.length > 0 && hasPermission('quotation:evaluate')"
          >
            <div class="task-section-title">
              <el-icon><List /></el-icon>
              <span>待评审报价（{{ stats.pending_tasks.pending_quotations.length }}）</span>
            </div>
            <div class="task-list">
              <div
                v-for="quotation in stats.pending_tasks.pending_quotations"
                :key="quotation.id"
                class="task-item"
                @click="handleViewQuotation(quotation.id)"
              >
                <div class="task-item-content">
                  <div class="task-item-title">{{ quotation.project_name }}</div>
                  <div class="task-item-meta">
                    <span>供应商：{{ quotation.supplier_name }}</span>
                    <span>报价金额：{{ formatCurrency(quotation.total_amount) }}</span>
                    <span>提交时间：{{ formatDateTime(quotation.submitted_at) }}</span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click.stop="handleViewQuotation(quotation.id)">
                  评审
                </el-button>
              </div>
            </div>
          </div>

          <el-empty v-if="!hasPendingTasks" description="暂无待办事项" :image-size="80" />
        </el-card>

        <!-- 最近活动 -->
        <el-card 
          class="activities-card"
          v-if="isSuperuser || hasPermission('project:view')"
        >
          <template #header>
            <span>最近活动</span>
          </template>
          <el-table
            :data="stats.recent_activities || []"
            style="width: 100%"
            :empty-text="'暂无活动记录'"
            :row-class-name="'activity-row'"
            :show-overflow-tooltip="true"
          >
            <el-table-column prop="created_at" label="时间" width="120">
              <template #default="{ row }">
                {{ formatRelativeTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户" width="100" />
            <el-table-column prop="action" label="操作" width="80">
              <template #default="{ row }">
                {{ getActivityActionText(row.action) }}
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-card>
      </div>
    </template>

    <!-- 供应商视图：参与的项目进度 -->
    <template v-else>
      <!-- 第一行：核心指标卡片（5个） -->
      <div class="stats-cards">
        <el-card 
          class="stat-card" 
          @click="handleCardClick('/supplier/participated-projects')"
          v-if="hasPermission('project:view')"
        >
          <div class="stat-content">
            <div class="stat-icon primary">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.participated_projects_count || 0 }}</div>
              <div class="stat-label">参与项目数</div>
            </div>
          </div>
        </el-card>

        <el-card 
          class="stat-card" 
          @click="handleCardClick('/supplier/latest-projects')"
          v-if="hasPermission('quotation:create')"
        >
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon><EditPen /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_quotation_projects_count || 0 }}</div>
              <div class="stat-label">待报价项目</div>
            </div>
          </div>
        </el-card>

        <el-card 
          class="stat-card" 
          @click="handleCardClick('/quotations', { status: 'submitted' })"
          v-if="hasPermission('quotation:view')"
        >
          <div class="stat-content">
            <div class="stat-icon info">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.submitted_quotations_count || 0 }}</div>
              <div class="stat-label">已提交报价</div>
            </div>
          </div>
        </el-card>

        <el-card 
          class="stat-card" 
          @click="handleCardClick('/quotations', { status: 'selected' })"
          v-if="hasPermission('quotation:view')"
        >
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.winning_projects_count || 0 }}</div>
              <div class="stat-label">中标项目数</div>
            </div>
          </div>
        </el-card>

      </div>


      <!-- 第三行：待办事项和参与项目列表 -->
      <div class="tasks-row">
        <!-- 待办事项 -->
        <el-card class="tasks-card">
          <template #header>
            <span>待办事项</span>
          </template>
          
          <!-- 待报价项目 -->
          <div 
            class="task-section" 
            v-if="stats.pending_quotation_projects?.length > 0 && hasPermission('quotation:create')"
          >
            <div class="task-section-title">
              <el-icon><EditPen /></el-icon>
              <span>待报价项目（{{ stats.pending_quotation_projects.length }}）</span>
            </div>
            <div class="task-list">
              <div
                v-for="project in stats.pending_quotation_projects"
                :key="project.id"
                class="task-item"
                :class="{ 'urgent': project.remaining_hours < 24 }"
                @click="handleViewProject(project.id)"
              >
                <div class="task-item-content">
                  <div class="task-item-title">{{ project.project_name }}</div>
                  <div class="task-item-meta">
                    <span>截止时间：{{ formatDateTime(project.bidding_deadline) }}</span>
                    <span class="remaining-time" :class="{ 'urgent': project.remaining_hours < 24 }">
                      剩余：{{ formatRemainingTime(project.remaining_hours) }}
                    </span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click.stop="handleQuotationProject(project.id)">
                  立即报价
                </el-button>
              </div>
            </div>
          </div>

          <!-- 草稿报价 -->
          <div 
            class="task-section" 
            v-if="stats.draft_quotations?.length > 0 && hasPermission('quotation:edit')"
          >
            <div class="task-section-title">
              <el-icon><Document /></el-icon>
              <span>草稿报价（{{ stats.draft_quotations.length }}）</span>
            </div>
            <div class="task-list">
              <div
                v-for="quotation in stats.draft_quotations"
                :key="quotation.id"
                class="task-item"
                @click="handleEditQuotation(quotation.id)"
              >
                <div class="task-item-content">
                  <div class="task-item-title">{{ quotation.project_name }}</div>
                  <div class="task-item-meta">
                    <span>报价金额：{{ formatCurrency(quotation.total_amount) }}</span>
                    <span>创建时间：{{ formatDateTime(quotation.created_at) }}</span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click.stop="handleEditQuotation(quotation.id)">
                  继续编辑
                </el-button>
              </div>
            </div>
          </div>

          <el-empty v-if="!hasSupplierPendingTasks" description="暂无待办事项" :image-size="80" />
        </el-card>

        <!-- 参与项目列表 -->
        <el-card 
          class="projects-card"
          v-if="hasPermission('project:view')"
        >
          <template #header>
            <span>参与项目列表</span>
          </template>
          <div class="projects-list" v-if="stats.participated_projects?.length > 0">
            <div
              v-for="project in stats.participated_projects.slice(0, 5)"
              :key="project.id"
              class="project-item"
              @click="handleViewProject(project.id)"
            >
              <div class="project-header">
                <div class="project-title">
                  <span class="project-no">{{ project.project_no }}</span>
                  <span class="project-name">{{ project.project_name }}</span>
                </div>
                <StatusTag :status="project.status" status-type="project" />
              </div>

              <div class="progress-section">
                <div class="progress-info">
                  <span class="progress-label">项目进度</span>
                  <span class="progress-percent">{{ project.progress }}%</span>
                </div>
                <el-progress
                  :percentage="project.progress"
                  :color="getProgressColor(project.progress)"
                  :stroke-width="8"
                />
              </div>

              <div class="project-details">
                <div v-if="project.quotation_status" class="detail-item">
                  <span class="detail-label">报价状态：</span>
                  <StatusTag :status="project.quotation_status" status-type="quotation" />
                </div>
                <div v-if="project.quotation_amount" class="detail-item">
                  <span class="detail-label">报价金额：</span>
                  <span class="detail-value">{{ formatCurrency(project.quotation_amount) }}</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无参与的项目" :image-size="80" />
        </el-card>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, Document, List, Promotion, 
  Clock, EditPen, Trophy
} from '@element-plus/icons-vue'
import { PageHeader, StatusTag } from '@/components'
import PieChart from '@/components/PieChart/index.vue'
import { formatDate, formatCurrency } from '@/utils'
import { getDashboardStats } from '@/api/dashboard'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

// 从用户store中解构权限检查方法
const { hasPermission, isSuperuser, roles } = userStore

const stats = ref({
  suppliers_count: 0,
  projects_count: 0,
  ongoing_projects_count: 0,
  pending_suppliers_count: 0,
  new_projects_this_month: 0,
  new_projects_last_month: 0,
  quotations_count: 0,
  project_status_stats: {},
  quotation_status_stats: {},
  pending_tasks: {},
  recent_activities: [],
  participated_projects_count: 0,
  pending_quotation_projects_count: 0,
  submitted_quotations_count: 0,
  winning_projects_count: 0,
  participated_projects: [],
  pending_quotation_projects: [],
  draft_quotations: []
})

const loading = ref(false)

const isSupplier = computed(() => {
  if (!userStore.roles || !Array.isArray(userStore.roles)) return false
  return userStore.roles.includes('supplier') && !userStore.isSuperuser
})

const hasPendingTasks = computed(() => {
  const tasks = stats.value.pending_tasks || {}
  return (
    (tasks.pending_suppliers?.length || 0) > 0 ||
    (tasks.upcoming_deadlines?.length || 0) > 0 ||
    (tasks.pending_quotations?.length || 0) > 0
  )
})

const hasSupplierPendingTasks = computed(() => {
  return (
    (stats.value.pending_quotation_projects?.length || 0) > 0 ||
    (stats.value.draft_quotations?.length || 0) > 0
  )
})

// 项目状态饼图数据
const projectStatusChartData = computed(() => {
  const statusStats = stats.value.project_status_stats || {}
  const statusMap = {
    0: '已停止',
    1: '进行中',
    3: '竞标中',
    4: '已完成',
    5: '已取消'
  }
  const colors = {
    0: '#909399',
    1: '#67C23A',
    3: '#409EFF',
    4: '#67C23A',
    5: '#F56C6C'
  }
  
  return Object.entries(statusStats).map(([status, count]) => ({
    value: count,
    name: statusMap[status] || `状态${status}`,
    itemStyle: {
      color: colors[status] || '#909399'
    }
  }))
})

// 报价状态饼图数据
const quotationStatusChartData = computed(() => {
  const statusStats = stats.value.quotation_status_stats || {}
  const statusMap = {
    draft: '草稿',
    submitted: '已提交',
    selected: '中标',
    rejected: '未中标',
    cancelled: '已取消'
  }
  const colors = {
    draft: '#909399',
    submitted: '#409EFF',
    selected: '#67C23A',
    rejected: '#E6A23C',
    cancelled: '#F56C6C'
  }
  
  return Object.entries(statusStats).map(([status, count]) => ({
    value: count,
    name: statusMap[status] || status,
    itemStyle: {
      color: colors[status] || '#909399'
    }
  }))
})

const fetchStats = async () => {
  loading.value = true
  try {
    const data = await getDashboardStats()
    stats.value = { ...stats.value, ...data }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const handleCardClick = (path, query = {}) => {
  router.push({ path, query })
}

const handleViewProject = projectId => {
  router.push(`/project/detail/${projectId}`)
}

const handleViewSupplier = supplierId => {
  router.push(`/supplier/detail/${supplierId}`)
}

const handleAuditSupplier = supplierId => {
  router.push(`/supplier/detail/${supplierId}?action=audit`)
}

const handleViewQuotation = quotationId => {
  router.push(`/quotation/detail/${quotationId}`)
}

const handleQuotationProject = projectId => {
  router.push(`/project/${projectId}/requirements`)
}

const handleEditQuotation = quotationId => {
  router.push(`/quotation/edit/${quotationId}`)
}

const formatDateTime = dateStr => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return formatDate(dateStr) + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatRemainingTime = hours => {
  if (!hours && hours !== 0) return ''
  if (hours < 24) {
    return `${hours} 小时`
  }
  const days = Math.floor(hours / 24)
  const remainingHours = hours % 24
  if (remainingHours > 0) {
    return `${days} 天 ${remainingHours} 小时`
  }
  return `${days} 天`
}

const formatRelativeTime = dateStr => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`
  return formatDateTime(dateStr)
}

const getActivityActionText = action => {
  const actionMap = {
    create: '创建',
    update: '更新',
    delete: '删除',
    audit: '审核',
    evaluate: '评审',
    submit: '提交',
    cancel: '取消'
  }
  return actionMap[action] || action
}

const getProgressColor = percentage => {
  if (percentage < 30) return '#909399'
  if (percentage < 60) return '#E6A23C'
  if (percentage < 100) return '#409EFF'
  return '#67C23A'
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.dashboard-container {
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: $spacing-lg;
    margin-bottom: $spacing-lg;
  }

  .stat-card {
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .stat-content {
      display: flex;
      align-items: center;
      gap: $spacing-lg;
    }

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: $border-radius-base;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: #ffffff;
      background: linear-gradient(135deg, var(--icon-color-start), var(--icon-color-end));

      &.primary {
        --icon-color-start: #409eff;
        --icon-color-end: #66b1ff;
      }

      &.success {
        --icon-color-start: #67c23a;
        --icon-color-end: #85ce61;
      }

      &.warning {
        --icon-color-start: #e6a23c;
        --icon-color-end: #ebb563;
      }

      &.danger {
        --icon-color-start: #f56c6c;
        --icon-color-end: #f78989;
      }

      &.info {
        --icon-color-start: #909399;
        --icon-color-end: #a6a9ad;
      }
    }

    .stat-info {
      flex: 1;

      .stat-value {
        font-size: 28px;
        font-weight: 500;
        color: $text-primary;
        margin-bottom: $spacing-xs;
      }

      .stat-label {
        font-size: 14px;
        color: $text-secondary;
      }

      .stat-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: $spacing-xs;
        font-size: 12px;

        .trend-up {
          color: $success-color;
        }

        .trend-down {
          color: $danger-color;
        }

        .trend-neutral {
          color: $text-secondary;
        }
      }
    }
  }

  .charts-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: $spacing-lg;
    margin-bottom: $spacing-lg;
  }

  .chart-card {
    .status-stats {
      display: flex;
      flex-wrap: wrap;
      gap: $spacing-lg;

      .status-item {
        display: flex;
        align-items: center;
        gap: $spacing-sm;

        .status-count {
          color: $text-secondary;
          font-size: 14px;
        }
      }
    }
  }

  .tasks-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: $spacing-lg;
    margin-bottom: $spacing-lg;
  }

  .tasks-card,
  .activities-card,
  .projects-card {
    min-height: 400px;

    :deep(.el-table) {
      .el-table__body-wrapper {
        overflow-x: hidden !important;
      }
    }


    .task-section {
      margin-bottom: $spacing-lg;

      &:last-child {
        margin-bottom: 0;
      }

      .task-section-title {
        display: flex;
        align-items: center;
        gap: $spacing-sm;
        font-size: 16px;
        font-weight: 500;
        color: $text-primary;
        margin-bottom: $spacing-md;
      }

      .task-list {
        .task-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: $spacing-md;
          border: 1px solid $border-color-lighter;
          border-radius: $border-radius-base;
          margin-bottom: $spacing-sm;
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            border-color: $primary-color;
            background-color: rgba(64, 158, 255, 0.05);
          }

          &.urgent {
            border-color: $danger-color;
            background-color: rgba(245, 108, 108, 0.05);
          }

          &:last-child {
            margin-bottom: 0;
          }

          .task-item-content {
            flex: 1;

            .task-item-title {
              font-size: 14px;
              font-weight: 500;
              color: $text-primary;
              margin-bottom: $spacing-xs;
            }

            .task-item-meta {
              display: flex;
              flex-wrap: wrap;
              gap: $spacing-md;
              font-size: 12px;
              color: $text-secondary;

              .remaining-time {
                &.urgent {
                  color: $danger-color;
                  font-weight: 500;
                }
              }
            }
          }
        }
      }
    }

  }

  .projects-list {
    .project-item {
      padding: $spacing-lg;
      border: 1px solid $border-color-lighter;
      border-radius: $border-radius-base;
      margin-bottom: $spacing-md;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: $primary-color;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      }

      &:last-child {
        margin-bottom: 0;
      }

      .project-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-md;

        .project-title {
          display: flex;
          align-items: center;
          gap: $spacing-sm;

          .project-no {
            color: $text-secondary;
            font-size: 12px;
          }

          .project-name {
            font-size: 16px;
            font-weight: 500;
            color: $text-primary;
          }
        }
      }

      .progress-section {
        margin-bottom: $spacing-md;

        .progress-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: $spacing-xs;

          .progress-label {
            font-size: 14px;
            color: $text-secondary;
          }

          .progress-percent {
            font-size: 16px;
            font-weight: 500;
            color: $primary-color;
          }
        }
      }

      .project-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: $spacing-sm;
        font-size: 14px;

        .detail-item {
          display: flex;
          align-items: center;
          gap: $spacing-xs;

          .detail-label {
            color: $text-secondary;
          }

          .detail-value {
            color: $text-primary;
            font-weight: 500;
          }
        }
      }
    }
  }
}
</style>
