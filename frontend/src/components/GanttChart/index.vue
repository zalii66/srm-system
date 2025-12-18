<template>
  <div class="gantt-chart-container" ref="chartContainer"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { formatDate } from '@/utils'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '400px'
  }
})

const chartContainer = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartContainer.value) return
  
  chartInstance = echarts.init(chartContainer.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance) return
  
  if (!props.data || props.data.length === 0) {
    chartInstance.clear()
    chartInstance.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    })
    return
  }
  
  const categories = props.data.map(p => p.project_name || p.project_no)
  const startDates = props.data.map(p => {
    const date = p.start_date ? new Date(p.start_date) : (p.created_at ? new Date(p.created_at) : new Date())
    return date.getTime()
  })
  const endDates = props.data.map(p => {
    if (p.end_date) {
      return new Date(p.end_date).getTime()
    }
    // 如果没有结束时间，使用开始时间+30天作为估算
    const start = p.start_date ? new Date(p.start_date) : (p.created_at ? new Date(p.created_at) : new Date())
    return start.getTime() + 30 * 24 * 60 * 60 * 1000
  })
  
  // 里程碑数据
  const milestoneData = []
  props.data.forEach((project, index) => {
    if (project.milestones && project.milestones.length > 0) {
      project.milestones.forEach(milestone => {
        if (milestone.planned_date) {
          milestoneData.push([
            index,
            new Date(milestone.planned_date).getTime(),
            milestone.name,
            milestone.is_critical ? 1 : 0
          ])
        }
      })
    }
  })
  
  const minDate = Math.min(...startDates)
  const maxDate = Math.max(...endDates)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const param = params[0]
        if (param.seriesName === '项目时间') {
          const project = props.data[param.dataIndex]
          let html = `<div style="margin-bottom: 8px;"><strong>${project.project_name}</strong></div>`
          if (project.start_date) {
            html += `<div>开始时间：${formatDate(project.start_date)}</div>`
          }
          if (project.end_date) {
            html += `<div>结束时间：${formatDate(project.end_date)}</div>`
          }
          if (project.bidding_deadline) {
            html += `<div>投标截止：${formatDate(project.bidding_deadline)}</div>`
          }
          return html
        } else if (param.seriesName === '里程碑') {
          return `<div><strong>${param.value[2]}</strong></div><div>计划时间：${formatDate(new Date(param.value[1]))}</div>`
        }
        return ''
      }
    },
    legend: {
      data: ['项目时间', '里程碑'],
      top: 30
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '15%',
      bottom: '10%'
    },
    xAxis: {
      type: 'time',
      min: minDate,
      max: maxDate,
      axisLabel: {
        formatter: function(value) {
          return formatDate(new Date(value))
        }
      }
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        formatter: function(value) {
          if (value.length > 15) {
            return value.substring(0, 15) + '...'
          }
          return value
        }
      }
    },
    series: [
      {
        name: '项目时间',
        type: 'custom',
        renderItem: function(params, api) {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const height = api.size([0, 1])[1] * 0.6
          
          const project = props.data[categoryIndex]
          const status = project.status || 0
          
          // 根据状态设置颜色
          let color = '#409EFF'
          if (status === 4) color = '#67C23A' // 已完成
          else if (status === 3) color = '#E6A23C' // 竞标中
          else if (status === 5) color = '#909399' // 已取消
          
          return {
            type: 'rect',
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: end[0] - start[0],
              height: height
            },
            style: {
              fill: color,
              stroke: '#fff',
              lineWidth: 1
            }
          }
        },
        encode: {
          x: [1, 2],
          y: 0
        },
        data: props.data.map((p, index) => {
          const start = p.start_date ? new Date(p.start_date).getTime() : (p.created_at ? new Date(p.created_at).getTime() : Date.now())
          const end = p.end_date ? new Date(p.end_date).getTime() : (start + 30 * 24 * 60 * 60 * 1000)
          return [index, start, end]
        })
      },
      {
        name: '里程碑',
        type: 'scatter',
        symbol: 'diamond',
        symbolSize: 12,
        itemStyle: {
          color: function(params) {
            return params.value[3] === 1 ? '#F56C6C' : '#909399'
          }
        },
        data: milestoneData
      }
    ]
  }
  
  chartInstance.setOption(option, true)
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}
</script>

<style scoped lang="scss">
.gantt-chart-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>

