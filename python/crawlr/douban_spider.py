#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import os

# 添加项目根目录到系统路径，以便导入MongoDB模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def get_douban_hot_tv(start=0, limit=20, tv_type="tv_american"):
    """
    获取豆瓣热门电视剧数据

    参数：
        start: 起始位置
        limit: 返回数量
        tv_type: 电视剧类型，如tv_american（美剧）

    返回：
        json格式的响应数据
    """
    # 构建URL
    url = "https://m.douban.com/rexxar/api/v2/tv/recommend"
    params = {
        "refresh": 0,
        "start": start,
        "count": limit,
        "selected_categories": '{"地区":"欧美"}',
        "uncollect": False,
        "score_range": "0,10",
        "tags": "欧美",
    }

    # 设置请求头，模拟浏览器行为
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Host": "m.douban.com",
        "Origin": "https://movie.douban.com",
        "Referer": "https://movie.douban.com/tv/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    }

    try:
        # 发送请求
        response = requests.get(url, params=params, headers=headers)

        # 检查响应状态
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


def parse_tv_data(data):
    """
    解析电视剧数据，提取关键信息

    参数：
        data: API返回的原始数据

    返回：
        处理后的电视剧信息列表
    """
    if not data or "items" not in data:
        return []

    result = []

    for item in data["items"]:
        # 从card_subtitle解析更多信息（包含年份、国家、类型等）
        subtitle = item.get("card_subtitle", "")
        subtitle_parts = subtitle.split(" / ") if subtitle else []

        # 提取年份
        year_part = subtitle_parts[0] if len(subtitle_parts) > 0 else ""
        year = year_part.split(" ")[0] if year_part else "未知"

        # 提取类型
        genres = subtitle_parts[1].split(" ") if len(subtitle_parts) > 1 else []

        # 提取导演和演员
        directors_actors = subtitle_parts[2:] if len(subtitle_parts) > 2 else []
        director_names = []
        actor_names = []

        if len(directors_actors) >= 1:
            director_part = directors_actors[0].split(" ")
            director_names = director_part[1:] if len(director_part) > 1 else []

        if len(directors_actors) >= 2:
            actor_part = directors_actors[1].split(" ")
            actor_names = actor_part

        # 提取图片链接
        pic_large = item.get("pic", {}).get("large", "") if item.get("pic") else ""

        # 构建详情链接
        item_id = item.get("id", "")
        detail_url = f"https://movie.douban.com/subject/{item_id}/" if item_id else ""

        tv_info = {
            "title": item.get("title", "未知"),
            "rating": item.get("rating", {}).get("value", "暂无评分"),
            "year": year,
            "genres": genres,
            "directors": director_names,
            "actors": actor_names,
            "intro": subtitle,
            "image": pic_large,
            "detail_url": detail_url,
            "id": item_id,
        }
        result.append(tv_info)

    return result


def get_all_tv_data():
    """
    获取所有分页的电视剧数据
    """
    all_items = []
    start = 0
    limit = 20  # 每次获取20条数据
    tv_type = "tv_american"  # 美剧类型

    print("开始获取所有豆瓣热门美剧数据...")

    while True:
        print(f"正在获取第 {start//limit + 1} 页数据...")
        raw_data = get_douban_hot_tv(start, limit, tv_type)

        if not raw_data or "items" not in raw_data or not raw_data["items"]:
            print("没有更多数据了")
            break

        # 解析当前页数据
        current_page_items = parse_tv_data(raw_data)
        if not current_page_items:
            print(f"第 {start//limit + 1} 页没有有效数据")
            break

        # 添加到总数据中
        all_items.extend(current_page_items)
        print(f"已获取 {len(current_page_items)} 条数据，总计 {len(all_items)} 条")

        # 准备获取下一页
        start += limit

        # 添加延时，避免请求过于频繁
        import time

        time.sleep(1)

    return all_items


def main():
    """
    主函数，执行数据获取和处理并保存到MongoDB
    """
    try:
        # 导入MongoDB模块（放在函数内避免循环导入问题）
        from python.mongodb.save_douban_hot import save_to_mongo

        # 获取所有数据
        all_tv_data = get_all_tv_data()

        if all_tv_data:
            # 保存到MongoDB数据库
            saved_count = save_to_mongo(all_tv_data)
            print(f"成功获取并处理 {len(all_tv_data)} 条美剧数据")
            print(f"成功保存 {saved_count} 条记录到MongoDB数据库")
        else:
            print("获取数据失败")
    except ImportError:
        print("错误：未能导入MongoDB模块，请确保项目结构正确")
    except Exception as e:
        print(f"保存数据时发生错误: {e}")


if __name__ == "__main__":
    main()
