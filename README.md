# NakuNode Prompter V1.0

<div align="center">

**专业的 AI 提示词生成工具 | Professional AI Prompt Generation Tool for ComfyUI**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/naku-yh/NakuNode_PromptGenerator)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-green)](https://github.com/comfyanonymous/ComfyUI)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

</div>

---

## 📖 简介 | Introduction

**NakuNode Prompter** 是一款专为 ComfyUI 设计的专业提示词生成工具集，集成了多种 AI 提示词生成和优化功能。支持 SiliconFlow 和 Custom API 服务，可生成高质量的文生图、视频生成提示词。

**NakuNode Prompter** is a professional prompt generation toolset designed for ComfyUI, integrating multiple AI prompt generation and optimization features. Supports SiliconFlow and Custom API services for generating high-quality text-to-image and video generation prompts.

### ✨ 主要特性 | Key Features

- 🎨 **多模态提示词生成** - 支持文生图、图生视频等多种生成模式
- 🎬 **专业视频提示词** - 专为 LTX Video 等视频模型优化的提示词生成
- 🤖 **AI 智能优化** - 集成 SiliconFlow/Custom API，智能润色提示词
- 🌐 **双语支持** - 完整的中英文界面和提示词输出
- 🎯 **可视化构建器** - 通过前端界面快速构建专业提示词
- 📸 **多图参考** - 支持单图、双图、多图等多种参考模式
- 🔑 **API KEY分离存储** - API KEY本地加密存储，避免分享工作流导致API KEY的外泄

---

## 📦 节点列表 | Node List

### 🎨 提示词生成节点 | Prompt Generation Nodes

#### 1. NakuNode-提示词进化器 | NakuNode-PromptEVO
**功能**: 图片提示词优化，支持 Qwen/Zimage 和 Flux.2 模型  
**Function**: Advanced text prompt generator supporting Qwen/Zimage and Flux.2 models

- 支持 SiliconFlow 和 Custom API 服务
-  comprehensive 人物和摄影参数控制
- 详细的调试信息输出

#### 2. NakuNode-单图视频提示词生成器 | ImageVideoPromptOptimizer
**功能**: 基于单张图片生成专业的视频提示词 For Wan2.2  
**Function**: Generate professional video prompts from a single image

- 自动图像缩放,无需额外增加图片缩放节点，保持图片清晰且不会过大
- SiliconFlow/Custom API 集成
- 输出中英文双语提示词

#### 3. NakuNode-首尾帧视频提示词生成器 | DualImageVideoScriptGenerator
**功能**: 基于首尾两张图片生成连贯的视频画面生成  
**Function**: Generate coherent video storyboards from start and end frames

- 可自定义视频时长（1-60 秒）
- 专业的分镜画面生成

#### 4. NakuNode-专业视频提示词润色器 | ProfessionalVideoPromptGenerator
**功能**: 专业的视频提示词润色工具  
**Function**: Professional video prompt polishing tool

- 生成中文和英文两个版本
- 基于通义万相视频提示词公式
- 支持 SiliconFlow/Custom API

### 🎬 LTX Video 专用节点 | LTX Video Specialized Nodes

#### 5. NakuNode-LTX 视频提示词生成器 | NakuNode-LTXPrompter
**功能**: 专为 LTX Video 模型设计的提示词生成器  
**Function**: Prompt generator designed for LTX Video model

- 支持文生视频和图生视频两种模式
- 音视频同步提示词生成
- 视频时长 1-20 秒可调

#### 6. NakuNode-LTX 首尾帧提示词生成器 | NakuNode-LTX_FTE_Prompter
**功能**: 基于首尾帧图片生成 LTX Video 专用提示词  
**Function**: Generate LTX Video prompts from first and last frame images

- 音视频同步生成支持
- 专业的 LTX-2 系统提示词
- 支持 VideoPrompt.js 前端构建

### 🖼️ 分镜与描述节点 | Storyboard & Description Nodes

#### 7. NakuNode-分镜图片生成器 | StoryboardImageGenerator
**功能**: 多图片分镜脚本生成器  
**Function**: Multi-image storyboard script generator

- 支持最多 6 张参考图片
- 好莱坞电影语法体系
- 紧凑输出格式（零空行）

#### 8. NakuNode-图片描述生成器 | NakuNode-ImagePrompter
**功能**: 基于图片生成客观的描述提示词  
**Function**: Generate objective description prompts from images

- 支持 SiliconFlow 和 Custom API
- 结构化输出格式

#### 9. NakuNode-视频参数 | NakuNode_VideoParameters
**功能**: 视频制作参数设计节点  
**Function**: Video production parameter design node

- 运镜方式选择
- 光线描述选择
- 视觉与后期效果选择

---

## 🔧 安装 | Installation

### 方法： | Method : 

```bash
# 进入 ComfyUI 自定义节点目录
cd ComfyUI/custom_nodes/

# 克隆仓库
git clone https://github.com/naku-yh/NakuNode_PromptGenerator.git

# 安装依赖
cd NakuNode_PromptGenerator
pip install -r requirements.txt
```

---

## 📖 使用指南 | Usage Guide

### 基础使用 | Basic Usage

1. **添加节点**: 在 ComfyUI 中右键 → NakuNode → 选择所需节点
2. **配置 API**: 填写 SiliconFlow API Key 或 Custom API 配置
3. **输入描述**: 在文本框中输入您的生成需求
4. **生成提示词**: 执行节点获取 AI 优化的提示词

**使用方法**:
1. 点击节点上的 **"Create it!"** 按钮
2. 在弹出的构建器界面中选择参数：
   - 📷 摄影参数（画面风格、相机视角、镜头选择等）
   - 🎬 视频参数（运镜方式、光线描述、视觉效果等）
3. 点击"确认"，生成的提示词将自动填充到节点输入框

### API 配置 | API Configuration

#### SiliconFlow 配置
1. 访问 https://siliconflow.cn/ 注册账号
2. 获取 API Key
3. 在节点中选择 "SiliconFlow" 作为 API 提供商
4. 填写 API Key 并选择模型

#### Custom API 配置
1. 选择 "Custom" 作为 API 提供商
2. 填写自定义 API 地址
3. 填写自定义 API Key
4. 选择对应的模型

---

## 📋 节点参数说明 | Node Parameters

### 通用参数 | Common Parameters

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `api_provider` | API 提供商选择 | SiliconFlow |
| `random_seed` | 随机种子（-1 为随机） | -1 |
| `SiliconFlow_API_KEY` | SiliconFlow API 密钥 | - |
| `User_API_KEY` | 自定义 API 密钥 | - |
| `custom_url` | 自定义 API 地址 | - |

### 模型选项 | Model Options

#### SiliconFlow 模型
- `KIMI-K2` - Moonshot AI Kimi K2
- `Qwen3` - Qwen3-235B-A22B-Instruct
- `DeepSeekV3` - DeepSeek V3.2
- `GLM` - GLM-4.7
- `KIMI` - Kimi K2.5

#### Custom API 模型
- `gpt_5.2` - GPT-5.2
- `gemini_3.1` - Gemini 3.1 Pro
- `Qwen_3.5` - Qwen3.5 Plus
- `Kimi_2.5` - Kimi K2.5

---

## 🎯 应用场景 | Use Cases

### 📸 人像摄影提示词生成
使用 **NakuNode-提示词进化器**，通过人物设计和摄影参数快速生成专业人像摄影提示词。

### 🎬 视频制作提示词
使用 **NakuNode-单图/首尾帧视频提示词生成器**，基于参考图片生成专业的视频拍摄脚本。

### 🤖 LTX Video 视频生成
使用 **NakuNode-LTX 系列节点**，生成符合 LTX Video 模型要求的音视频同步提示词。

### 📝 提示词润色优化
使用 **NakuNode-专业视频提示词润色器**，将简单的描述润色为专业的提示词。

---

## 🔗 链接 | Links

- **GitHub 仓库**: https://github.com/naku-yh/NakuNode_PromptGenerator
- **ComfyUI**: https://github.com/comfyanonymous/ComfyUI
- **SiliconFlow**: https://siliconflow.cn/

---

## 📝 更新日志 | Changelog

### V。1 - API KEY分离加密存储机制 ｜ 0228
### V1.0 - 初始版本 | Initial Release

---

## 📄 许可证 | License

MIT License

---

## 🙏 致谢 | Acknowledgments

感谢以下项目和团队：
- ComfyUI 团队

---

<div align="center">

**NakuNode Prompter V1.0**

Made with ❤️ by Naku

[返回顶部](#nakunode-prompter-v10)

</div>
