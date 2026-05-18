"""
utils.py - 工具函数

提供项目中通用的辅助函数。
"""

import sys
from typing import Optional


def check_python_version(min_version: tuple = (3, 8)) -> bool:
    """
    检查Python版本是否满足最低要求。

    Args:
        min_version: 最低版本号元组，如 (3, 8)

    Returns:
        是否满足版本要求
    """
    return sys.version_info >= min_version


def get_python_version() -> str:
    """
    获取当前Python版本字符串。

    Returns:
        版本字符串，如 "3.10.12"
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def format_bytes(size_bytes: int) -> str:
    """
    将字节数格式化为人类可读的字符串。

    Args:
        size_bytes: 字节数

    Returns:
        格式化后的字符串，如 "16.5 GB"
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串到指定长度。

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def parse_number(value: str) -> Optional[float]:
    """
    解析数字字符串。

    支持格式: "7", "7B", "7.5B", "7b" 等。

    Args:
        value: 数字字符串

    Returns:
        解析后的浮点数，失败返回None
    """
    value = value.strip().upper()
    # 移除常见的后缀
    for suffix in ("B", "K", "M", "G"):
        if value.endswith(suffix):
            value = value[:-1]
            break

    try:
        return float(value)
    except ValueError:
        return None


def resolve_model_name(name: str, candidates: list) -> Optional[str]:
    """
    模糊匹配模型名称。

    Args:
        name: 用户输入的模型名称
        candidates: 候选模型名称列表

    Returns:
        最佳匹配的模型名称，未找到返回None
    """
    name_lower = name.lower().strip()

    # 精确匹配
    for candidate in candidates:
        if candidate.lower() == name_lower:
            return candidate

    # 包含匹配
    matches = [c for c in candidates if name_lower in c.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # 返回最短的匹配（最精确）
        return min(matches, key=len)

    return None
