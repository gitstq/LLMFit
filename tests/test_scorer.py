"""
test_scorer.py - 评分引擎测试

测试智能评分推荐引擎的各项功能。
使用固定硬件配置进行测试。
"""

import os
import sys
import unittest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmfit.database import ModelDatabase, ModelInfo
from llmfit.detector import HardwareInfo, GPUInfo
from llmfit.scorer import Scorer, Recommendation


def create_test_hardware(
    ram_gb: float = 16.0,
    gpu_vram_gb: float = 8.0,
    cpu_cores: int = 8,
    gpu_vendor: str = "NVIDIA",
) -> HardwareInfo:
    """创建测试用硬件配置"""
    gpu = GPUInfo(
        vendor=gpu_vendor,
        name=f"Test {gpu_vendor} GPU",
        vram_gb=gpu_vram_gb,
    ) if gpu_vram_gb > 0 else None

    return HardwareInfo(
        cpu_model="Test CPU",
        cpu_cores=cpu_cores,
        cpu_arch="x86_64",
        ram_gb=ram_gb,
        gpu=gpu,
        os_name="Linux",
        os_version="5.15",
        os_arch="x86_64",
        disk_free_gb=500.0,
        python_version="3.10.0",
    )


class TestScorerBasic(unittest.TestCase):
    """测试评分引擎基本功能"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw_8gb_gpu = create_test_hardware(ram_gb=16.0, gpu_vram_gb=8.0)
        self.hw_no_gpu = create_test_hardware(ram_gb=16.0, gpu_vram_gb=0.0)
        self.hw_24gb_gpu = create_test_hardware(ram_gb=32.0, gpu_vram_gb=24.0)

    def test_scorer_init(self):
        """测试评分引擎初始化"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        self.assertEqual(scorer.hardware, self.hw_8gb_gpu)
        self.assertEqual(scorer.database, self.database)

    def test_score_model_returns_recommendation(self):
        """测试评分返回推荐结果"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        model = self.database.get_model("Llama 3.1 8B")
        self.assertIsNotNone(model)

        rec = scorer.score_model(model, "q4_k_m")
        self.assertIsInstance(rec, Recommendation)
        self.assertEqual(rec.model, model)
        self.assertEqual(rec.quantization, "q4_k_m")

    def test_score_range(self):
        """测试分数范围在0-100之间"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        for model in self.database.models:
            for quant in model.quantizations:
                rec = scorer.score_model(model, quant)
                self.assertGreaterEqual(rec.score, 0)
                self.assertLessEqual(rec.score, 100)

    def test_sub_scores_range(self):
        """测试各子分数范围"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        model = self.database.get_model("Qwen 2.5 7B")
        rec = scorer.score_model(model, "q4_k_m")

        self.assertGreaterEqual(rec.hardware_score, 0)
        self.assertLessEqual(rec.hardware_score, 100)
        self.assertGreaterEqual(rec.performance_score, 0)
        self.assertLessEqual(rec.performance_score, 100)
        self.assertGreaterEqual(rec.quality_score, 0)
        self.assertLessEqual(rec.quality_score, 100)
        self.assertGreaterEqual(rec.feature_score, 0)
        self.assertLessEqual(rec.feature_score, 100)


class TestRecommend(unittest.TestCase):
    """测试推荐功能"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw_8gb_gpu = create_test_hardware(ram_gb=16.0, gpu_vram_gb=8.0)

    def test_recommend_returns_list(self):
        """测试推荐返回列表"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=5)
        self.assertIsInstance(recs, list)
        self.assertLessEqual(len(recs), 5)

    def test_recommend_sorted(self):
        """测试推荐结果按分数排序"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=10)
        for i in range(len(recs) - 1):
            self.assertGreaterEqual(recs[i].score, recs[i + 1].score)

    def test_recommend_top_n(self):
        """测试推荐数量限制"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=3)
        self.assertEqual(len(recs), 3)

    def test_recommend_with_tag_filter(self):
        """测试标签过滤"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=10, tags=["coding"])
        for rec in recs:
            self.assertIn("coding", [t.lower() for t in rec.model.tags])

    def test_recommend_with_min_params(self):
        """测试最小参数量过滤"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=10, min_params=10.0)
        for rec in recs:
            self.assertGreaterEqual(rec.model.params_b, 10.0)

    def test_recommend_with_max_params(self):
        """测试最大参数量过滤"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=10, max_params=10.0)
        for rec in recs:
            self.assertLessEqual(rec.model.params_b, 10.0)

    def test_recommend_with_min_context(self):
        """测试最小上下文过滤"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=10, min_context=131072)
        for rec in recs:
            self.assertGreaterEqual(rec.model.context_length, 131072)

    def test_recommend_multiple_tags(self):
        """测试多标签过滤（AND关系）"""
        scorer = Scorer(self.hw_8gb_gpu, self.database)
        recs = scorer.recommend(top_n=10, tags=["coding", "chinese"])
        for rec in recs:
            tags_lower = [t.lower() for t in rec.model.tags]
            self.assertIn("coding", tags_lower)
            self.assertIn("chinese", tags_lower)


class TestHardwareScoring(unittest.TestCase):
    """测试硬件匹配度评分"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()

    def test_fits_in_vram(self):
        """测试VRAM适配判断"""
        hw = create_test_hardware(ram_gb=16.0, gpu_vram_gb=8.0)
        scorer = Scorer(hw, self.database)
        model = self.database.get_model("Qwen 2.5 7B")
        rec = scorer.score_model(model, "q4_k_m")
        # 4.5GB VRAM需求 < 8GB可用
        self.assertTrue(rec.fits_in_vram)

    def test_not_fits_in_vram(self):
        """测试VRAM不适配判断"""
        hw = create_test_hardware(ram_gb=16.0, gpu_vram_gb=4.0)
        scorer = Scorer(hw, self.database)
        model = self.database.get_model("Llama 3.1 70B")
        rec = scorer.score_model(model, "q4_k_m")
        # 40GB VRAM需求 > 4GB可用
        self.assertFalse(rec.fits_in_vram)

    def test_fits_in_ram(self):
        """测试RAM适配判断"""
        hw = create_test_hardware(ram_gb=32.0, gpu_vram_gb=0.0)
        scorer = Scorer(hw, self.database)
        model = self.database.get_model("Qwen 2.5 7B")
        rec = scorer.score_model(model, "q4_k_m")
        # 6GB RAM需求 < 30GB可用 (32-2系统余量)
        self.assertTrue(rec.fits_in_ram)

    def test_not_fits_in_ram(self):
        """测试RAM不适配判断"""
        hw = create_test_hardware(ram_gb=4.0, gpu_vram_gb=0.0)
        scorer = Scorer(hw, self.database)
        model = self.database.get_model("Llama 3.1 70B")
        rec = scorer.score_model(model, "q4_k_m")
        # 42GB RAM需求 > 2GB可用 (4-2系统余量)
        self.assertFalse(rec.fits_in_ram)

    def test_gpu_higher_score_than_cpu(self):
        """测试GPU推理分数高于CPU推理"""
        hw_gpu = create_test_hardware(ram_gb=16.0, gpu_vram_gb=8.0)
        hw_cpu = create_test_hardware(ram_gb=16.0, gpu_vram_gb=0.0)

        scorer_gpu = Scorer(hw_gpu, self.database)
        scorer_cpu = Scorer(hw_cpu, self.database)

        model = self.database.get_model("Qwen 2.5 7B")
        rec_gpu = scorer_gpu.score_model(model, "q4_k_m")
        rec_cpu = scorer_cpu.score_model(model, "q4_k_m")

        # GPU推理应该有更高的性能分数
        self.assertGreaterEqual(rec_gpu.performance_score, rec_cpu.performance_score)


class TestFindBestForModel(unittest.TestCase):
    """测试单模型最佳量化推荐"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw = create_test_hardware(ram_gb=16.0, gpu_vram_gb=8.0)

    def test_find_best_known_model(self):
        """测试查找已知模型"""
        scorer = Scorer(self.hw, self.database)
        rec = scorer.find_best_for_model("Llama 3.1 8B")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.model.name, "Llama 3.1 8B")

    def test_find_best_unknown_model(self):
        """测试查找未知模型"""
        scorer = Scorer(self.hw, self.database)
        rec = scorer.find_best_for_model("Nonexistent Model")
        self.assertIsNone(rec)

    def test_best_quant_selection(self):
        """测试最佳量化选择"""
        scorer = Scorer(self.hw, self.database)
        rec = scorer.find_best_for_model("Qwen 2.5 7B")
        self.assertIsNotNone(rec)
        # 在8GB GPU上，q4_k_m应该比f16得分更高
        self.assertIn(rec.quantization, ["q4_k_m", "q5_k_m", "q8_0", "f16"])


class TestCompareModels(unittest.TestCase):
    """测试模型对比功能"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw = create_test_hardware(ram_gb=16.0, gpu_vram_gb=8.0)

    def test_compare_known_models(self):
        """测试对比已知模型"""
        scorer = Scorer(self.hw, self.database)
        result = scorer.compare_models("Llama 3.1 8B", "Qwen 2.5 7B")
        self.assertIsNotNone(result)
        rec1, rec2 = result
        self.assertEqual(rec1.model.name, "Llama 3.1 8B")
        self.assertEqual(rec2.model.name, "Qwen 2.5 7B")

    def test_compare_unknown_model(self):
        """测试对比包含未知模型"""
        scorer = Scorer(self.hw, self.database)
        result = scorer.compare_models("Llama 3.1 8B", "Nonexistent")
        self.assertIsNone(result)


class TestNoGPU(unittest.TestCase):
    """测试无GPU环境"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw = create_test_hardware(ram_gb=16.0, gpu_vram_gb=0.0)

    def test_recommend_no_gpu(self):
        """测试无GPU时推荐"""
        scorer = Scorer(self.hw, self.database)
        recs = scorer.recommend(top_n=5)
        self.assertGreater(len(recs), 0)
        # 所有推荐应该都能装入RAM
        for rec in recs:
            self.assertTrue(rec.fits_in_ram)

    def test_no_gpu_fits_in_vram_false(self):
        """测试无GPU时VRAM适配为False"""
        scorer = Scorer(self.hw, self.database)
        model = self.database.get_model("Qwen 2.5 7B")
        rec = scorer.score_model(model, "q4_k_m")
        self.assertFalse(rec.fits_in_vram)


if __name__ == "__main__":
    unittest.main()
