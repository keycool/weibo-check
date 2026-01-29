#!/usr/bin/env python3
"""
热搜数据获取模块
从天API获取微博、抖音、微信热搜数据并保存为JSON格式
"""
import sys
import os
import argparse
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import requests

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.path_utils import PathManager


class HotSearchFetcher:
    """通用热搜数据获取器"""

    def __init__(self, source: str = "weibo", config_path: Optional[Path] = None, api_key: Optional[str] = None):
        """
        初始化获取器

        Args:
            source: 热搜来源 (weibo, douyin, wechat)
            config_path: 配置文件路径
            api_key: API密钥
        """
        self.source = source
        # 初始化配置加载器
        config_path = config_path or PathManager().get_config_file()
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()

        # 初始化路径管理器
        self.path_manager = PathManager()

        # 从配置加载API参数
        api_config = self.config["api"]["tianapi"]
        
        # 验证source是否合法
        sources = api_config.get("sources", {})
        if source not in sources:
            available = ", ".join(sources.keys())
            raise ValueError(f"不支持的来源 '{source}'。可用来源: {available}")
            
        self.api_url = sources[source]
        self.timeout = api_config.get("timeout", 30)
        self.max_retries = api_config.get("max_retries", 3)

        # 获取API密钥
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = self.config_loader.get_api_key()
            except ValueError:
                self.api_key = ""

        self.output_config = self.config.get("output", {})
        self.paths_config = self.config.get("paths", {})

    def check_api_key(self) -> bool:
        """检查API密钥是否已设置"""
        if not self.api_key:
            print("错误: API密钥未设置！")
            return False
        return True

    def fetch_hot_search(self) -> Optional[Dict[str, Any]]:
        """从请求源获取数据"""
        params = {"key": self.api_key}

        for attempt in range(self.max_retries):
            try:
                print(f"正在获取 {self.source} 数据 (尝试 {attempt + 1}/{self.max_retries})...")
                response = requests.get(
                    self.api_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                if not self._validate_response(data):
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None

                print(f"成功获取 {len(data.get('result', []))} 个话题")
                return data

            except Exception as e:
                print(f"尝试 {attempt + 1} 失败: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def _validate_response(self, data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict): return False
        if data.get("code") != 200:
            print(f"API返回错误: {data.get('msg')}")
            return False
        return "result" in data

    def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        result = raw_data.get("result", [])
        if isinstance(result, dict):
            result = result.get("list", [])

        topics = []
        for idx, item in enumerate(result, 1):
            # 天API的字段可能因接口而异，这里做一层兼容
            topic = {
                "rank": idx,
                "title": item.get("word", item.get("title", item.get("hotword", "未知话题"))),
                "hot_value": item.get("hotnum", item.get("hot", item.get("hotwordnum", item.get("num", "N/A")))),
                "url": item.get("url", ""),
                "description": item.get("desc", item.get("description", item.get("hottag", "")))
            }
            topics.append(topic)

        timestamp_format = self.paths_config.get("timestamp_format", "%Y%m%d_%H%M%S")
        return {
            "fetch_time": datetime.now().isoformat(),
            "source": self.source,
            "api_code": raw_data.get("code"),
            "api_message": raw_data.get("msg"),
            "topics": topics,
            "total_count": len(topics),
            "timestamp": datetime.now().strftime(timestamp_format)
        }

    def save_to_json(self, data: Dict[str, Any]) -> Path:
        data_dir = self.path_manager.ensure_data_dir()
        timestamp = data.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
        filename_format = self.paths_config.get("raw_filename_format", "{source}_raw_{timestamp}.json")
        filename = filename_format.format(source=self.source, timestamp=timestamp)
        filepath = data_dir / filename

        encoding = self.output_config.get("encoding", "utf-8")
        indent = self.output_config.get("json_indent", 2)

        with open(filepath, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

        return filepath

    def run(self) -> int:
        if not self.check_api_key(): return 1
        raw_data = self.fetch_hot_search()
        if raw_data is None: return 1
        processed_data = self.process_data(raw_data)
        try:
            filepath = self.save_to_json(processed_data)
            print(f"成功: 数据已保存到 {filepath}")
            return 0
        except Exception as e:
            print(f"保存失败: {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(description="获取各大平台热搜数据")
    parser.add_argument("--source", default="weibo", choices=["weibo", "douyin", "wechat"], help="来源平台")
    parser.add_argument("--api-key", default=None, help="API密钥")
    args = parser.parse_args()
    
    fetcher = HotSearchFetcher(source=args.source, api_key=args.api_key)
    return fetcher.run()


if __name__ == "__main__":
    sys.exit(main())
