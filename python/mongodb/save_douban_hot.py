#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将豆瓣热门电视剧数据保存到MongoDB数据库
"""

import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import List, Dict, Any, Optional
from datetime import datetime

# 配置信息
CONFIG = {
    "mongodb_uri": "mongodb://root:Alone117@127.0.0.1:27017/douban?authSource=admin",  # MongoDB连接字符串
    "db_name": "douban",  # 数据库名
    "collection_name": "hot_tv",  # 集合名
}


class DoubanToMongoDB:
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

    def create_indexes(self) -> None:
        """
        创建索引以提高查询性能
        """
        if self.collection is None:
            return

        # 创建标题索引
        self.collection.create_index("title", name="title_index")
        # 创建评分索引（降序）
        self.collection.create_index([("rating", -1)], name="rating_index")
        # 创建年份索引
        self.collection.create_index("year", name="year_index")

        print("已创建索引")

    def save_as_single_record(self, data_list: List[Dict[str, Any]]) -> int:
        """
        将整个数据列表作为一条记录保存到MongoDB

        :param data_list: 要保存的数据列表
        :return: 成功保存的记录数（0或1）
        """
        if self.collection is None:
            print("错误：未连接到MongoDB")
            return 0

        try:
            # 创建一条包含当前时间和所有数据的记录
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            record = {
                "_id": f"douban_hot_tv_{now.strftime('%Y%m%d')}",
                "created_at": today,
                "data_count": len(data_list),
                "items": data_list,
            }

            # 插入或更新数据
            result = self.collection.insert_one(record)

            if result.inserted_id:
                print(f"成功保存数据集合 (ID: {result.inserted_id})")
                print(f"数据集合包含 {len(data_list)} 条电视剧记录")
                return 1
            return 0

        except Exception as e:
            print(f"保存数据集合时出错: {e}")
            return 0

    def close(self) -> None:
        """
        关闭MongoDB连接
        """
        if self.client:
            self.client.close()
            print("已关闭MongoDB连接")


def save_to_mongo(
    data_list: List[Dict[str, Any]], config: Dict[str, str] = None
) -> int:
    """
    将数据保存到MongoDB的便捷函数

    :param data_list: 要保存的数据列表
    :param config: 可选的配置信息，不提供则使用默认配置
    :return: 成功保存的记录数
    """
    # 检查数据列表是否为空
    if not data_list:
        print("没有数据可保存")
        return 0

    # 使用提供的配置或默认配置
    cfg = config or CONFIG
    db_handler = DoubanToMongoDB(cfg)

    try:
        # 连接数据库
        if not db_handler.connect():
            return 0

        # 创建索引
        db_handler.create_indexes()

        # 将数据保存为一条记录
        saved_count = db_handler.save_as_single_record(data_list)
        return saved_count

    except Exception as e:
        print(f"保存到MongoDB时发生错误: {e}")
        return 0
    finally:
        # 关闭连接
        db_handler.close()


if __name__ == "__main__":
    pass
