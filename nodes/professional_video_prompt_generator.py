# -*- coding: utf-8 -*-
"""
NakuNode - Professional Video Prompt Generator
Modified to match PromptEVO API logic (SiliconFlow/Custom)
Note: Original system prompt preserved, PRO_OPTIONS removed
Added VideoPrompt.js frontend support
"""
import random
import json
import time

try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None


class ProfessionalVideoPromptGenerator:
    """
    专业视频提示词润色器 - Professional video prompt polisher
    Modified to use SiliconFlow/Custom API providers (same as PromptEVO)
    Note: PRO_OPTIONS removed, use VideoPrompt.js frontend instead
    """

    @classmethod
    def INPUT_TYPES(s):
        # Create AI provider list - SiliconFlow and Custom (same as PromptEVO)
        provider_list = ["SiliconFlow", "Custom"]

        inputs = {
            "required": {
                "User_Description": ("STRING", {"multiline": True, "default": "A cute cat running on the beach at sunset"}),
                "api_provider": (provider_list, {"default": "SiliconFlow"}),
                "random_seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            },
            "optional": {
                # SiliconFlow API settings
                "SiliconFlow_API_KEY": ("STRING", {"multiline": False, "default": "Please enter SiliconFlow API Key"}),
                "siliconflow_model": (["KIMI-K2", "Qwen3", "DeepSeekV3", "GLM", "KIMI"], {"default": "Qwen3"}),
                # Custom API settings
                "User_API_KEY": ("STRING", {"multiline": False, "default": "Please enter your API Key"}),
                "custom_url": ("STRING", {"multiline": False, "default": "https://api.siliconflow.cn/v1"}),
                "custom_model": (["gpt_5.2", "gemini_3.1", "Qwen_3.5", "Kimi_2.5"], {"default": "gpt_5.2"}),
            }
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Chinese Prompt", "English Prompt")
    FUNCTION = "generate_prompt"
    CATEGORY = "NakuNode/Video Prompt"

    def get_system_prompt(self):
        """Get the original system prompt - DO NOT MODIFY"""
        return """你是一名熟悉生成通义万相 AI 视频制作提示词的智能体，基于通义万相 AI 生视频功能的提示词使用公式生成最佳提示词 prompt，提示词的格式以一段完整的自然语言句子为最终输出 prompt，需要给到中文和英文两版提示词：

以下几种提示词使用公式：

提示词方式 1：主体（主体描述）＋场景（场景描述）＋运动（运动描述）＋镜头语言＋氛围词 ＋风格化
主体描述：主体描述是对主体外观特征细节的描述，可通过形容词或短句列举，例如「一位身着少数民族服饰的黑发苗族少女」、「一位来自异世界的飞天仙子，身着破旧却华丽的服饰，背后展开一对由废墟碎片构成的奇异翅膀」。
场景描述：场景描述是对主体所处环境特征细节的描述，可通过形容词或短句列举。
运动描述：运动描述是对运动特征细节的描述，包含运动的幅度、速率和运动作用的效果，例如「猛烈地摇摆」、「缓慢地移动」、「打碎了玻璃」。
镜头语言：镜头语言包含景别、视角、镜头、运镜等，常见镜头语言详见下方提示词词典。
氛围词：氛围词是对预期画面氛围的描述，例如「梦幻」、「孤独」、「宏伟」，常见氛围词详见下方提示词词典。
风格化：风格化是对画面风格语言的描述，例如「赛博朋克」、「勾线插画」、「废土风格」，常见风格化详见下方提示词词典。
情感修饰词：
梦幻般的、紧张的、宁静的、未来感的、复古的
"画面充满神秘感，背景有若隐若现的星光"
"快速运镜配合紧张的音乐节奏，营造悬疑氛围"
示例优化：
原始提示词：机器人在城市中行走。
优化后：
未来主义风格的银色人形机器人以流畅机械动作穿越霓虹灯闪烁的赛博朋克都市，雨滴在玻璃幕墙反射出霓虹光斑，镜头以手持跟拍方式从低角度仰视，背景虚化为紫色光晕。

提示词方式 2：适用于对镜头运动有明确要求、在提示词方式 1 之上添加更具体的运镜描述可以有效提升视频的动感和叙事性。
提示词=风格化运镜描述＋主体（主体描述）＋场景（场景描述）＋运动（运动描述）+镜头语言＋氛围词：运镜描述是对镜头运动的具体描述，在时间线上，将镜头运动和画面内容的变化有效结合可以有效提升视频叙事的丰富性和专业度。可以通过代入导演的视角来想象和书写运镜过程。需要注意将镜头运动的时长合理控制在 5s 内，避免过于复杂的运镜，同时如果是图片生成视频，请注意这是一个镜头的内容，不可以有切镜的描述例如从全景切特写。
镜头词典参考：
景别：特写、全景、中景
视角：第一人称视角、俯视
镜头类型：广角镜头、鱼眼镜头、微距镜头、移轴镜头
风格化词汇：
艺术风格：水墨画、油画、赛博朋克、蒸汽波、浮世绘
光影效果：柔和自然光、冷色调月光、强光照射
材质细节：金属光泽、丝绸质感、半透明材质
示例优化：
原始提示词：太空飞船起飞。
优化后：
深空中的银色宇宙飞船喷射蓝色等离子火焰垂直升空，镜头以广角从飞船底部仰拍并缓慢旋转，背景有星云流动效果。

提示词方式 3：适用于有明确该类创意需求的用户，在提示词方式 1/提示词方式 2 的基础上添加形变描述可以有效提升视频的趣味性，带来意想不到的视觉效果。
提示词 = 主体 A（主体描述）+ 形变过程 + 主体 B（主体描述）＋场景（场景描述）+ 运动（运动描述）+ 镜头语言＋氛围词＋风格化
主体 A：主体 A 指主体形变前的特征和状态。
形变过程：形变过程是对主体从 A 形态变为 B 形态的过程描述。详细的过程描述可以有效提升形变的自然度和生动性。
主体 B：主体 B 指主体形变后的特征和状态。
动态变形指令：
物体变形：逐渐变形为…（如「机器人手臂逐渐变形为机械藤蔓」）。
材质变化：表面纹理从…变为…（如「水晶雕像表面纹理从光滑变为像素化」）。
粒子化/融合：分裂成粒子重组为…（如「火焰化作金色粒子重组为凤凰」）。
示例优化：
原始提示词：花朵绽放。
优化后：
黑色土壤中缓慢升起透明晶体，晶体内部逐渐绽放出霓虹粉色的机械花朵，花瓣边缘分裂成发光粒子形成光晕，镜头从侧面俯拍花朵盛开过程。

避免生成画面模糊，可添加清晰度参数：8K 分辨率，超清细节。
示例：8K 分辨率的机械蜘蛛攀爬在锈蚀金属表面
避免生成风格不统一，可添加明确艺术流派：新海诚风格，柔和水彩质感等。
示例：新海诚风格的樱花雨与少年奔跑场景
避免运动不连贯，可添加描述镜头轨迹：镜头以 360°环绕主体匀速移动。
示例：镜头以 360°环绕芭蕾舞者旋转拍摄。

最后请确保包含以下要素，同时需要合并为一句自然语句（中文及英文）：
主体：明确核心对象（人物、物体、抽象概念）。
场景：环境细节（室内/室外、季节、时间）。
动作/运动：动态过程或静态姿势。
视觉风格：艺术流派、画质要求。
镜头指令：视角、景别、运动路径。（若没有镜头运动的话请强调镜头固定不动）
增强细节：光线、色彩、特效、情绪氛围。"""

    def generate_prompt(self, User_Description, api_provider, random_seed,
                        SiliconFlow_API_KEY="", siliconflow_model="Qwen3",
                        User_API_KEY="", custom_url="https://api.siliconflow.cn/v1",
                        custom_model="gpt_5.2", **kwargs):
        # Set random seed
        if random_seed == -1:
            random_seed = random.randint(0, 0xffffffffffffffff)
        random.seed(random_seed)

        # User description directly from input (no PRO_OPTIONS)
        full_description = User_Description

        try:
            # Select API settings based on provider
            if api_provider == "SiliconFlow":
                api_key = SiliconFlow_API_KEY
            else:
                api_key = User_API_KEY

            # Check if API key is provided
            if not api_key or api_key in ["Please enter SiliconFlow API Key", "Please enter your API Key"]:
                print(f"[NakuNode VideoPromptGen] API key not provided, returning user prompt directly")
                return (full_description, full_description)

            print(f"\n[NakuNode VideoPromptGen] {'='*60}")
            print(f"[NakuNode VideoPromptGen] Starting request - API Provider: {api_provider}")
            print(f"[NakuNode VideoPromptGen] {'='*60}")
            print(f"[NakuNode VideoPromptGen] User Description: {full_description[:100]}...")

            # SiliconFlow model mapping (same as PromptEVO)
            model_mapping = {
                "KIMI-K2": "Pro/moonshotai/Kimi-K2-Instruct-0905",
                "Qwen3": "Qwen/Qwen3-235B-A22B-Instruct-2507",
                "DeepSeekV3": "Pro/deepseek-ai/DeepSeek-V3.2",
                "GLM": "Pro/zai-org/GLM-4.7",
                "KIMI": "Pro/moonshotai/Kimi-K2.5"
            }

            # Custom API model mapping
            custom_model_mapping = {
                "gpt_5.2": "gpt-5.2",
                "gemini_3.1": "gemini-3.1-pro-preview",
                "Qwen_3.5": "qwen3.5-plus",
                "Kimi_2.5": "kimi-k2.5"
            }

            # Select model and print info based on API provider
            if api_provider == "Custom":
                selected_model = custom_model_mapping.get(custom_model, "gpt-5.2")
                api_url = custom_url.rstrip('/')
                use_stream = False
                print(f"[NakuNode VideoPromptGen] Using Custom API")
                print(f"[NakuNode VideoPromptGen] Custom API URL: {custom_url}")
                print(f"[NakuNode VideoPromptGen] Using Custom API model: {selected_model}")
            else:
                selected_model = model_mapping.get(siliconflow_model, "Pro/zai-org/GLM-4.7")
                api_url = "https://api.siliconflow.cn/v1/chat/completions"
                use_stream = True
                print(f"[NakuNode VideoPromptGen] Using SiliconFlow API")
                print(f"[NakuNode VideoPromptGen] SiliconFlow URL: https://api.siliconflow.cn/v1/chat/completions")
                print(f"[NakuNode VideoPromptGen] Using SiliconFlow model: {selected_model}")

            print(f"[NakuNode VideoPromptGen] Optimizing prompt with {api_provider}...")

            # Call API using requests library
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Build complete API URL for Custom
            if api_provider == "Custom" and not api_url.endswith('/v1/chat/completions'):
                api_url = api_url + '/v1/chat/completions'

            print(f"[NakuNode VideoPromptGen] Request URL: {api_url}")
            print(f"[NakuNode VideoPromptGen] Stream mode: {use_stream}")

            # Build messages - using original system prompt
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"根据以下用户描述，生成视频提示词：{full_description}"}
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

            print(f"[NakuNode VideoPromptGen] Sending request...")

            if use_stream:
                # SiliconFlow stream mode
                response = requests.post(api_url, headers=headers, json=payload, stream=True, timeout=120)
                print(f"[NakuNode VideoPromptGen] HTTP status code: {response.status_code}")

                if response.status_code == 200:
                    print(f"[NakuNode VideoPromptGen] API call successful")
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
                    print(f"[NakuNode VideoPromptGen] Stream response received, length: {len(full_content)}")
                    optimized_response = full_content
                else:
                    error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                    print(error_msg)
                    return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
            else:
                # Custom API non-stream mode
                response = requests.post(api_url, headers=headers, json=payload, timeout=120)
                print(f"[NakuNode VideoPromptGen] HTTP status code: {response.status_code}")

                if response.status_code == 200:
                    print(f"[NakuNode VideoPromptGen] API call successful")
                    response_data = response.json()

                    # Parse response
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        optimized_response = response_data['choices'][0]['message']['content']
                        print(f"[NakuNode VideoPromptGen] API response: {optimized_response[:100]}...")
                    else:
                        error_msg = f"API response format error: {response_data}"
                        print(error_msg)
                        return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
                else:
                    error_msg = f"HTTP error: {response.status_code} - {response.text[:200]}"
                    print(error_msg)
                    return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")

            print(f"[NakuNode VideoPromptGen] Optimized response received")

            # Parse response to extract Chinese and English versions
            zh_part = ""
            en_part = ""

            # Try to parse response to extract Chinese and English versions
            lines = optimized_response.split('\n')
            chinese_lines = []
            english_lines = []

            for line in lines:
                line = line.strip()

                # Check if contains Chinese characters
                if any('\u4e00' <= char <= '\u9fff' for char in line):
                    if not line.startswith("English:") and not line.startswith("英文:") and "English" not in line and "英文" not in line:
                        chinese_lines.append(line)

                # Check if may contain English
                if any(char.isalpha() or char.isspace() or char in ',.!?:;\'\"-()[]{}' for char in line) and not any('\u4e00' <= char <= '\u9fff' for char in line):
                    if line and not line.startswith("中文:") and not line.startswith("Chinese:") and "中文" not in line and "Chinese" not in line:
                        english_lines.append(line)

            # Merge results
            zh_part = ' '.join(chinese_lines).strip()
            en_part = ' '.join(english_lines).strip()

            # If parsing is not successful, use full response for both languages
            if not zh_part and not en_part:
                zh_part = optimized_response
                en_part = optimized_response
            elif not zh_part:
                zh_part = full_description
            elif not en_part:
                en_part = full_description

            # If parsed result is not good enough, return full AI response
            if len(zh_part) < len(full_description) / 2:
                zh_part = optimized_response
            if len(en_part) < len(full_description) / 2:
                en_part = optimized_response

            return (zh_part, en_part)
        except requests.exceptions.Timeout:
            error_msg = "API request timeout"
            print(error_msg)
            return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (f"Error: {error_msg}. Original: {full_description}", f"Error: {error_msg}")
        except Exception as e:
            print(f"[NakuNode VideoPromptGen] Error during API call: {e}")
            import traceback
            traceback.print_exc()
            return (f"Error: {str(e)}. Original: {full_description}", f"Error: {str(e)}")


# --- Register node to ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "ProfessionalVideoPromptGenerator": ProfessionalVideoPromptGenerator
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ProfessionalVideoPromptGenerator": "NakuNode 专业视频提示词润色器"
}
