#!/usr/bin/env python3
"""
微博热搜数据获取模块
从天API获取微博热搜数据并保存为JSON格式

支持配置文件和环境变量，实现灵活的参数配置
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


class WeiboFetcher:
    """微博热搜数据获取器"""

    def __init__(self, config_path: Optional[Path] = None, api_key: Optional[str] = None):
        """
        初始化获取器

        Args:
            config_path: 配置文件路径，默认为config/config.yaml
            api_key: API密钥，覆盖配置文件和环境变量
        """
        # 初始化配置加载器
        config_path = config_path or PathManager().get_config_file()
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()

        # 初始化路径管理器
        self.path_manager = PathManager()

        # 从配置加载API参数
        api_config = self.config["api"]["tianapi"]
        self.api_url = api_config["base_url"]
        self.timeout = api_config["timeout"]
        self.max_retries = api_config["max_retries"]

        # 获取API密钥（优先级: 参数 > 环境变量 > 配置文件）
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = self.config_loader.get_api_key()
            except ValueError as e:
                # 不直接退出，允许后续设置
                self.api_key = ""

        # 获取输出配置
        self.output_config = self.config["output"]
        self.paths_config = self.config["paths"]

    def check_api_key(self) -> bool:
        """检查API密钥是否已设置"""
        if not self.api_key:
            print("错误: API密钥未设置！请通过以下方式之一设置：")
            print("1. 环境变量: export TIANAPI_KEY=your_key")
            print("2. 配置文件: config.yaml中的api.tianapi.key")
            print("3. 命令行参数: --api-key YOUR_KEY")
            return False
        return True

    def fetch_hot_search(self) -> Optional[Dict[str, Any]]:
        """
        从天API获取热搜数据

        Returns:
            包含热搜话题的字典，失败时返回None
        """
        params = {"key": self.api_key}

        for attempt in range(self.max_retries):
            try:
                print(f"正在获取数据 (尝试 {attempt + 1}/{self.max_retries})...")
                response = requests.get(
                    self.api_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()

                # 验证响应
                if not self._validate_response(data):
                    print(f"无效的响应结构: {data}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    return None

                print(f"成功获取 {len(data.get('result', []))} 个话题")
                return data

            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return None

        return None

    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """
        验证API响应结构

        期望格式: {"code": 200, "msg": "success", "result": {"list": [...]}}
        或: {"code": 200, "msg": "success", "result": [...]}

        Args:
            data: API响应数据

        Returns:
            响应是否有效
        """
        if not isinstance(data, dict):
            return False

        if data.get("code") != 200:
            print(f"API返回错误代码: {data.get('code')}, 消息: {data.get('msg')}")
            return False

        if "result" not in data:
            return False

        result = data["result"]
        # 处理两种格式: result为list或result为包含list的dict
        if isinstance(result, dict):
            if "list" not in result or not isinstance(result["list"], list):
                return False
        elif not isinstance(result, list):
            return False

        return True

    def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理原始API数据为结构化格式

        Args:
            raw_data: 原始API响应数据

        Returns:
            处理后的数据字典
        """
        result = raw_data.get("result", [])

        # 处理两种格式
        if isinstance(result, dict):
            result = result.get("list", [])

        topics = []
        for idx, item in enumerate(result, 1):
            # 处理不同的字段名
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
            "source": "tianapi_weibohot",
            "api_code": raw_data.get("code"),
            "api_message": raw_data.get("msg"),
            "topics": topics,
            "total_count": len(topics),
            "timestamp": datetime.now().strftime(timestamp_format)
        }

    def save_to_json(self, data: Dict[str, Any]) -> Path:
        """
        保存数据到带时间戳的JSON文件

        Args:
            data: 要保存的数据

        Returns:
            保存的文件路径
        """
        # 确保数据目录存在
        data_dir = self.path_manager.ensure_data_dir()

        # 生成文件名
        timestamp = data.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
        filename_format = self.paths_config.get("raw_filename_format", "weibo_raw_{timestamp}.json")
        filename = filename_format.format(timestamp=timestamp)
        filepath = data_dir / filename

        # 保存文件
        encoding = self.output_config.get("encoding", "utf-8")
        indent = self.output_config.get("json_indent", 2)

        with open(filepath, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

        return filepath

    def run(self) -> int:
        """
        执行完整的数据获取流程

        Returns:
            退出代码 (0=成功, 1=失败)
        """
        # 检查API密钥
        if not self.check_api_key():
            return 1

        print("开始获取微博热搜数据...")

        # 获取数据
        raw_data = self.fetch_hot_search()

        if raw_data is None:
            print("错误: 所有重试后仍无法获取数据")
            return 1

        # 处理数据
        processed_data = self.process_data(raw_data)

        # 保存到JSON
        try:
            filepath = self.save_to_json(processed_data)
            print(f"\n成功: 数据已保存到 {filepath}")
            print(f"总话题数: {processed_data['total_count']}")
            print(f"获取时间: {processed_data['fetch_time']}")
            return 0
        except Exception as e:
            print(f"错误: 保存数据失败: {e}")
            return 1


def main():
    """主执行函数"""
    parser = argparse.ArgumentParser(
        description="从天API获取微博热搜数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m src.fetch_weibo                    # 使用默认配置
  python -m src.fetch_weibo --config custom.yaml  # 使用自定义配置
  python -m src.fetch_weibo --api-key YOUR_KEY    # 指定API密钥
        """
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="配置文件路径 (默认: config/config.yaml)"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="天API密钥 (覆盖配置文件和环境变量)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出目录 (覆盖配置文件)"
    )

    args = parser.parse_args()

    # 确定配置文件路径
    config_path = args.config
    if config_path is None:
        # 使用默认配置文件
        path_manager = PathManager()
        config_path = path_manager.get_config_file()

    # 初始化获取器（传入API密钥参数）
    fetcher = WeiboFetcher(config_path, api_key=args.api_key)

    # 处理输出目录参数
    if args.output:
        # 覆盖输出目录
        fetcher.path_manager.ensure_dir(args.output)
        fetcher.path_manager.project_root = args.output

    # 执行
    return fetcher.run()


if __name__ == "__main__":
    sys.exit(main())
