"""
formatter.py - 多格式输出模块

支持表格(table)、JSON、Markdown三种输出格式。
使用纯Python标准库实现，包括ANSI彩色终端输出。
"""

import json
from typing import Any, Dict, List, Optional

from .database import ModelInfo
from .detector import HardwareInfo
from .scorer import Recommendation


# ANSI颜色代码
class Colors:
    """ANSI终端颜色常量"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_RED = "\033[41m"


def colorize(text: str, color: str) -> str:
    """
    为文本添加ANSI颜色。

    Args:
        text: 原始文本
        color: ANSI颜色代码

    Returns:
        带颜色代码的文本
    """
    return f"{color}{text}{Colors.RESET}"


def bold(text: str) -> str:
    """加粗文本"""
    return colorize(text, Colors.BOLD)


def supports_color() -> bool:
    """
    检测终端是否支持颜色输出。

    Returns:
        是否支持ANSI颜色
    """
    import os
    import sys

    # 如果显式设置了NO_COLOR环境变量
    if os.environ.get("NO_COLOR"):
        return False

    # 检查是否为TTY
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        return True

    # 检查常见终端环境变量
    term = os.environ.get("TERM", "")
    if term in ("xterm", "xterm-256color", "screen", "screen-256color",
                 "tmux", "tmux-256color", "vt100", "ansi"):
        return True

    return False


def _safe_text(text: str) -> str:
    """
    移除文本中的ANSI颜色代码，用于表格宽度计算。

    Args:
        text: 可能包含ANSI代码的文本

    Returns:
        纯文本
    """
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


def _pad_cell(text: str, width: int, align: str = "left") -> str:
    """
    填充表格单元格。

    Args:
        text: 单元格文本
        width: 目标宽度
        align: 对齐方式 ("left", "right", "center")

    Returns:
        填充后的文本
    """
    visible_len = len(_safe_text(text))
    padding = max(0, width - visible_len)

    if align == "right":
        return " " * padding + text
    elif align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        return " " * left_pad + text + " " * right_pad
    else:
        return text + " " * padding


class Formatter:
    """
    多格式输出格式化器。

    支持表格、JSON、Markdown三种输出格式，
    可选彩色终端输出。
    """

    def __init__(self, use_color: bool = True) -> None:
        """
        初始化格式化器。

        Args:
            use_color: 是否使用彩色输出
        """
        self.use_color = use_color and supports_color()

    def _c(self, text: str, color: str) -> str:
        """条件性着色"""
        if self.use_color:
            return colorize(text, color)
        return text

    # ==================== 硬件信息格式化 ====================

    def format_hardware(self, hw: HardwareInfo, fmt: str = "table") -> str:
        """
        格式化硬件信息。

        Args:
            hw: 硬件信息
            fmt: 输出格式 ("table", "json", "markdown")

        Returns:
            格式化后的字符串
        """
        if fmt == "json":
            return self._format_hardware_json(hw)
        elif fmt == "markdown":
            return self._format_hardware_markdown(hw)
        else:
            return self._format_hardware_table(hw)

    def _format_hardware_table(self, hw: HardwareInfo) -> str:
        """表格格式输出硬件信息"""
        lines = []
        lines.append(self._c("=" * 60, Colors.CYAN))
        lines.append(self._c("  LLMFit - 硬件检测结果", Colors.BOLD + Colors.CYAN))
        lines.append(self._c("=" * 60, Colors.CYAN))
        lines.append("")

        # CPU信息
        lines.append(self._c(f"  CPU:  ", Colors.BOLD) + hw.cpu_model)
        lines.append(f"        核心: {hw.cpu_cores}  |  架构: {hw.cpu_arch}")
        lines.append("")

        # RAM信息
        ram_color = Colors.GREEN if hw.ram_gb >= 16 else (Colors.YELLOW if hw.ram_gb >= 8 else Colors.RED)
        lines.append(self._c(f"  RAM:  ", Colors.BOLD) + self._c(f"{hw.ram_gb:.1f} GB", ram_color))
        lines.append("")

        # GPU信息
        if hw.has_gpu():
            gpu = hw.gpu
            lines.append(self._c(f"  GPU:  ", Colors.BOLD) + self._c(gpu.name, Colors.GREEN))
            lines.append(f"        厂商: {gpu.vendor}  |  显存: {gpu.vram_gb:.1f} GB")
            if gpu.driver_version != "Unknown":
                lines.append(f"        驱动: {gpu.driver_version}")
            if gpu.compute_capability:
                lines.append(f"        CUDA计算能力: {gpu.compute_capability}")
            if gpu.metal_support:
                lines.append(f"        Metal支持: 是")
        else:
            lines.append(self._c("  GPU:  ", Colors.BOLD) + self._c("未检测到独立GPU", Colors.YELLOW))
            lines.append("        (将使用CPU推理，速度较慢)")
        lines.append("")

        # 系统信息
        lines.append(self._c(f"  系统: ", Colors.BOLD) + f"{hw.os_name} {hw.os_version} ({hw.os_arch})")
        lines.append(f"  Python: {hw.python_version}")
        lines.append(f"  磁盘可用: {hw.disk_free_gb:.1f} GB")
        lines.append("")

        # 适配建议
        if hw.has_gpu():
            if hw.gpu.vram_gb >= 24:
                tip = "可运行 70B+ 级别模型 (Q4量化)"
            elif hw.gpu.vram_gb >= 16:
                tip = "可运行 30B-70B 级别模型 (Q4量化)"
            elif hw.gpu.vram_gb >= 8:
                tip = "可运行 7B-14B 级别模型 (Q4/Q5量化)"
            elif hw.gpu.vram_gb >= 4:
                tip = "可运行 7B 级别模型 (Q4量化)"
            else:
                tip = "建议使用 3B-7B 小模型 (Q4量化)"
        else:
            if hw.ram_gb >= 32:
                tip = "可使用CPU运行 7B-14B 模型 (Q4量化)"
            elif hw.ram_gb >= 16:
                tip = "可使用CPU运行 7B 模型 (Q4量化)"
            else:
                tip = "建议使用 3B 以下小模型 (Q4量化)"

        lines.append(self._c(f"  建议: ", Colors.BOLD) + tip)
        lines.append("")
        lines.append(self._c("=" * 60, Colors.CYAN))

        return "\n".join(lines)

    def _format_hardware_json(self, hw: HardwareInfo) -> str:
        """JSON格式输出硬件信息"""
        data = {
            "cpu": {
                "model": hw.cpu_model,
                "cores": hw.cpu_cores,
                "architecture": hw.cpu_arch,
            },
            "ram_gb": round(hw.ram_gb, 2),
            "gpu": None,
            "os": {
                "name": hw.os_name,
                "version": hw.os_version,
                "architecture": hw.os_arch,
            },
            "disk_free_gb": round(hw.disk_free_gb, 2),
            "python_version": hw.python_version,
        }

        if hw.has_gpu():
            data["gpu"] = {
                "vendor": hw.gpu.vendor,
                "name": hw.gpu.name,
                "vram_gb": round(hw.gpu.vram_gb, 2),
                "driver_version": hw.gpu.driver_version,
                "compute_capability": hw.gpu.compute_capability,
                "metal_support": hw.gpu.metal_support,
            }

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_hardware_markdown(self, hw: HardwareInfo) -> str:
        """Markdown格式输出硬件信息"""
        lines = [
            "# 硬件检测结果",
            "",
            "| 项目 | 详情 |",
            "|------|------|",
            f"| CPU | {hw.cpu_model} |",
            f"| CPU核心数 | {hw.cpu_cores} |",
            f"| CPU架构 | {hw.cpu_arch} |",
            f"| RAM | {hw.ram_gb:.1f} GB |",
        ]

        if hw.has_gpu():
            gpu = hw.gpu
            lines.extend([
                f"| GPU | {gpu.name} |",
                f"| GPU厂商 | {gpu.vendor} |",
                f"| 显存 | {gpu.vram_gb:.1f} GB |",
                f"| 驱动版本 | {gpu.driver_version} |",
            ])
        else:
            lines.append("| GPU | 未检测到 |")

        lines.extend([
            f"| 操作系统 | {hw.os_name} {hw.os_version} |",
            f"| 系统架构 | {hw.os_arch} |",
            f"| Python版本 | {hw.python_version} |",
            f"| 磁盘可用空间 | {hw.disk_free_gb:.1f} GB |",
        ])

        return "\n".join(lines)

    # ==================== 模型列表格式化 ====================

    def format_model_list(self, models: List[ModelInfo], fmt: str = "table") -> str:
        """
        格式化模型列表。

        Args:
            models: 模型列表
            fmt: 输出格式

        Returns:
            格式化后的字符串
        """
        if fmt == "json":
            return self._format_model_list_json(models)
        elif fmt == "markdown":
            return self._format_model_list_markdown(models)
        else:
            return self._format_model_list_table(models)

    def _format_model_list_table(self, models: List[ModelInfo]) -> str:
        """表格格式输出模型列表"""
        if not models:
            return self._c("未找到匹配的模型", Colors.YELLOW)

        # 表头
        headers = ["#", "模型名称", "系列", "参数量", "上下文", "量化", "基准分", "标签"]
        col_widths = [3, 28, 12, 10, 10, 22, 8, 30]

        lines = []
        lines.append(self._build_table_row(headers, col_widths, is_header=True))
        lines.append(self._build_table_separator(col_widths))

        for i, model in enumerate(models, 1):
            quant_str = ", ".join(model.quantizations)
            tags_str = ", ".join(model.tags[:4])
            if len(model.tags) > 4:
                tags_str += "..."

            row = [
                str(i),
                model.name,
                model.family,
                f"{model.params_b:.0f}B" if model.params_b == int(model.params_b) else f"{model.params_b}B",
                f"{model.context_length // 1024}K" if model.context_length >= 1024 else str(model.context_length),
                quant_str,
                str(model.benchmark_score),
                tags_str,
            ]
            lines.append(self._build_table_row(row, col_widths))

        lines.append("")
        lines.append(f"共 {len(models)} 个模型")

        return "\n".join(lines)

    def _format_model_list_json(self, models: List[ModelInfo]) -> str:
        """JSON格式输出模型列表"""
        data = []
        for m in models:
            data.append({
                "name": m.name,
                "family": m.family,
                "params_b": m.params_b,
                "quantizations": m.quantizations,
                "context_length": m.context_length,
                "vram_gb": m.vram_gb,
                "ram_gb": m.ram_gb,
                "license": m.license,
                "tags": m.tags,
                "release_date": m.release_date,
                "benchmark_score": m.benchmark_score,
                "description": m.description,
            })
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_model_list_markdown(self, models: List[ModelInfo]) -> str:
        """Markdown格式输出模型列表"""
        if not models:
            return "未找到匹配的模型"

        lines = [
            "# 支持的模型列表",
            "",
            f"共 {len(models)} 个模型",
            "",
            "| # | 模型名称 | 系列 | 参数量 | 上下文 | 量化 | 基准分 | 标签 |",
            "|---|----------|------|--------|--------|------|--------|------|",
        ]

        for i, m in enumerate(models, 1):
            quant_str = ", ".join(m.quantizations)
            tags_str = ", ".join(m.tags[:4])
            ctx = f"{m.context_length // 1024}K" if m.context_length >= 1024 else str(m.context_length)
            params = f"{m.params_b:.0f}B" if m.params_b == int(m.params_b) else f"{m.params_b}B"
            lines.append(f"| {i} | {m.name} | {m.family} | {params} | {ctx} | {quant_str} | {m.benchmark_score} | {tags_str} |")

        return "\n".join(lines)

    # ==================== 推荐结果格式化 ====================

    def format_recommendations(
        self,
        recommendations: List[Recommendation],
        fmt: str = "table",
    ) -> str:
        """
        格式化推荐结果。

        Args:
            recommendations: 推荐列表
            fmt: 输出格式

        Returns:
            格式化后的字符串
        """
        if fmt == "json":
            return self._format_recommendations_json(recommendations)
        elif fmt == "markdown":
            return self._format_recommendations_markdown(recommendations)
        else:
            return self._format_recommendations_table(recommendations)

    def _format_recommendations_table(self, recs: List[Recommendation]) -> str:
        """表格格式输出推荐结果"""
        if not recs:
            return self._c("未找到适合的模型推荐", Colors.YELLOW)

        lines = []
        lines.append(self._c("=" * 90, Colors.CYAN))
        lines.append(self._c("  LLMFit - 模型推荐结果", Colors.BOLD + Colors.CYAN))
        lines.append(self._c("=" * 90, Colors.CYAN))
        lines.append("")

        # 表头
        headers = ["#", "模型", "量化", "总分", "硬件", "性能", "质量", "功能", "内存使用", "预估速度"]
        col_widths = [3, 26, 8, 6, 6, 6, 6, 6, 28, 20]

        lines.append(self._build_table_row(headers, col_widths, is_header=True))
        lines.append(self._build_table_separator(col_widths))

        for i, rec in enumerate(recs, 1):
            # 分数着色
            score_color = (
                Colors.GREEN if rec.score >= 70
                else (Colors.YELLOW if rec.score >= 50 else Colors.RED)
            )
            score_text = self._c(str(rec.score), score_color)

            # 适配状态图标
            if rec.fits_in_vram:
                fit_icon = self._c("GPU", Colors.GREEN)
            elif rec.fits_in_ram:
                fit_icon = self._c("CPU", Colors.YELLOW)
            else:
                fit_icon = self._c("X", Colors.RED)

            row = [
                str(i),
                rec.model.name,
                rec.quantization,
                score_text,
                str(rec.hardware_score),
                str(rec.performance_score),
                str(rec.quality_score),
                str(rec.feature_score),
                rec.memory_usage,
                rec.estimated_speed,
            ]
            lines.append(self._build_table_row(row, col_widths))

        lines.append("")
        lines.append(f"共推荐 {len(recs)} 个模型配置")

        # 最佳推荐提示
        if recs:
            best = recs[0]
            lines.append("")
            lines.append(self._c(f"  最佳推荐: {best.model.name} ({best.quantization})", Colors.BOLD + Colors.GREEN))
            lines.append(f"  总分: {best.score} | {best.memory_usage} | {best.estimated_speed}")

        lines.append("")
        lines.append(self._c("=" * 90, Colors.CYAN))

        return "\n".join(lines)

    def _format_recommendations_json(self, recs: List[Recommendation]) -> str:
        """JSON格式输出推荐结果"""
        data = []
        for rec in recs:
            data.append({
                "rank": recs.index(rec) + 1,
                "model": rec.model.name,
                "family": rec.model.family,
                "params_b": rec.model.params_b,
                "quantization": rec.quantization,
                "total_score": rec.score,
                "scores": {
                    "hardware": rec.hardware_score,
                    "performance": rec.performance_score,
                    "quality": rec.quality_score,
                    "feature": rec.feature_score,
                },
                "fits_in_vram": rec.fits_in_vram,
                "fits_in_ram": rec.fits_in_ram,
                "memory_usage": rec.memory_usage,
                "estimated_speed": rec.estimated_speed,
            })
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_recommendations_markdown(self, recs: List[Recommendation]) -> str:
        """Markdown格式输出推荐结果"""
        if not recs:
            return "未找到适合的模型推荐"

        lines = [
            "# 模型推荐结果",
            "",
            f"共推荐 {len(recs)} 个模型配置",
            "",
            "| # | 模型 | 量化 | 总分 | 硬件 | 性能 | 质量 | 功能 | 内存使用 | 预估速度 |",
            "|---|------|------|------|------|------|------|------|----------|----------|",
        ]

        for i, rec in enumerate(recs, 1):
            fit = "GPU" if rec.fits_in_vram else ("CPU" if rec.fits_in_ram else "X")
            lines.append(
                f"| {i} | {rec.model.name} | {rec.quantization} | "
                f"**{rec.score}** | {rec.hardware_score} | {rec.performance_score} | "
                f"{rec.quality_score} | {rec.feature_score} | {rec.memory_usage} | "
                f"{rec.estimated_speed} |"
            )

        lines.append("")
        best = recs[0]
        lines.append(f"**最佳推荐**: {best.model.name} ({best.quantization}) - 总分 {best.score}")

        return "\n".join(lines)

    # ==================== 模型详情格式化 ====================

    def format_model_detail(self, model: ModelInfo, fmt: str = "table") -> str:
        """
        格式化模型详情。

        Args:
            model: 模型信息
            fmt: 输出格式

        Returns:
            格式化后的字符串
        """
        if fmt == "json":
            return self._format_model_list_json([model])
        elif fmt == "markdown":
            return self._format_model_detail_markdown(model)
        else:
            return self._format_model_detail_table(model)

    def _format_model_detail_table(self, model: ModelInfo) -> str:
        """表格格式输出模型详情"""
        lines = []
        lines.append(self._c("=" * 60, Colors.CYAN))
        lines.append(self._c(f"  {model.name}", Colors.BOLD + Colors.CYAN))
        lines.append(self._c("=" * 60, Colors.CYAN))
        lines.append("")

        info_items = [
            ("系列", model.family),
            ("参数量", f"{model.params_b}B"),
            ("上下文长度", f"{model.context_length:,}"),
            ("开源协议", model.license),
            ("发布日期", model.release_date),
            ("基准分数", str(model.benchmark_score)),
            ("描述", model.description),
        ]

        for label, value in info_items:
            lines.append(f"  {self._c(label + ':', Colors.BOLD):<16} {value}")

        lines.append("")
        lines.append(self._c("  支持的量化格式:", Colors.BOLD))

        # 量化信息表格
        headers = ["量化格式", "VRAM需求", "RAM需求"]
        col_widths = [15, 15, 15]
        lines.append(self._build_table_row(headers, col_widths, is_header=True, indent=4))
        lines.append(self._build_table_separator(col_widths, indent=4))

        for quant in model.quantizations:
            vram = model.vram_gb.get(quant, 0)
            ram = model.ram_gb.get(quant, 0)
            row = [quant, f"{vram:.1f} GB", f"{ram:.1f} GB"]
            lines.append(self._build_table_row(row, col_widths, indent=4))

        lines.append("")
        lines.append(self._c("  能力标签:", Colors.BOLD))
        lines.append(f"  {', '.join(model.tags)}")

        return "\n".join(lines)

    def _format_model_detail_markdown(self, model: ModelInfo) -> str:
        """Markdown格式输出模型详情"""
        lines = [
            f"# {model.name}",
            "",
            f"**描述**: {model.description}",
            "",
            "| 属性 | 值 |",
            "|------|-----|",
            f"| 系列 | {model.family} |",
            f"| 参数量 | {model.params_b}B |",
            f"| 上下文长度 | {model.context_length:,} |",
            f"| 开源协议 | {model.license} |",
            f"| 发布日期 | {model.release_date} |",
            f"| 基准分数 | {model.benchmark_score} |",
            "",
            "## 量化格式",
            "",
            "| 量化格式 | VRAM需求 | RAM需求 |",
            "|----------|----------|---------|",
        ]

        for quant in model.quantizations:
            vram = model.vram_gb.get(quant, 0)
            ram = model.ram_gb.get(quant, 0)
            lines.append(f"| {quant} | {vram:.1f} GB | {ram:.1f} GB |")

        lines.extend([
            "",
            f"**标签**: {', '.join(model.tags)}",
        ])

        return "\n".join(lines)

    # ==================== 模型对比格式化 ====================

    def format_comparison(
        self,
        rec1: Recommendation,
        rec2: Recommendation,
        fmt: str = "table",
    ) -> str:
        """
        格式化模型对比结果。

        Args:
            rec1: 第一个模型推荐
            rec2: 第二个模型推荐
            fmt: 输出格式

        Returns:
            格式化后的字符串
        """
        if fmt == "json":
            return self._format_comparison_json(rec1, rec2)
        elif fmt == "markdown":
            return self._format_comparison_markdown(rec1, rec2)
        else:
            return self._format_comparison_table(rec1, rec2)

    def _format_comparison_table(self, rec1: Recommendation, rec2: Recommendation) -> str:
        """表格格式输出模型对比"""
        lines = []
        lines.append(self._c("=" * 70, Colors.CYAN))
        lines.append(self._c("  模型对比", Colors.BOLD + Colors.CYAN))
        lines.append(self._c("=" * 70, Colors.CYAN))
        lines.append("")

        # 对比项
        m1, m2 = rec1.model, rec2.model
        comparisons = [
            ("模型名称", m1.name, m2.name),
            ("系列", m1.family, m2.family),
            ("参数量", f"{m1.params_b}B", f"{m2.params_b}B"),
            ("推荐量化", rec1.quantization, rec2.quantization),
            ("上下文长度", f"{m1.context_length:,}", f"{m2.context_length:,}"),
            ("基准分数", str(m1.benchmark_score), str(m2.benchmark_score)),
            ("", "", ""),
            ("适配总分", str(rec1.score), str(rec2.score)),
            ("硬件匹配度", str(rec1.hardware_score), str(rec2.hardware_score)),
            ("性能表现", str(rec1.performance_score), str(rec2.performance_score)),
            ("模型质量", str(rec1.quality_score), str(rec2.quality_score)),
            ("功能丰富度", str(rec1.feature_score), str(rec2.feature_score)),
            ("", "", ""),
            ("内存使用", rec1.memory_usage, rec2.memory_usage),
            ("预估速度", rec1.estimated_speed, rec2.estimated_speed),
            ("VRAM适配", "是" if rec1.fits_in_vram else "否", "是" if rec2.fits_in_vram else "否"),
            ("RAM适配", "是" if rec1.fits_in_ram else "否", "是" if rec2.fits_in_ram else "否"),
        ]

        headers = ["对比项", rec1.model.name, rec2.model.name]
        col_widths = [16, 26, 26]

        lines.append(self._build_table_row(headers, col_widths, is_header=True))
        lines.append(self._build_table_separator(col_widths))

        for label, val1, val2 in comparisons:
            if not label:
                lines.append(self._build_table_separator(col_widths))
                continue
            row = [label, val1, val2]
            lines.append(self._build_table_row(row, col_widths))

        # 胜出提示
        lines.append("")
        if rec1.score > rec2.score:
            winner = rec1
        elif rec2.score > rec1.score:
            winner = rec2
        else:
            winner = None

        if winner:
            lines.append(
                self._c(f"  推荐: {winner.model.name} ({winner.quantization}) - 总分 {winner.score}",
                        Colors.BOLD + Colors.GREEN)
            )
        else:
            lines.append(self._c("  两个模型评分相同", Colors.YELLOW))

        return "\n".join(lines)

    def _format_comparison_json(self, rec1: Recommendation, rec2: Recommendation) -> str:
        """JSON格式输出模型对比"""
        data = {
            "model_1": self._rec_to_dict(rec1),
            "model_2": self._rec_to_dict(rec2),
            "winner": rec1.model.name if rec1.score > rec2.score else (
                rec2.model.name if rec2.score > rec1.score else "tie"
            ),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_comparison_markdown(self, rec1: Recommendation, rec2: Recommendation) -> str:
        """Markdown格式输出模型对比"""
        m1, m2 = rec1.model, rec2.model
        lines = [
            "# 模型对比",
            "",
            f"| 对比项 | {m1.name} | {m2.name} |",
            "|--------|----------|----------|",
            f"| 参数量 | {m1.params_b}B | {m2.params_b}B |",
            f"| 推荐量化 | {rec1.quantization} | {rec2.quantization} |",
            f"| 上下文长度 | {m1.context_length:,} | {m2.context_length:,} |",
            f"| 基准分数 | {m1.benchmark_score} | {m2.benchmark_score} |",
            f"| **适配总分** | **{rec1.score}** | **{rec2.score}** |",
            f"| 硬件匹配度 | {rec1.hardware_score} | {rec2.hardware_score} |",
            f"| 性能表现 | {rec1.performance_score} | {rec2.performance_score} |",
            f"| 模型质量 | {rec1.quality_score} | {rec2.quality_score} |",
            f"| 功能丰富度 | {rec1.feature_score} | {rec2.feature_score} |",
            f"| 内存使用 | {rec1.memory_usage} | {rec2.memory_usage} |",
            f"| 预估速度 | {rec1.estimated_speed} | {rec2.estimated_speed} |",
        ]

        if rec1.score > rec2.score:
            lines.append(f"\n**推荐**: {m1.name}")
        elif rec2.score > rec1.score:
            lines.append(f"\n**推荐**: {m2.name}")
        else:
            lines.append("\n**结果**: 平局")

        return "\n".join(lines)

    # ==================== 辅助方法 ====================

    def _rec_to_dict(self, rec: Recommendation) -> Dict[str, Any]:
        """将Recommendation转换为字典"""
        return {
            "model": rec.model.name,
            "family": rec.model.family,
            "params_b": rec.model.params_b,
            "quantization": rec.quantization,
            "total_score": rec.score,
            "scores": {
                "hardware": rec.hardware_score,
                "performance": rec.performance_score,
                "quality": rec.quality_score,
                "feature": rec.feature_score,
            },
            "fits_in_vram": rec.fits_in_vram,
            "fits_in_ram": rec.fits_in_ram,
            "memory_usage": rec.memory_usage,
            "estimated_speed": rec.estimated_speed,
        }

    def _build_table_row(
        self,
        cells: List[str],
        widths: List[int],
        is_header: bool = False,
        indent: int = 0,
    ) -> str:
        """
        构建表格行。

        Args:
            cells: 单元格内容列表
            widths: 各列宽度
            is_header: 是否为表头
            indent: 缩进空格数

        Returns:
            表格行字符串
        """
        prefix = " " * indent
        parts = []
        for cell, width in zip(cells, widths):
            text = _pad_cell(str(cell), width)
            if is_header and self.use_color:
                text = colorize(text, Colors.BOLD)
            parts.append(text)
        return f"{prefix}| {' | '.join(parts)} |"

    def _build_table_separator(
        self,
        widths: List[int],
        indent: int = 0,
    ) -> str:
        """
        构建表格分隔线。

        Args:
            widths: 各列宽度
            indent: 缩进空格数

        Returns:
            分隔线字符串
        """
        prefix = " " * indent
        parts = ["-" * (w + 2) for w in widths]
        return f"{prefix}|{'|'.join(parts)}|"
