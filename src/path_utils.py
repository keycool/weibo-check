#!/usr/bin/env python3
"""
Path utility module for cross-platform path management.
自动检测项目根目录并提供跨平台路径处理功能。
"""
import os
from pathlib import Path
from typing import Optional, Union


class PathManager:
    """
    跨平台路径管理器
    自动检测项目根目录并提供统一的路径访问接口
    """

    # 项目根目录的标识文件/目录
    PROJECT_MARKERS = [
        ".claude",
        "config",
        "src",
        "data"
    ]

    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        """
        初始化路径管理器

        Args:
            project_root: 项目根目录路径，如果为None则自动检测
        """
        if project_root is None:
            project_root = self._find_project_root()
        self.project_root = Path(project_root).resolve()

    def _find_project_root(self) -> Path:
        """
        自动查找项目根目录
        通过查找包含.claude目录的位置来确定项目根目录

        Returns:
            Path: 项目根目录路径
        """
        # 从当前文件所在位置开始向上查找
        current = Path(__file__).parent.parent

        # 如果已经在项目根目录（包含.claude），直接返回
        if (current / ".claude").exists():
            return current

        # 向上查找，最多查找5层
        for _ in range(5):
            if any(marker == ".claude" for marker in self.PROJECT_MARKERS):
                if (current / ".claude").exists():
                    return current
            parent = current.parent
            if parent == current:  # 已到根目录
                break
            current = parent

        # 如果找不到，返回当前工作目录
        return Path.cwd()

    @property
    def root(self) -> Path:
        """获取项目根目录"""
        return self.project_root

    def get_data_dir(self) -> Path:
        """获取数据目录"""
        return self.project_root / "data"

    def get_config_dir(self) -> Path:
        """获取配置目录"""
        return self.project_root / "config"

    def get_source_dir(self) -> Path:
        """获取源代码目录"""
        return self.project_root / "src"

    def get_docs_dir(self) -> Path:
        """获取文档目录"""
        return self.project_root / "docs"

    def get_logs_dir(self) -> Path:
        """获取日志目录"""
        return self.project_root / "logs"

    def get_config_file(self, filename: str = "config.yaml") -> Path:
        """
        获取配置文件路径

        Args:
            filename: 配置文件名

        Returns:
            Path: 配置文件的完整路径
        """
        return self.get_config_dir() / filename

    def resolve_path(self, relative_path: Union[str, Path]) -> Path:
        """
        解析相对路径为绝对路径

        Args:
            relative_path: 相对于项目根目录的路径

        Returns:
            Path: 解析后的绝对路径
        """
        return (self.project_root / relative_path).resolve()

    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """
        确保目录存在，如果不存在则创建

        Args:
            path: 目录路径

        Returns:
            Path: 目录路径
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_data_dir(self) -> Path:
        """确保数据目录存在"""
        return self.ensure_dir(self.get_data_dir())

    def ensure_logs_dir(self) -> Path:
        """确保日志目录存在"""
        return self.ensure_dir(self.get_logs_dir())

    def get_raw_data_path(self, timestamp: str) -> Path:
        """
        获取原始数据文件路径

        Args:
            timestamp: 时间戳字符串

        Returns:
            Path: 原始数据文件路径
        """
        return self.get_data_dir() / f"weibo_raw_{timestamp}.json"

    def get_report_path(self, timestamp: str) -> Path:
        """
        获取分析报告文件路径

        Args:
            timestamp: 时间戳字符串

        Returns:
            Path: 分析报告文件路径
        """
        return self.get_data_dir() / f"weibo_analysis_{timestamp}.html"

    def get_intermediate_path(self, timestamp: str) -> Path:
        """
        获取中间结果文件路径

        Args:
            timestamp: 时间戳字符串

        Returns:
            Path: 中间结果文件路径
        """
        return self.get_data_dir() / f"weibo_analysis_{timestamp}.json"

    def join(self, *parts) -> Path:
        """
        拼接路径片段

        Args:
            *parts: 路径片段

        Returns:
            Path: 拼接后的路径
        """
        return Path(*parts)

    def __str__(self) -> str:
        return f"PathManager(root={self.project_root})"

    def __repr__(self) -> str:
        return self.__str__()


# 全局路径管理器实例（单例）
_global_path_manager: Optional[PathManager] = None


def get_path_manager() -> PathManager:
    """
    获取全局路径管理器实例（单例模式）

    Returns:
        PathManager: 全局路径管理器实例
    """
    global _global_path_manager
    if _global_path_manager is None:
        _global_path_manager = PathManager()
    return _global_path_manager


def reset_path_manager():
    """重置全局路径管理器（主要用于测试）"""
    global _global_path_manager
    _global_path_manager = None
