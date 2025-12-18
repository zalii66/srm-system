<template>
  <div class="milestones-management-container">
    <PageHeader :title="`项目时间节点管理 - ${project.project_name || ''}`" :subtitle="`项目编号：${project.project_no || ''}`">
      <template #extra>
        <el-button @click="handleBack">返回</el-button>
        <el-button type="primary" @click="handleAddMilestone">添加节点</el-button>
        <el-button type="success" @click="handleImportTemplate" :disabled="milestones.length > 0">
          导入模板
        </el-button>
      </template>
    </PageHeader>

    <el-card v-loading="loading">
      <div class="progress-summary">
        <div class="progress-info">
          <span class="progress-label">项目总进度：</span>
          <span class="progress-value">{{ projectProgress?.total_progress || 0 }}%</span>
        </div>
        <div class="progress-stats">
          <span>已完成：{{ projectProgress?.completed_milestones || 0 }}/{{ projectProgress?.total_milestones || 0 }}</span>
          <span class="divider">|</span>
          <span>关键节点：{{ projectProgress?.critical_milestones?.completed || 0 }}/{{ projectProgress?.critical_milestones?.total || 0 }}</span>
        </div>
      </div>
    </el-card>

    <el-card>
      <MilestoneTimeline
        :milestones="milestones"
        :readonly="false"
        @complete="handleMilestoneComplete"
        @edit="handleMilestoneEdit"
        @delete="handleMilestoneDelete"
      />
    </el-card>

    <!-- 时间节点编辑对话框 -->
    <el-dialog
      v-model="milestoneDialogVisible"
      :title="milestoneDialogTitle"
      :width="DIALOG_WIDTH.MEDIUM"
      :close-on-click-modal="false"
      @close="resetMilestoneForm"
    >
      <el-form ref="milestoneFormRef" :model="milestoneForm" :rules="milestoneRules" :label-width="FORM_LABEL_WIDTH.DEFAULT">
        <el-form-item label="节点名称" prop="milestone_name">
          <el-input v-model="milestoneForm.milestone_name" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="节点描述" prop="description">
          <el-input v-model="milestoneForm.description" type="textarea" :rows="3" placeholder="请输入节点描述" />
        </el-form-item>
        <el-form-item label="计划时间" prop="planned_date">
          <el-date-picker
            v-model="milestoneForm.planned_date"
            type="datetime"
            placeholder="选择计划时间"
            class="w-full"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="实际完成时间" prop="actual_date">
          <el-date-picker
            v-model="milestoneForm.actual_date"
            type="datetime"
            placeholder="选择实际完成时间"
            class="w-full"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="milestoneForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="是否关键节点" prop="is_critical">
          <el-switch v-model="milestoneForm.is_critical" />
        </el-form-item>
        <el-form-item label="供应商可见" prop="is_visible_to_supplier">
          <el-switch v-model="milestoneForm.is_visible_to_supplier" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="milestoneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMilestone">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PageHeader, MilestoneTimeline } from '@/components'
import { getProjectDetail } from '@/api/project'
import { DIALOG_WIDTH, FORM_LABEL_WIDTH } from '@/utils'
import {
  getMilestones,
  createMilestone,
  updateMilestone,
  deleteMilestone,
  completeMilestone,
  importMilestoneTemplate,
  getProjectProgress
} from '@/api/milestone'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const milestones = ref([])
const project = reactive({
  id: null,
  project_no: '',
  project_name: ''
})
const projectProgress = ref(null)
const milestoneDialogVisible = ref(false)
const milestoneDialogTitle = ref('添加时间节点')
const editingMilestone = ref(null)
const milestoneFormRef = ref(null)
const milestoneForm = reactive({
  milestone_name: '',
  description: '',
  planned_date: null,
  actual_date: null,
  status: 0,
  progress: 0,
  sort_order: 0,
  is_critical: false,
  is_visible_to_supplier: true
})

const milestoneRules = {
  milestone_name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }]
}

const fetchProjectInfo = async () => {
  try {
    const data = await getProjectDetail(route.params.id)
    project.id = data.id
    project.project_no = data.project_no
    project.project_name = data.project_name
  } catch (error) {
    ElMessage.error('获取项目信息失败')
  }
}

const fetchMilestones = async () => {
  loading.value = true
  try {
    const data = await getMilestones(route.params.id, true)
    milestones.value = data || []
  } catch (error) {
    console.error('获取时间节点失败:', error)
    milestones.value = []
  } finally {
    loading.value = false
  }
}

const fetchProjectProgress = async () => {
  try {
    const data = await getProjectProgress(route.params.id)
    projectProgress.value = data
  } catch (error) {
    console.error('获取项目进度失败:', error)
  }
}

const handleBack = () => {
  router.push(`/project/detail/${route.params.id}`)
}

const handleAddMilestone = () => {
  editingMilestone.value = null
  milestoneDialogTitle.value = '添加时间节点'
  resetMilestoneForm()
  milestoneDialogVisible.value = true
}

const handleMilestoneEdit = milestone => {
  editingMilestone.value = milestone
  milestoneDialogTitle.value = '编辑时间节点'
  milestoneForm.milestone_name = milestone.milestone_name
  milestoneForm.description = milestone.description || ''
  milestoneForm.planned_date = milestone.planned_date || null
  milestoneForm.actual_date = milestone.actual_date || null
  milestoneForm.status = milestone.status
  milestoneForm.progress = milestone.progress
  milestoneForm.sort_order = milestone.sort_order
  milestoneForm.is_critical = milestone.is_critical
  milestoneForm.is_visible_to_supplier = milestone.is_visible_to_supplier
  milestoneDialogVisible.value = true
}

const resetMilestoneForm = () => {
  milestoneForm.milestone_name = ''
  milestoneForm.description = ''
  milestoneForm.planned_date = null
  milestoneForm.actual_date = null
  milestoneForm.status = 0
  milestoneForm.progress = 0
  milestoneForm.sort_order = milestones.value.length + 1
  milestoneForm.is_critical = false
  milestoneForm.is_visible_to_supplier = true
  milestoneFormRef.value?.resetFields()
}

const handleSaveMilestone = async () => {
  if (!milestoneFormRef.value) return
  await milestoneFormRef.value.validate(async valid => {
    if (valid) {
      try {
        if (editingMilestone.value) {
          await updateMilestone(route.params.id, editingMilestone.value.id, milestoneForm)
          ElMessage.success('更新成功')
        } else {
          await createMilestone(route.params.id, milestoneForm)
          ElMessage.success('添加成功')
        }
        milestoneDialogVisible.value = false
        await fetchMilestones()
        await fetchProjectProgress()
      } catch (error) {
        const errorMsg =
          error?.response?.data?.detail || error?.response?.data?.message || error?.message || '操作失败'
        ElMessage.error(errorMsg)
      }
    }
  })
}

const handleMilestoneComplete = async milestone => {
  try {
    await completeMilestone(route.params.id, milestone.id)
    ElMessage.success('节点已标记为完成')
    await fetchMilestones()
    await fetchProjectProgress()
  } catch (error) {
    ElMessage.error('标记节点完成失败')
  }
}

const handleMilestoneDelete = async milestone => {
  try {
    await deleteMilestone(route.params.id, milestone.id)
    ElMessage.success('节点已删除')
    await fetchMilestones()
    await fetchProjectProgress()
  } catch (error) {
    const errorMsg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || '删除失败'
    ElMessage.error(errorMsg)
  }
}

const handleImportTemplate = async () => {
  try {
    await ElMessageBox.confirm(
      '导入模板将创建默认的时间节点（需求发布、报价截止、报价评审等）。确定要导入吗？',
      '导入节点模板',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    await importMilestoneTemplate(route.params.id)
    ElMessage.success('模板导入成功')
    await fetchMilestones()
    await fetchProjectProgress()
  } catch (error) {
    if (error === 'cancel') return
    const errorMsg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || '导入失败'
    ElMessage.error(errorMsg)
  }
}

onMounted(async () => {
  await fetchProjectInfo()
  await fetchMilestones()
  await fetchProjectProgress()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.milestones-management-container {
  min-height: 100%;

  .progress-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;

    .progress-info {
      display: flex;
      align-items: center;
      gap: $spacing-sm;

      .progress-label {
        font-size: 14px;
        color: $text-secondary;
      }

      .progress-value {
        font-size: 24px;
        font-weight: 500;
        color: $primary-color;
      }
    }

    .progress-stats {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      font-size: 14px;
      color: $text-secondary;

      .divider {
        color: $border-color;
      }
    }
  }
}
</style>

