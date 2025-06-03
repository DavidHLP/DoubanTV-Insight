<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDoubanStore } from '@/stores/douban';
import type { TVShow } from '@/api/douban';
import { ElSkeleton, ElCard, ElTag, ElRate } from 'element-plus';

const router = useRouter();
const doubanStore = useDoubanStore();
const searchQuery = ref('');

const filteredShows = computed(() => {
  if (!searchQuery.value) {
    return doubanStore.tvShows.slice(0, 12);
  }

  return doubanStore.tvShows
    .filter(show =>
      show.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      show.category.some(cat => cat.toLowerCase().includes(searchQuery.value.toLowerCase()))
    )
    .slice(0, 12);
});

const navigateToDetail = (show: TVShow) => {
  // 使用encodeURIComponent对URL进行编码以便安全传递
  const encodedUrl = encodeURIComponent(show.url);
  router.push({ name: 'detail', params: { id: encodedUrl } });
};

const getRandomGradient = () => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  return gradients[Math.floor(Math.random() * gradients.length)];
};
</script>

<template>
  <div class="home-container">
    <section class="hero-section">
      <div class="hero-content">
        <h1>豆瓣电视剧数据分析</h1>
        <p>探索热门电视剧的数据洞察与趋势分析</p>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索电视剧名称或类型"
            prefix-icon="Search"
            clearable
          />
        </div>
      </div>
    </section>

    <section class="featured-section">
      <div class="section-header">
        <h2>热门电视剧</h2>
        <router-link to="/ranking" class="view-all">查看全部</router-link>
      </div>

      <div class="shows-grid">
        <el-skeleton :loading="doubanStore.loading" animated :count="12">
          <template #default>
            <div
              v-for="show in filteredShows"
              :key="show.url"
              class="show-card"
              @click="navigateToDetail(show)"
            >
              <el-card :body-style="{ padding: '0px' }" shadow="hover">
                <div class="card-image">
                  <img :src="`http://localhost:8000/api/proxy/image?url=${encodeURIComponent(show.cover)}`" :alt="show.title" class="card-img" />
                  <div class="card-overlay">
                    <div class="rate-tag">{{ show.rate }} <el-rate :model-value="show.rate / 2" disabled text-color="#ff9900" /></div>
                  </div>
                </div>
                <div class="card-content">
                  <h3 class="card-title">{{ show.title }}</h3>
                  <div class="card-info">
                    <span>{{ show.year }}</span>
                  </div>
                  <div class="card-categories">
                    <el-tag
                      v-for="(category, index) in show.category.slice(0, 3)"
                      :key="index"
                      size="small"
                      :style="{ background: getRandomGradient(), color: '#fff', border: 'none' }"
                    >
                      {{ category }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </div>
          </template>
        </el-skeleton>
      </div>
    </section>

    <section class="stats-section">
      <div class="section-header">
        <h2>数据洞察</h2>
        <router-link to="/analysis" class="view-all">查看分析</router-link>
      </div>

      <div class="stats-cards">
        <el-card class="stats-card" shadow="hover">
          <h3>评分分布</h3>
          <p>探索不同评分区间的电视剧分布情况</p>
          <router-link to="/analysis?tab=rating" class="stats-link">查看详情</router-link>
        </el-card>

        <el-card class="stats-card" shadow="hover">
          <h3>类型分析</h3>
          <p>了解最受欢迎的电视剧类型和流行趋势</p>
          <router-link to="/analysis?tab=category" class="stats-link">查看详情</router-link>
        </el-card>

        <el-card class="stats-card" shadow="hover">
          <h3>年份趋势</h3>
          <p>跟踪电视剧评分随时间变化的趋势</p>
          <router-link to="/analysis?tab=year" class="stats-link">查看详情</router-link>
        </el-card>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.hero-section {
  height: 400px;
  background: linear-gradient(135deg, #41b883 0%, #35495e 100%);
  border-radius: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
  margin-bottom: 2rem;
}

.hero-content {
  max-width: 800px;
  padding: 2rem;
}

.hero-content h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero-content p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.search-box {
  max-width: 500px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.75rem;
  color: #2c3e50;
}

.view-all {
  color: #41b883;
  text-decoration: none;
  font-weight: 500;
}

.shows-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.show-card {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.show-card:hover {
  transform: translateY(-5px);
}

.card-image {
  height: 240px;
  position: relative;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.3s ease;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 50%);
  display: flex;
  align-items: flex-end;
  padding: 1rem;
}

.rate-tag {
  color: white;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-content {
  padding: 1rem;
}

.card-title {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-info {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #606266;
  margin-bottom: 0.5rem;
}

.card-categories {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stats-card {
  padding: 1rem;
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #41b883;
}

.stats-card p {
  color: #606266;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.stats-link {
  display: inline-block;
  color: #41b883;
  text-decoration: none;
  font-weight: 500;
}
</style>
