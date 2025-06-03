import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  getHotTVShows,
  getRateStats,
  getCategoryStats,
  getYearStats,
} from '@/api/douban';
import type { TVShow } from '@/api/douban';

export const useDoubanStore = defineStore('douban', () => {
  // 状态
  const tvShows = ref<TVShow[]>([]);
  const loading = ref(false);
  // 将统计数据类型改为数组类型，匹配后端API返回的格式
  const rateStats = ref<Array<{ name: string, value: number }>>([]);
  const categoryStats = ref<Array<{ name: string, value: number }>>([]);

  const yearStats = ref<Array<{ name: string, value: number }>>([]);

  // 计算属性
  const highRatedShows = computed(() => {
    return tvShows.value
      .filter(show => Number(show.rate) >= 8.0)
      .sort((a, b) => Number(b.rate) - Number(a.rate));
  });

  const recentShows = computed(() => {
    return [...tvShows.value]
      .sort((a, b) => Number(b.year) - Number(a.year))
      .slice(0, 10);
  });

  // 获取所有数据
  async function fetchAllData() {
    loading.value = true;
    try {
      // 先获取统计数据
      const [rateData, categoryData, yearData] = await Promise.all([
        getRateStats(),
        getCategoryStats(),
        getYearStats()
      ]);

      // 正确处理统计数据，确保它们是数组类型
      if (rateData.data && Array.isArray(rateData.data)) {
        rateStats.value = rateData.data;
      }
      if (categoryData.data && Array.isArray(categoryData.data)) {
        categoryStats.value = categoryData.data;
      }
      if (yearData.data && Array.isArray(yearData.data)) {
        yearStats.value = yearData.data;
      }

      // 获取所有电视剧数据（不使用默认分页）
      const showsResponse = await getHotTVShows({ page: 1, page_size: 1000 }); // 使用较大的page_size以获取所有数据

      // 确保数据是数组类型
      tvShows.value = showsResponse.data && showsResponse.data.items ? showsResponse.data.items : [];

      console.log('数据加载成功:', {
        tvShows: tvShows.value.length,
        rateStats: rateStats.value.length,
        categoryStats: categoryStats.value.length,
        yearStats: yearStats.value.length
      });
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      loading.value = false;
    }
  }

  // 按类型筛选电视剧
  function filterByCategory(category: string) {
    return tvShows.value.filter(show => show.category.includes(category));
  }



  // 按年份筛选电视剧
  function filterByYear(year: number) {
    return tvShows.value.filter(show => show.year === year);
  }

  // 按评分范围筛选电视剧
  function filterByRateRange(min: number, max: number) {
    return tvShows.value.filter(
      show => Number(show.rate) >= min && Number(show.rate) <= max
    );
  }

  return {
    tvShows,
    loading,
    rateStats,
    categoryStats,

    yearStats,
    highRatedShows,
    recentShows,
    fetchAllData,
    filterByCategory,

    filterByYear,
    filterByRateRange
  };
});
