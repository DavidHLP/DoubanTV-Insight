# 豆瓣电视剧数据分析可视化系统 (DoubanTV-Insight)

## 项目简介

豆瓣电视剧数据分析可视化系统是一个全栈应用，旨在通过爬取、分析和可视化豆瓣电视剧数据，帮助用户发现热门电视剧趋势、评分分布以及类型、地区、年份等多维度的统计信息。系统提供了直观的数据展示和灵活的筛选功能，为用户提供全面的电视剧数据洞察。

## 功能特点

### 数据采集与管理
- 自动爬取豆瓣热门电视剧数据
- 数据持久化存储至MongoDB数据库
- 定期更新数据，确保信息时效性

### 数据分析与展示
- 电视剧评分分布统计
- 类型（剧情、喜剧、悬疑等）分布分析
- 制作地区数据统计
- 年份趋势分析

### 用户交互
- 灵活的搜索和筛选功能（按关键词、类型、地区、年份、评分等）
- 排序功能（按评分、年份、标题等）
- 分页浏览热门电视剧列表
- 电视剧详情查看

### 可视化呈现
- 交互式图表展示统计数据
- 响应式设计，适配不同设备

## 技术架构

### 前端 (Vue)
- 框架：Vue 3 + TypeScript
- UI组件库：Element Plus
- 数据可视化：ECharts
- 状态管理：Pinia
- 路由管理：Vue Router
- HTTP客户端：Axios
- 实时通信：SockJS + StompJS
- 构建工具：Vite

### 后端 (Python)
- Web框架：FastAPI
- 数据库：MongoDB
- 数据爬取：自定义爬虫模块
- 图片代理：解决跨域问题的图片代理服务

### 数据流向
1. 爬虫程序定期从豆瓣网站采集热门电视剧数据
2. 数据经过清洗和结构化，存储到MongoDB数据库
3. FastAPI后端提供RESTful API接口
4. Vue前端通过API获取数据并进行可视化展示

## 安装说明

### 环境要求
- Python 3.8+
- Node.js 16+
- MongoDB 4.4+

### 后端部署

1. 进入Python目录
```bash
cd python
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖包
```bash
pip install fastapi uvicorn pymongo httpx
```

4. 配置MongoDB连接
在 `python/mongodb/select_douban_hot.py` 文件中修改MongoDB连接信息：
```python
CONFIG = {
    "mongodb_uri": "mongodb://用户名:密码@主机:端口/douban?authSource=admin",
    "db_name": "douban",
    "collection_name": "hot_tv",
}
```

5. 启动API服务
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端部署

1. 进入Vue目录
```bash
cd vue
```

2. 安装依赖
```bash
npm install
# 或
yarn install
```

3. 开发模式运行
```bash
npm run dev
# 或
yarn dev
```

4. 构建生产版本
```bash
npm run build
# 或
yarn build
```

## 使用指南

### API文档
启动后端服务后，访问 http://localhost:8000/docs 可查看完整的API文档和交互式测试界面。

### 主要API端点

- `GET /api/douban/hot-tv` - 获取热门电视剧列表，支持过滤、排序和分页
- `GET /api/douban/rate-stats` - 获取评分统计数据
- `GET /api/douban/category-stats` - 获取类型统计数据
- `GET /api/douban/area-stats` - 获取地区统计数据
- `GET /api/douban/year-stats` - 获取年份统计数据
- `GET /api/douban/tv-detail` - 获取单个电视剧详情

### 前端页面

启动前端服务后，访问 http://localhost:5173 可访问系统主页：

- 首页：展示数据概览和统计图表
- 列表页：提供电视剧列表浏览和筛选功能
- 详情页：展示单部电视剧的详细信息

## 数据更新

系统默认通过爬虫程序定期从豆瓣网站更新数据。若需手动更新，可运行：

```bash
python python/crawlr/douban_crawler.py
```

## 项目结构

```
/
├── python/                 # 后端代码
│   ├── api/                # FastAPI应用
│   │   └── main.py         # API主程序
│   ├── crawlr/             # 爬虫模块
│   │   └── douban_crawler.py  # 豆瓣爬虫
│   └── mongodb/            # MongoDB操作模块
│       ├── save_douban_hot.py    # 数据存储
│       └── select_douban_hot.py  # 数据查询
│
└── vue/                    # 前端代码
    ├── public/             # 静态资源
    ├── src/                # 源代码
    │   ├── assets/         # 资源文件
    │   ├── components/     # 组件
    │   ├── router/         # 路由配置
    │   ├── stores/         # Pinia状态管理
    │   ├── views/          # 页面视图
    │   └── App.vue         # 主组件
    ├── package.json        # 依赖配置
    └── vite.config.ts      # Vite配置
```

## 开发者信息

- 项目开发：David H
- 联系方式：请通过GitHub Issues提交问题或建议

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。