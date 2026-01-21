#!/usr/bin/env python3
"""
Configuration loader with YAML and environment variable support.
支持YAML配置文件和环境变量的配置加载器。
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigLoader:
    """
    配置加载器
    支持从YAML文件加载配置，并通过环境变量覆盖
    """

    # 环境变量前缀
    ENV_PREFIX = "WEIBO_SKILL_"

    # 默认配置
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "api": {
            "tianapi": {
                "base_url": "https://apis.tianapi.com/weibohot/index",
                "timeout": 30,
                "max_retries": 3,
                "key": ""
            }
        },
        "analysis": {
            "topic_count": 20,
            "enable_web_search": True,
            "search_delay": 2,
            "scoring": {
                "interesting": 80,
                "useful": 20,
                "interesting_detail": {
                    "novelty": 20,
                    "resonance": 20,
                    "viral": 20,
                    "entertainment": 20
                },
                "useful_detail": {
                    "practical": 10,
                    "market": 10
                }
            }
        },
        "paths": {
            "data_dir": "data",
            "raw_filename_format": "weibo_raw_{timestamp}.json",
            "report_filename_format": "weibo_analysis_{timestamp}.html",
            "timestamp_format": "%Y%m%d_%H%M%S"
        },
        "output": {
            "json_indent": 2,
            "encoding": "utf-8",
            "save_intermediate": True,
            "intermediate_filename": "weibo_analysis_{timestamp}.json"
        },
        "logging": {
            "level": "INFO",
            "file": "logs/skill.log",
            "console": True,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "html": {
            "title": "微博热搜产品创意分析",
            "theme": "dark",
            "enable_animation": True,
            "enable_search": True,
            "enable_filter": True
        },
        "grades": {
            "excellent": 80,
            "good": 60,
            "average": 0
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，如果为None则使用默认位置
        """
        self.config_path = config_path
        self._config: Optional[Dict] = None

    def load(self) -> Dict[str, Any]:
        """
        加载配置
        优先级: 环境变量 > YAML配置 > 默认配置

        Returns:
            Dict: 合并后的配置字典
        """
        if self._config is None:
            # 1. 加载默认配置
            self._config = self._deep_copy(self.DEFAULT_CONFIG)

            # 2. 如果YAML可用且配置文件存在，加载YAML配置
            if YAML_AVAILABLE and self.config_path and self.config_path.exists():
                yaml_config = self._load_yaml(self.config_path)
                self._config = self._deep_merge(self._config, yaml_config)

            # 3. 加载环境变量覆盖
            self._config = self._load_env_overrides(self._config)

        return self._config

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """
        从YAML文件加载配置

        Args:
            path: YAML文件路径

        Returns:
            Dict: 配置字典
        """
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _load_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从环境变量加载配置覆盖

        支持的环境变量：
        - TIANAPI_KEY: API密钥
        - WEIBO_SKILL_TOPIC_COUNT: 分析话题数量
        - WEIBO_SKILL_DATA_DIR: 数据目录
        - WEIBO_SKILL_LOG_LEVEL: 日志级别

        Args:
            config: 基础配置字典

        Returns:
            Dict: 应用环境变量覆盖后的配置
        """
        # API密钥（特殊处理，不带前缀）
        api_key = os.getenv("TIANAPI_KEY")
        if api_key:
            config["api"]["tianapi"]["key"] = api_key

        # 分析话题数量
        topic_count = os.getenv(f"{self.ENV_PREFIX}TOPIC_COUNT")
        if topic_count and topic_count.isdigit():
            config["analysis"]["topic_count"] = int(topic_count)

        # 数据目录
        data_dir = os.getenv(f"{self.ENV_PREFIX}DATA_DIR")
        if data_dir:
            config["paths"]["data_dir"] = data_dir

        # 日志级别
        log_level = os.getenv(f"{self.ENV_PREFIX}LOG_LEVEL")
        if log_level:
            config["logging"]["level"] = log_level.upper()

        return config

    def get_api_key(self) -> str:
        """
        获取API密钥

        Returns:
            str: API密钥
        """
        config = self.load()
        api_key = config.get("api", {}).get("tianapi", {}).get("key", "")

        if not api_key:
            raise ValueError(
                "API密钥未设置！请通过以下方式之一设置：\n"
                "1. 环境变量: export TIANAPI_KEY=your_key\n"
                "2. 配置文件: config.yaml中的api.tianapi.key"
            )

        return api_key

    def get_topic_count(self) -> int:
        """获取分析话题数量"""
        config = self.load()
        return config.get("analysis", {}).get("topic_count", 20)

    def get_data_dir(self) -> str:
        """获取数据目录"""
        config = self.load()
        return config.get("paths", {}).get("data_dir", "data")

    def get_log_level(self) -> str:
        """获取日志级别"""
        config = self.load()
        return config.get("logging", {}).get("level", "INFO")

    @staticmethod
    def _deep_copy(obj: Any) -> Any:
        """深度复制对象"""
        if isinstance(obj, dict):
            return {k: ConfigLoader._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ConfigLoader._deep_copy(v) for v in obj]
        return obj

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """
        深度合并两个字典

        Args:
            base: 基础字典
            override: 覆盖字典

        Returns:
            Dict: 合并后的字典
        """
        result = ConfigLoader._deep_copy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        config = self.load()
        return config[key]

    def get(self, key: str, default: Any = None) -> Any:
        """字典式get方法"""
        config = self.load()
        return config.get(key, default)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    便捷函数：加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        Dict: 配置字典
    """
    loader = ConfigLoader(config_path)
    return loader.load()
