"""
scorer.py - 智能评分推荐引擎

根据用户硬件配置，计算每个模型在每个量化级别的适配分数。
评分维度：硬件匹配度(40%)、性能表现(30%)、模型质量(20%)、功能丰富度(10%)。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .database import ModelDatabase, ModelInfo
from .detector import HardwareInfo


@dataclass
class Recommendation:
    """模型推荐结果"""
    model: ModelInfo                  # 模型信息
    quantization: str                 # 推荐的量化格式
    score: float                      # 总适配分数(0-100)
    hardware_score: float             # 硬件匹配度分数
    performance_score: float          # 性能表现分数
    quality_score: float              # 模型质量分数
    feature_score: float              # 功能丰富度分数
    fits_in_vram: bool                # 是否能放入VRAM
    fits_in_ram: bool                 # 是否能放入RAM
    estimated_speed: str              # 预估速度等级
    memory_usage: str                 # 内存使用描述


class Scorer:
    """
    智能评分推荐引擎。

    根据硬件配置和用户偏好，为每个模型计算综合适配分数，
    并输出排序后的推荐列表。
    """

    # 评分权重
    WEIGHT_HARDWARE = 0.40    # 硬件匹配度权重
    WEIGHT_PERFORMANCE = 0.30  # 性能表现权重
    WEIGHT_QUALITY = 0.20      # 模型质量权重
    WEIGHT_FEATURE = 0.10      # 功能丰富度权重

    # 系统内存余量(GB)
    SYSTEM_MEMORY_OVERHEAD = 2.0

    def __init__(
        self,
        hardware: HardwareInfo,
        database: ModelDatabase,
    ) -> None:
        """
        初始化评分引擎。

        Args:
            hardware: 硬件信息
            database: 模型数据库
        """
        self.hardware = hardware
        self.database = database

    def score_model(
        self,
        model: ModelInfo,
        quantization: str,
    ) -> Recommendation:
        """
        为单个模型在指定量化级别下计算适配分数。

        Args:
            model: 模型信息
            quantization: 量化格式

        Returns:
            Recommendation推荐结果
        """
        # 计算各维度分数
        hw_score = self._calc_hardware_score(model, quantization)
        perf_score = self._calc_performance_score(model, quantization)
        quality_score = self._calc_quality_score(model)
        feature_score = self._calc_feature_score(model)

        # 加权总分
        total_score = (
            hw_score * self.WEIGHT_HARDWARE
            + perf_score * self.WEIGHT_PERFORMANCE
            + quality_score * self.WEIGHT_QUALITY
            + feature_score * self.WEIGHT_FEATURE
        )

        # 判断是否能装入内存
        vram_needed = model.vram_gb.get(quantization, float("inf"))
        ram_needed = model.ram_gb.get(quantization, float("inf"))

        fits_vram = self.hardware.has_gpu() and vram_needed <= self.hardware.gpu.vram_gb
        fits_ram = ram_needed <= (self.hardware.ram_gb - self.SYSTEM_MEMORY_OVERHEAD)

        # 预估速度等级
        speed = self._estimate_speed(model, quantization, fits_vram)

        # 内存使用描述
        mem_desc = self._describe_memory_usage(model, quantization, fits_vram, fits_ram)

        return Recommendation(
            model=model,
            quantization=quantization,
            score=round(total_score, 1),
            hardware_score=round(hw_score, 1),
            performance_score=round(perf_score, 1),
            quality_score=round(quality_score, 1),
            feature_score=round(feature_score, 1),
            fits_in_vram=fits_vram,
            fits_in_ram=fits_ram,
            estimated_speed=speed,
            memory_usage=mem_desc,
        )

    def recommend(
        self,
        top_n: int = 10,
        min_params: Optional[float] = None,
        max_params: Optional[float] = None,
        tags: Optional[List[str]] = None,
        min_context: Optional[int] = None,
    ) -> List[Recommendation]:
        """
        生成推荐列表。

        对每个模型的所有量化级别进行评分，返回综合最优的推荐。

        Args:
            top_n: 返回前N个推荐
            min_params: 最小参数量(十亿)
            max_params: 最大参数量(十亿)
            tags: 标签过滤
            min_context: 最小上下文长度

        Returns:
            按分数排序的推荐列表
        """
        # 过滤模型
        models = self.database.filter_models(
            min_params=min_params,
            max_params=max_params,
            tags=tags,
            min_context=min_context,
        )

        # 为每个模型的每个量化级别评分
        all_recommendations: List[Recommendation] = []
        for model in models:
            for quant in model.quantizations:
                rec = self.score_model(model, quant)
                all_recommendations.append(rec)

        # 按分数排序
        all_recommendations.sort(key=lambda r: r.score, reverse=True)

        # 返回前N个
        return all_recommendations[:top_n]

    def find_best_for_model(self, model_name: str) -> Optional[Recommendation]:
        """
        找到指定模型的最佳量化级别。

        Args:
            model_name: 模型名称

        Returns:
            最佳推荐，未找到模型返回None
        """
        model = self.database.get_model(model_name)
        if model is None:
            return None

        best_rec: Optional[Recommendation] = None
        for quant in model.quantizations:
            rec = self.score_model(model, quant)
            if best_rec is None or rec.score > best_rec.score:
                best_rec = rec

        return best_rec

    def compare_models(
        self,
        name1: str,
        name2: str,
    ) -> Optional[Tuple[Recommendation, Recommendation]]:
        """
        对比两个模型。

        Args:
            name1: 第一个模型名称
            name2: 第二个模型名称

        Returns:
            两个模型的最佳推荐元组，任一未找到返回None
        """
        rec1 = self.find_best_for_model(name1)
        rec2 = self.find_best_for_model(name2)

        if rec1 is None or rec2 is None:
            return None

        return (rec1, rec2)

    def _calc_hardware_score(self, model: ModelInfo, quantization: str) -> float:
        """
        计算硬件匹配度分数(0-100)。

        评估模型在该量化级别下是否能装入VRAM/RAM，
        以及资源利用率。
        """
        vram_needed = model.vram_gb.get(quantization, float("inf"))
        ram_needed = model.ram_gb.get(quantization, float("inf"))

        available_ram = max(self.hardware.ram_gb - self.SYSTEM_MEMORY_OVERHEAD, 0)
        available_vram = self.hardware.gpu.vram_gb if self.hardware.has_gpu() else 0

        score = 0.0

        # RAM适配性 (最高50分)
        if ram_needed <= available_ram:
            # 能装入RAM，根据利用率给分
            utilization = ram_needed / available_ram if available_ram > 0 else 1.0
            if utilization <= 0.5:
                score += 50  # 资源利用合理
            elif utilization <= 0.75:
                score += 45  # 较好
            elif utilization <= 0.9:
                score += 40  # 可接受
            else:
                score += 30  # 接近极限
        elif ram_needed <= available_ram + 4:
            # 稍微超出，可能需要swap
            score += 15
        else:
            # 完全无法装入
            score += 0

        # VRAM适配性 (最高50分)
        if self.hardware.has_gpu():
            if vram_needed <= available_vram:
                # 能装入VRAM
                utilization = vram_needed / available_vram if available_vram > 0 else 1.0
                if utilization <= 0.5:
                    score += 50
                elif utilization <= 0.75:
                    score += 45
                elif utilization <= 0.9:
                    score += 40
                else:
                    score += 30
            elif vram_needed <= available_vram * 1.5:
                # 部分offload到RAM
                score += 20
            else:
                # 大部分需要offload
                score += 5
        else:
            # 无GPU，只能用CPU+RAM
            # 给予基础分，因为仍然可以运行
            score += 20

        return min(score, 100.0)

    def _calc_performance_score(self, model: ModelInfo, quantization: str) -> float:
        """
        计算性能表现分数(0-100)。

        基于参数量、量化级别和硬件能力评估推理速度。
        """
        score = 50.0  # 基础分

        # 参数量影响（越小越快）
        if model.params_b <= 3:
            score += 30
        elif model.params_b <= 8:
            score += 25
        elif model.params_b <= 15:
            score += 15
        elif model.params_b <= 35:
            score += 5
        elif model.params_b <= 70:
            score -= 5
        else:
            score -= 15

        # 量化级别影响（量化越高越快）
        quant_speed_bonus = {
            "q4_k_m": 15,
            "q5_k_m": 12,
            "q8_0": 5,
            "f16": 0,
        }
        score += quant_speed_bonus.get(quantization, 5)

        # GPU加速加成
        if self.hardware.has_gpu():
            vram_needed = model.vram_gb.get(quantization, float("inf"))
            if vram_needed <= self.hardware.gpu.vram_gb:
                score += 10  # 完全GPU推理

        # CPU核心数加成
        if self.hardware.cpu_cores >= 16:
            score += 5
        elif self.hardware.cpu_cores >= 8:
            score += 3

        return max(0, min(score, 100.0))

    def _calc_quality_score(self, model: ModelInfo) -> float:
        """
        计算模型质量分数(0-100)。

        基于基准测试分数和模型参数量。
        """
        # 主要使用基准分
        score = model.benchmark_score

        # 参数量修正（同基准分下，更大参数量略优）
        if model.params_b >= 30:
            score = min(score + 3, 100)
        elif model.params_b >= 10:
            score = min(score + 1, 100)

        return max(0, min(score, 100.0))

    def _calc_feature_score(self, model: ModelInfo) -> float:
        """
        计算功能丰富度分数(0-100)。

        基于模型标签数量、上下文长度等。
        """
        score = 30.0  # 基础分

        # 标签数量加成
        tag_count = len(model.tags)
        score += min(tag_count * 5, 25)

        # 上下文长度加成
        if model.context_length >= 131072:
            score += 20
        elif model.context_length >= 32768:
            score += 15
        elif model.context_length >= 8192:
            score += 10

        # 特殊能力加成
        special_tags = {"vision", "tool-use", "rag", "coding", "math"}
        special_count = len(set(model.tags) & special_tags)
        score += special_count * 5

        return max(0, min(score, 100.0))

    def _estimate_speed(
        self,
        model: ModelInfo,
        quantization: str,
        fits_vram: bool,
    ) -> str:
        """
        预估推理速度等级。

        Returns:
            速度等级描述字符串
        """
        if fits_vram:
            if model.params_b <= 3:
                return "极快 (>30 tok/s)"
            elif model.params_b <= 8:
                return "很快 (15-30 tok/s)"
            elif model.params_b <= 15:
                return "快 (8-15 tok/s)"
            elif model.params_b <= 35:
                return "中等 (4-8 tok/s)"
            elif model.params_b <= 70:
                return "较慢 (2-4 tok/s)"
            else:
                return "慢 (<2 tok/s)"
        else:
            # CPU推理或部分offload
            if model.params_b <= 3:
                return "中等 (5-10 tok/s)"
            elif model.params_b <= 8:
                return "较慢 (2-5 tok/s)"
            elif model.params_b <= 15:
                return "慢 (1-3 tok/s)"
            else:
                return "很慢 (<1 tok/s)"

    def _describe_memory_usage(
        self,
        model: ModelInfo,
        quantization: str,
        fits_vram: bool,
        fits_ram: bool,
    ) -> str:
        """
        生成内存使用描述。
        """
        vram_needed = model.vram_gb.get(quantization, 0)
        ram_needed = model.ram_gb.get(quantization, 0)

        if fits_vram:
            return f"VRAM {vram_needed:.1f}GB / RAM {ram_needed:.1f}GB (GPU推理)"
        elif fits_ram:
            return f"RAM {ram_needed:.1f}GB (CPU/GPU混合推理)"
        else:
            return f"RAM {ram_needed:.1f}GB (需要更多内存或更低量化)"
