<template>
  <div class="product-library-container">
    <PageHeader :title="isAdmin ? '产品库' : '产品库'" :subtitle="isAdmin ? '查看所有供应商的报价产品信息' : '查看和管理您的报价产品信息'" />

    <SearchForm v-model="searchForm" @search="fetchData" @reset="resetSearch">
      <el-form-item v-if="isAdmin" label="供应商">
        <el-select
          v-model="searchForm.supplier_id"
          placeholder="请选择供应商"
          clearable
          filterable
        >
          <el-option
            v-for="supplier in supplierList"
            :key="supplier.id"
            :label="supplier.company_name"
            :value="supplier.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="产品关键词">
        <el-input
          v-model="searchForm.keyword"
          placeholder="请输入产品名称或规格型号"
          clearable
        />
      </el-form-item>
      <el-form-item label="项目名称">
        <el-input v-model="searchForm.project_name" placeholder="请输入项目名称" clearable />
      </el-form-item>
    </SearchForm>

    <!-- 统计卡片 -->
    <div v-if="statistics" class="statistics-cards">
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-label">产品总数</div>
          <div class="stat-value">{{ statistics.total_products }}</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-label">报价单数</div>
          <div class="stat-value">{{ statistics.total_quotations }}</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-label">关联项目</div>
          <div class="stat-value">{{ statistics.total_projects }}</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-label">品牌数量</div>
          <div class="stat-value">{{ statistics.brand_count }}</div>
        </div>
      </el-card>
    </div>

    <DataTable
      v-model:page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      @change="fetchData"
    >
      <el-table-column prop="id" label="ID" width="90" />
      <el-table-column prop="product_name" label="产品名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="specification" label="规格型号" min-width="170" show-overflow-tooltip />
      <el-table-column prop="brand" label="品牌" width="120" />
      <el-table-column prop="model" label="型号" width="120" show-overflow-tooltip />
      <el-table-column prop="unit_price" label="单价" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.unit_price) }}
        </template>
      </el-table-column>
      <el-table-column v-if="isAdmin" prop="supplier_name" label="供应商" min-width="180" show-overflow-tooltip />
      <el-table-column prop="quotation_date" label="报价日期" width="120">
        <template #default="{ row }">
          {{ formatDateOnly(row.quotation_date) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right">
        <template #default="{ row }">
          <ActionButtons :buttons="getActionButtons(row)" />
        </template>
      </el-table-column>
    </DataTable>

    <!-- 产品详情对话框 -->
    <el-dialog v-model="detailVisible" title="产品详情" :width="DIALOG_WIDTH.LARGE">
      <div v-if="productDetail" class="product-detail">
        <!-- 产品信息 -->
        <div class="detail-section">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="产品名称" :span="1">
              {{ productDetail.product_name }}
            </el-descriptions-item>
            <el-descriptions-item label="规格型号" :span="1">
              {{ productDetail.specification || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="品牌" :span="1">
              {{ productDetail.brand || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="型号" :span="1">
              {{ productDetail.model || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="数量" :span="1">
              {{ formatNumber(productDetail.quantity) }}
            </el-descriptions-item>
            <el-descriptions-item label="单价" :span="1">
              {{ formatCurrency(productDetail.unit_price) }}
            </el-descriptions-item>
            <el-descriptions-item label="金额" :span="1">
              {{ formatCurrency(productDetail.amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="1">
              {{ productDetail.remarks || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 报价信息 -->
        <div class="detail-section">
          <div class="section-title">报价信息</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="报价状态" :span="1">
              <StatusTag :status="productDetail.quotation_status" status-type="quotation" />
            </el-descriptions-item>
            <el-descriptions-item label="报价总金额" :span="1">
              {{ formatCurrency(productDetail.quotation_total) }}
            </el-descriptions-item>
            <el-descriptions-item label="报价日期" :span="1">
              {{ formatDateOnly(productDetail.quotation_date) }}
            </el-descriptions-item>
            <el-descriptions-item v-if="productDetail.submitted_at" label="提交时间" :span="1">
              {{ formatDateOnly(productDetail.submitted_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 供应商信息 -->
        <div class="detail-section">
          <div class="section-title">供应商信息</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="供应商名称" :span="2">
              {{ productDetail.supplier_name }}
            </el-descriptions-item>
            <el-descriptions-item label="联系人" :span="1">
              {{ productDetail.contact_person || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话" :span="1">
              {{ productDetail.contact_phone || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 关联项目 -->
        <div class="detail-section">
          <div class="section-title">关联项目</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目编号" :span="1">
              {{ productDetail.project_no }}
            </el-descriptions-item>
            <el-descriptions-item label="项目名称" :span="1">
              {{ productDetail.project_name }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { PageHeader, SearchForm, DataTable, StatusTag, ActionButtons } from '@/components'
import { getProductLibraryList, getProductDetail, getProductStatistics } from '@/api/productLibrary'
import { getSupplierList } from '@/api/supplier'
import { useUserStore } from '@/stores/user'
import { formatDate, formatDateOnly, formatCurrency, formatNumber } from '@/utils'
import { debounce } from '@/utils'
import { DIALOG_WIDTH } from '@/utils/constants'

const userStore = useUserStore()
const loading = ref(false)
const tableData = ref([])
const statistics = ref(null)
const detailVisible = ref(false)
const productDetail = ref(null)
const supplierList = ref([])

const isAdmin = computed(() => {
  return userStore.userInfo?.is_superuser
})

const searchForm = reactive({
  supplier_id: null,
  keyword: '',
  project_name: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    // 仅传有值的过滤项，避免后端接收空字符串
    if (searchForm.supplier_id) {
      params.supplier_id = searchForm.supplier_id
    }
    if (searchForm.keyword && searchForm.keyword.trim()) {
      params.keyword = searchForm.keyword.trim()
    }
    if (searchForm.project_name && searchForm.project_name.trim()) {
      params.project_name = searchForm.project_name.trim()
    }
    
    const response = await getProductLibraryList(params)
    tableData.value = response.items || response.results || response.data?.items || []
    pagination.total = response.total || response.data?.total || 0
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const response = await getProductStatistics()
    statistics.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 供应商列表缓存，避免重复请求
let supplierListCache = null
let supplierListCacheTime = 0
const SUPPLIER_LIST_CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

const fetchSupplierList = async () => {
  if (!isAdmin.value) return
  
  // 使用缓存，避免重复请求
  const now = Date.now()
  if (supplierListCache && (now - supplierListCacheTime) < SUPPLIER_LIST_CACHE_DURATION) {
    supplierList.value = supplierListCache
    return
  }
  
  try {
    // 只获取第一页，限制数量，提高加载速度
    const response = await getSupplierList({ 
      page: 1, 
      page_size: 100,
      status: 1  // 只获取审核通过的供应商
    })
    
    const items = response.items || []
    supplierList.value = items
    supplierListCache = items
    supplierListCacheTime = now
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    // 如果带status参数失败，尝试不带status参数获取
    if (error.response?.status === 422 || error.response?.status === 403) {
      try {
        const response2 = await getSupplierList({ page: 1, page_size: 100 })
        const items = (response2.items || []).filter(s => s.status === 1)
        supplierList.value = items
        supplierListCache = items
        supplierListCacheTime = now
      } catch (error2) {
        console.error('获取供应商列表失败（第二次尝试）:', error2)
        supplierList.value = []
      }
    } else {
      supplierList.value = []
    }
  }
}

const resetSearch = () => {
  searchForm.supplier_id = null
  searchForm.keyword = ''
  searchForm.project_name = ''
  pagination.page = 1
  fetchData()
}

// 防抖搜索函数 - 统一使用500ms延迟
const debouncedSearch = debounce(() => {
  pagination.page = 1
  fetchData()
}, 500)

// 监听产品关键词变化，自动搜索（防抖）
watch(
  () => searchForm.keyword,
  () => {
    debouncedSearch()
  }
)

// 监听项目名称变化，自动搜索（防抖）
watch(
  () => searchForm.project_name,
  () => {
    debouncedSearch()
  }
)

// 监听供应商变化，直接搜索（无需防抖）
watch(
  () => searchForm.supplier_id,
  () => {
    pagination.page = 1
    fetchData()
  }
)

// 获取操作按钮配置
const getActionButtons = row => {
  return [
    {
      key: 'view',
      label: '查看详情',
      type: 'primary',
      size: 'small',
      handler: () => handleView(row.id)
    }
  ]
}

const handleView = async id => {
  try {
    const response = await getProductDetail(id)
    productDetail.value = response.data || response
    detailVisible.value = true
  } catch (error) {
    console.error('获取产品详情失败:', error)
    ElMessage.error('获取产品详情失败')
  }
}

onMounted(() => {
  // 并行加载，但统计数据延迟加载，不影响列表显示
  Promise.all([
    fetchSupplierList(),
    fetchData()
  ]).then(() => {
    // 列表加载完成后再加载统计数据
    fetchStatistics()
  })
})

onActivated(() => {
  // 激活时只刷新列表数据，不重新加载供应商列表（使用缓存）
  fetchData()
  // 统计数据也延迟加载
  setTimeout(() => {
    fetchStatistics()
  }, 500)
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.product-library-container {
  min-height: 100%;

  .statistics-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: $spacing-md;
    margin-bottom: $spacing-lg;

    .stat-card {
      .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: $spacing-md 0;

        .stat-label {
          font-size: 14px;
          color: $text-secondary;
          margin-bottom: $spacing-xs;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 500;
          color: $primary-color;
        }
      }
    }
  }

}
</style>

