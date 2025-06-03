<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDoubanStore } from '@/stores/douban';
import type { TVShow } from '@/api/douban';
import { ElTable, ElTableColumn, ElInput, ElSelect, ElOption, ElTag, ElImage, ElPagination, ElRate } from 'element-plus';

const router = useRouter();
const doubanStore = useDoubanStore();

const searchQuery = ref('');

const selectedCategory = ref('');
const selectedYear = ref('');
const currentPage = ref(1);
const pageSize = ref(10);



// 获取所有类型选项
const categoryOptions = computed(() => {
  const categories = new Set<string>();
  doubanStore.tvShows.forEach(show => {
    show.category.forEach(cat => categories.add(cat));
  });
  return Array.from(categories).sort();
});

// 获取所有年份选项
const yearOptions = computed(() => {
  const years = new Set<number>();
  doubanStore.tvShows.forEach(show => {
    if (show.year) years.add(show.year);
  });
  return Array.from(years).sort().reverse();
});

// 筛选后的电视剧列表
const filteredShows = computed(() => {
  return doubanStore.tvShows.filter(show => {
    // 标题搜索
    const titleMatch = !searchQuery.value || 
      show.title.toLowerCase().includes(searchQuery.value.toLowerCase());
    

    
    // 类型筛选
    const categoryMatch = !selectedCategory.value || 
      show.category.includes(selectedCategory.value);
    
    // 年份筛选
    const yearMatch = !selectedYear.value || 
      show.year === parseInt(selectedYear.value);
    
    return titleMatch && categoryMatch && yearMatch;
  });
});

// 排序后的电视剧列表
const sortedShows = computed(() => {
  return [...filteredShows.value].sort((a, b) => Number(b.rate) - Number(a.rate));
});

// 分页后的电视剧列表
const paginatedShows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return sortedShows.value.slice(start, end);
});

// 总电视剧数量
const totalShows = computed(() => filteredShows.value.length);

// 重置所有筛选条件
const resetFilters = () => {
  searchQuery.value = '';

  selectedCategory.value = '';
  selectedYear.value = '';
  currentPage.value = 1;
};

// 处理页面变化
const handlePageChange = (page: number) => {
  currentPage.value = page;
};

// 导航到详情页
const navigateToDetail = (show: TVShow) => {
  const encodedUrl = encodeURIComponent(show.url);
  router.push({ name: 'detail', params: { id: encodedUrl } });
};

// 格式化分类标签
const formatCategories = (categories: string[]) => {
  return categories.join('、');
};
</script>

<template>
  <div class="ranking-container">
    <h1 class="page-title">电视剧排行榜</h1>
    
    <div class="filter-section">
      <div class="search-box">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索电视剧名称" 
          clearable
          prefix-icon="Search"
        />
      </div>
      
      <div class="filter-options">

        
        <el-select 
          v-model="selectedCategory" 
          placeholder="选择类型" 
          clearable
          class="filter-select"
        >
          <el-option 
            v-for="category in categoryOptions" 
            :key="category" 
            :label="category" 
            :value="category" 
          />
        </el-select>
        
        <el-select 
          v-model="selectedYear" 
          placeholder="选择年份" 
          clearable
          class="filter-select"
        >
          <el-option 
            v-for="year in yearOptions" 
            :key="year" 
            :label="year.toString()" 
            :value="year.toString()" 
          />
        </el-select>
        
        <el-button type="primary" plain @click="resetFilters">重置筛选</el-button>
      </div>
    </div>
    
    <div class="table-container">
      <el-table 
        :data="paginatedShows" 
        style="width: 100%" 
        :empty-text="doubanStore.loading ? '加载中...' : '没有符合条件的电视剧'"
        @row-click="(row) => navigateToDetail(row)"
        row-class-name="clickable-row"
      >
        <el-table-column label="排名" width="80">
          <template #default="scope">
            <div class="rank-cell">
              <span class="rank-number" :class="{ 
                'top-rank': scope.$index + (currentPage - 1) * pageSize < 3 
              }">
                {{ scope.$index + 1 + (currentPage - 1) * pageSize }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="海报" width="120">
          <template #default="scope">
            <el-image 
              :src="`http://localhost:8000/api/proxy/image?url=${encodeURIComponent(scope.row.cover)}`" 
              fit="cover"
              :preview-src-list="[`http://localhost:8000/api/proxy/image?url=${encodeURIComponent(scope.row.cover)}`]"
              class="poster-image"
              loading="lazy"
            >
              <template #error>
                <div class="image-placeholder">暂无图片</div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="片名" min-width="200">
          <template #default="scope">
            <div class="title-cell">
              <div class="show-title">{{ scope.row.title }}</div>
              <div class="show-year">({{ scope.row.year }})</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="rate" label="评分" width="150" sortable>
          <template #default="scope">
            <div class="rate-cell">
              <span class="rate-number">{{ scope.row.rate }}</span>
              <el-rate 
                :model-value="Number(scope.row.rate) / 2" 
                disabled 
                text-color="#ff9900"
                score-template="{value}"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="area" label="地区" width="120" />
        
        <el-table-column label="类型" min-width="180">
          <template #default="scope">
            <div class="category-cell">
              {{ formatCategories(scope.row.category) }}
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:currentPage="currentPage"
          :page-size="pageSize"
          layout="total, prev, pager, next, jumper"
          :total="totalShows"
          @current-change="handlePageChange"
          background
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ranking-container {
  padding: 1rem 0;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
  text-align: center;
}

.filter-section {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-box {
  max-width: 400px;
}

.filter-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  width: 180px;
}

.table-container {
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background-color: #f5f7fa;
}

.rank-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.rank-number {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #ebeef5;
  color: #606266;
  font-weight: bold;
}

.top-rank {
  background-color: #ffce44;
  color: white;
}

.poster-image {
  width: 80px;
  height: 120px;
  border-radius: 4px;
  object-fit: cover;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.poster-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
}

.image-placeholder {
  width: 80px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
  border-radius: 4px;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.show-title {
  font-weight: bold;
}

.show-year {
  color: #909399;
}

.rate-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.rate-number {
  font-weight: bold;
  color: #ff9900;
  font-size: 1.1rem;
}

.category-cell {
  white-space: normal;
  line-height: 1.5;
}

.pagination-container {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
}
</style>
