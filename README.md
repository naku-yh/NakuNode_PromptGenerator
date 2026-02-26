# NakuNode-Prompter

**NakuNode Prompt Generator V1.16 Dev**
**A professional prompt generator for WAN / Qwen / Flux / LTX**

A comprehensive ComfyUI node pack that integrates multiple prompt generation and guidance systems for AI image and video generation.

## Features

- **Advanced Prompt Generation** - Professional prompt generation with AI-powered enhancement
- **API Integration** - Support for SiliconFlow and Custom API services
- **Comprehensive Parameter Controls** - Extensive parameterized prompt generation with portrait, photography, environment, and scene controls
- **Advanced Guidance** - Normalized Attention Guidance (NAG) and Noise Added Guidance methods
- **Multi-Modal Support** - Support for image-based prompt generation and optimization
- **LTX Video Optimization** - Specialized prompt engineering for LTX Video model
- **Storyboard Generation** - Multi-image storyboard prompt generation with Hollywood cinematography grammar

## Included Nodes

### Advanced Prompt Generators
- **NakuNode-PromptEVO** - Advanced prompt generator with AI model selection (Qwen/Zimage, Flux.2) and API integration
  - Supports SiliconFlow and Custom API services
  - Comprehensive character controls (nationality, gender, age, body type, clothing, expressions, hairstyles, hair colors)
  - Photography parameters (camera angles, lenses, film types, color palettes, compositions)
  - Detailed debugging information

### Video Prompt Generators
- **NakuNode 专业视频提示词润色器** - Professional video prompt polisher with multiple categories (art styles, camera angles, lighting, etc.)
- **NakuNode-单图视频提示词生成器** - Generate video prompts from single image with LLM optimization
- **NakuNode-首尾帧视频提示词生成器** - Generate video scripts from start/end frame images

### Storyboard Generator
- **NakuNode 分镜图片生成** - Multi-image storyboard generator with Hollywood cinematography grammar
  - Supports up to 6 reference images
  - Universal Fluid Structure for camera movement (9 lens templates)
  - Special handling for single-image and multi-image scenarios
  - Compact output format with zero blank lines

### LTX Video Prompt Generator
- **NakuNode-LTXPrompter** - Specialized prompt generator for LTX Video model (Text-to-Video / Image-to-Video)
  - Optimized for LTX Video's DiT architecture and T5 text encoder
  - Focuses on temporal continuity and physical interactions
  - Uses professional cinematography terminology
  - Generates flowing English paragraphs instead of tag lists

- **NakuNode LTX FTE Prompter** - LTX First-and-Tail-End prompt generator
  - Generate LTX prompts from first and last frame images
  - Supports video duration setting (1-20 seconds)
  - Audio-video synchronization support

### Guidance Systems
- NakuNode NAG Applier (Attention) - Normalized Attention Guidance
- NakuNode Noise Guider (Original Nunchaku) - Noise Added Guidance

### Design Prompt Tools (NakuNode_Design_Prompt)
- **NakuNode_人设设计** - Comprehensive human characteristic controls
  - 16 parameter categories: nationality, skin color, gender, age, body type, clothing, face shape, eye type, eye color, expression, nose type, lip shape, hairstyle, hair color, skin texture
  - Random option for each category
- **NakuNode_摄影参数** - Camera, lens, film, and composition controls
  - 6 parameter categories: style, camera angle, lens, aperture, film type, composition
  - Random option for each category
- **NakuNode_场景设计** - Environment scene presets
  - 2 categories: Outdoor Scenes (52 options), Indoor Scenes (62 options)
  - Random option for each category

### Video Prompt Tools
- **NakuNode 专业视频提示词生成器** - Generate video prompts using professional options (art styles, camera angles, lighting, etc.)
- **NakuNode-单图视频提示词优化器** - Optimize video prompts based on input images

### Utility Nodes
- **NakuNode-文本修改节点** - Text editing utility for modifying prompts
- **NakuNode-ImagePrompter** - Image-based prompt generation with AI services
  - Supports SiliconFlow and Custom API
  - Generates objective image descriptions with structured format

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Note: Make sure to install additional dependencies for API services:
   ```bash
   pip install openai requests pillow
   ```

2. Place this folder in your ComfyUI `custom_nodes` directory.

3. Restart ComfyUI.

## Usage

The nodes will appear in ComfyUI under the "NakuNode" category.

### Using NakuNode-PromptEVO
1. Select your preferred AI model (Qwen/Zimage or Flux.2)
2. Choose API provider (SiliconFlow or Custom) and provide API key
3. Fill in your text requirements
4. Adjust character and photography parameters as needed
5. The node will generate enhanced prompts using AI services

### Using NakuNode 分镜图片生成
1. Connect 1-6 reference images
2. Fill in storyboard description
3. Set storyboard count (1-12)
4. Choose API provider and provide API key
5. The node will generate continuous storyboard prompts with Hollywood cinematography grammar

## API Configuration

### SiliconFlow
- Register at https://siliconflow.cn/
- Obtain your API key
- Select SiliconFlow as the API provider in the node
- Choose model: QWENVL (Qwen3-VL-30B), GLM (GLM-4.6V), or KIMI (Kimi-K2.5)
- Uses streaming mode for API requests

### Custom API
- For custom API endpoints compatible with OpenAI format
- Provide your custom URL (default: https://api.siliconflow.cn/v1)
- Choose model: gpt_5.2, gemini_3.1, Qwen_3.5, or Kimi_2.5
- Uses non-streaming mode for API requests

## Version History
- **V1.16 Dev**: 
  - Added NakuNode_场景设计 (Environment Design) with 114 scene presets (52 outdoor + 62 indoor)
  - Updated NakuNode_ImagePrompter with SiliconFlow/Custom API support and streaming mode
  - Fixed API URL logic for SiliconFlow (now uses correct https://api.siliconflow.cn/v1/chat/completions)
  - Added streaming mode support for SiliconFlow API (all nodes)
  - Removed Zhipu AI support, replaced with Custom API option
  - All node parameters converted to English (internal system prompts unchanged)
  - Added comprehensive debug output with [NakuNode] prefix
- **V1.15 Dev**: Updated API input image size limit to 1920px (longest edge)
- **V1.10 Dev**: Updated version to 1.10 Dev
- **V1.09 Dev**: Added NakuNode-LTXPrompter for LTX Video model with specialized prompt engineering
- **V1.08 Dev**: Updated QwenEdit model prompt with advanced focus relay mechanism and fluid structure
- **V1.05 Dev**: Added comprehensive character controls, API integration, and debugging features
- **V1.0 Dev**: Initial release with basic prompt generation and guidance systems
