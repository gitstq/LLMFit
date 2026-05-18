"""
detector.py - 硬件检测模块

检测CPU、GPU、RAM、VRAM、操作系统、磁盘空间等硬件信息。
使用纯Python标准库实现，零外部依赖。
GPU检测通过subprocess调用系统命令，失败则优雅降级。
"""

import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class GPUInfo:
    """GPU信息数据类"""
    vendor: str = "Unknown"          # GPU厂商: NVIDIA, AMD, Apple, Intel, Unknown
    name: str = "Unknown"            # GPU型号名称
    vram_gb: float = 0.0             # 显存大小(GB)
    driver_version: str = "Unknown"  # 驱动版本
    compute_capability: str = ""     # CUDA计算能力(仅NVIDIA)
    metal_support: bool = False      # Metal支持(Apple Silicon)


@dataclass
class HardwareInfo:
    """硬件信息汇总数据类"""
    cpu_model: str = "Unknown"
    cpu_cores: int = 0
    cpu_arch: str = "Unknown"
    ram_gb: float = 0.0
    gpu: Optional[GPUInfo] = None
    os_name: str = "Unknown"
    os_version: str = "Unknown"
    os_arch: str = "Unknown"
    disk_free_gb: float = 0.0
    python_version: str = "Unknown"

    def has_gpu(self) -> bool:
        """是否有可用GPU"""
        return self.gpu is not None and self.gpu.vram_gb > 0

    def total_memory_gb(self) -> float:
        """获取总可用内存(GB)，包括RAM和VRAM"""
        total = self.ram_gb
        if self.has_gpu():
            total += self.gpu.vram_gb
        return total


def _run_command(cmd: List[str], timeout: float = 5.0) -> Optional[str]:
    """
    安全执行系统命令并返回输出。

    Args:
        cmd: 命令和参数列表
        timeout: 超时时间(秒)

    Returns:
        命令输出字符串，失败返回None
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, PermissionError):
        return None


def detect_cpu() -> Tuple[str, int, str]:
    """
    检测CPU信息。

    Returns:
        (CPU型号, 核心数, 架构)
    """
    cpu_model = "Unknown"
    cpu_cores = 0
    cpu_arch = platform.machine() or "Unknown"

    # 获取CPU核心数
    try:
        cpu_cores = os.cpu_count() or 0
    except (AttributeError, OSError):
        pass

    system = platform.system()

    if system == "Linux":
        # Linux: 从 /proc/cpuinfo 读取
        cpu_model = _detect_cpu_linux()
    elif system == "Darwin":
        # macOS: 使用 sysctl
        cpu_model = _detect_cpu_macos()
    elif system == "Windows":
        # Windows: 使用环境变量或wmic
        cpu_model = _detect_cpu_windows()

    # 如果检测失败，使用platform提供的信息
    if cpu_model == "Unknown":
        cpu_model = platform.processor() or "Unknown"

    return cpu_model, cpu_cores, cpu_arch


def _detect_cpu_linux() -> str:
    """在Linux上检测CPU型号"""
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        # 查找model name
        match = re.search(r"model name\s*:\s*(.+)", content)
        if match:
            return match.group(1).strip()
    except (OSError, IOError):
        pass
    return "Unknown"


def _detect_cpu_macos() -> str:
    """在macOS上检测CPU型号"""
    output = _run_command(["sysctl", "-n", "machdep.cpu.brand_string"])
    if output:
        return output.strip()
    return "Unknown"


def _detect_cpu_windows() -> str:
    """在Windows上检测CPU型号"""
    # 尝试使用wmic
    output = _run_command(
        ["wmic", "cpu", "get", "name"],
        timeout=10.0,
    )
    if output:
        lines = [l.strip() for l in output.split("\n") if l.strip()]
        if len(lines) > 1:
            return lines[1]
    # 回退到环境变量
    return os.environ.get("PROCESSOR_IDENTIFIER", "Unknown")


def detect_ram() -> float:
    """
    检测系统总RAM大小。

    Returns:
        RAM大小(GB)
    """
    system = platform.system()

    if system == "Linux":
        return _detect_ram_linux()
    elif system == "Darwin":
        return _detect_ram_macos()
    elif system == "Windows":
        return _detect_ram_windows()

    return 0.0


def _detect_ram_linux() -> float:
    """在Linux上检测RAM"""
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    # 格式: MemTotal:       16384000 kB
                    parts = line.split()
                    kb = float(parts[1])
                    return kb / (1024 * 1024)  # 转换为GB
    except (OSError, IOError, ValueError, IndexError):
        pass
    return 0.0


def _detect_ram_macos() -> float:
    """在macOS上检测RAM"""
    output = _run_command(["sysctl", "-n", "hw.memsize"])
    if output:
        try:
            bytes_val = int(output.strip())
            return bytes_val / (1024 ** 3)
        except ValueError:
            pass
    return 0.0


def _detect_ram_windows() -> float:
    """在Windows上检测RAM"""
    output = _run_command(
        ["wmic", "computersystem", "get", "totalphysicalmemory"],
        timeout=10.0,
    )
    if output:
        lines = [l.strip() for l in output.split("\n") if l.strip()]
        if len(lines) > 1:
            try:
                bytes_val = int(lines[1])
                return bytes_val / (1024 ** 3)
            except ValueError:
                pass
    return 0.0


def detect_gpu() -> Optional[GPUInfo]:
    """
    检测GPU信息。

    支持NVIDIA (nvidia-smi), AMD (lspci), Apple Silicon (system_profiler)。
    检测失败时优雅降级返回None。

    Returns:
        GPUInfo对象，无GPU时返回None
    """
    system = platform.system()

    # 优先检测NVIDIA GPU
    nvidia_gpu = _detect_nvidia_gpu()
    if nvidia_gpu:
        return nvidia_gpu

    # 检测Apple Silicon GPU
    if system == "Darwin":
        apple_gpu = _detect_apple_gpu()
        if apple_gpu:
            return apple_gpu

    # 检测AMD GPU (Linux)
    if system == "Linux":
        amd_gpu = _detect_amd_gpu_linux()
        if amd_gpu:
            return amd_gpu

    return None


def _detect_nvidia_gpu() -> Optional[GPUInfo]:
    """通过nvidia-smi检测NVIDIA GPU"""
    output = _run_command(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,compute_cap", "--format=csv,noheader"],
        timeout=10.0,
    )
    if not output:
        return None

    try:
        # 格式: "NVIDIA GeForce RTX 4090, 24564 MiB, 535.129.03, 8.9"
        parts = [p.strip() for p in output.split(",")]
        if len(parts) >= 2:
            name = parts[0]
            # 解析显存
            mem_str = parts[1].strip()
            vram_gb = _parse_memory_string(mem_str)
            driver = parts[2].strip() if len(parts) > 2 else "Unknown"
            compute_cap = parts[3].strip() if len(parts) > 3 else ""

            return GPUInfo(
                vendor="NVIDIA",
                name=name,
                vram_gb=vram_gb,
                driver_version=driver,
                compute_capability=compute_cap,
            )
    except (ValueError, IndexError):
        pass
    return None


def _detect_apple_gpu() -> Optional[GPUInfo]:
    """在macOS上检测Apple Silicon GPU"""
    # 检查是否为Apple Silicon
    arch = platform.machine()
    if arch != "arm64":
        return None

    # 使用system_profiler获取GPU信息
    output = _run_command(
        ["system_profiler", "SPDisplaysDataType"],
        timeout=15.0,
    )
    if not output:
        return None

    try:
        # 解析GPU名称和显存
        gpu_name = "Apple Silicon GPU"
        vram_gb = 0.0

        # 提取芯片名称
        chip_match = re.search(r"Chipset Model:\s*(.+)", output)
        if chip_match:
            gpu_name = chip_match.group(1).strip()

        # 提取显存大小
        vram_match = re.search(r"Total Number of Cores:\s*(\d+)", output)
        if vram_match:
            cores = int(vram_match.group(1))
            # Apple Silicon GPU共享统一内存，这里返回0表示共享内存
            # 实际可用显存约等于总RAM - 系统占用

        # 尝试获取Metal支持信息
        metal_match = re.search(r"Metal:\s*(.+)", output)
        metal_support = bool(metal_match and "supported" in metal_match.group(1).lower())

        return GPUInfo(
            vendor="Apple",
            name=gpu_name,
            vram_gb=0.0,  # Apple Silicon使用统一内存
            metal_support=metal_support,
        )
    except (ValueError, AttributeError):
        pass
    return None


def _detect_amd_gpu_linux() -> Optional[GPUInfo]:
    """在Linux上通过lspci检测AMD GPU"""
    output = _run_command(["lspci"], timeout=10.0)
    if not output:
        return None

    try:
        for line in output.split("\n"):
            if "VGA" in line and ("AMD" in line or "Radeon" in line or "ATI" in line):
                # 提取GPU名称
                name_match = re.search(r":\s*(.+)$", line)
                name = name_match.group(1).strip() if name_match else "AMD GPU"

                # 尝试通过rocm-smi获取显存
                vram_gb = _detect_amd_vram()

                return GPUInfo(
                    vendor="AMD",
                    name=name,
                    vram_gb=vram_gb,
                )
    except (ValueError, AttributeError):
        pass
    return None


def _detect_amd_vram() -> float:
    """尝试通过rocm-smi获取AMD GPU显存"""
    output = _run_command(["rocm-smi", "--showmeminfo", "vram", "--csv"], timeout=10.0)
    if output:
        try:
            for line in output.split("\n"):
                if "VRAM" in line and "Total" in line:
                    # 尝试解析显存值
                    match = re.search(r"(\d+)", line)
                    if match:
                        vram_mb = int(match.group(1))
                        return vram_mb / 1024.0
        except (ValueError, AttributeError):
            pass
    return 0.0


def detect_os() -> Tuple[str, str, str]:
    """
    检测操作系统信息。

    Returns:
        (系统名称, 系统版本, 系统架构)
    """
    os_name = platform.system()
    os_version = platform.version()
    os_arch = platform.machine() or "Unknown"

    # 更友好的系统名称
    os_name_map = {
        "Linux": "Linux",
        "Darwin": "macOS",
        "Windows": "Windows",
    }
    friendly_name = os_name_map.get(os_name, os_name)

    # 获取更详细的版本信息
    if os_name == "Linux":
        # 尝试读取发行版信息
        try:
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        pretty = line.split("=", 1)[1].strip().strip('"')
                        friendly_name = pretty
                        break
        except (OSError, IOError):
            pass
    elif os_name == "Darwin":
        output = _run_command(["sw_vers", "-productVersion"])
        if output:
            os_version = output.strip()
        friendly_name = "macOS"
    elif os_name == "Windows":
        friendly_name = "Windows"
        os_version = platform.win32_ver()[1] if hasattr(platform, "win32_ver") else os_version

    return friendly_name, os_version, os_arch


def detect_disk_free(path: str = "/") -> float:
    """
    检测指定路径所在分区的可用磁盘空间。

    Args:
        path: 要检查的路径

    Returns:
        可用空间(GB)
    """
    system = platform.system()

    if system == "Linux" or system == "Darwin":
        return _detect_disk_free_unix(path)
    elif system == "Windows":
        return _detect_disk_free_windows(path)

    return 0.0


def _detect_disk_free_unix(path: str) -> float:
    """在Unix系统上检测磁盘可用空间"""
    try:
        stat = os.statvfs(path)
        free_bytes = stat.f_bavail * stat.f_frsize
        return free_bytes / (1024 ** 3)
    except (OSError, AttributeError):
        return 0.0


def _detect_disk_free_windows(path: str) -> float:
    """在Windows上检测磁盘可用空间"""
    try:
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes)
        )
        return free_bytes.value / (1024 ** 3)
    except (AttributeError, OSError):
        return 0.0


def detect_all() -> HardwareInfo:
    """
    执行完整的硬件检测，返回所有硬件信息。

    Returns:
        HardwareInfo对象，包含所有检测到的硬件信息
    """
    cpu_model, cpu_cores, cpu_arch = detect_cpu()
    ram_gb = detect_ram()
    gpu = detect_gpu()
    os_name, os_version, os_arch = detect_os()
    disk_free = detect_disk_free()

    # 确定磁盘检测路径
    if platform.system() == "Windows":
        disk_path = os.environ.get("SystemDrive", "C:\\")
    else:
        disk_path = "/"

    disk_free = detect_disk_free(disk_path)

    return HardwareInfo(
        cpu_model=cpu_model,
        cpu_cores=cpu_cores,
        cpu_arch=cpu_arch,
        ram_gb=ram_gb,
        gpu=gpu,
        os_name=os_name,
        os_version=os_version,
        os_arch=os_arch,
        disk_free_gb=disk_free,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )


def _parse_memory_string(mem_str: str) -> float:
    """
    解析内存字符串为GB。

    支持格式: "24564 MiB", "24 GB", "24564", "24.5 GiB" 等。

    Args:
        mem_str: 内存字符串

    Returns:
        内存大小(GB)
    """
    mem_str = mem_str.strip()

    # 尝试匹配数字+单位
    match = re.match(r"([\d.]+)\s*(MiB|GiB|MB|GB|KB)?", mem_str, re.IGNORECASE)
    if not match:
        return 0.0

    value = float(match.group(1))
    unit = (match.group(2) or "").upper()

    if unit in ("MIB", "MB"):
        return value / 1024.0
    elif unit in ("GIB", "GB"):
        return value
    elif unit in ("KIB", "KB"):
        return value / (1024 * 1024)
    else:
        # 无单位，假设为MiB（nvidia-smi默认输出）
        return value / 1024.0
