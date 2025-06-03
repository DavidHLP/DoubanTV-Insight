#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
豆瓣电视剧数据分析可视化系统 - FastAPI 后端
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, Depends, Response
import httpx
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# 添加项目根目录到系统路径，以便导入MongoDB模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 导入MongoDB查询模块
from python.mongodb.select_douban_hot import query_mongo

# 创建FastAPI应用
app = FastAPI(
    title="豆瓣电视剧数据分析API",
    description="提供豆瓣热门电视剧数据查询和统计分析的API",
    version="1.0.0",
)

# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],  # 允许前端开发服务器的来源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)


# 模型定义
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None


# 依赖项：获取MongoDB连接
def get_db():
    db = query_mongo()
    if not db:
        raise HTTPException(status_code=500, detail="无法连接到MongoDB数据库")
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_model=ResponseModel)
async def root():
    """
    API根路径，返回API基本信息
    """
    return {
        "code": 200,
        "message": "欢迎使用豆瓣电视剧数据分析API",
        "data": {
            "api_name": "豆瓣电视剧数据分析API",
            "version": "1.0.0",
            "documentation": "/docs",
        },
    }


@app.get("/api/douban/hot-tv", response_model=ResponseModel)
async def get_hot_tv(
    db=Depends(get_db),
    keyword: Optional[str] = Query(None, description="标题关键词"),
    category: Optional[str] = Query(None, description="类型"),
    area: Optional[str] = Query(None, description="地区"),
    year: Optional[int] = Query(None, description="年份"),
    min_rate: Optional[float] = Query(None, description="最低评分"),
    max_rate: Optional[float] = Query(None, description="最高评分"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    sort_by: str = Query("rate", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
):
    """
    获取热门电视剧列表，支持过滤、排序和分页
    """
    try:
        # 获取最新数据
        all_data = db.get_latest_data()

        # 过滤数据
        filtered_data = all_data

        # 按关键词过滤
        if keyword:
            filtered_data = [
                tv for tv in filtered_data if keyword.lower() in tv["title"].lower()
            ]

        # 按类型过滤
        if category:
            filtered_data = [tv for tv in filtered_data if category in tv["category"]]

        # 按地区过滤
        if area:
            filtered_data = [tv for tv in filtered_data if area == tv["area"]]

        # 按年份过滤
        if year:
            filtered_data = [tv for tv in filtered_data if tv["year"] == year]

        # 按评分区间过滤
        if min_rate is not None:
            filtered_data = [
                tv for tv in filtered_data if float(tv["rate"]) >= min_rate
            ]
        if max_rate is not None:
            filtered_data = [
                tv for tv in filtered_data if float(tv["rate"]) <= max_rate
            ]

        # 排序
        reverse = sort_order.lower() == "desc"
        if sort_by == "rate":
            filtered_data.sort(
                key=lambda x: (
                    float(x["rate"])
                    if isinstance(x["rate"], (int, float, str))
                    and str(x["rate"]).replace(".", "", 1).isdigit()
                    else 0
                ),
                reverse=reverse,
            )
        elif sort_by == "year":
            filtered_data.sort(key=lambda x: x["year"], reverse=reverse)
        elif sort_by == "title":
            filtered_data.sort(key=lambda x: x["title"], reverse=reverse)

        # 计算总数
        total_count = len(filtered_data)

        # 分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = filtered_data[start_idx:end_idx]

        return {
            "code": 200,
            "message": "获取热门电视剧列表成功",
            "data": {
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "items": paginated_data,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门电视剧列表失败: {str(e)}")


@app.get("/api/douban/rate-stats", response_model=ResponseModel)
async def get_rate_stats(db=Depends(get_db)):
    """
    获取评分统计数据
    """
    try:
        rate_stats = db.get_rate_stats()

        # 转换为前端所需格式
        formatted_stats = [
            {"name": key, "value": value} for key, value in rate_stats.items()
        ]

        return {"code": 200, "message": "获取评分统计数据成功", "data": formatted_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评分统计数据失败: {str(e)}")


@app.get("/api/douban/category-stats", response_model=ResponseModel)
async def get_category_stats(db=Depends(get_db)):
    """
    获取类型统计数据
    """
    try:
        category_stats = db.get_category_stats()

        # 转换为前端所需格式
        formatted_stats = [
            {"name": key, "value": value} for key, value in category_stats.items()
        ]

        return {"code": 200, "message": "获取类型统计数据成功", "data": formatted_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取类型统计数据失败: {str(e)}")


@app.get("/api/douban/area-stats", response_model=ResponseModel)
async def get_area_stats(db=Depends(get_db)):
    """
    获取地区统计数据
    """
    try:
        area_stats = db.get_area_stats()

        # 转换为前端所需格式
        formatted_stats = [
            {"name": key, "value": value} for key, value in area_stats.items()
        ]

        return {"code": 200, "message": "获取地区统计数据成功", "data": formatted_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地区统计数据失败: {str(e)}")


@app.get("/api/douban/year-stats", response_model=ResponseModel)
async def get_year_stats(db=Depends(get_db)):
    """
    获取年份统计数据
    """
    try:
        year_stats = db.get_year_stats()

        # 转换为前端所需格式
        formatted_stats = [
            {"name": key, "value": value} for key, value in sorted(year_stats.items())
        ]

        return {"code": 200, "message": "获取年份统计数据成功", "data": formatted_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取年份统计数据失败: {str(e)}")


@app.get("/api/douban/tv-detail", response_model=ResponseModel)
async def get_tv_detail(url: str, db=Depends(get_db)):
    """
    获取单个电视剧详情
    """
    try:
        tv_detail = db.get_tv_by_url(url)

        if not tv_detail:
            return {"code": 404, "message": "未找到指定电视剧", "data": None}

        return {"code": 200, "message": "获取电视剧详情成功", "data": tv_detail}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取电视剧详情失败: {str(e)}")


@app.get("/api/proxy/image")
async def proxy_image(url: str):
    """
    图片代理接口，解决跨域问题
    """
    try:
        async with httpx.AsyncClient() as client:
            # 添加豆瓣网站常用的请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
                "Referer": "https://movie.douban.com/",
            }
            response = await client.get(url, headers=headers, follow_redirects=True)

            # 返回图片内容
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # 启动FastAPI应用
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
