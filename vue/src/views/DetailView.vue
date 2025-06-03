<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTVShowDetail } from '@/api/douban';
import type { TVShow } from '@/api/douban';
import { ElSkeleton, ElImage, ElTag, ElRate, ElDivider, ElDescriptions, ElDescriptionsItem } from 'element-plus';

const route = useRoute();
const router = useRouter();
const tvShow = ref<TVShow | null>(null);
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    loading.value = true;

    if (!route.params.id) {
      error.value = '无效的电视剧ID';
      return;
    }

    // 解码URL参数
    const decodedUrl = decodeURIComponent(route.params.id as string);

    // 调用API获取详情
    const response = await getTVShowDetail(decodedUrl);
    tvShow.value = response.data;
  } catch (err) {
    console.error('获取电视剧详情失败:', err);
    error.value = '获取电视剧详情失败，请稍后重试';
  } finally {
    loading.value = false;
  }
});

// 返回上一页
const goBack = () => {
  router.back();
};

// 获取随机渐变色
const getRandomGradient = (index: number) => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  return gradients[index % gradients.length];
};
</script>

<template>
  <div class="detail-container">
    <div class="back-button" @click="goBack">
      <el-icon><arrow-left /></el-icon> 返回
    </div>

    <el-skeleton :loading="loading" animated>
      <template #default>
        <div v-if="error" class="error-message">
          <el-icon><warning /></el-icon>
          <span>{{ error }}</span>
        </div>

        <div v-else-if="tvShow" class="tv-detail">
          <div class="detail-header">
            <div class="poster-container">
              <el-image
                :src="`http://localhost:8000/api/proxy/image?url=${encodeURIComponent(tvShow.cover)}`"
                fit="cover"
                :preview-src-list="[`http://localhost:8000/api/proxy/image?url=${encodeURIComponent(tvShow.cover)}`]"
                class="poster-image"
              >
                <template #error>
                  <div class="image-placeholder">暂无图片</div>
                </template>
              </el-image>
            </div>

            <div class="basic-info">
              <h1 class="title">{{ tvShow.title }}</h1>

              <div class="rating-section">
                <div class="rating-score">{{ tvShow.rate }}</div>
                <el-rate
                  :model-value="Number(tvShow.rate) / 2"
                  disabled
                  text-color="#ff9900"
                  score-template="{value}"
                  size="large"
                />
              </div>

              <div class="tags-section">
                <el-tag
                  v-for="(category, index) in tvShow.category"
                  :key="index"
                  size="large"
                  :style="{ background: getRandomGradient(index), color: '#fff', border: 'none', marginRight: '8px', marginBottom: '8px' }"
                >
                  {{ category }}
                </el-tag>
              </div>

              <el-descriptions :column="1" border>
                <el-descriptions-item label="上映年份">{{ tvShow.year }}</el-descriptions-item>

                <el-descriptions-item label="导演">{{ tvShow.directors?.join('、') || '暂无信息' }}</el-descriptions-item>
                <el-descriptions-item label="主演">{{ tvShow.actors?.join('、') || '暂无信息' }}</el-descriptions-item>
                <el-descriptions-item label="更新时间">{{ tvShow.update_time }}</el-descriptions-item>
              </el-descriptions>

              <a :href="tvShow.url" target="_blank" class="douban-link">
                在豆瓣查看 <el-icon><link /></el-icon>
              </a>
            </div>
          </div>

          <el-divider>剧情简介</el-divider>

          <div class="description-section">
            <p v-if="tvShow.description">{{ tvShow.description }}</p>
            <p v-else class="no-description">暂无剧情简介</p>
          </div>
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped>
.detail-container {
  padding: 1rem 0;
  position: relative;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #606266;
  cursor: pointer;
  padding: 0.5rem 0;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.back-button:hover {
  color: #41b883;
}

.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem;
  color: #f56c6c;
  font-size: 1.25rem;
}

.tv-detail {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.detail-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.poster-container {
  flex-shrink: 0;
}

.poster-image {
  width: 240px;
  height: 360px;
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s, box-shadow 0.3s;
}

.poster-image:hover {
  transform: scale(1.02);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
}

.image-placeholder {
  width: 240px;
  height: 360px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 14px;
  border-radius: 8px;
}

.basic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.rating-score {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ff9900;
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.douban-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #41b883;
  text-decoration: none;
  font-weight: 500;
  margin-top: 1rem;
}

.douban-link:hover {
  text-decoration: underline;
}

.description-section {
  line-height: 1.8;
  font-size: 1.1rem;
  color: #606266;
  white-space: pre-line;
}

.no-description {
  color: #909399;
  font-style: italic;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .poster-container {
    margin-bottom: 1.5rem;
  }

  .tags-section {
    justify-content: center;
  }
}
</style>
