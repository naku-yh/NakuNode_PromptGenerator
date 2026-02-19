# NakuNode-Prompter

**NakuNode Promt Generator V1.15 Dev
A professional promts generator for WAN / Qwen / Flux / LTX**

A comprehensive ComfyUI node pack that integrates multiple prompt generation and guidance systems for AI image and video generation.

## Features

- **Advanced Prompt Generation** - Professional prompt generation with AI-powered enhancement
- **API Integration** - Support for SiliconFlow and Zhipu AI services
- **Comprehensive Parameter Controls** - Extensive parameterized prompt generation with portrait, photography, and scene controls
- **Advanced Guidance** - Normalized Attention Guidance (NAG) and Noise Added Guidance methods
- **Multi-Modal Support** - Support for image-based prompt generation and optimization
- **LTX Video Optimization** - Specialized prompt engineering for LTX Video model

## Included Nodes

### Advanced Prompt Generators
- **NakuNode-PromptEVO** - Advanced prompt generator with AI model selection (Qwen/Zimage, Flux.2) and API integration
  - Supports SiliconFlow and Zhipu AI services
  - Comprehensive character controls (nationality, gender, age, body type, clothing, expressions, hairstyles, hair colors)
  - Photography parameters (camera angles, lenses, film types, color palettes, compositions)
  - Detailed debugging information

### Video Prompt Generator
- Professional video prompt generation with multiple categories (art styles, camera angles, lighting, etc.)
- LLM integration for prompt polishing with service providers

### LTX Video Prompt Generator
- **NakuNode-LTXPrompter** - Specialized prompt generator for LTX Video model
  - Optimized for LTX Video's DiT architecture and T5 text encoder
  - Focuses on temporal continuity and physical interactions
  - Uses professional cinematography terminology
  - Generates flowing English paragraphs instead of tag lists

### Guidance Systems
- NakuNode NAG Applier (Attention) - Normalized Attention Guidance
- NakuNode Noise Guider (Original Nunchaku) - Noise Added Guidance

### Prompt Generation
- NakuNode Kontext Prompt Generator - Advanced AI-assisted prompt generation
- NakuNode 人像参数 - Comprehensive human characteristic controls
- NakuNode 专业摄影参数 - Camera, lens, film, and composition controls
- NakuNode 遾具预设 - Pre-defined object prompts

### Video Prompt Tools
- NakuNode 专业视频提示词生成器 - Generate video prompts using professional options (art styles, camera angles, lighting, etc.)
- NakuNode-单图视频提示词优化器 - Optimize video prompts based on input images

### Utility Nodes
- NakuNode-文本修改节点 - Text editing utility for modifying prompts
- NakuNode-ImagePrompter - Image-based prompt generation with AI services

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Note: Make sure to install additional dependencies for API services:
   ```bash
   pip install openai zhipuai
   ```

2. Place this folder in your ComfyUI `custom_nodes` directory.

3. Restart ComfyUI.

## Usage

The nodes will appear in ComfyUI under the "NakuNode" category.

### Using NakuNode-PromptEVO
1. Select your preferred AI model (Qwen/Zimage or Flux.2)
2. Choose API provider (SiliconFlow or Zhipu) and provide API key
3. Fill in your text requirements
4. Adjust character and photography parameters as needed
5. The node will generate enhanced prompts using AI services

## API Configuration

### SiliconFlow
- Register at https://siliconflow.cn/
- Obtain your API key
- Select SiliconFlow as the API provider in the node

### Zhipu AI
- Register at https://www.zhipuai.cn/
- Obtain your API key
- Select Zhipu as the API provider in the node

## Version History
- V1.15 Dev: Updated API input image size limit to 1920px (longest edge)
- V1.10 Dev: Updated version to 1.10 Dev
- V1.09 Dev: Added NakuNode-LTXPrompter for LTX Video model with specialized prompt engineering
- V1.08 Dev: Updated QwenEdit model prompt with advanced focus relay mechanism and fluid structure
- V1.05 Dev: Added comprehensive character controls, API integration, and debugging features
- V1.0 Dev: Initial release with basic prompt generation and guidance systems
