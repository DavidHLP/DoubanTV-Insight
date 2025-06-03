<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useDoubanStore } from '@/stores/douban';
import * as echarts from 'echarts/core';
import { BarChart, PieChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { ElTabs, ElTabPane, ElCard, ElSkeleton } from 'element-plus';

// 注册必要的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  PieChart,
  LineChart,
  CanvasRenderer
]);

const route = useRoute();
const doubanStore = useDoubanStore();
const activeTab = ref(route.query.tab?.toString() || 'rating');

// 图表容器引用
const ratingChartRef = ref<HTMLElement | null>(null);
const categoryChartRef = ref<HTMLElement | null>(null);
const yearChartRef = ref<HTMLElement | null>(null);

// 图表实例
let ratingChart: echarts.ECharts | null = null;
let categoryChart: echarts.ECharts | null = null;
let yearChart: echarts.ECharts | null = null;

// 监听标签页变化，重新调整图表大小
const handleTabChange = () => {
  // 延迟执行以确保DOM已经更新
  setTimeout(() => {
    handleResize();
  }, 100);
};

onMounted(() => {
  // 在DOM元素渲染完成后初始化图表
  // 延迟初始化图表，确保DOM已完全渲染
  setTimeout(() => {
    initCharts();
  }, 300);

  // 监听窗口大小变化以调整图表
  window.addEventListener('resize', handleResize);
});

const handleResize = () => {
  ratingChart?.resize();
  categoryChart?.resize();
  yearChart?.resize();
};

const initCharts = () => {
  // 如果数据还没有加载完成，等待数据加载后再初始化图表
  if (doubanStore.loading) {
    setTimeout(initCharts, 100);
    return;
  }

  initRatingChart();
  initCategoryChart();
  initYearChart();
};

// 初始化评分分布图表
const initRatingChart = () => {
  if (!ratingChartRef.value) return;

  // 确保容器已经有宽度和高度
  if (ratingChartRef.value.offsetWidth === 0) {
    setTimeout(initRatingChart, 100);
    return;
  }

  // 创建图表实例
  ratingChart = echarts.init(ratingChartRef.value);

  // 使用后端返回的评分统计数据
  let rateData = [];
  const rateRanges = ['0-5', '5-6', '6-7', '7-8', '8-9', '9-10'];

  // 检查是否有后端统计数据
  if (doubanStore.rateStats && doubanStore.rateStats.length > 0) {
    rateData = [...doubanStore.rateStats];
  } else {
    // 后备方案：从电视剧数据中计算统计信息
    rateData = rateRanges.map(range => {
      const [min, max] = range.split('-').map(Number);
      const count = doubanStore.tvShows.filter(
        show => Number(show.rate) >= min && Number(show.rate) < max
      ).length;
      return { name: range, value: count };
    });
  }

  // 设置图表选项
  const option = {
    title: {
      text: '电视剧评分分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 'bottom',
      data: rateRanges
    },
    series: [
      {
        name: '评分分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: rateData
      }
    ],
    color: ['#FF6B6B', '#FF9E40', '#FFCE44', '#6BCB77', '#4D96FF', '#9B5DE5']
  };

  // 使用配置项设置图表
  ratingChart.setOption(option);
};

// 初始化类型分布图表
const initCategoryChart = () => {
  if (!categoryChartRef.value) return;

  // 确保容器已经有宽度和高度
  if (categoryChartRef.value.offsetWidth === 0) {
    setTimeout(initCategoryChart, 100);
    return;
  }

  categoryChart = echarts.init(categoryChartRef.value);

  // 使用后端返回的类型统计数据
  let categoryData = [];

  // 检查是否有后端统计数据
  if (doubanStore.categoryStats && doubanStore.categoryStats.length > 0) {
    categoryData = [...doubanStore.categoryStats]
      .sort((a, b) => b.value - a.value)
      .slice(0, 15); // 只取前15个类型，避免图表过于拥挤
  } else {
    // 后备方案：从电视剧数据中计算统计信息
    // 先将所有类型合并到一个数组中，然后计算每个类型的出现次数
    const categoryMap = new Map();
    doubanStore.tvShows.forEach(show => {
      show.category.forEach(cat => {
        categoryMap.set(cat, (categoryMap.get(cat) || 0) + 1);
      });
    });

    // 转换为图表数据格式并按数量排序
    categoryData = Array.from(categoryMap.entries())
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 15); // 只取前15个类型，避免图表过于拥挤
  }

  const option = {
    title: {
      text: '电视剧类型分布 (Top 15)',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    xAxis: {
      type: 'category',
      data: categoryData.map(item => item.name),
      axisLabel: {
        interval: 0,
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: categoryData.map(item => ({
          value: item.value,
          itemStyle: {
            color: `rgba(65, 184, 131, ${0.5 + Math.random() * 0.5})`
          }
        })),
        type: 'bar'
      }
    ],
    grid: {
      bottom: '15%'
    }
  };

  categoryChart.setOption(option);
};



// 初始化年份趋势图表
const initYearChart = () => {
  if (!yearChartRef.value) return;

  // 确保容器已经有宽度和高度
  if (yearChartRef.value.offsetWidth === 0) {
    setTimeout(initYearChart, 100);
    return;
  }

  yearChart = echarts.init(yearChartRef.value);

  // 使用后端返回的年份统计数据
  let yearData = [];
  let years = [];
  const yearMap = new Map();
  const yearRatingMap = new Map();
  const yearRatingAvg = new Map();

  // 检查是否有后端统计数据
  if (doubanStore.yearStats && doubanStore.yearStats.length > 0) {
    yearData = [...doubanStore.yearStats];

    // 从统计数据中提取年份和数量
    yearData.forEach(item => {
      yearMap.set(item.name, item.value);
    });

    console.log(doubanStore.tvShows);
    // 从电视剧数据中计算评分信息
    doubanStore.tvShows.forEach(show => {
      if (!show.year) return;

      // 按年份统计平均评分
      if (!yearRatingMap.has(show.year)) {
        yearRatingMap.set(show.year, { total: 0, count: 0 });
      }
      const data = yearRatingMap.get(show.year);
      data.total += Number(show.rate);
      data.count += 1;
    });

    // 计算每年的平均评分
    yearRatingMap.forEach((data, year) => {
      if (parseFloat(data.count) > 0) {
        yearRatingAvg.set(parseInt(year), parseFloat(data.total) / parseFloat(data.count));
      }
    });

    // 确保所有年份都有评分数据
    yearMap.forEach((count, year) => {
      if (!yearRatingAvg.has(parseInt(year))) {
        yearRatingAvg.set(parseInt(year), 0);
      }
    });

    // 获取所有年份并排序
    years = Array.from(yearMap.keys()).sort();

  }

  const option = {
    title: {
      text: '电视剧年份趋势与评分',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      }
    },
    legend: {
      data: ['电视剧数量', '平均评分'],
      bottom: 'bottom'
    },
    xAxis: [
      {
        type: 'category',
        data: years,
        axisPointer: {
          type: 'shadow'
        },
        axisLabel: {
          interval: 0,
          rotate: 45
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '数量',
        min: 0,
        position: 'left'
      },
      {
        type: 'value',
        name: '评分',
        min: 0,
        max: 10,
        position: 'right'
      }
    ],
    series: [
      {
        name: '电视剧数量',
        type: 'bar',
        data: years.map(year => yearMap.get(year))
      },
      {
        name: '平均评分',
        type: 'line',
        yAxisIndex: 1,
        data: years.map(year => {
          // 确保有评分数据并转为数字类型
          const score = yearRatingAvg.get(parseInt(year));
          if (score === undefined) {
            return 0;
          }
          // 保留一位小数并转为数字
          return parseFloat(score.toFixed(1));
        }),
        lineStyle: {
          width: 3,
          color: '#FF9E40'
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ],
    grid: {
      bottom: '15%'
    }
  };

  yearChart.setOption(option);
};
</script>

<template>
  <div class="analysis-container">
    <h1 class="page-title">数据分析</h1>

    <el-skeleton :loading="doubanStore.loading" animated>
      <template #default>
        <el-tabs v-model="activeTab" class="analysis-tabs" @tab-change="handleTabChange">
          <el-tab-pane label="评分分布" name="rating">
            <el-card class="chart-card">
              <div ref="ratingChartRef" class="chart-container"></div>
              <div class="chart-description">
                <h3>评分分析</h3>
                <p>该图表展示了豆瓣热门电视剧评分的分布情况，帮助了解不同评分区间的电视剧数量比例。评分在8分以上的作品通常被认为是优质之作，评分在9分以上的则是经典佳作。</p>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="类型分析" name="category">
            <el-card class="chart-card">
              <div ref="categoryChartRef" class="chart-container"></div>
              <div class="chart-description">
                <h3>类型分析</h3>
                <p>该图表展示了热门电视剧类型的分布，反映当前观众对不同类型电视剧的喜好趋势。柱状高度表示该类型电视剧的数量，可以清晰看出最受欢迎的电视剧类型。</p>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="年份趋势" name="year">
            <el-card class="chart-card">
              <div ref="yearChartRef" class="chart-container"></div>
              <div class="chart-description">
                <h3>年份趋势分析</h3>
                <p>该图表展示了不同年份的热门电视剧数量和平均评分变化趋势。柱状图表示每年的电视剧数量，折线图表示每年电视剧的平均评分，可以观察电视剧质量随时间的变化。</p>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped>
.analysis-container {
  padding: 1rem 0;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
  text-align: center;
}

.analysis-tabs {
  margin-top: 1rem;
}

.chart-card {
  margin-bottom: 2rem;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-bottom: 1.5rem;
  min-width: 300px;
  /* 确保最小宽度 */
  display: flex;
  justify-content: center;
}

.chart-description {
  padding: 0 1rem;
}

.chart-description h3 {
  margin-bottom: 0.5rem;
  color: #41b883;
  font-size: 1.25rem;
}

.chart-description p {
  color: #606266;
  font-size: 0.95rem;
  line-height: 1.6;
}
</style>
