# NakuNode-Prompter

**NakuNode Promt Generator V1.0 Dev ------------------A professional promts generator for WAN / Qwen / Flux**

A comprehensive ComfyUI node pack that integrates multiple prompt generation and guidance systems for AI image and video generation.

## Features

- **Video Prompt Generation** - Professional video prompt generator with LLM polishing capabilities
- **Advanced Guidance** - Normalized Attention Guidance (NAG) and Noise Added Guidance methods
- **Comprehensive Prompting** - Extensive parameterized prompt generation with portrait, photography, and scene controls

## Included Nodes

### Video Prompt Generator
- Professional video prompt generation with multiple categories (art styles, camera angles, lighting, etc.)
- LLM integration for prompt polishing with service providers

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

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place this folder in your ComfyUI `custom_nodes` directory.

3. Restart ComfyUI.

## Usage

The nodes will appear in ComfyUI under the "NakuNode" category.