"""
setup.py - LLMFit 安装配置
"""

from setuptools import setup, find_packages

setup(
    name="llmfit",
    version="1.0.0",
    description="轻量级本地LLM硬件适配与智能推荐引擎",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="LLMFit Team",
    license="MIT",
    url="https://github.com/llmfit/llmfit",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "black>=22.0",
            "ruff>=0.1.0",
            "isort>=5.0",
            "pytest>=7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llmfit=llmfit.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
