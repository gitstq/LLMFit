"""
database.py - LLM模型数据库

内置包含20+主流开源LLM的数据集，完全离线可用。
每个模型包含参数量、量化格式、VRAM/RAM需求、基准分等信息。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ModelInfo:
    """LLM模型信息数据类"""
    name: str                           # 模型名称
    family: str                         # 模型系列
    params_b: float                     # 参数量（十亿）
    quantizations: List[str]            # 支持的量化格式
    context_length: int                 # 上下文长度
    vram_gb: Dict[str, float]           # 各量化级别的VRAM需求(GB)
    ram_gb: Dict[str, float]            # 各量化级别的RAM需求(GB)
    license: str                        # 开源协议
    tags: List[str]                     # 能力标签
    release_date: str                   # 发布日期
    benchmark_score: float              # 综合基准分(0-100)
    description: str = ""               # 模型描述


# 内置模型数据库
BUILTIN_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="Llama 3.1 8B",
        family="Llama",
        params_b=8.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 5.0, "q5_k_m": 5.8, "q8_0": 8.5, "f16": 16.0},
        ram_gb={"q4_k_m": 6.5, "q5_k_m": 7.3, "q8_0": 10.0, "f16": 18.0},
        license="Llama 3.1 Community",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-07",
        benchmark_score=78,
        description="Meta最新一代开源模型，支持128K上下文，综合能力出色",
    ),
    ModelInfo(
        name="Llama 3.1 70B",
        family="Llama",
        params_b=70.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 40.0, "q5_k_m": 46.0, "q8_0": 72.0, "f16": 140.0},
        ram_gb={"q4_k_m": 42.0, "q5_k_m": 48.0, "q8_0": 74.0, "f16": 142.0},
        license="Llama 3.1 Community",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-07",
        benchmark_score=90,
        description="Meta旗舰开源模型，接近GPT-4水平",
    ),
    ModelInfo(
        name="Qwen 2.5 7B",
        family="Qwen",
        params_b=7.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 4.5, "q5_k_m": 5.2, "q8_0": 7.5, "f16": 14.0},
        ram_gb={"q4_k_m": 6.0, "q5_k_m": 6.7, "q8_0": 9.0, "f16": 16.0},
        license="Apache 2.0",
        tags=["coding", "reasoning", "multilingual", "chinese", "math"],
        release_date="2024-09",
        benchmark_score=80,
        description="通义千问最新一代7B模型，中文能力突出",
    ),
    ModelInfo(
        name="Qwen 2.5 72B",
        family="Qwen",
        params_b=72.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 42.0, "q5_k_m": 48.0, "q8_0": 74.0, "f16": 144.0},
        ram_gb={"q4_k_m": 44.0, "q5_k_m": 50.0, "q8_0": 76.0, "f16": 146.0},
        license="Apache 2.0",
        tags=["coding", "reasoning", "multilingual", "chinese", "math"],
        release_date="2024-09",
        benchmark_score=92,
        description="通义千问旗舰模型，综合性能顶级",
    ),
    ModelInfo(
        name="Mistral 7B v0.3",
        family="Mistral",
        params_b=7.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=32768,
        vram_gb={"q4_k_m": 4.4, "q5_k_m": 5.1, "q8_0": 7.4, "f16": 14.0},
        ram_gb={"q4_k_m": 5.9, "q5_k_m": 6.6, "q8_0": 8.9, "f16": 16.0},
        license="Apache 2.0",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-05",
        benchmark_score=72,
        description="Mistral AI经典7B模型，推理效率高",
    ),
    ModelInfo(
        name="Mixtral 8x7B",
        family="Mistral",
        params_b=46.7,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=32768,
        vram_gb={"q4_k_m": 26.0, "q5_k_m": 30.0, "q8_0": 48.0, "f16": 93.0},
        ram_gb={"q4_k_m": 28.0, "q5_k_m": 32.0, "q8_0": 50.0, "f16": 95.0},
        license="Apache 2.0",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-01",
        benchmark_score=85,
        description="Mistral MoE架构模型，稀疏激活高效推理",
    ),
    ModelInfo(
        name="Phi-3 Mini 3.8B",
        family="Phi",
        params_b=3.8,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 2.5, "q5_k_m": 2.9, "q8_0": 4.2, "f16": 7.6},
        ram_gb={"q4_k_m": 4.0, "q5_k_m": 4.4, "q8_0": 5.7, "f16": 9.1},
        license="MIT",
        tags=["reasoning", "coding", "english"],
        release_date="2024-04",
        benchmark_score=68,
        description="微软小参数高质量模型，适合边缘部署",
    ),
    ModelInfo(
        name="Phi-3 Medium 14B",
        family="Phi",
        params_b=14.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 8.0, "q5_k_m": 9.3, "q8_0": 14.0, "f16": 28.0},
        ram_gb={"q4_k_m": 9.5, "q5_k_m": 10.8, "q8_0": 15.5, "f16": 30.0},
        license="MIT",
        tags=["reasoning", "coding", "english"],
        release_date="2024-04",
        benchmark_score=76,
        description="微软中等规模模型，性能与效率平衡",
    ),
    ModelInfo(
        name="Gemma 2 9B",
        family="Gemma",
        params_b=9.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=8192,
        vram_gb={"q4_k_m": 5.5, "q5_k_m": 6.3, "q8_0": 9.5, "f16": 18.0},
        ram_gb={"q4_k_m": 7.0, "q5_k_m": 7.8, "q8_0": 11.0, "f16": 20.0},
        license="Gemma",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-06",
        benchmark_score=77,
        description="Google Gemma第二代模型，知识丰富",
    ),
    ModelInfo(
        name="Gemma 2 27B",
        family="Gemma",
        params_b=27.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=8192,
        vram_gb={"q4_k_m": 16.0, "q5_k_m": 18.5, "q8_0": 28.0, "f16": 54.0},
        ram_gb={"q4_k_m": 18.0, "q5_k_m": 20.5, "q8_0": 30.0, "f16": 56.0},
        license="Gemma",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-06",
        benchmark_score=86,
        description="Google Gemma第二代大模型，性能强劲",
    ),
    ModelInfo(
        name="DeepSeek V3 (671B MoE)",
        family="DeepSeek",
        params_b=671.0,
        quantizations=["q4_k_m"],
        context_length=131072,
        vram_gb={"q4_k_m": 380.0},
        ram_gb={"q4_k_m": 400.0},
        license="DeepSeek",
        tags=["reasoning", "coding", "math", "chinese", "multilingual"],
        release_date="2024-12",
        benchmark_score=95,
        description="DeepSeek旗舰MoE模型，综合能力顶尖",
    ),
    ModelInfo(
        name="DeepSeek-Coder-V2 236B",
        family="DeepSeek",
        params_b=236.0,
        quantizations=["q4_k_m", "q5_k_m"],
        context_length=131072,
        vram_gb={"q4_k_m": 130.0, "q5_k_m": 150.0},
        ram_gb={"q4_k_m": 135.0, "q5_k_m": 155.0},
        license="DeepSeek",
        tags=["coding", "reasoning", "math", "chinese"],
        release_date="2024-06",
        benchmark_score=88,
        description="DeepSeek代码专用MoE模型，编程能力极强",
    ),
    ModelInfo(
        name="Yi 1.5 9B",
        family="Yi",
        params_b=9.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=4096,
        vram_gb={"q4_k_m": 5.5, "q5_k_m": 6.3, "q8_0": 9.5, "f16": 18.0},
        ram_gb={"q4_k_m": 7.0, "q5_k_m": 7.8, "q8_0": 11.0, "f16": 20.0},
        license="Apache 2.0",
        tags=["reasoning", "multilingual", "chinese", "english"],
        release_date="2024-03",
        benchmark_score=73,
        description="零一万物Yi系列模型，中英双语优秀",
    ),
    ModelInfo(
        name="Yi 1.5 34B",
        family="Yi",
        params_b=34.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=4096,
        vram_gb={"q4_k_m": 20.0, "q5_k_m": 23.0, "q8_0": 35.0, "f16": 68.0},
        ram_gb={"q4_k_m": 22.0, "q5_k_m": 25.0, "q8_0": 37.0, "f16": 70.0},
        license="Apache 2.0",
        tags=["reasoning", "multilingual", "chinese", "english"],
        release_date="2024-03",
        benchmark_score=84,
        description="零一万物34B模型，综合能力优秀",
    ),
    ModelInfo(
        name="Command R 35B",
        family="Command",
        params_b=35.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 20.0, "q5_k_m": 23.0, "q8_0": 36.0, "f16": 70.0},
        ram_gb={"q4_k_m": 22.0, "q5_k_m": 25.0, "q8_0": 38.0, "f16": 72.0},
        license="CC-BY-NC-4.0",
        tags=["reasoning", "multilingual", "rag", "tool-use"],
        release_date="2024-04",
        benchmark_score=82,
        description="Cohere RAG专用模型，擅长检索增强生成",
    ),
    ModelInfo(
        name="Command R+ 104B",
        family="Command",
        params_b=104.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0"],
        context_length=131072,
        vram_gb={"q4_k_m": 60.0, "q5_k_m": 69.0, "q8_0": 108.0},
        ram_gb={"q4_k_m": 62.0, "q5_k_m": 71.0, "q8_0": 110.0},
        license="CC-BY-NC-4.0",
        tags=["reasoning", "multilingual", "rag", "tool-use"],
        release_date="2024-04",
        benchmark_score=89,
        description="Cohere旗舰RAG模型，企业级应用",
    ),
    ModelInfo(
        name="Qwen 2.5 14B",
        family="Qwen",
        params_b=14.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 8.5, "q5_k_m": 9.8, "q8_0": 14.5, "f16": 28.0},
        ram_gb={"q4_k_m": 10.0, "q5_k_m": 11.3, "q8_0": 16.0, "f16": 30.0},
        license="Apache 2.0",
        tags=["coding", "reasoning", "multilingual", "chinese", "math"],
        release_date="2024-09",
        benchmark_score=82,
        description="通义千问14B，性能与资源消耗的理想平衡",
    ),
    ModelInfo(
        name="Qwen 2.5 32B",
        family="Qwen",
        params_b=32.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 19.0, "q5_k_m": 22.0, "q8_0": 33.0, "f16": 64.0},
        ram_gb={"q4_k_m": 21.0, "q5_k_m": 24.0, "q8_0": 35.0, "f16": 66.0},
        license="Apache 2.0",
        tags=["coding", "reasoning", "multilingual", "chinese", "math"],
        release_date="2024-09",
        benchmark_score=87,
        description="通义千问32B，中端硬件的最佳选择之一",
    ),
    ModelInfo(
        name="Qwen 2.5 3B",
        family="Qwen",
        params_b=3.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=32768,
        vram_gb={"q4_k_m": 2.0, "q5_k_m": 2.3, "q8_0": 3.3, "f16": 6.0},
        ram_gb={"q4_k_m": 3.5, "q5_k_m": 3.8, "q8_0": 4.8, "f16": 7.5},
        license="Apache 2.0",
        tags=["coding", "reasoning", "chinese", "edge"],
        release_date="2024-09",
        benchmark_score=58,
        description="通义千问超小模型，适合嵌入式和边缘设备",
    ),
    ModelInfo(
        name="Mistral Nemo 12B",
        family="Mistral",
        params_b=12.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 7.2, "q5_k_m": 8.3, "q8_0": 12.5, "f16": 24.0},
        ram_gb={"q4_k_m": 8.7, "q5_k_m": 9.8, "q8_0": 14.0, "f16": 26.0},
        license="Apache 2.0",
        tags=["reasoning", "coding", "multilingual", "english"],
        release_date="2024-07",
        benchmark_score=79,
        description="Mistral与NVIDIA合作开发，128K上下文",
    ),
    ModelInfo(
        name="Phi-3 Small 7B",
        family="Phi",
        params_b=7.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=8192,
        vram_gb={"q4_k_m": 4.2, "q5_k_m": 4.8, "q8_0": 7.2, "f16": 14.0},
        ram_gb={"q4_k_m": 5.7, "q5_k_m": 6.3, "q8_0": 8.7, "f16": 16.0},
        license="MIT",
        tags=["reasoning", "coding", "english"],
        release_date="2024-04",
        benchmark_score=70,
        description="微软Phi-3系列7B版本，紧凑高效",
    ),
    ModelInfo(
        name="InternLM2.5 20B",
        family="InternLM",
        params_b=20.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 12.0, "q5_k_m": 13.8, "q8_0": 21.0, "f16": 40.0},
        ram_gb={"q4_k_m": 13.5, "q5_k_m": 15.3, "q8_0": 22.5, "f16": 42.0},
        license="Apache 2.0",
        tags=["reasoning", "coding", "chinese", "math", "tool-use"],
        release_date="2024-08",
        benchmark_score=83,
        description="上海AI Lab书生浦语模型，工具调用能力突出",
    ),
    ModelInfo(
        name="Gemma 2 2B",
        family="Gemma",
        params_b=2.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=8192,
        vram_gb={"q4_k_m": 1.5, "q5_k_m": 1.7, "q8_0": 2.3, "f16": 4.0},
        ram_gb={"q4_k_m": 3.0, "q5_k_m": 3.2, "q8_0": 3.8, "f16": 5.5},
        license="Gemma",
        tags=["reasoning", "coding", "english", "edge"],
        release_date="2024-06",
        benchmark_score=52,
        description="Google超小模型，适合轻量级应用",
    ),
    ModelInfo(
        name="MiniCPM 2.6 8B",
        family="MiniCPM",
        params_b=8.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=131072,
        vram_gb={"q4_k_m": 5.0, "q5_k_m": 5.8, "q8_0": 8.5, "f16": 16.0},
        ram_gb={"q4_k_m": 6.5, "q5_k_m": 7.3, "q8_0": 10.0, "f16": 18.0},
        license="Apache 2.0",
        tags=["reasoning", "multilingual", "chinese", "vision"],
        release_date="2024-10",
        benchmark_score=74,
        description="面壁智能端侧模型，支持多模态",
    ),
    ModelInfo(
        name="Hunyuan-Lite 7B",
        family="Hunyuan",
        params_b=7.0,
        quantizations=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        context_length=32768,
        vram_gb={"q4_k_m": 4.5, "q5_k_m": 5.2, "q8_0": 7.5, "f16": 14.0},
        ram_gb={"q4_k_m": 6.0, "q5_k_m": 6.7, "q8_0": 9.0, "f16": 16.0},
        license="Hunyuan",
        tags=["reasoning", "chinese", "multilingual"],
        release_date="2024-07",
        benchmark_score=71,
        description="腾讯混元轻量模型，中文理解优秀",
    ),
]


class ModelDatabase:
    """LLM模型数据库，提供查询和过滤功能"""

    def __init__(self, models: Optional[List[ModelInfo]] = None) -> None:
        """
        初始化模型数据库。

        Args:
            models: 模型列表，默认使用内置数据集
        """
        self._models = models if models is not None else list(BUILTIN_MODELS)
        self._index_by_name: Dict[str, ModelInfo] = {
            m.name.lower(): m for m in self._models
        }

    @property
    def models(self) -> List[ModelInfo]:
        """获取所有模型"""
        return list(self._models)

    @property
    def count(self) -> int:
        """获取模型总数"""
        return len(self._models)

    def get_model(self, name: str) -> Optional[ModelInfo]:
        """
        按名称查找模型（模糊匹配）。

        Args:
            name: 模型名称（不区分大小写）

        Returns:
            匹配的ModelInfo，未找到返回None
        """
        name_lower = name.lower().strip()
        # 精确匹配
        if name_lower in self._index_by_name:
            return self._index_by_name[name_lower]
        # 模糊匹配
        for model in self._models:
            if name_lower in model.name.lower():
                return model
        return None

    def get_families(self) -> List[str]:
        """获取所有模型系列"""
        families = sorted(set(m.family for m in self._models))
        return families

    def get_tags(self) -> List[str]:
        """获取所有标签"""
        tags = sorted(set(tag for m in self._models for tag in m.tags))
        return tags

    def filter_models(
        self,
        min_params: Optional[float] = None,
        max_params: Optional[float] = None,
        tags: Optional[List[str]] = None,
        min_context: Optional[int] = None,
        family: Optional[str] = None,
    ) -> List[ModelInfo]:
        """
        按条件过滤模型。

        Args:
            min_params: 最小参数量(十亿)
            max_params: 最大参数量(十亿)
            tags: 需要包含的标签列表（AND关系）
            min_context: 最小上下文长度
            family: 模型系列

        Returns:
            过滤后的模型列表
        """
        result = self._models

        if min_params is not None:
            result = [m for m in result if m.params_b >= min_params]

        if max_params is not None:
            result = [m for m in result if m.params_b <= max_params]

        if tags:
            result = [
                m for m in result
                if all(tag.lower() in [t.lower() for t in m.tags] for tag in tags)
            ]

        if min_context is not None:
            result = [m for m in result if m.context_length >= min_context]

        if family is not None:
            result = [m for m in result if m.family.lower() == family.lower()]

        return result
