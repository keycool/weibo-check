#!/usr/bin/env python3
"""
临时文件清理模块

自动清理项目根目录下的临时文件（tmpclaude-*），
保留最新的N个文件。

该模块独立于主程序逻辑，可单独运行或作为钩子调用。
"""
import sys
import io
from pathlib import Path
from typing import List, Tuple

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# 可配置：保留的最新文件数量
KEEP_COUNT = 3


def get_temp_files(project_root: Path) -> List[Tuple[Path, float]]:
    """获取项目根目录下的所有临时文件，按修改时间排序"""
    temp_files = []

    for item in project_root.iterdir():
        # 检查是否是以 tmpclaude- 开头的临时文件（文件，非目录）
        if item.is_file() and item.name.startswith("tmpclaude-"):
            temp_files.append((item, item.stat().st_mtime))

    # 按修改时间降序排序（最新的在前）
    temp_files.sort(key=lambda x: x[1], reverse=True)

    return temp_files


def cleanup_temp_files(keep_count: int = KEEP_COUNT, verbose: bool = True) -> int:
    """
    清理临时文件，保留最新的N个

    Args:
        keep_count: 保留的最新文件数量
        verbose: 是否打印详细信息

    Returns:
        删除的文件数量
    """
    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    if verbose:
        print(f"🔍 检查临时文件目录: {project_root}")

    # 获取所有临时文件
    temp_files = get_temp_files(project_root)

    if not temp_files:
        if verbose:
            print("✅ 没有找到临时文件")
        return 0

    total_count = len(temp_files)

    if verbose:
        print(f"📁 找到 {total_count} 个临时文件")

    # 如果文件数量不超过保留数量，不需要清理
    if total_count <= keep_count:
        if verbose:
            print(f"✅ 文件数量 ({total_count}) <= 保留数量 ({keep_count})，无需清理")
        return 0

    # 计算需要删除的文件
    files_to_keep = temp_files[:keep_count]
    files_to_delete = temp_files[keep_count:]

    if verbose:
        print(f"🗑️ 将删除 {len(files_to_delete)} 个旧文件，保留 {len(files_to_keep)} 个最新文件:")
        for file_path, _ in files_to_keep:
            print(f"   ✅ {file_path.name}")

    # 删除旧文件
    deleted_count = 0
    for file_path, _ in files_to_delete:
        try:
            file_path.unlink()
            if verbose:
                print(f"   🗑️ 已删除: {file_path.name}")
            deleted_count += 1
        except Exception as e:
            if verbose:
                print(f"   ❌ 删除失败: {file_path.name} - {e}")

    if verbose:
        print(f"✨ 清理完成！删除了 {deleted_count} 个临时文件")

    return deleted_count


def run_cleanup():
    """独立运行入口点"""
    # 可以通过命令行参数指定保留数量
    keep_count = KEEP_COUNT

    if len(sys.argv) > 1:
        try:
            keep_count = int(sys.argv[1])
        except ValueError:
            print(f"错误: 无效的数字参数 '{sys.argv[1]}'，使用默认值 {KEEP_COUNT}")

    deleted = cleanup_temp_files(keep_count=keep_count)
    return 0 if deleted >= 0 else 1


if __name__ == "__main__":
    sys.exit(run_cleanup())
