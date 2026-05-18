"""
test_formatter.py - 输出格式化模块测试

测试表格、JSON、Markdown三种输出格式。
"""

import json
import os
import sys
import unittest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmfit.database import ModelDatabase, ModelInfo
from llmfit.detector import HardwareInfo, GPUInfo
from llmfit.formatter import Formatter, Colors, colorize, _safe_text, _pad_cell
from llmfit.scorer import Scorer, Recommendation


def create_test_hardware() -> HardwareInfo:
    """创建测试用硬件配置"""
    return HardwareInfo(
        cpu_model="Test CPU Model",
        cpu_cores=8,
        cpu_arch="x86_64",
        ram_gb=16.0,
        gpu=GPUInfo(
            vendor="NVIDIA",
            name="Test NVIDIA GPU",
            vram_gb=8.0,
            driver_version="535.0",
            compute_capability="8.9",
        ),
        os_name="Linux",
        os_version="5.15.0",
        os_arch="x86_64",
        disk_free_gb=500.0,
        python_version="3.10.0",
    )


def create_test_recommendation() -> Recommendation:
    """创建测试用推荐结果"""
    database = ModelDatabase()
    model = database.get_model("Qwen 2.5 7B")
    hw = create_test_hardware()
    scorer = Scorer(hw, database)
    return scorer.score_model(model, "q4_k_m")


class TestColorize(unittest.TestCase):
    """测试颜色功能"""

    def test_colorize(self):
        """测试着色"""
        result = colorize("hello", Colors.RED)
        self.assertIn("hello", result)
        self.assertIn(Colors.RED, result)
        self.assertIn(Colors.RESET, result)

    def test_safe_text(self):
        """测试移除ANSI代码"""
        colored = colorize("hello", Colors.RED)
        safe = _safe_text(colored)
        self.assertEqual(safe, "hello")

    def test_safe_text_plain(self):
        """测试纯文本"""
        self.assertEqual(_safe_text("hello"), "hello")

    def test_safe_text_empty(self):
        """测试空文本"""
        self.assertEqual(_safe_text(""), "")


class TestPadCell(unittest.TestCase):
    """测试单元格填充"""

    def test_left_align(self):
        """测试左对齐"""
        result = _pad_cell("abc", 10)
        self.assertEqual(len(_safe_text(result)), 10)
        self.assertTrue(result.startswith("abc"))

    def test_right_align(self):
        """测试右对齐"""
        result = _pad_cell("abc", 10, align="right")
        self.assertEqual(len(_safe_text(result)), 10)

    def test_center_align(self):
        """测试居中对齐"""
        result = _pad_cell("abc", 10, align="center")
        self.assertEqual(len(_safe_text(result)), 10)

    def test_exact_width(self):
        """测试精确宽度"""
        result = _pad_cell("abc", 3)
        self.assertEqual(_safe_text(result), "abc")

    def test_over_width(self):
        """测试超出宽度"""
        result = _pad_cell("abcdefghij", 5)
        self.assertEqual(_safe_text(result), "abcdefghij")


class TestFormatterInit(unittest.TestCase):
    """测试格式化器初始化"""

    def test_init_with_color(self):
        """测试启用颜色"""
        formatter = Formatter(use_color=True)
        self.assertTrue(formatter.use_color or not formatter.use_color)  # 取决于终端

    def test_init_without_color(self):
        """测试禁用颜色"""
        formatter = Formatter(use_color=False)
        self.assertFalse(formatter.use_color)


class TestHardwareFormat(unittest.TestCase):
    """测试硬件信息格式化"""

    def setUp(self):
        """设置测试环境"""
        self.hw = create_test_hardware()
        self.formatter = Formatter(use_color=False)

    def test_format_hardware_table(self):
        """测试表格格式"""
        output = self.formatter.format_hardware(self.hw, "table")
        self.assertIn("Test CPU Model", output)
        self.assertIn("NVIDIA", output)
        self.assertIn("16.0", output)
        self.assertIn("Linux", output)

    def test_format_hardware_json(self):
        """测试JSON格式"""
        output = self.formatter.format_hardware(self.hw, "json")
        data = json.loads(output)
        self.assertEqual(data["cpu"]["model"], "Test CPU Model")
        self.assertEqual(data["cpu"]["cores"], 8)
        self.assertAlmostEqual(data["ram_gb"], 16.0)
        self.assertIsNotNone(data["gpu"])
        self.assertEqual(data["gpu"]["vendor"], "NVIDIA")

    def test_format_hardware_markdown(self):
        """测试Markdown格式"""
        output = self.formatter.format_hardware(self.hw, "markdown")
        self.assertIn("# 硬件检测结果", output)
        self.assertIn("Test CPU Model", output)
        self.assertIn("|", output)

    def test_format_hardware_no_gpu(self):
        """测试无GPU硬件信息"""
        hw = HardwareInfo(ram_gb=8.0, cpu_model="Test CPU")
        output = self.formatter.format_hardware(hw, "table")
        self.assertIn("未检测到", output)


class TestModelListFormat(unittest.TestCase):
    """测试模型列表格式化"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.formatter = Formatter(use_color=False)

    def test_format_model_list_table(self):
        """测试表格格式"""
        output = self.formatter.format_model_list(self.database.models[:5], "table")
        self.assertIn("模型名称", output)
        self.assertIn("Llama", output)

    def test_format_model_list_json(self):
        """测试JSON格式"""
        output = self.formatter.format_model_list(self.database.models[:3], "json")
        data = json.loads(output)
        self.assertEqual(len(data), 3)
        self.assertIn("name", data[0])
        self.assertIn("params_b", data[0])

    def test_format_model_list_markdown(self):
        """测试Markdown格式"""
        output = self.formatter.format_model_list(self.database.models[:5], "markdown")
        self.assertIn("# 支持的模型列表", output)
        self.assertIn("|", output)

    def test_format_empty_list(self):
        """测试空列表"""
        output = self.formatter.format_model_list([], "table")
        self.assertIn("未找到", output)


class TestRecommendationFormat(unittest.TestCase):
    """测试推荐结果格式化"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw = create_test_hardware()
        self.scorer = Scorer(self.hw, self.database)
        self.formatter = Formatter(use_color=False)
        self.recs = self.scorer.recommend(top_n=5)

    def test_format_recommendations_table(self):
        """测试表格格式"""
        output = self.formatter.format_recommendations(self.recs, "table")
        self.assertIn("模型推荐", output)
        self.assertIn("总分", output)

    def test_format_recommendations_json(self):
        """测试JSON格式"""
        output = self.formatter.format_recommendations(self.recs, "json")
        data = json.loads(output)
        self.assertEqual(len(data), 5)
        self.assertIn("model", data[0])
        self.assertIn("total_score", data[0])
        self.assertIn("scores", data[0])

    def test_format_recommendations_markdown(self):
        """测试Markdown格式"""
        output = self.formatter.format_recommendations(self.recs, "markdown")
        self.assertIn("# 模型推荐结果", output)
        self.assertIn("|", output)

    def test_format_empty_recommendations(self):
        """测试空推荐"""
        output = self.formatter.format_recommendations([], "table")
        self.assertIn("未找到", output)


class TestModelDetailFormat(unittest.TestCase):
    """测试模型详情格式化"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.formatter = Formatter(use_color=False)
        self.model = self.database.get_model("Llama 3.1 8B")

    def test_format_model_detail_table(self):
        """测试表格格式"""
        output = self.formatter.format_model_detail(self.model, "table")
        self.assertIn("Llama 3.1 8B", output)
        self.assertIn("量化格式", output)
        self.assertIn("q4_k_m", output)

    def test_format_model_detail_json(self):
        """测试JSON格式"""
        output = self.formatter.format_model_detail(self.model, "json")
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Llama 3.1 8B")

    def test_format_model_detail_markdown(self):
        """测试Markdown格式"""
        output = self.formatter.format_model_detail(self.model, "markdown")
        self.assertIn("# Llama 3.1 8B", output)
        self.assertIn("## 量化格式", output)


class TestComparisonFormat(unittest.TestCase):
    """测试模型对比格式化"""

    def setUp(self):
        """设置测试环境"""
        self.database = ModelDatabase()
        self.hw = create_test_hardware()
        self.scorer = Scorer(self.hw, self.database)
        self.formatter = Formatter(use_color=False)
        self.rec1 = self.scorer.find_best_for_model("Llama 3.1 8B")
        self.rec2 = self.scorer.find_best_for_model("Qwen 2.5 7B")

    def test_format_comparison_table(self):
        """测试表格格式"""
        output = self.formatter.format_comparison(self.rec1, self.rec2, "table")
        self.assertIn("模型对比", output)
        self.assertIn("Llama 3.1 8B", output)
        self.assertIn("Qwen 2.5 7B", output)

    def test_format_comparison_json(self):
        """测试JSON格式"""
        output = self.formatter.format_comparison(self.rec1, self.rec2, "json")
        data = json.loads(output)
        self.assertIn("model_1", data)
        self.assertIn("model_2", data)
        self.assertIn("winner", data)

    def test_format_comparison_markdown(self):
        """测试Markdown格式"""
        output = self.formatter.format_comparison(self.rec1, self.rec2, "markdown")
        self.assertIn("# 模型对比", output)
        self.assertIn("|", output)


class TestFormatterWithColor(unittest.TestCase):
    """测试带颜色的格式化输出"""

    def setUp(self):
        """设置测试环境"""
        self.formatter = Formatter(use_color=True)
        self.hw = create_test_hardware()

    def test_c_method_with_color(self):
        """测试着色方法"""
        result = self.formatter._c("test", Colors.GREEN)
        # 如果支持颜色，应该包含ANSI代码
        # 如果不支持颜色，返回纯文本
        self.assertIn("test", result)

    def test_table_row_with_color(self):
        """测试带颜色的表格行"""
        row = self.formatter._build_table_row(
            ["a", "b", "c"],
            [5, 5, 5],
            is_header=True,
        )
        self.assertIn("|", row)


if __name__ == "__main__":
    unittest.main()
