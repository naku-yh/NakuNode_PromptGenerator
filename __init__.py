# NakuNode-Prompter for ComfyUI
# Integration of multiple prompt generation and guidance systems

import os
import json

# 汉化支持 - 加载语言文件
def load_translation(lang='zh'):
    """加载翻译文件"""
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales', lang)
    if not os.path.exists(locales_dir):
        return {}
    
    translations = {}
    try:
        # 加载 nodeDefs.json
        nodeDefs_path = os.path.join(locales_dir, 'nodeDefs.json')
        if os.path.exists(nodeDefs_path):
            with open(nodeDefs_path, 'r', encoding='utf-8') as f:
                translations['nodeDefs'] = json.load(f)
        
        # 加载 main.json
        main_path = os.path.join(locales_dir, 'main.json')
        if os.path.exists(main_path):
            with open(main_path, 'r', encoding='utf-8') as f:
                translations['main'] = json.load(f)
    except Exception as e:
        print(f"[NakuNode-Prompter] Warning: Failed to load translation for {lang}: {e}")
    
    return translations

# 应用翻译到节点显示名称
def apply_translations(translations):
    """应用翻译到节点显示名称"""
    if 'nodeDefs' not in translations:
        return
    
    for node_class, node_data in translations['nodeDefs'].items():
        if node_class in NODE_DISPLAY_NAME_MAPPINGS:
            if 'display_name' in node_data:
                # 更新显示名称
                NODE_DISPLAY_NAME_MAPPINGS[node_class] = node_data['display_name']

# Removed WAN22 nodes
WAN22_NODE_CLASS_MAPPINGS = {}
WAN22_NODE_DISPLAY_NAME_MAPPINGS = {}
WAN22_AVAILABLE = False

try:
    from .nodes.NAKUNode_Flux_QwenEdit_Prompt import NODE_CLASS_MAPPINGS as DESIGN_PROMPT_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as DESIGN_PROMPT_NODE_DISPLAY_NAME_MAPPINGS
    DESIGN_PROMPT_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Design Prompt nodes: {e}")
    DESIGN_PROMPT_NODE_CLASS_MAPPINGS = {}
    DESIGN_PROMPT_NODE_DISPLAY_NAME_MAPPINGS = {}
    DESIGN_PROMPT_AVAILABLE = False

try:
    from .nodes.image_video_prompt_optimizer import NODE_CLASS_MAPPINGS as IMG_OPTIMIZER_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMG_OPTIMIZER_NODE_DISPLAY_NAME_MAPPINGS
    IMG_OPTIMIZER_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Image Video Prompt Optimizer nodes: {e}")
    IMG_OPTIMIZER_NODE_CLASS_MAPPINGS = {}
    IMG_OPTIMIZER_NODE_DISPLAY_NAME_MAPPINGS = {}
    IMG_OPTIMIZER_AVAILABLE = False

try:
    from .nodes.professional_video_prompt_generator import NODE_CLASS_MAPPINGS as PROFESSIONAL_VIDEO_PROMPT_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as PROFESSIONAL_VIDEO_PROMPT_NODE_DISPLAY_NAME_MAPPINGS
    PROFESSIONAL_VIDEO_PROMPT_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Professional Video Prompt Generator nodes: {e}")
    PROFESSIONAL_VIDEO_PROMPT_NODE_CLASS_MAPPINGS = {}
    PROFESSIONAL_VIDEO_PROMPT_NODE_DISPLAY_NAME_MAPPINGS = {}
    PROFESSIONAL_VIDEO_PROMPT_AVAILABLE = False

try:
    from .nodes.dual_image_video_script_generator import NODE_CLASS_MAPPINGS as DUAL_IMAGE_SCRIPT_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as DUAL_IMAGE_SCRIPT_NODE_DISPLAY_NAME_MAPPINGS
    DUAL_IMAGE_SCRIPT_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Dual Image Video Script Generator nodes: {e}")
    DUAL_IMAGE_SCRIPT_NODE_CLASS_MAPPINGS = {}
    DUAL_IMAGE_SCRIPT_NODE_DISPLAY_NAME_MAPPINGS = {}
    DUAL_IMAGE_SCRIPT_AVAILABLE = False

try:
    from .nodes.storyboard_image_generator import NODE_CLASS_MAPPINGS as STORYBOARD_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as STORYBOARD_NODE_DISPLAY_NAME_MAPPINGS
    STORYBOARD_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Storyboard Image Generator nodes: {e}")
    STORYBOARD_NODE_CLASS_MAPPINGS = {}
    STORYBOARD_NODE_DISPLAY_NAME_MAPPINGS = {}
    STORYBOARD_AVAILABLE = False

try:
    from .nodes.NakuNode_TextEditor import NODE_CLASS_MAPPINGS as TEXT_EDITOR_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TEXT_EDITOR_NODE_DISPLAY_NAME_MAPPINGS
    TEXT_EDITOR_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Text Editor nodes: {e}")
    TEXT_EDITOR_NODE_CLASS_MAPPINGS = {}
    TEXT_EDITOR_NODE_DISPLAY_NAME_MAPPINGS = {}
    TEXT_EDITOR_AVAILABLE = False

try:
    from .nodes.NakuNode_ImagePrompter import NODE_CLASS_MAPPINGS as IMAGE_PROMPTER_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS
    IMAGE_PROMPTER_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Image Prompter nodes: {e}")
    IMAGE_PROMPTER_NODE_CLASS_MAPPINGS = {}
    IMAGE_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS = {}
    IMAGE_PROMPTER_AVAILABLE = False

try:
    from .nodes.NakuNode_PromptEVO import NODE_CLASS_MAPPINGS as PROMPT_EVO_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as PROMPT_EVO_NODE_DISPLAY_NAME_MAPPINGS
    PROMPT_EVO_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import PromptEVO nodes: {e}")
    PROMPT_EVO_NODE_CLASS_MAPPINGS = {}
    PROMPT_EVO_NODE_DISPLAY_NAME_MAPPINGS = {}
    PROMPT_EVO_AVAILABLE = False

try:
    from .nodes.NakuNode_LTXPrompter import NODE_CLASS_MAPPINGS as LTX_PROMPTER_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as LTX_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS
    LTX_PROMPTER_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import LTX Prompter nodes: {e}")
    LTX_PROMPTER_NODE_CLASS_MAPPINGS = {}
    LTX_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS = {}
    LTX_PROMPTER_AVAILABLE = False

try:
    from .nodes.NakuNode_LTX_FTE_Prompter import NODE_CLASS_MAPPINGS as LTX_FTE_PROMPTER_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as LTX_FTE_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS
    LTX_FTE_PROMPTER_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import LTX FTE Prompter nodes: {e}")
    LTX_FTE_PROMPTER_NODE_CLASS_MAPPINGS = {}
    LTX_FTE_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS = {}
    LTX_FTE_PROMPTER_AVAILABLE = False

try:
    from .nodes.NakuNode_VideoParameters import NODE_CLASS_MAPPINGS as VIDEO_PARAMS_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as VIDEO_PARAMS_NODE_DISPLAY_NAME_MAPPINGS
    VIDEO_PARAMS_AVAILABLE = True
except ImportError as e:
    print(f"[NakuNode-Prompter] Warning: Could not import Video Parameters nodes: {e}")
    VIDEO_PARAMS_NODE_CLASS_MAPPINGS = {}
    VIDEO_PARAMS_NODE_DISPLAY_NAME_MAPPINGS = {}
    VIDEO_PARAMS_AVAILABLE = False

# Combine all node mappings
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(WAN22_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(DESIGN_PROMPT_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(IMG_OPTIMIZER_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(PROFESSIONAL_VIDEO_PROMPT_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(DUAL_IMAGE_SCRIPT_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(STORYBOARD_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(TEXT_EDITOR_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(IMAGE_PROMPTER_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(PROMPT_EVO_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(LTX_PROMPTER_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(LTX_FTE_PROMPTER_NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(VIDEO_PARAMS_NODE_CLASS_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(WAN22_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DESIGN_PROMPT_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(IMG_OPTIMIZER_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(PROFESSIONAL_VIDEO_PROMPT_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DUAL_IMAGE_SCRIPT_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(STORYBOARD_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_EDITOR_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(PROMPT_EVO_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(LTX_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(LTX_FTE_PROMPTER_NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(VIDEO_PARAMS_NODE_DISPLAY_NAME_MAPPINGS)

WEB_DIRECTORY = "web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

# 加载并应用中文翻译
try:
    zh_translations = load_translation('zh')
    if zh_translations:
        apply_translations(zh_translations)
        print("[NakuNode-Prompter] Chinese translation loaded successfully")
except Exception as e:
    print(f"[NakuNode-Prompter] Warning: Failed to apply Chinese translation: {e}")

# Print version and capability information
print("NakuNode Prompt Generator V1.16 Dev -- A professional prompt generator for WAN / Qwen / Flux / LTX")

# Print summary of available nodes
print(f"[NakuNode-Prompter] Loaded {len(NODE_CLASS_MAPPINGS)} total nodes")
if DESIGN_PROMPT_AVAILABLE:
    print(f"[NakuNode-Prompter] Design Prompt nodes available: {list(DESIGN_PROMPT_NODE_CLASS_MAPPINGS.keys())}")
if STORYBOARD_AVAILABLE:
    print(f"[NakuNode-Prompter] Storyboard nodes available: {list(STORYBOARD_NODE_CLASS_MAPPINGS.keys())}")
if TEXT_EDITOR_AVAILABLE:
    print(f"[NakuNode-Prompter] Text Editor nodes available: {list(TEXT_EDITOR_NODE_CLASS_MAPPINGS.keys())}")
if IMAGE_PROMPTER_AVAILABLE:
    print(f"[NakuNode-Prompter] Image Prompter nodes available: {list(IMAGE_PROMPTER_NODE_CLASS_MAPPINGS.keys())}")
if PROMPT_EVO_AVAILABLE:
    print(f"[NakuNode-Prompter] PromptEVO nodes available: {list(PROMPT_EVO_NODE_CLASS_MAPPINGS.keys())}")
if LTX_PROMPTER_AVAILABLE:
    print(f"[NakuNode-Prompter] LTX Prompter nodes available: {list(LTX_PROMPTER_NODE_CLASS_MAPPINGS.keys())}")
if LTX_FTE_PROMPTER_AVAILABLE:
    print(f"[NakuNode-Prompter] LTX FTE Prompter nodes available: {list(LTX_FTE_PROMPTER_NODE_CLASS_MAPPINGS.keys())}")
if VIDEO_PARAMS_AVAILABLE:
    print(f"[NakuNode-Prompter] Video Parameters nodes available: {list(VIDEO_PARAMS_NODE_CLASS_MAPPINGS.keys())}")