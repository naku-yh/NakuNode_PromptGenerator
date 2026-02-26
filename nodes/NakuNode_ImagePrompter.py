# -*- coding: utf-8 -*-
import random
import json
from PIL import Image
import io
import base64

# 尝试导入必要的库，如果失败则在调用时抛出更友好的错误
try:
    import requests
except ImportError:
    requests = None

# SiliconFlow 模型映射
SILICONFLOW_MODELS = {
    "QWENVL": "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "GLM": "zai-org/GLM-4.6V",
    "KIMI": "Pro/moonshotai/Kimi-K2.5"
}

# Custom API 模型映射
CUSTOM_MODELS = {
    "gpt_5.2": "gpt-5.2",
    "gemini_3.1": "gemini-3.1-pro-preview",
    "Qwen_3.5": "qwen3.5-plus",
    "Kimi_2.5": "kimi-k2.5"
}


class NakuNodeImagePrompter:
    """
    NakuNode Image Prompter - 生成客观的图片描述
    """

    @classmethod
    def INPUT_TYPES(s):
        # 创建 AI 服务商列表
        provider_list = ["SiliconFlow", "Custom"]

        inputs = {
            "required": {
                "image": ("IMAGE", {}),
                "text_request": ("STRING", {"multiline": True, "default": "请输入对图片的具体需求或补充说明"}),
                "api_provider": (provider_list, {"default": "SiliconFlow"}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "SiliconFlow_API_KEY": ("STRING", {"multiline": False, "default": "请填写 SiliconFlow API Key"}),
                "User_API_KEY": ("STRING", {"multiline": False, "default": "请填写您的 API Key"}),
                "custom_url": ("STRING", {"multiline": False, "default": "https://api.siliconflow.cn/v1"}),
                "custom_model": (["gpt_5.2", "gemini_3.1", "Qwen_3.5", "Kimi_2.5"], {"default": "gpt_5.2"}),
                "siliconflow_model": (["QWENVL", "GLM", "KIMI"], {"default": "QWENVL"}),
            }
        }

        return inputs

    RETURN_TYPES = ("STRING",)  # 输出描述
    RETURN_NAMES = ("图片描述",)
    FUNCTION = "generate_description"
    CATEGORY = "NakuNode/图片描述"

    def tensor_to_base64(self, image_tensor):
        """将张量转换为 base64 编码的图片"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode ImagePrompter] Warning: numpy is not installed.")
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

        # 调整图片大小以避免 API 错误
        MAX_DIMENSION = 1920
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = MAX_DIMENSION
                new_height = int(MAX_DIMENSION / aspect_ratio)
            else:
                new_height = MAX_DIMENSION
                new_width = int(MAX_DIMENSION * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[NakuNode ImagePrompter] Image resized to {img.width}x{img.height} to prevent API errors.")

        # 将图片保存到内存中的缓冲区
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    def generate_description(self, image, text_request, api_provider, seed, SiliconFlow_API_KEY=None, User_API_KEY=None, custom_url="https://api.siliconflow.cn/v1", custom_model="gpt_5.2", siliconflow_model="QWENVL", **kwargs):
        # 设置随机种子
        if seed == -1:
            seed = random.randint(0, 0xffffffffffffffff)
        random.seed(seed)

        # 将图片转换为 base64
        image_base64 = self.tensor_to_base64(image)
        if not image_base64:
            raise ValueError("无法处理输入的图片")

        # 根据 AI 服务商选择 API Key
        if api_provider == "SiliconFlow":
            api_key = SiliconFlow_API_KEY
        else:
            api_key = User_API_KEY

        # 检查 API Key 是否填写
        if not api_key or api_key in ["请填写 SiliconFlow API Key", "请填写您的 API Key"]:
            print(f"[NakuNode ImagePrompter] API Key 未填写，返回空描述")
            return ("",)

        # 构建请求
        full_prompt = f"文字需求：{text_request}"

        try:
            print(f"\n[NakuNode ImagePrompter] ========================================")
            print(f"[NakuNode ImagePrompter] 开始生成图片描述")
            print(f"[NakuNode ImagePrompter] AI 服务商：{api_provider}")
            print(f"[NakuNode ImagePrompter] 随机种子：{seed}")
            print(f"[NakuNode ImagePrompter] SiliconFlow 模型：{siliconflow_model}")
            print(f"[NakuNode ImagePrompter] Custom 模型：{custom_model}")
            print(f"[NakuNode ImagePrompter] Custom URL: {custom_url}")
            print(f"[NakuNode ImagePrompter] 文字需求：{text_request[:100]}...")
            print(f"[NakuNode ImagePrompter] ========================================\n")

            # 调用 API
            description_response = self.call_llm_api(api_provider, api_key, full_prompt, image_base64, siliconflow_model, custom_url, custom_model)
            print(f"[NakuNode ImagePrompter] 生成完成：{description_response[:100]}...")

            # 返回 AI 生成的描述
            return (description_response,)
        except Exception as e:
            print(f"[NakuNode ImagePrompter] Error during description generation: {e}")
            # 发生错误时返回错误信息
            return (f"生成错误：{e}. 请检查 API 密钥和网络连接。",)

    def call_llm_api(self, api_provider, api_key, prompt, image_base64, siliconflow_model="QWENVL", custom_url="https://api.siliconflow.cn/v1", custom_model="gpt_5.2"):
        # 内置系统提示词 - 不可修改
        system_prompt = """你是一名图片生成专家，通过分析用户输入的图片（画风、风格、色彩搭配、氛围等等，如果有画面有文字需具体描述字体形态、字体颜色、字体大小、字体位置、字体效果等等）以及文字需求，最终以 [主体描述] + [细节修饰] + [艺术风格] + [画面构图] + [光照/色彩] + [画质参数] 这样的格式输出一段客观描述的自然语句，不要有废话。不要带有主观情绪的词句例如"兼具典雅传统与时尚活力""既增添神秘感与优雅气质""增添了时尚活力与异域奇幻感"等等。示例："一位身穿未来科技感银色战甲的女战士，站在火星红色荒漠上，背景是巨大的地球和星空，赛博朋克风格，电影级光影，超高清 8K，细节丰富，景深强烈"。需要避免以下问题：1.模糊不清的描述（如"好看的东西"）2.自相矛盾的元素（如"白天的满天繁星"）3.过于冗长或堆砌无关词汇。"""

        if not requests:
            raise ImportError("requests 库缺失。请在您的 ComfyUI 环境中运行 'pip install requests' 来安装。")

        # 构建消息，包含图片
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"根据以下文字需求和附带的图片，生成客观的图片描述：{prompt}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]}
        ]

        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

        # 根据服务商选择模型和 URL
        if api_provider == "Custom":
            selected_model = CUSTOM_MODELS.get(custom_model, "gpt-5.2")
            api_url = custom_url.rstrip('/')
            use_stream = False
            print(f"[NakuNode ImagePrompter] 使用 Custom API: {selected_model}")
            print(f"[NakuNode ImagePrompter] Custom URL: {custom_url}")
        else:
            selected_model = SILICONFLOW_MODELS.get(siliconflow_model, "Qwen/Qwen3-VL-30B-A3B-Instruct")
            api_url = "https://api.siliconflow.cn/v1/chat/completions"
            use_stream = True
            print(f"[NakuNode ImagePrompter] 使用 SiliconFlow API: {selected_model}")
            print(f"[NakuNode ImagePrompter] SiliconFlow URL: https://api.siliconflow.cn/v1/chat/completions")

        # 构建完整的 API URL（仅 Custom 模式需要）
        if api_provider == "Custom" and not api_url.endswith('/v1/chat/completions'):
            api_url = api_url + '/v1/chat/completions'

        print(f"[NakuNode ImagePrompter] 请求 URL: {api_url}")
        print(f"[NakuNode ImagePrompter] Stream 模式：{use_stream}")

        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": use_stream,
            "temperature": 0.7,
            "max_tokens": 2048
        }

        try:
            print(f"[NakuNode ImagePrompter] 发送 HTTP 请求...")

            if use_stream:
                # SiliconFlow 流式模式处理
                response = requests.post(api_url, headers=headers, json=payload, stream=True, timeout=120)
                print(f"[NakuNode ImagePrompter] HTTP 状态码：{response.status_code}")

                if response.status_code == 200:
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
                    print(f"[NakuNode ImagePrompter] 流式响应接收完成")
                    return full_content
                else:
                    return f"Error: {response.status_code} - {response.text[:200]}"
            else:
                # Custom API 非流式模式处理
                response = requests.post(api_url, headers=headers, json=payload, timeout=120)
                print(f"[NakuNode ImagePrompter] HTTP 状态码：{response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                return f"Error: {response.status_code}"
        except requests.exceptions.Timeout:
            return "Error: API request timeout"
        except requests.exceptions.RequestException as e:
            return f"Error: HTTP request failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


# --- 注册节点到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "NakuNodeImagePrompter": NakuNodeImagePrompter
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNodeImagePrompter": "NakuNode-ImagePrompter"
}
