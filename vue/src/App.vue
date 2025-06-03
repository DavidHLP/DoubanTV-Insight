<script setup lang="ts">
import { RouterView } from 'vue-router';
import { onMounted } from 'vue';
import { useDoubanStore } from '@/stores/douban';

const doubanStore = useDoubanStore();

onMounted(() => {
  doubanStore.fetchAllData();
});
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo">豆瓣电视剧数据分析</div>
      <nav class="main-nav">
        <router-link to="/">首页</router-link>
        <router-link to="/analysis">数据分析</router-link>
        <router-link to="/ranking">排行榜</router-link>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <p>© 2025 豆瓣电视剧数据分析可视化系统</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #f5f7fa;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #41b883;
}

.main-nav {
  display: flex;
  gap: 1.5rem;
}

.main-nav a {
  text-decoration: none;
  color: #606266;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
}

.main-nav a:hover,
.main-nav a.router-link-active {
  color: #41b883;
}

.main-nav a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #41b883;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: #909399;
  background-color: #fff;
  border-top: 1px solid #ebeef5;
}
</style>
