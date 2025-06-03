#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从MongoDB数据库中查询豆瓣热门电视剧数据
"""

import json
import os
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Any, Optional
from datetime import datetime

# 配置信息
CONFIG = {
    "mongodb_uri": "mongodb://root:Alone117@127.0.0.1:27017/douban?authSource=admin",  # MongoDB连接字符串
    "db_name": "douban",  # 数据库名
    "collection_name": "hot_tv",  # 集合名
}


class DoubanMongoDBQuery:
    def __init__(self, config: Dict[str, str]):
        """
        初始化MongoDB连接

        :param config: 配置字典，包含MongoDB连接信息
        """
        self.config = config
        self.client = None
        self.db = None
        self.collection = None

    def connect(self) -> bool:
        """
        连接到MongoDB服务器

        :return: 连接是否成功
        """
        try:
            self.client = MongoClient(self.config["mongodb_uri"])
            # 检查连接是否成功
            self.client.admin.command("ping")
            self.db = self.client[self.config["db_name"]]
            self.collection = self.db[self.config["collection_name"]]
            print(f"成功连接到MongoDB: {self.config['mongodb_uri']}")
            return True
        except ConnectionFailure as e:
            print(f"MongoDB连接失败: {e}")
            return False

    def get_latest_data(self) -> List[Dict[str, Any]]:
        """
        获取最新的一条记录中的所有电视剧数据

        :return: 电视剧数据列表
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return []

        try:
            # 按创建时间降序排序，获取最新的一条记录
            latest_record = self.collection.find_one(sort=[("created_at", DESCENDING)])

            if latest_record and "items" in latest_record:
                # 转换数据格式
                tv_list = []
                for item in latest_record["items"]:
                    tv_list.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("detail_url", ""),
                            "cover": item.get("image", ""),
                            "rate": item.get("rating", 0),
                            "description": item.get("intro", ""),
                            "category": item.get("genres", []),
                            "area": item.get("country", ""),
                            "directors": item.get("directors", []),
                            "actors": item.get("actors", []),
                            "year": (
                                int(item.get("year", 0))
                                if item.get("year", "").isdigit()
                                else 0
                            ),
                            "update_time": latest_record.get(
                                "created_at", datetime.utcnow()
                            ).strftime("%Y-%m-%d"),
                        }
                    )
                return tv_list
            return []

        except Exception as e:
            print(f"获取最新数据时出错: {e}")
            return []

    def get_rate_stats(self) -> Dict[str, int]:
        """
        获取评分统计数据

        :return: 评分统计数据字典
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return {}

        try:
            # 获取最新数据
            tv_list = self.get_latest_data()

            # 初始化评分区间
            rate_stats = {"0-5": 0, "5-6": 0, "6-7": 0, "7-8": 0, "8-9": 0, "9-10": 0}

            # 统计每个评分区间的电视剧数量
            for tv in tv_list:
                rate = (
                    float(tv["rate"])
                    if isinstance(tv["rate"], (int, float, str))
                    and str(tv["rate"]).replace(".", "", 1).isdigit()
                    else 0
                )

                if rate < 5:
                    rate_stats["0-5"] += 1
                elif rate < 6:
                    rate_stats["5-6"] += 1
                elif rate < 7:
                    rate_stats["6-7"] += 1
                elif rate < 8:
                    rate_stats["7-8"] += 1
                elif rate < 9:
                    rate_stats["8-9"] += 1
                else:
                    rate_stats["9-10"] += 1

            return rate_stats

        except Exception as e:
            print(f"获取评分统计数据时出错: {e}")
            return {}

    def get_category_stats(self) -> Dict[str, int]:
        """
        获取类型统计数据

        :return: 类型统计数据字典
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return {}

        try:
            # 获取最新数据
            tv_list = self.get_latest_data()

            # 统计每个类型的电视剧数量
            category_stats = {}
            for tv in tv_list:
                for category in tv["category"]:
                    if category in category_stats:
                        category_stats[category] += 1
                    else:
                        category_stats[category] = 1

            return category_stats

        except Exception as e:
            print(f"获取类型统计数据时出错: {e}")
            return {}

    def get_area_stats(self) -> Dict[str, int]:
        """
        获取地区统计数据

        :return: 地区统计数据字典
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return {}

        try:
            # 获取最新数据
            tv_list = self.get_latest_data()

            # 统计每个地区的电视剧数量
            area_stats = {}
            for tv in tv_list:
                area = tv["area"]
                if area in area_stats:
                    area_stats[area] += 1
                else:
                    area_stats[area] = 1

            return area_stats

        except Exception as e:
            print(f"获取地区统计数据时出错: {e}")
            return {}

    def get_year_stats(self) -> Dict[str, int]:
        """
        获取年份统计数据

        :return: 年份统计数据字典
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return {}

        try:
            # 获取最新数据
            tv_list = self.get_latest_data()

            # 统计每个年份的电视剧数量
            year_stats = {}
            for tv in tv_list:
                year = tv["year"]
                if year > 0:  # 跳过无效年份
                    year_str = str(year)
                    if year_str in year_stats:
                        year_stats[year_str] += 1
                    else:
                        year_stats[year_str] = 1

            return year_stats

        except Exception as e:
            print(f"获取年份统计数据时出错: {e}")
            return {}

    def get_tv_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        根据URL获取单个电视剧详情

        :param url: 电视剧详情页URL
        :return: 电视剧详情数据或None
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return None

        try:
            # 获取最新数据
            tv_list = self.get_latest_data()

            # 查找匹配URL的电视剧
            for tv in tv_list:
                if tv["url"] == url:
                    return tv

            return None

        except Exception as e:
            print(f"获取电视剧详情时出错: {e}")
            return None

    def close(self) -> None:
        """
        关闭MongoDB连接
        """
        if self.client:
            self.client.close()
            print("已关闭MongoDB连接")


def query_mongo(config: Dict[str, str] = None):
    """
    创建MongoDB查询实例的便捷函数

    :param config: 可选的配置信息，不提供则使用默认配置
    :return: MongoDB查询实例
    """
    # 使用提供的配置或默认配置
    cfg = config or CONFIG
    db_handler = DoubanMongoDBQuery(cfg)

    # 连接数据库
    if not db_handler.connect():
        return None

    return db_handler


if __name__ == "__main__":
    # 测试查询功能
    db_query = query_mongo()
    if db_query:
        try:
            # 获取最新数据
            latest_data = db_query.get_latest_data()
            print(f"获取到 {len(latest_data)} 条电视剧数据")

            # 获取统计数据
            rate_stats = db_query.get_rate_stats()
            print(f"评分统计: {rate_stats}")

            category_stats = db_query.get_category_stats()
            print(f"类型统计: {category_stats}")

            area_stats = db_query.get_area_stats()
            print(f"地区统计: {area_stats}")

            year_stats = db_query.get_year_stats()
            print(f"年份统计: {year_stats}")

        finally:
            # 关闭连接
            db_query.close()
