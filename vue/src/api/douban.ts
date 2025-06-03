import request from '@/utils/request';

export interface TVShow {
  title: string;
  url: string;
  cover: string;
  rate: number;
  description: string;
  category: string[];
  directors: string[];
  actors: string[];
  year: number;
  update_time: string;
}

// 定义请求参数接口
export interface HotTVShowsParams {
  keyword?: string;
  category?: string;
  area?: string;
  year?: number;
  min_rate?: number;
  max_rate?: number;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: string;
}

// 获取豆瓣热门电视剧数据，支持分页和筛选参数
export function getHotTVShows(params?: HotTVShowsParams) {
  return request({
    url: '/api/douban/hot-tv',
    method: 'get',
    params
  });
}

// 获取电视剧评分统计
export function getRateStats() {
  return request({
    url: '/api/douban/rate-stats',
    method: 'get'
  });
}

// 获取电视剧类型分布
export function getCategoryStats() {
  return request({
    url: '/api/douban/category-stats',
    method: 'get'
  });
}



// 获取电视剧年份分布
export function getYearStats() {
  return request({
    url: '/api/douban/year-stats',
    method: 'get'
  });
}

// 获取电视剧详情
export function getTVShowDetail(url: string) {
  return request({
    url: '/api/douban/tv-detail',
    method: 'get',
    params: { url }
  });
}
