"""
test_detector.py - 硬件检测模块测试

测试CPU、RAM、GPU、OS、磁盘检测功能。
使用mock避免依赖实际硬件环境。
"""

import os
import platform
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmfit.detector import (
    HardwareInfo,
    GPUInfo,
    detect_cpu,
    detect_ram,
    detect_os,
    detect_disk_free,
    detect_gpu,
    detect_all,
    _parse_memory_string,
    _run_command,
)


class TestParseMemoryString(unittest.TestCase):
    """测试内存字符串解析"""

    def test_mib_format(self):
        """测试MiB格式"""
        self.assertAlmostEqual(_parse_memory_string("24564 MiB"), 23.984375, places=2)

    def test_gb_format(self):
        """测试GB格式"""
        self.assertAlmostEqual(_parse_memory_string("24 GB"), 24.0)

    def test_gib_format(self):
        """测试GiB格式"""
        self.assertAlmostEqual(_parse_memory_string("24.5 GiB"), 24.5)

    def test_mb_format(self):
        """测试MB格式"""
        self.assertAlmostEqual(_parse_memory_string("8192 MB"), 8.0)

    def test_plain_number(self):
        """测试纯数字（假设为MiB）"""
        self.assertAlmostEqual(_parse_memory_string("8192"), 8.0)

    def test_decimal_mib(self):
        """测试小数MiB"""
        self.assertAlmostEqual(_parse_memory_string("5120.5 MiB"), 5.0, places=1)

    def test_empty_string(self):
        """测试空字符串"""
        self.assertAlmostEqual(_parse_memory_string(""), 0.0)

    def test_invalid_string(self):
        """测试无效字符串"""
        self.assertAlmostEqual(_parse_memory_string("invalid"), 0.0)


class TestRunCommand(unittest.TestCase):
    """测试命令执行"""

    def test_valid_command(self):
        """测试有效命令"""
        result = _run_command(["echo", "hello"])
        self.assertIsNotNone(result)
        self.assertIn("hello", result)

    def test_invalid_command(self):
        """测试无效命令"""
        result = _run_command(["nonexistent_command_xyz"])
        self.assertIsNone(result)

    def test_timeout(self):
        """测试超时"""
        result = _run_command(["sleep", "10"], timeout=0.1)
        self.assertIsNone(result)


class TestDetectCPU(unittest.TestCase):
    """测试CPU检测"""

    @patch("llmfit.detector.os.cpu_count", return_value=8)
    def test_cpu_cores(self, mock_count):
        """测试CPU核心数"""
        _, cores, _ = detect_cpu()
        self.assertEqual(cores, 8)

    @patch("llmfit.detector.os.cpu_count", return_value=None)
    def test_cpu_cores_none(self, mock_count):
        """测试CPU核心数为None"""
        _, cores, _ = detect_cpu()
        self.assertEqual(cores, 0)

    @patch("llmfit.detector.platform.machine", return_value="x86_64")
    def test_cpu_arch(self, mock_machine):
        """测试CPU架构"""
        _, _, arch = detect_cpu()
        self.assertEqual(arch, "x86_64")

    @patch("llmfit.detector.platform.machine", return_value="arm64")
    def test_cpu_arch_arm(self, mock_machine):
        """测试ARM架构"""
        _, _, arch = detect_cpu()
        self.assertEqual(arch, "arm64")


class TestDetectRAM(unittest.TestCase):
    """测试RAM检测"""

    @patch("llmfit.detector.platform.system", return_value="Linux")
    def test_linux_ram(self, mock_sys):
        """测试Linux RAM检测"""
        # 创建临时meminfo文件
        meminfo_content = "MemTotal:       16384000 kB\n"
        with patch("builtins.open", unittest.mock.mock_open(read_data=meminfo_content)):
            ram = detect_ram()
            self.assertAlmostEqual(ram, 15.625, places=2)

    @patch("llmfit.detector.platform.system", return_value="Unknown")
    def test_unknown_os_ram(self, mock_sys):
        """测试未知系统RAM检测"""
        ram = detect_ram()
        self.assertEqual(ram, 0.0)


class TestDetectOS(unittest.TestCase):
    """测试操作系统检测"""

    @patch("llmfit.detector.platform.system", return_value="Linux")
    @patch("llmfit.detector.platform.version", return_value="#1 SMP")
    @patch("llmfit.detector.platform.machine", return_value="x86_64")
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_linux_os(self, mock_open, mock_machine, mock_ver, mock_sys):
        """测试Linux系统检测（无os-release文件时回退到Linux）"""
        name, version, arch = detect_os()
        self.assertEqual(name, "Linux")
        self.assertEqual(arch, "x86_64")

    @patch("llmfit.detector.platform.system", return_value="Darwin")
    @patch("llmfit.detector.platform.version", return_value="Darwin Kernel")
    @patch("llmfit.detector.platform.machine", return_value="arm64")
    def test_macos_os(self, mock_machine, mock_ver, mock_sys):
        """测试macOS系统检测"""
        name, version, arch = detect_os()
        self.assertEqual(name, "macOS")
        self.assertEqual(arch, "arm64")

    @patch("llmfit.detector.platform.system", return_value="Windows")
    @patch("llmfit.detector.platform.version", return_value="10.0")
    @patch("llmfit.detector.platform.machine", return_value="AMD64")
    def test_windows_os(self, mock_machine, mock_ver, mock_sys):
        """测试Windows系统检测"""
        name, version, arch = detect_os()
        self.assertEqual(name, "Windows")


class TestDetectDiskFree(unittest.TestCase):
    """测试磁盘空间检测"""

    @patch("llmfit.detector.platform.system", return_value="Linux")
    def test_linux_disk(self, mock_sys):
        """测试Linux磁盘检测"""
        # 创建mock statvfs
        mock_stat = MagicMock()
        mock_stat.f_bavail = 1024 * 1024  # 1M blocks
        mock_stat.f_frsize = 4096  # 4K block size
        with patch("llmfit.detector.os.statvfs", return_value=mock_stat):
            free = detect_disk_free("/")
            # 1M * 4K = 4GB
            self.assertAlmostEqual(free, 4.0, places=1)

    @patch("llmfit.detector.platform.system", return_value="Unknown")
    def test_unknown_os_disk(self, mock_sys):
        """测试未知系统磁盘检测"""
        free = detect_disk_free("/")
        self.assertEqual(free, 0.0)


class TestDetectGPU(unittest.TestCase):
    """测试GPU检测"""

    @patch("llmfit.detector._detect_nvidia_gpu", return_value=None)
    @patch("llmfit.detector.platform.system", return_value="Linux")
    @patch("llmfit.detector._detect_amd_gpu_linux", return_value=None)
    def test_no_gpu(self, mock_amd, mock_sys, mock_nvidia):
        """测试无GPU"""
        gpu = detect_gpu()
        self.assertIsNone(gpu)

    @patch("llmfit.detector._detect_nvidia_gpu")
    def test_nvidia_gpu_detected(self, mock_nvidia):
        """测试NVIDIA GPU检测"""
        mock_gpu = GPUInfo(
            vendor="NVIDIA",
            name="NVIDIA GeForce RTX 4090",
            vram_gb=24.0,
            driver_version="535.129.03",
            compute_capability="8.9",
        )
        mock_nvidia.return_value = mock_gpu
        gpu = detect_gpu()
        self.assertIsNotNone(gpu)
        self.assertEqual(gpu.vendor, "NVIDIA")
        self.assertEqual(gpu.vram_gb, 24.0)


class TestHardwareInfo(unittest.TestCase):
    """测试HardwareInfo数据类"""

    def test_has_gpu_true(self):
        """测试有GPU"""
        hw = HardwareInfo(
            gpu=GPUInfo(vendor="NVIDIA", vram_gb=8.0),
            ram_gb=16.0,
        )
        self.assertTrue(hw.has_gpu())

    def test_has_gpu_false(self):
        """测试无GPU"""
        hw = HardwareInfo(ram_gb=16.0)
        self.assertFalse(hw.has_gpu())

    def test_has_gpu_zero_vram(self):
        """测试GPU显存为0"""
        hw = HardwareInfo(
            gpu=GPUInfo(vendor="NVIDIA", vram_gb=0.0),
            ram_gb=16.0,
        )
        self.assertFalse(hw.has_gpu())

    def test_total_memory(self):
        """测试总内存计算"""
        hw = HardwareInfo(
            ram_gb=16.0,
            gpu=GPUInfo(vendor="NVIDIA", vram_gb=8.0),
        )
        self.assertAlmostEqual(hw.total_memory_gb(), 24.0)

    def test_total_memory_no_gpu(self):
        """测试无GPU时总内存"""
        hw = HardwareInfo(ram_gb=16.0)
        self.assertAlmostEqual(hw.total_memory_gb(), 16.0)


class TestDetectAll(unittest.TestCase):
    """测试完整硬件检测"""

    @patch("llmfit.detector.detect_disk_free", return_value=100.0)
    @patch("llmfit.detector.detect_os", return_value=("Linux", "5.15", "x86_64"))
    @patch("llmfit.detector.detect_gpu", return_value=None)
    @patch("llmfit.detector.detect_ram", return_value=16.0)
    @patch("llmfit.detector.detect_cpu", return_value=("Test CPU", 8, "x86_64"))
    def test_detect_all(
        self, mock_cpu, mock_ram, mock_gpu, mock_os, mock_disk
    ):
        """测试完整检测流程"""
        hw = detect_all()
        self.assertEqual(hw.cpu_model, "Test CPU")
        self.assertEqual(hw.cpu_cores, 8)
        self.assertAlmostEqual(hw.ram_gb, 16.0)
        self.assertIsNone(hw.gpu)
        self.assertEqual(hw.os_name, "Linux")
        self.assertAlmostEqual(hw.disk_free_gb, 100.0)


if __name__ == "__main__":
    unittest.main()
