# -*- coding: utf-8 -*-
import random
import json
import time
import io
import base64
import urllib3
import ssl

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 尝试导入必要的库，如果失败则在调用时抛出更友好的错误
try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import requests
except ImportError:
    requests = None

# Import API utils
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from api_utils import get_api_credentials, parse_api_string_for_node

try:
    import jwt
except ImportError:
    jwt = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# Built-in prompt templates
BUILTIN_PROMPTS = {
    "Qwen/Zimage": {
        "system_prompt": "你是一位拥有顶级审美和摄影知识的 AI 艺术总监。你的任务是接收用户的简单指令，对指令进行延展，增加更多的细节描述。最终以 [画面风格] +[主体描述] +[场景描述]+ [细节修饰] + [画面构图] + [光线信息] +[画面色彩倾向]+ [画质参数] 这样的格式输出一段客观描述的自然语句。\n画面风格包括：例如\"真实的画面\"\"日式动漫\"\"写实照片\"\"真实的写真照\"等等\n主体描述包括：主体人物的详细描述（地域、性别、年龄、体型、动作、表情、情绪、服装造型）,画面焦点的主体描述（物体/生物的细节描述，例如颜色、形状、细节、动作、大小等等）\n细节修饰包括：突出 1-3 个关键细节（如面料纹理、饰品反光、发丝飘动、环境虚化等）\n画面构图包括：运用一种或多种经典构图法（如三分法、框架式、引导线、低角度仰拍等）,优先优化用户指令中的构图效果，若用户未指定，则输出最具美感的构图。\n光线信息包括：根据氛围和场景，选择最匹配的光线类型（如侧逆光、黄金时刻逆光、漫射光等）。优先优化用户指令中的光线效果，例如用户输入\"逆光\"。优化结果应为：\"一束从人物侧后方出现的温暖光源，勾勒出人物的脸部的轮廓。\"\n最终输出一段不多于 500 字的中文自然语句，语句不能出现换行的情况，不能出现除了\"，\"\"。\"\"！\"\"：\"以外的其他符号。避免中英混杂。\n可以增加一些氛围的描述例如\"高级感\"、\"电影调色\"、\"冷暖色调对比\"能有效提升画面的质感，避免产生廉价的\"网感\"图片。\n# 示例参考：\n用户：\"一个妖娆的古装女子\"\n最终输出：一位 20 岁左右的盛唐贵女，柳叶眉丹凤眼，红唇微启，乌黑高髻插点翠鎏金步摇与珍珠流苏簪，佩戴多层璎珞项圈，身穿大红色织金蹙金绣齐胸襦裙，衣襟袖口满布凤凰牡丹缠枝纹，金线熠熠生辉，腰系碧玉蹀躞带，侧身回眸一手抚髻一手搭雕花屏风，S 型身姿妖娆眼神妩媚，背景为唐代宫廷内殿烛光摇曳纱帘半透，超精细工笔重彩风格参考《簪花仕女图》与敦煌壁画色彩，8K，高清细节。\n\n需要避免以下问题：\n1.模糊不清的描述（如\"好看的东西\"）。\n2.自相矛盾的元素（如\"白天的满天繁星\"）。\n3.过于冗长或堆砌无关词汇。\n4.描述出现换行的情况。",
        "user_prompt": "{request}"
    },
    "Flux.2": {
        "system_prompt": "You are a top art director proficient in lighting, composition, color psychology, and digital rendering techniques. You deeply understand the underlying logic of top AI painting models like Midjourney and Flux. Your goal is to transform simple user concepts into **visually striking, exquisitely detailed, cinematic-quality** painting prompts.\n\n## Workflow\n1. **Analyze:** Extract the core subject, emotional tone, and scene from user input.\n2. **Enhance:** Automatically supplement missing aesthetic elements (lighting, materials, camera parameters, art style).\n3. **Structure:** Reorganize according to the golden formula: [Subject & Action] + [Environment & Context] + [Lighting & Atmosphere] + [Camera & Composition] + [Style & Medium] + [Color Palette] + [Quality Boosters].\n4. **Output:** Provide English natural language prompts. No line breaks allowed.\n\n## The Golden Formula\n[Subject & Action] + [Environment & Context] + [Lighting & Atmosphere] + [Camera & Composition] + [Style & Medium] + [Color Palette] + [Quality Boosters]\n\n## Knowledge Base\n\n### 1. Lighting (Determines Quality)\n* **Keywords:** Cinematic lighting, Volumetric lighting, Rembrandt lighting, Bioluminescence, Subsurface scattering, God rays.\n\n### 2. Composition (Determines Tension)\n* **Keywords:** Golden ratio, Rule of thirds, Low angle shot, Extreme close-up, Wide angle, Depth of field.\n\n### 3. Texture & Material (Determines Realism)\n* **Keywords:** Hyper-realistic, Intricate details, 8k texture, Unreal Engine 5 render, Ray tracing.\n\n### 4. Style Modifiers\n* **Keywords:** Cyberpunk, Steampunk, Baroque, Minimalism, Ukiyo-e, Concept art.\n\n## Rules\n1. **Language:** Always output **English** prompts in natural language. No line breaks.\n2. **No Conflicts:** Ensure style words don't conflict (e.g., don't write 'black and white' and 'rainbow' together).\n3. **Quality:** Must include quality-boosting 'spells' (Masterpiece, Best quality, Sharp focus).\n\n## Interaction Example\n**User Input:**\nCharacter: A beautiful woman in Hanfu in snow, lonely and aesthetic\n\n**Example Output:**\nA beautiful young woman in traditional Hanfu, delicate pale skin with realistic texture, sorrowful eyes looking at the distance, petite figure. Wearing a red silk Hanfu cloak, heavy fabric draped elegantly over shoulders, snowflakes melting on the fabric, distinct contrast between red cloth and white snow. Standing alone in a vast snowy landscape, minimalist composition, massive negative space, soft overcast light, muted colors with vibrant red accent, cinematic shot, depth of field, shot on 35mm film, ethereal atmosphere, ultra-detailed, 8k",
        "user_prompt": "{request}"
    }
}


class NakuNodePromptEVO:
    """
    NakuNode Prompt Evolution - Text-driven prompt generator
    """

    @classmethod
    def INPUT_TYPES(s):
        # Create AI model selection list
        model_list = ["Qwen/Zimage", "Flux.2"]

        inputs = {
            "required": {
                "ai_model": (model_list, {"default": "Qwen/Zimage"}),
                "text_request": ("STRING", {"multiline": True, "default": "Please enter your image generation request"}),
            },
            "optional": {
                "api_provider": (["SiliconFlow", "Custom"], {"default": "SiliconFlow"}),
                "siliconflow_model": (["MiniMax2.5", "GLM5", "DeepSeek3.2", "Kimi K2"], {"default": "MiniMax2.5"}),
                "custom_model": (["GPT5.2", "Gemini Pro 3.1", "Gemini Pro 3", "Claude Opus 4.6", "Qwen 3.5", "Kimi 2.5"], {"default": "GPT5.2"}),
                "api_string": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "连接 API Setting 节点"
                }),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
                "extra_prompts": ("STRING", {"multiline": False, "default": ""}),
            }
        }

        return inputs

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("generated_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "NakuNode/Prompt Generation"

    def generate_prompt(self, text_request, ai_model, api_string, seed,
                        extra_prompts="", siliconflow_model="Qwen3", custom_model="gpt_5.2", api_provider="SiliconFlow", **kwargs):
        # Set random seed
        if seed == -1:
            seed = random.randint(0, 0xffffffffffffffff)
        random.seed(seed)

        print(f"\n{'='*60}")
        print(f"[NakuNode-Prompt] Starting request - AI Model: {ai_model}")
        print(f"{'='*60}")
        print(f"[NakuNode-Prompt] Text Request: {text_request}")
        print(f"[NakuNode-Prompt] Extra Prompts: {extra_prompts}")
        
        # Parse and display extra prompts in debug format
        if extra_prompts and extra_prompts.strip():
            print(f"\n{'='*60}")
            print("[NakuNode-Prompt] === Prompt Builder Parameters ===")
            print(f"{'='*60}")
            
            # Split by dots to separate categories
            categories = extra_prompts.split('.')
            category_names = ["📷 Photography", "👤 Character", "🌍 Scene"]
            
            for i, cat in enumerate(categories):
                if i < len(category_names) and cat.strip():
                    print(f"\n[{category_names[i]}]")
                    # Split by comma to get individual items
                    items = [item.strip() for item in cat.split(',') if item.strip()]
                    for j, item in enumerate(items, 1):
                        print(f"  {j}. {item}")
            
            print(f"\n{'='*60}")
            
            enhanced_text_request = f"{text_request}, {extra_prompts}"
            print(f"[NakuNode-Prompt] Enhanced request: {enhanced_text_request}")
        else:
            enhanced_text_request = text_request
            print(f"[NakuNode-Prompt] No extra prompts, using original request: {enhanced_text_request}")

        # Get prompt template for selected model
        model_config = BUILTIN_PROMPTS.get(ai_model, BUILTIN_PROMPTS["Qwen/Zimage"])
        print(f"[NakuNode-Prompt] Using model config: {ai_model}")

        # Build complete prompt
        system_prompt = model_config["system_prompt"]
        user_prompt = model_config["user_prompt"].format(request=enhanced_text_request)
        print(f"[NakuNode-Prompt] System Prompt: {system_prompt[:100]}...")
        print(f"[NakuNode-Prompt] System Prompt length: {len(system_prompt)} characters")
        print(f"[NakuNode-Prompt] User Prompt length: {len(user_prompt)} characters")
        print(f"[NakuNode-Prompt] User Prompt: {user_prompt[:100]}...")

        # Select API key based on provider
        parse_api_string_for_node(api_string, "NakuNode PromptEVO")
        api_provider, api_key, api_url, sf_key, c_key, c_url = get_api_credentials(api_string, preferred_provider=api_provider)
        
        # Print API provider info
        print(f"[NakuNode-Prompt] API Provider: {api_provider}")
        print(f"[NakuNode-Prompt] SiliconFlow API Key: {'已设置' if sf_key else '未设置'}")
        print(f"[NakuNode-Prompt] Custom API Key: {'已设置' if c_key else '未设置'}")
        print(f"[NakuNode-Prompt] Custom API URL: {c_url}")

        # Decide whether to call API based on API provider and model selection
        if not api_key or api_key in ["Please enter SiliconFlow API Key", "Please enter your API Key", ""]:
            # Do not call API, directly return user input text with extra prompts
            print("[NakuNode-Prompt] API key is empty or not filled, returning user request directly")
            return (enhanced_text_request,)
        elif api_provider in ["SiliconFlow", "Custom"]:
            if not api_key or api_key == "Please enter SiliconFlow API Key" or api_key == "Please enter your API Key":
                print("[NakuNode-Prompt] Error: API key is empty or not filled")
                raise ValueError("When using API, please fill in your API key in the API Key field.")

            if OpenAI is None:
                print("[NakuNode-Prompt] Error: OpenAI library not installed")
                raise ImportError("Please install openai library: pip install openai")

            # SiliconFlow model mapping
            model_mapping = {
                "MiniMax2.5": "Pro/MiniMaxAI/MiniMax-M2.5",
                "GLM5": "Pro/zai-org/GLM-5",
                "DeepSeek3.2": "Pro/deepseek-ai/DeepSeek-V3.2",
                "Kimi K2": "Pro/moonshotai/Kimi-K2-Thinking"
            }

            # Custom API model mapping
            custom_model_mapping = {
                "GPT5.2": "gpt-5.2",
                "Gemini Pro 3.1": "gemini-3.1-pro-preview",
                "Gemini Pro 3": "gemini-3-pro-preview",
                "Claude Opus 4.6": "claude-opus-4-6",
                "Qwen 3.5": "qwen3.5-plus",
                "Kimi 2.5": "kimi-k2.5"
            }

            # Select model and print info based on API provider
            if api_provider == "Custom":
                selected_model = custom_model_mapping.get(custom_model, "gpt-5.2")
                # 使用解析后的 c_url 而不是原始的 custom_url 参数
                api_url = c_url.rstrip('/')
                use_stream = False
                print(f"[NakuNode-Prompt] Using Custom API")
                print(f"[NakuNode-Prompt] Custom API URL: {c_url}")
                print(f"[NakuNode-Prompt] Using Custom API model: {selected_model}")
            else:
                selected_model = model_mapping.get(siliconflow_model, "Pro/MiniMaxAI/MiniMax-M2.5")
                api_url = "https://api.siliconflow.cn/v1/chat/completions"
                use_stream = True
                print(f"[NakuNode-Prompt] Using SiliconFlow API")
                print(f"[NakuNode-Prompt] SiliconFlow URL: https://api.siliconflow.cn/v1/chat/completions")
                print(f"[NakuNode-Prompt] Using SiliconFlow model: {selected_model}")

            try:
                print("[NakuNode-Prompt] Sending HTTP request...")

                # Build complete API URL for Custom
                if api_provider == "Custom" and not api_url.endswith('/v1/chat/completions'):
                    api_url = api_url + '/v1/chat/completions'

                print(f"[NakuNode-Prompt] Request URL: {api_url}")
                print(f"[NakuNode-Prompt] Stream mode: {use_stream}")

                # Use requests library to send HTTP request
                import json
                import requests

                headers = {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                # Print prompt content to be sent
                print(f"[NakuNode-Prompt] Sending System Prompt: {system_prompt[:200]}...")
                print(f"[NakuNode-Prompt] Sending User Prompt: {user_prompt[:200]}...")

                payload = {
                    "model": selected_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "n": 1,
                    "stream": use_stream,
                    "max_tokens": 2048
                }

                print("[NakuNode-Prompt] Sending request...")
                
                if use_stream:
                    # SiliconFlow stream mode
                    response = requests.post(api_url, headers=headers, json=payload, stream=True, timeout=60, verify=False)
                    print(f"[NakuNode-Prompt] HTTP status code: {response.status_code}")

                    if response.status_code == 200:
                        print("[NakuNode-Prompt] API call successful")
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
                        print(f"[NakuNode-Prompt] Stream response received, length: {len(full_content)}")
                        return (full_content,)
                    else:
                        error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                        print(error_msg)
                        return (error_msg,)
                else:
                    # Custom API non-stream mode - 添加重试机制
                    max_retries = 3
                    retry_delay = 2  # 秒
                    response = None
                    
                    for attempt in range(max_retries):
                        try:
                            print(f"[NakuNode-Prompt] Sending request (attempt {attempt + 1}/{max_retries})...")
                            response = requests.post(api_url, headers=headers, json=payload, timeout=60, verify=False)
                            print(f"[NakuNode-Prompt] HTTP status code: {response.status_code}")

                            if response.status_code == 200:
                                print("[NakuNode-Prompt] API call successful")
                                response_data = response.json()

                                # Parse response
                                if 'choices' in response_data and len(response_data['choices']) > 0:
                                    result = response_data['choices'][0]['message']['content']
                                    print(f"[NakuNode-Prompt] API response: {result[:100]}...")
                                    return (result,)
                                else:
                                    error_msg = f"API response format error: {response_data}"
                                    print(error_msg)
                                    return (error_msg,)
                            else:
                                error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                                print(error_msg)
                                # 如果是服务器错误（5xx），尝试重试
                                if response.status_code >= 500 and attempt < max_retries - 1:
                                    print(f"[NakuNode-Prompt] Server error, retrying in {retry_delay} seconds...")
                                    time.sleep(retry_delay)
                                    continue
                                return (error_msg,)
                        except requests.exceptions.ConnectionError as e:
                            print(f"[NakuNode-Prompt] Connection error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                            if attempt < max_retries - 1:
                                print(f"[NakuNode-Prompt] Retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # 指数退避
                            else:
                                error_msg = f"Connection failed after {max_retries} attempts: {str(e)}"
                                print(error_msg)
                                return (error_msg,)
                        except requests.exceptions.Timeout:
                            error_msg = "API request timeout"
                            print(error_msg)
                            return (error_msg,)
                        except Exception as e:
                            error_msg = f"Unexpected error: {str(e)}"
                            print(error_msg)
                            return (error_msg,)

            except requests.exceptions.Timeout:
                error_msg = "API request timeout"
                print(error_msg)
                return (error_msg,)
            except requests.exceptions.RequestException as e:
                error_msg = f"HTTP request failed: {str(e)}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                return (error_msg,)
            except Exception as e:
                error_msg = f"API call failed: {str(e)}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                return (error_msg,)
        else:
            print(f"[NakuNode-Prompt] Unknown API provider: {api_provider}, not calling API")
            full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}"
            return (full_prompt,)


# --- Register node to ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "NakuNodePromptEVO": NakuNodePromptEVO
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNodePromptEVO": "NakuNode-PromptEVO"
}
