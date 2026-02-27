# -*- coding: utf-8 -*-
"""
NakuNode - Dual Image Video Script Generator
Modified to match PromptEVO API logic (SiliconFlow/Custom)
Note: Original system prompt and dual image inputs are preserved
PRO_OPTIONS removed - now using VideoPrompt.js frontend
Added VideoDuration_count input for dynamic video duration
Added API String support for encrypted API key storage
"""
import random
import json
import time
from PIL import Image
import io
import base64
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None

# Import API utils
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from api_utils import get_api_credentials, parse_api_string_for_node


class DualImageVideoScriptGenerator:
    """
    双图视频脚本生成器 - 基于两张图片生成专业的视频分镜脚本
    Modified to use SiliconFlow/Custom API providers (same as PromptEVO)
    Note: PRO_OPTIONS removed, use VideoPrompt.js frontend instead
    Added VideoDuration_count for dynamic video duration control
    """

    @classmethod
    def INPUT_TYPES(s):
        inputs = {
            "required": {
                "起始图片": ("IMAGE", {}),
                "结束图片": ("IMAGE", {}),
                "用户描述": ("STRING", {"multiline": True, "default": "根据两张图片生成一段连贯的视频分镜脚本"}),
                "VideoDuration_count": ("INT", {"default": 5, "min": 1, "max": 60}),
            },
            "optional": {
                "api_provider": (["SiliconFlow", "Custom"], {"default": "SiliconFlow"}),
                "siliconflow_model": (["QWEN3VL", "GLM4.6V", "KIMI2.5"], {"default": "QWEN3VL"}),
                "custom_model": (["GPT5.2", "Gemini Pro 3.1", "Gemini Pro 3", "Claude Opus 4.6", "Kimi 2.5"], {"default": "GPT5.2"}),
                "api_string": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "连接 API Setting 节点"
                }),
                "random_seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")  # AI 改写提示词，初始提示词
    RETURN_NAMES = ("AI 改写提示词", "初始提示词")
    FUNCTION = "generate_script"
    CATEGORY = "NakuNode/提示词生成"

    def tensor_to_base64(self, image_tensor):
        """将张量转换为 base64 编码的图片 - Same as ImageVideoPromptOptimizer"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode DualImageScriptGen] Warning: numpy is not installed.")
            return None

        # 转换张量到 numpy 数组并确保值在正确范围内
        i = 255. * image_tensor.cpu().numpy()
        img_array = np.clip(i, 0, 255).astype(np.uint8)

        # 如果是批次图片，选择第一个
        if len(img_array.shape) == 4:
            img_array = img_array[0]

        # 如果有通道维度，确保顺序正确
        if img_array.shape[-1] == 3 or img_array.shape[-1] == 4:  # RGB or RGBA
            img = Image.fromarray(img_array)
        elif img_array.shape[0] == 3 or img_array.shape[0] == 4:  # Channel-first format
            img = Image.fromarray(np.transpose(img_array, (1, 2, 0)))
        else:
            img = Image.fromarray(img_array)

        # 调整图片大小以避免 API 错误 - Same as ImageVideoPromptOptimizer (2560px max)
        MAX_DIMENSION = 2560
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = MAX_DIMENSION
                new_height = int(MAX_DIMENSION / aspect_ratio)
            else:
                new_height = MAX_DIMENSION
                new_width = int(MAX_DIMENSION * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[NakuNode DualImageScriptGen] Image resized to {img.width}x{img.height} using Lanczos resampling.")

        # 将图片保存到内存中的缓冲区
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    def clean_special_markers(self, text):
        """清理文本中的特殊标记"""
        import re

        # 定义要移除的特殊标记模式
        patterns = [
            r'<\|begin_of_box\|>.*?<\|end_of_box\|>',  # 移除 begin_of_box 到 end_of_box 的内容
            r'<\|.*?\|>',  # 移除所有 <|...|> 格式的标记
            r'<box>.*?</box>',  # 移除 <box>...</box> 格式的内容
            r'<.*?>',  # 移除所有 HTML/XML 风格的标签
        ]

        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL)

        # 清理多余的空白字符
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # 移除多余的空行
        cleaned_text = cleaned_text.strip()

        return cleaned_text

    def get_system_prompt(self, video_duration=5):
        """Get the system prompt with video duration - Updated version"""
        return f"""你是一位专业视频导演，参考输入的首尾帧图片生成一段完整的视频生成 Prompt，不要废话，以自然语言呈现，不要表格形式。根据用户输入的提示词或者脚本描述，以及要求的视频时长，输出一段完整的首尾帧视频生成 Prompt。这段视频是通过分析首帧（Image1）和尾帧（Image2）两张图片判断其内在逻辑，联系，生成一段连贯的，有逻辑的，专业的视频生成提示词。在创作时，需要严格按照如下需求：
1、分析两张图片，起始图和结尾图的差异，如两个图片差异较小，请专注于动态细节的表示，让动作更佳自然的变换，如两个图片差异较大，比如场景改变等，用明确的详细的运镜方式让整个画面的衔接更流畅。
2、描述时候不要废话，用户要求的时长为{video_duration}秒，需要在逻辑范围内视频可以表现出该时长的镜头，避免描述过于抽象，请明确场景内主角，环境，场景，特效等变化
3、核心描述需要同时参考图像和用户输入的提示词，描述图像间的合理变化，镜头的合理变化，环境的合理变化，特效的合理变化，场景的变化，动作的变化，服装的变化等等
4、如果有主体，比如是人物，动物，角色等，核心的动作变化应该以主体的变化为主，需要详细描述
5、如果有必要可以附加以下内容作为辅助，最重要的是第三条
描述光源：
光源类型：日光、人工光、月光、实用光、火光、荧光、阴天光、混合光、晴天光等
光线类型：可以描述为柔光、硬光、顶光、侧光、背光、底光、边缘光、剪影、低对比度、高对比度
时间段：白天、夜晚、黄昏、日落、黎明、日出。
描述景别：
景别类型：微距特写、特写、近景、中景，中近景、中全景、全景、广角
描述构图：
描述构图类型：中心构图、平衡构图、侧重构图、对称构图、短边构图
描述镜头：
镜头描述 - 镜头尺寸：标准焦距、中焦距、广角、长焦、望远、超广角 - 鱼眼等
镜头描述 - 镜头角度：过肩角度、高角度、低角度、平视角度、倾斜角度、航拍、俯视角度、贴地角度等
镜头描述 - 镜头类型：单人镜头、双人镜头、三人镜头、群像镜头、定场镜头等
色调 暖色调、冷色调、高饱和度、低饱和度等。
描述情绪：
人物情绪：愤怒、恐惧、高兴、悲伤、惊讶、诧异、微笑、淡定、忧伤、痛苦等
描述运镜：
基础运镜 镜头推进、镜头拉远、镜头向右移动、镜头向左移动、镜头上摇 高级运镜 手持镜头、复合运镜、跟随镜头、环绕运镜等
风格化 - 视觉风格 毛毡风格、3D 卡通、像素风格、木偶动画、3D 游戏、黏土风格、二次元、水彩画、黑白动画、油画风格 风格化 - 特效镜头 移轴摄影、延时拍摄等
6、特別注意：确保镜头与镜头之间的衔接流畅，不能出现例如「手持跟拍轨道推进」这种不合理的运镜方式，因为手持跟拍是有抖动的，轨道推进是平滑的。
7、最终输出一段中文的自然语言，不能换行，不能在段头和段尾增加意义不明的符号，提示词以：中文提示词/... 这样的格式输出。例如：中文提示词/一位身穿红色西装外套的女性..."""

    def generate_script(self, 起始图片,结束图片,用户描述,VideoDuration_count, api_string, random_seed,
                        siliconflow_model="Qwen3", custom_model="gpt_5.2", api_provider="SiliconFlow", **kwargs):
        # 设置随机种子
        if random_seed == -1:
            random_seed = random.randint(0, 0xffffffffffffffff)
        random.seed(random_seed)

        # 用户描述直接使用输入值
        full_description = 用户描述

        # 将图片转换为 base64
        start_image_base64 = self.tensor_to_base64(起始图片)
        end_image_base64 = self.tensor_to_base64(结束图片)

        if not start_image_base64 or not end_image_base64:
            raise ValueError("无法处理输入的图片")

        # 构建请求
        full_prompt = f"用户描述：{full_description}"

        # Parse API String and get credentials
        parse_api_string_for_node(api_string, "NakuNode DualImageScriptGen")
        api_provider, api_key, api_url, sf_key, c_key, c_url = get_api_credentials(api_string, preferred_provider=api_provider)

        try:
            # Check if API key is provided (using parsed credentials)
            if not api_key or api_key in ["Please enter SiliconFlow API Key", "Please enter your API Key", ""]:
                print(f"[NakuNode DualImageScriptGen] API key not provided, returning user prompt directly")
                return (full_description, full_description)

            # Print API provider info
            print(f"[NakuNode DualImageScriptGen] API Provider: {api_provider}")
            print(f"[NakuNode DualImageScriptGen] SiliconFlow API Key: {'已设置' if sf_key else '未设置'}")
            print(f"[NakuNode DualImageScriptGen] Custom API Key: {'已设置' if c_key else '未设置'}")
            print(f"[NakuNode DualImageScriptGen] Custom API URL: {c_url}")

            print(f"\n[NakuNode DualImageScriptGen] {'='*60}")
            print(f"[NakuNode DualImageScriptGen] Starting request...")
            print(f"[NakuNode DualImageScriptGen] {'='*60}")
            print(f"[NakuNode DualImageScriptGen] User Description: {full_description[:100]}...")
            print(f"[NakuNode DualImageScriptGen] Video Duration: {VideoDuration_count} seconds")

            # SiliconFlow model mapping for image analysis
            model_mapping = {
                "QWEN3VL": "Qwen/Qwen3-VL-235B-A22B-Instruct",
                "GLM4.6V": "zai-org/GLM-4.6V",
                "KIMI2.5": "Pro/moonshotai/Kimi-K2.5"
            }

            # Custom API model mapping
            custom_model_mapping = {
                "GPT5.2": "gpt-5.2",
                "Gemini Pro 3.1": "gemini-3.1-pro-preview",
                "Gemini Pro 3": "gemini-3-pro-preview",
                "Claude Opus 4.6": "claude-opus-4-6",
                "Kimi 2.5": "kimi-k2.5"
            }

            # Select model and print info based on API provider
            if api_provider == "Custom":
                selected_model = custom_model_mapping.get(custom_model, "gpt-5.2")
                api_url = c_url.rstrip('/')
                use_stream = False
                print(f"[NakuNode DualImageScriptGen] Using Custom API")
                print(f"[NakuNode DualImageScriptGen] Custom API URL: {c_url}")
                print(f"[NakuNode DualImageScriptGen] Using Custom API model: {selected_model}")
            else:
                selected_model = model_mapping.get(siliconflow_model, "Qwen/Qwen3-VL-235B-A22B-Instruct")
                api_url = "https://api.siliconflow.cn/v1/chat/completions"
                use_stream = True
                print(f"[NakuNode DualImageScriptGen] Using SiliconFlow API")
                print(f"[NakuNode DualImageScriptGen] SiliconFlow URL: https://api.siliconflow.cn/v1/chat/completions")
                print(f"[NakuNode DualImageScriptGen] Using SiliconFlow model: {selected_model}")

            print(f"[NakuNode DualImageScriptGen] Generating script with {api_provider}...")

            # Call API using requests library
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Build complete API URL for Custom
            if api_provider == "Custom" and not api_url.endswith('/v1/chat/completions'):
                api_url = api_url + '/v1/chat/completions'

            print(f"[NakuNode DualImageScriptGen] Request URL: {api_url}")
            print(f"[NakuNode DualImageScriptGen] Stream mode: {use_stream}")

            # Build messages with two images - using updated system prompt with duration
            messages = [
                {"role": "system", "content": self.get_system_prompt(VideoDuration_count)},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下用户描述和两张图片，生成视频分镜脚本：{full_prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{start_image_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{end_image_base64}"}}
                ]}
            ]

            payload = {
                "model": selected_model,
                "messages": messages,
                "temperature": 0.7,
                "top_p": 0.9,
                "n": 1,
                "stream": use_stream,
                "max_tokens": 2048
            }

            print(f"[NakuNode DualImageScriptGen] Sending request...")

            if use_stream:
                # SiliconFlow stream mode
                response = requests.post(api_url, headers=headers, json=payload, stream=True, timeout=120, verify=False)
                print(f"[NakuNode DualImageScriptGen] HTTP status code: {response.status_code}")

                if response.status_code == 200:
                    print(f"[NakuNode DualImageScriptGen] API call successful")
                    full_content = ""
                    for chunk in response.iter_lines():
                        if chunk:
                            chunk_str = chunk.decode('utf-8').replace('data: ', '')
                            if chunk_str != "[DONE]" and chunk_str.strip():
                                try:
                                    chunk_data = json.loads(chunk_str)
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_content += content
                                except json.JSONDecodeError:
                                    continue
                    print(f"[NakuNode DualImageScriptGen] Stream response received, length: {len(full_content)}")
                    optimized_response = full_content
                else:
                    error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                    print(error_msg)
                    return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
            else:
                # Custom API non-stream mode - 添加重试机制
                max_retries = 3
                retry_delay = 2  # 秒
                response = None
                
                for attempt in range(max_retries):
                    try:
                        print(f"[NakuNode DualImageScriptGen] Sending request (attempt {attempt + 1}/{max_retries})...")
                        response = requests.post(api_url, headers=headers, json=payload, timeout=120, verify=False)
                        print(f"[NakuNode DualImageScriptGen] HTTP status code: {response.status_code}")

                        if response.status_code == 200:
                            print(f"[NakuNode DualImageScriptGen] API call successful")
                            response_data = response.json()

                            # Parse response
                            if 'choices' in response_data and len(response_data['choices']) > 0:
                                optimized_response = response_data['choices'][0]['message']['content']
                                print(f"[NakuNode DualImageScriptGen] API response: {optimized_response[:100]}...")
                                break
                            else:
                                error_msg = f"API response format error: {response_data}"
                                print(error_msg)
                                return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
                        else:
                            error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                            print(error_msg)
                            # 如果是服务器错误（5xx），尝试重试
                            if response.status_code >= 500 and attempt < max_retries - 1:
                                print(f"[NakuNode DualImageScriptGen] Server error, retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                continue
                            return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
                    except requests.exceptions.ConnectionError as e:
                        print(f"[NakuNode DualImageScriptGen] Connection error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            print(f"[NakuNode DualImageScriptGen] Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # 指数退避
                        else:
                            error_msg = f"Connection failed after {max_retries} attempts: {str(e)}"
                            print(error_msg)
                            return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
                    except requests.exceptions.Timeout:
                        error_msg = "API request timeout"
                        print(error_msg)
                        return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
                    except Exception as e:
                        error_msg = f"Unexpected error: {str(e)}"
                        print(error_msg)
                        return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")

            print(f"[NakuNode DualImageScriptGen] Generated response received")

            # 清理响应中的特殊标记
            cleaned_response = self.clean_special_markers(optimized_response)

            # 解析响应，查找中文提示词格式
            zh_part = cleaned_response

            # 检查是否包含"中文提示词/"格式
            if "中文提示词/" in cleaned_response:
                start_idx = cleaned_response.find("中文提示词/") + len("中文提示词/")
                zh_part = cleaned_response[start_idx:].strip()

                # 查找可能的结束标记或截取适当长度
                if '\n' in zh_part:
                    zh_part = zh_part.split('\n')[0].strip()
            elif "中文提示词:" in cleaned_response:
                start_idx = cleaned_response.find("中文提示词:") + len("中文提示词:")
                zh_part = cleaned_response[start_idx:].strip()

                if '\n' in zh_part:
                    zh_part = zh_part.split('\n')[0].strip()
            elif "中文：" in cleaned_response:
                start_idx = cleaned_response.find("中文：") + len("中文：")
                zh_part = cleaned_response[start_idx:].strip()

                if '\n' in zh_part:
                    zh_part = zh_part.split('\n')[0].strip()
            elif "中文:" in cleaned_response:
                start_idx = cleaned_response.find("中文:") + len("中文:")
                zh_part = cleaned_response[start_idx:].strip()

                if '\n' in zh_part:
                    zh_part = zh_part.split('\n')[0].strip()

            # 如果解析结果太短，使用 AI 的完整响应
            if len(zh_part) < len(cleaned_response) / 2:
                zh_part = cleaned_response

            # 确保中文部分不是空的
            if not zh_part.strip():
                zh_part = cleaned_response

            # 返回结果 (AI 改写提示词，初始提示词)
            return (zh_part, full_description)
        except requests.exceptions.Timeout:
            error_msg = "API request timeout"
            print(error_msg)
            return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (f"处理错误：{error_msg}. 原始描述：{full_description}", f"Error: {error_msg}")
        except Exception as e:
            print(f"[NakuNode DualImageScriptGen] Error during API call: {e}")
            import traceback
            traceback.print_exc()
            return (f"处理错误：{str(e)}. 原始描述：{full_description}", f"Error: {str(e)}")


# --- 注册节点到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "DualImageVideoScriptGenerator": DualImageVideoScriptGenerator
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "DualImageVideoScriptGenerator": "NakuNode-首尾帧视频提示词生成器"
}
