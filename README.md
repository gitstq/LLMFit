<div align="center">

# LLMFit

**轻量级本地LLM硬件适配与智能推荐引擎**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-success.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

一键检测硬件，智能推荐最适合你设备的开源大语言模型。

</div>

---

> **语言切换 / Language**
> [简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

---

<a id="简体中文"></a>

# 简体中文

## 🎉 项目介绍

LLMFit 是一款专为本地大语言模型（LLM）用户打造的命令行工具，致力于解决一个普遍痛点：**面对数十种开源模型，我的硬件到底能跑哪个？**

在本地部署 LLM 的过程中，用户往往需要反复查阅模型文档、对比显存需求、估算量化效果，整个过程繁琐且容易出错。LLMFit 将这一切自动化——只需一行命令，即可完成硬件检测、模型匹配和智能推荐。

**核心价值：**
- **省时**：告别手动查表和反复试错，一条命令获得最佳推荐
- **精准**：内置 25+ 主流开源 LLM 的详细硬件需求数据，评分算法覆盖四大维度
- **轻量**：纯 Python 标准库实现，零外部依赖，安装即用
- **直观**：彩色终端 UI + 多格式输出，信息一目了然

**差异化亮点：**
- 完全离线运行，无需联网即可完成所有检测和推荐
- 跨平台支持（Windows / macOS / Linux），自动适配 NVIDIA、AMD、Apple Silicon GPU
- 支持多种量化格式（Q4_K_M / Q5_K_M / Q8_0 / F16）的精细化资源评估

---

## ✨ 核心特性

- 🔍 **自动硬件检测**：一键识别 CPU 型号与核心数、GPU 型号与显存、系统内存、磁盘空间
- 📊 **智能评分引擎**：从硬件匹配度、性能表现、模型质量、功能丰富度四个维度综合评估
- 🗄️ **内置模型数据库**：涵盖 Llama 3.1、Qwen 2.5、Mistral、Phi-3、Gemma 2、DeepSeek 等 25+ 模型
- 🎨 **彩色终端 UI**：直观的表格输出，分数颜色编码，关键信息高亮显示
- 📋 **多格式输出**：支持表格（table）、JSON、Markdown 三种输出格式
- ⚖️ **模型对比**：并排对比两个模型在当前硬件上的适配情况
- 🏷️ **灵活过滤**：按标签、参数量、上下文长度等多维度筛选模型
- 🌐 **跨平台兼容**：Windows、macOS、Linux 全平台支持，自动适配各类 GPU
- 📦 **零外部依赖**：纯 Python 3.8+ 标准库实现，pip install 即可使用
- 🚫 **完全离线**：无需联网，所有检测和推荐均在本地完成

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 安装

**方式一：通过 pip 安装（推荐）**

```bash
pip install llmfit
```

**方式二：从源码安装**

```bash
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit
pip install -e .
```

### 启动

安装完成后，在终端中直接运行：

```bash
llmfit
```

首次运行将自动检测你的硬件配置，并推荐最适合的模型。

---

## 📖 详细使用指南

### 命令总览

| 命令 | 说明 |
|------|------|
| `llmfit` | 显示硬件信息 + 推荐最佳模型（默认行为） |
| `llmfit detect` | 仅检测并显示硬件信息 |
| `llmfit list` | 列出所有支持的模型 |
| `llmfit recommend` | 根据硬件配置推荐模型 |
| `llmfit compare <m1> <m2>` | 对比两个模型的硬件适配情况 |
| `llmfit info <model_name>` | 查看指定模型的详细信息 |

### 全局参数

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--format` | `-f` | 输出格式：`table` / `json` / `markdown` | `table` |
| `--no-color` | | 禁用彩色终端输出 | 关闭 |
| `--version` | `-v` | 显示版本号 | - |

### detect - 硬件检测

检测并展示当前系统的完整硬件配置信息。

```bash
llmfit detect
```

输出内容包括：CPU 型号与核心数、系统内存、GPU 型号与显存、操作系统、磁盘可用空间、Python 版本，以及基于硬件的模型适配建议。

### list - 模型列表

列出数据库中所有支持的 LLM 模型。

```bash
# 列出所有模型
llmfit list

# 按模型系列过滤
llmfit list --family Qwen

# JSON 格式输出
llmfit list --format json
```

### recommend - 智能推荐

根据当前硬件配置，智能推荐最适合的模型。

```bash
# 推荐前 10 个模型（默认）
llmfit recommend

# 推荐前 5 个模型
llmfit recommend --top 5

# 按标签过滤（支持多次使用，为 AND 关系）
llmfit recommend --tag coding
llmfit recommend --tag coding --tag chinese

# 设置最小参数量（单位：十亿）
llmfit recommend --min-params 7

# 设置最大参数量
llmfit recommend --max-params 15

# 设置最小上下文长度
llmfit recommend --min-context 32768

# 指定输出格式
llmfit recommend --format json
llmfit recommend --format markdown
```

**recommend 参数一览：**

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--top` | `-n` | 推荐数量 | 10 |
| `--tag` | `-t` | 按标签过滤（可多次使用） | 无 |
| `--min-params` | | 最小参数量（十亿） | 无 |
| `--max-params` | | 最大参数量（十亿） | 无 |
| `--min-context` | | 最小上下文长度 | 无 |

### compare - 模型对比

并排对比两个模型在当前硬件上的适配情况。

```bash
llmfit compare "Llama 3.1 8B" "Qwen 2.5 7B"
```

对比结果包含：参数量、推荐量化格式、上下文长度、基准分数、各维度评分、内存使用、预估推理速度等。

### info - 模型详情

查看指定模型的完整信息。

```bash
llmfit info "Llama 3.1 8B"
```

输出包括：模型描述、参数量、上下文长度、开源协议、发布日期、基准分数、各量化格式的 VRAM/RAM 需求、能力标签等。

### 典型使用场景

```bash
# 场景一：新手一键上手 —— 检测硬件并获得最佳推荐
llmfit

# 场景二：开发者选型 —— 找到最适合编程的模型
llmfit recommend --tag coding --top 5

# 场景三：资源受限环境 —— 在 8GB 显存显卡上找最佳模型
llmfit recommend --max-params 8

# 场景四：长文本处理 —— 需要超长上下文支持
llmfit recommend --min-context 131072

# 场景五：模型选型纠结 —— 对比两个候选模型
llmfit compare "Qwen 2.5 14B" "Mistral Nemo 12B"

# 场景六：自动化集成 —— JSON 格式输出供脚本处理
llmfit recommend --top 3 --format json
```

---

## 💡 设计思路与迭代规划

### 设计理念

LLMFit 的核心设计理念是 **"让本地 LLM 部署的选型决策变得简单"**。我们相信，降低用户从"想用 LLM"到"成功运行 LLM"之间的门槛，是推动本地 LLM 普及的关键一步。

### 技术选型原因

| 决策 | 原因 |
|------|------|
| **纯 Python 标准库** | 最大化降低安装门槛，避免依赖冲突，确保在任何 Python 环境中都能运行 |
| **CLI 工具形态** | 面向开发者和技术用户，CLI 是最高效的交互方式，也便于集成到自动化流程中 |
| **内置离线数据库** | 模型数据内置在代码中，无需联网，启动即用，隐私友好 |
| **多维度加权评分** | 单一指标无法全面反映适配度，加权评分能更准确地匹配用户需求 |
| **ANSI 彩色输出** | 终端环境下的信息可读性远高于纯文本，颜色编码帮助用户快速定位关键信息 |

### 评分体系

LLMFit 采用四维加权评分体系：

| 维度 | 权重 | 说明 |
|------|------|------|
| 硬件匹配度 | 40% | 评估模型在各量化级别下是否能装入 VRAM/RAM，以及资源利用率 |
| 性能表现 | 30% | 综合参数量、量化级别、GPU 加速和 CPU 核心数评估推理速度 |
| 模型质量 | 20% | 基于基准测试分数和模型参数量评估输出质量 |
| 功能丰富度 | 10% | 评估上下文长度、多语言支持、特殊能力（视觉、工具调用等） |

### 后续规划

- [ ] 支持自定义模型数据库（用户可添加自己的模型数据）
- [ ] 增加 GPU 推理框架检测（llama.cpp、Ollama、vLLM 等）
- [ ] 提供交互式 TUI 界面
- [ ] 支持模型下载链接和一键下载
- [ ] 增加历史评分记录和硬件升级后的对比功能
- [ ] 支持更多 GPU 厂商（Intel Arc 等）
- [ ] 提供 Web 版本

---

## 📦 打包与部署指南

### 通过 pip 安装（推荐用户）

```bash
pip install llmfit
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit

# 安装
pip install .
```

### 开发模式安装

如果你希望参与开发，建议使用可编辑模式安装：

```bash
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

开发依赖包括：black（代码格式化）、ruff（代码检查）、isort（导入排序）、pytest（单元测试）。

### 运行测试

```bash
pytest
```

---

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！

### 提交 Issue

- 使用清晰的标题描述问题或建议
- 附上运行环境信息（操作系统、Python 版本、GPU 型号）
- 如果是 Bug，请提供复现步骤和完整错误信息

### 提交 Pull Request

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 确保代码通过测试：`pytest`
4. 确保代码风格一致：`black . && ruff check .`
5. 提交变更：`git commit -m "feat: 描述你的改动"`
6. 推送分支：`git push origin feature/your-feature-name`
7. 创建 Pull Request

### Commit 规范

请使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

## 📄 开源协议

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2024 LLMFit Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="繁體中文"></a>

# 繁體中文

## 🎉 專案介紹

LLMFit 是一款專為本地大語言模型（LLM）使用者打造的命令列工具，致力於解決一個普遍痛點：**面對數十種開源模型，我的硬體到底能跑哪個？**

在本地部署 LLM 的過程中，使用者往往需要反覆查閱模型文件、對比顯存需求、估算量化效果，整個過程繁瑣且容易出錯。LLMFit 將這一切自動化——只需一行命令，即可完成硬體檢測、模型匹配和智慧推薦。

**核心價值：**
- **省時**：告別手動查表和反覆試錯，一條命令獲得最佳推薦
- **精準**：內建 25+ 主流開源 LLM 的詳細硬體需求資料，評分演算法覆蓋四大維度
- **輕量**：純 Python 標準函式庫實作，零外部依賴，安裝即用
- **直觀**：彩色終端 UI + 多格式輸出，資訊一目了然

**差異化亮點：**
- 完全離線運行，無需連網即可完成所有檢測和推薦
- 跨平台支援（Windows / macOS / Linux），自動適配 NVIDIA、AMD、Apple Silicon GPU
- 支援多種量化格式（Q4_K_M / Q5_K_M / Q8_0 / F16）的精細化資源評估

---

## ✨ 核心特性

- 🔍 **自動硬體檢測**：一鍵識別 CPU 型號與核心數、GPU 型號與顯存、系統記憶體、磁碟空間
- 📊 **智慧評分引擎**：從硬體匹配度、效能表現、模型品質、功能豐富度四個維度綜合評估
- 🗄️ **內建模型資料庫**：涵蓋 Llama 3.1、Qwen 2.5、Mistral、Phi-3、Gemma 2、DeepSeek 等 25+ 模型
- 🎨 **彩色終端 UI**：直觀的表格輸出，分數顏色編碼，關鍵資訊高亮顯示
- 📋 **多格式輸出**：支援表格（table）、JSON、Markdown 三種輸出格式
- ⚖️ **模型對比**：並排對比兩個模型在當前硬體上的適配情況
- 🏷️ **靈活過濾**：按標籤、參數量、上下文長度等多維度篩選模型
- 🌐 **跨平台相容**：Windows、macOS、Linux 全平台支援，自動適配各類 GPU
- 📦 **零外部依賴**：純 Python 3.8+ 標準函式庫實作，pip install 即可使用
- 🚫 **完全離線**：無需連網，所有檢測和推薦均在本地完成

---

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- 支援的作業系統：Windows、macOS、Linux

### 安裝

**方式一：透過 pip 安裝（推薦）**

```bash
pip install llmfit
```

**方式二：從原始碼安裝**

```bash
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit
pip install -e .
```

### 啟動

安裝完成後，在終端中直接執行：

```bash
llmfit
```

首次執行將自動檢測你的硬體配置，並推薦最適合的模型。

---

## 📖 詳細使用指南

### 指令總覽

| 指令 | 說明 |
|------|------|
| `llmfit` | 顯示硬體資訊 + 推薦最佳模型（預設行為） |
| `llmfit detect` | 僅檢測並顯示硬體資訊 |
| `llmfit list` | 列出所有支援的模型 |
| `llmfit recommend` | 根據硬體配置推薦模型 |
| `llmfit compare <m1> <m2>` | 對比兩個模型的硬體適配情況 |
| `llmfit info <model_name>` | 查看指定模型的詳細資訊 |

### 全域參數

| 參數 | 縮寫 | 說明 | 預設值 |
|------|------|------|--------|
| `--format` | `-f` | 輸出格式：`table` / `json` / `markdown` | `table` |
| `--no-color` | | 停用彩色終端輸出 | 關閉 |
| `--version` | `-v` | 顯示版本號 | - |

### detect - 硬體檢測

檢測並展示當前系統的完整硬體配置資訊。

```bash
llmfit detect
```

輸出內容包括：CPU 型號與核心數、系統記憶體、GPU 型號與顯存、作業系統、磁碟可用空間、Python 版本，以及基於硬體的模型適配建議。

### list - 模型列表

列出資料庫中所有支援的 LLM 模型。

```bash
# 列出所有模型
llmfit list

# 按模型系列過濾
llmfit list --family Qwen

# JSON 格式輸出
llmfit list --format json
```

### recommend - 智慧推薦

根據當前硬體配置，智慧推薦最適合的模型。

```bash
# 推薦前 10 個模型（預設）
llmfit recommend

# 推薦前 5 個模型
llmfit recommend --top 5

# 按標籤過濾（支援多次使用，為 AND 關係）
llmfit recommend --tag coding
llmfit recommend --tag coding --tag chinese

# 設定最小參數量（單位：十億）
llmfit recommend --min-params 7

# 設定最大參數量
llmfit recommend --max-params 15

# 設定最小上下文長度
llmfit recommend --min-context 32768

# 指定輸出格式
llmfit recommend --format json
llmfit recommend --format markdown
```

**recommend 參數一覽：**

| 參數 | 縮寫 | 說明 | 預設值 |
|------|------|------|--------|
| `--top` | `-n` | 推薦數量 | 10 |
| `--tag` | `-t` | 按標籤過濾（可多次使用） | 無 |
| `--min-params` | | 最小參數量（十億） | 無 |
| `--max-params` | | 最大參數量（十億） | 無 |
| `--min-context` | | 最小上下文長度 | 無 |

### compare - 模型對比

並排對比兩個模型在當前硬體上的適配情況。

```bash
llmfit compare "Llama 3.1 8B" "Qwen 2.5 7B"
```

對比結果包含：參數量、推薦量化格式、上下文長度、基準分數、各維度評分、記憶體使用、預估推理速度等。

### info - 模型詳情

查看指定模型的完整資訊。

```bash
llmfit info "Llama 3.1 8B"
```

輸出包括：模型描述、參數量、上下文長度、開源協議、發布日期、基準分數、各量化格式的 VRAM/RAM 需求、能力標籤等。

### 典型使用場景

```bash
# 場景一：新手一鍵上手 —— 檢測硬體並獲得最佳推薦
llmfit

# 場景二：開發者選型 —— 找到最適合程式設計的模型
llmfit recommend --tag coding --top 5

# 場景三：資源受限環境 —— 在 8GB 顯存顯卡上找最佳模型
llmfit recommend --max-params 8

# 場景四：長文本處理 —— 需要超長上下文支援
llmfit recommend --min-context 131072

# 場景五：模型選型糾結 —— 對比兩個候選模型
llmfit compare "Qwen 2.5 14B" "Mistral Nemo 12B"

# 場景六：自動化整合 —— JSON 格式輸出供腳本處理
llmfit recommend --top 3 --format json
```

---

## 💡 設計思路與迭代規劃

### 設計理念

LLMFit 的核心設計理念是 **「讓本地 LLM 部署的選型決策變得簡單」**。我們相信，降低使用者從「想用 LLM」到「成功運行 LLM」之間的門檻，是推動本地 LLM 普及的關鍵一步。

### 技術選型原因

| 決策 | 原因 |
|------|------|
| **純 Python 標準函式庫** | 最大化降低安裝門檻，避免依賴衝突，確保在任何 Python 環境中都能運行 |
| **CLI 工具形態** | 面向開發者和技術使用者，CLI 是最高效的互動方式，也便於整合到自動化流程中 |
| **內建離線資料庫** | 模型資料內建在程式碼中，無需連網，啟動即用，隱私友善 |
| **多維度加權評分** | 單一指標無法全面反映適配度，加權評分能更準確地匹配使用者需求 |
| **ANSI 彩色輸出** | 終端環境下的資訊可讀性遠高於純文本，顏色編碼幫助使用者快速定位關鍵資訊 |

### 評分體系

LLMFit 採用四維加權評分體系：

| 維度 | 權重 | 說明 |
|------|------|------|
| 硬體匹配度 | 40% | 評估模型在各量化級別下是否能裝入 VRAM/RAM，以及資源利用率 |
| 效能表現 | 30% | 綜合參數量、量化級別、GPU 加速和 CPU 核心數評估推理速度 |
| 模型品質 | 20% | 基於基準測試分數和模型參數量評估輸出品質 |
| 功能豐富度 | 10% | 評估上下文長度、多語言支援、特殊能力（視覺、工具呼叫等） |

### 後續規劃

- [ ] 支援自訂模型資料庫（使用者可新增自己的模型資料）
- [ ] 增加 GPU 推理框架檢測（llama.cpp、Ollama、vLLM 等）
- [ ] 提供互動式 TUI 介面
- [ ] 支援模型下載連結和一鍵下載
- [ ] 增加歷史評分記錄和硬體升級後的對比功能
- [ ] 支援更多 GPU 廠商（Intel Arc 等）
- [ ] 提供 Web 版本

---

## 📦 打包與部署指南

### 透過 pip 安裝（推薦使用者）

```bash
pip install llmfit
```

### 從原始碼安裝

```bash
# 複製倉庫
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit

# 安裝
pip install .
```

### 開發模式安裝

如果你希望參與開發，建議使用可編輯模式安裝：

```bash
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit
pip install -e .

# 安裝開發依賴（可選）
pip install -e ".[dev]"
```

開發依賴包括：black（程式碼格式化）、ruff（程式碼檢查）、isort（匯入排序）、pytest（單元測試）。

### 執行測試

```bash
pytest
```

---

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！

### 提交 Issue

- 使用清晰的標題描述問題或建議
- 附上執行環境資訊（作業系統、Python 版本、GPU 型號）
- 如果是 Bug，請提供重現步驟和完整錯誤資訊

### 提交 Pull Request

1. Fork 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature-name`
3. 確保程式碼通過測試：`pytest`
4. 確保程式碼風格一致：`black . && ruff check .`
5. 提交變更：`git commit -m "feat: 描述你的改動"`
6. 推送分支：`git push origin feature/your-feature-name`
7. 建立 Pull Request

### Commit 規範

請使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` Bug 修復
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具相關

---

## 📄 開源協議

本專案基於 [MIT License](https://opensource.org/licenses/MIT) 開源。

```
MIT License

Copyright (c) 2024 LLMFit Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="english"></a>

# English

## 🎉 Introduction

LLMFit is a command-line tool designed for users who want to run Large Language Models (LLMs) locally. It addresses a common pain point: **with dozens of open-source models available, which one can my hardware actually run?**

When deploying LLMs locally, users often have to repeatedly consult model documentation, compare VRAM requirements, and estimate quantization effects -- a tedious and error-prone process. LLMFit automates all of this. With a single command, it performs hardware detection, model matching, and intelligent recommendation.

**Core Value:**
- **Time-saving**: No more manual lookups and trial-and-error -- get the best recommendation with one command
- **Accurate**: Built-in detailed hardware requirement data for 25+ mainstream open-source LLMs, with a scoring algorithm covering four dimensions
- **Lightweight**: Pure Python standard library implementation with zero external dependencies -- install and run
- **Intuitive**: Colorful terminal UI with multi-format output, making information clear at a glance

**Key Differentiators:**
- Runs completely offline -- no internet connection needed for detection or recommendations
- Cross-platform support (Windows / macOS / Linux) with automatic detection of NVIDIA, AMD, and Apple Silicon GPUs
- Fine-grained resource evaluation across multiple quantization formats (Q4_K_M / Q5_K_M / Q8_0 / F16)

---

## ✨ Core Features

- 🔍 **Automatic Hardware Detection**: Identify CPU model and core count, GPU model and VRAM, system RAM, and disk space with one command
- 📊 **Intelligent Scoring Engine**: Comprehensive evaluation across four dimensions -- hardware compatibility, performance, model quality, and feature richness
- 🗄️ **Built-in Model Database**: Covers 25+ models including Llama 3.1, Qwen 2.5, Mistral, Phi-3, Gemma 2, DeepSeek, and more
- 🎨 **Colorful Terminal UI**: Intuitive table output with color-coded scores and highlighted key information
- 📋 **Multi-format Output**: Supports table, JSON, and Markdown output formats
- ⚖️ **Model Comparison**: Side-by-side comparison of two models' hardware compatibility
- 🏷️ **Flexible Filtering**: Filter models by tag, parameter count, context length, and more
- 🌐 **Cross-platform**: Full support for Windows, macOS, and Linux with automatic GPU detection
- 📦 **Zero Dependencies**: Built entirely with Python 3.8+ standard library -- just pip install and go
- 🚫 **Fully Offline**: All detection and recommendation happens locally, no internet required

---

## 🚀 Quick Start

### Requirements

- Python 3.8 or later
- Supported OS: Windows, macOS, Linux

### Installation

**Option 1: Install via pip (Recommended)**

```bash
pip install llmfit
```

**Option 2: Install from source**

```bash
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit
pip install -e .
```

### Launch

After installation, simply run in your terminal:

```bash
llmfit
```

On first run, it will automatically detect your hardware configuration and recommend the best-suited model.

---

## 📖 Detailed Usage Guide

### Command Overview

| Command | Description |
|---------|-------------|
| `llmfit` | Display hardware info + recommend the best model (default behavior) |
| `llmfit detect` | Detect and display hardware information only |
| `llmfit list` | List all supported models |
| `llmfit recommend` | Recommend models based on hardware configuration |
| `llmfit compare <m1> <m2>` | Compare two models' hardware compatibility |
| `llmfit info <model_name>` | View detailed information for a specific model |

### Global Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--format` | `-f` | Output format: `table` / `json` / `markdown` | `table` |
| `--no-color` | | Disable colored terminal output | Off |
| `--version` | `-v` | Show version number | - |

### detect - Hardware Detection

Detects and displays your system's complete hardware configuration.

```bash
llmfit detect
```

Output includes: CPU model and core count, system RAM, GPU model and VRAM, operating system, available disk space, Python version, and hardware-based model suitability suggestions.

### list - Model List

Lists all LLM models in the database.

```bash
# List all models
llmfit list

# Filter by model family
llmfit list --family Qwen

# JSON format output
llmfit list --format json
```

### recommend - Smart Recommendations

Recommends the most suitable models based on your current hardware configuration.

```bash
# Recommend top 10 models (default)
llmfit recommend

# Recommend top 5 models
llmfit recommend --top 5

# Filter by tag (can be used multiple times, AND relationship)
llmfit recommend --tag coding
llmfit recommend --tag coding --tag chinese

# Set minimum parameter count (in billions)
llmfit recommend --min-params 7

# Set maximum parameter count
llmfit recommend --max-params 15

# Set minimum context length
llmfit recommend --min-context 32768

# Specify output format
llmfit recommend --format json
llmfit recommend --format markdown
```

**recommend options reference:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--top` | `-n` | Number of recommendations | 10 |
| `--tag` | `-t` | Filter by tag (can be used multiple times) | None |
| `--min-params` | | Minimum parameter count (billions) | None |
| `--max-params` | | Maximum parameter count (billions) | None |
| `--min-context` | | Minimum context length | None |

### compare - Model Comparison

Side-by-side comparison of two models' hardware compatibility.

```bash
llmfit compare "Llama 3.1 8B" "Qwen 2.5 7B"
```

Comparison results include: parameter count, recommended quantization, context length, benchmark scores, per-dimension scores, memory usage, and estimated inference speed.

### info - Model Details

View complete information for a specific model.

```bash
llmfit info "Llama 3.1 8B"
```

Output includes: model description, parameter count, context length, license, release date, benchmark score, VRAM/RAM requirements for each quantization format, and capability tags.

### Common Use Cases

```bash
# Scenario 1: Getting started -- detect hardware and get the best recommendation
llmfit

# Scenario 2: Developer model selection -- find the best model for coding
llmfit recommend --tag coding --top 5

# Scenario 3: Resource-constrained environment -- find the best model for an 8GB VRAM GPU
llmfit recommend --max-params 8

# Scenario 4: Long document processing -- need extended context support
llmfit recommend --min-context 131072

# Scenario 5: Choosing between models -- compare two candidates
llmfit compare "Qwen 2.5 14B" "Mistral Nemo 12B"

# Scenario 6: Automation integration -- JSON output for script processing
llmfit recommend --top 3 --format json
```

---

## 💡 Design Philosophy & Roadmap

### Design Philosophy

LLMFit's core design philosophy is to **"make local LLM deployment model selection simple"**. We believe that lowering the barrier from "wanting to use LLMs" to "successfully running LLMs" is a key step in promoting local LLM adoption.

### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Pure Python standard library** | Minimizes installation barriers, avoids dependency conflicts, and ensures compatibility across all Python environments |
| **CLI tool format** | CLI is the most efficient interaction method for developers and technical users, and integrates easily into automation workflows |
| **Built-in offline database** | Model data is embedded in the code -- no internet required, instant startup, privacy-friendly |
| **Multi-dimensional weighted scoring** | A single metric cannot comprehensively reflect suitability; weighted scoring more accurately matches user needs |
| **ANSI colored output** | Information readability in terminal environments far exceeds plain text; color coding helps users quickly identify key information |

### Scoring System

LLMFit uses a four-dimensional weighted scoring system:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Hardware Compatibility | 40% | Evaluates whether the model fits in VRAM/RAM at each quantization level, and resource utilization |
| Performance | 30% | Estimates inference speed based on parameter count, quantization level, GPU acceleration, and CPU core count |
| Model Quality | 20% | Assesses output quality based on benchmark scores and model parameter count |
| Feature Richness | 10% | Evaluates context length, multilingual support, and special capabilities (vision, tool use, etc.) |

### Roadmap

- [ ] Support custom model databases (users can add their own model data)
- [ ] Add GPU inference framework detection (llama.cpp, Ollama, vLLM, etc.)
- [ ] Provide interactive TUI interface
- [ ] Support model download links and one-click download
- [ ] Add historical scoring records and post-upgrade comparison features
- [ ] Support additional GPU vendors (Intel Arc, etc.)
- [ ] Provide a web version

---

## 📦 Packaging & Deployment

### Install via pip (For Users)

```bash
pip install llmfit
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit

# Install
pip install .
```

### Development Mode Installation

If you want to contribute to the project, we recommend installing in editable mode:

```bash
git clone https://github.com/gitstq/LLMFit.git
cd LLMFit
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

Development dependencies include: black (code formatting), ruff (linting), isort (import sorting), pytest (unit testing).

### Running Tests

```bash
pytest
```

---

## 🤝 Contributing

We welcome and appreciate contributions of all forms!

### Submitting Issues

- Use a clear title to describe the problem or suggestion
- Include your runtime environment (OS, Python version, GPU model)
- For bugs, provide reproduction steps and the complete error message

### Submitting Pull Requests

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Ensure tests pass: `pytest`
4. Ensure code style consistency: `black . && ruff check .`
5. Commit your changes: `git commit -m "feat: describe your changes"`
6. Push the branch: `git push origin feature/your-feature-name`
7. Create a Pull Request

### Commit Convention

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test-related changes
- `chore:` Build/tooling changes

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

```
MIT License

Copyright (c) 2024 LLMFit Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**LLMFit** -- Made with ❤️ by [LLMFit Team](https://github.com/gitstq/LLMFit)

[GitHub](https://github.com/gitstq/LLMFit) | [MIT License](https://opensource.org/licenses/MIT)

</div>
