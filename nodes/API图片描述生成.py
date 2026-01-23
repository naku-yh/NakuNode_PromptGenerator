# -*- coding: utf-8 -*-
import random
import json
import time
from PIL import Image
import io
import base64

# 尝试导入必要的库，如果失败则在调用时抛出更友好的错误
try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None


# SiliconFlow 模型映射
SILICONFLOW_MODELS = {
    "QWENVL": "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "GLM": "zai-org/GLM-4.6V"
}


class APIDescriptionGenerator:
    """
    API图片描述生成 - 生成客观的图片描述
    """

    @classmethod
    def INPUT_TYPES(s):
        # 创建AI服务商列表
        provider_list = ["智谱AI", "硅基流动"]

        inputs = {
            "required": {
                "图片": ("IMAGE", {}),
                "文字需求": ("STRING", {"multiline": True, "default": "请输入对图片的具体需求或补充说明"}),
                "AI服务商": (provider_list,),
                "API_KEY": ("STRING", {"multiline": False, "default": "选择内置服务商时无需填写"}),
                "随机种子": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        inputs["optional"] = {
            "硅基流动模型选择": (["QWENVL", "GLM"], {"default": "QWENVL"}),  # 仅在选择硅基流动时使用
        }

        return inputs

    RETURN_TYPES = ("STRING",)  # 输出描述
    RETURN_NAMES = ("图片描述",)
    FUNCTION = "generate_description"
    CATEGORY = "NakuNode/图片描述"

    def tensor_to_base64(self, image_tensor):
        """将张量转换为base64编码的图片"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode APIDescriptionGenerator] Warning: numpy is not installed.")
            return None

        # 转换张量到numpy数组并确保值在正确范围内
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

        # 调整图片大小以避免API错误
        MAX_DIMENSION = 1024
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = MAX_DIMENSION
                new_height = int(MAX_DIMENSION / aspect_ratio)
            else:
                new_height = MAX_DIMENSION
                new_width = int(MAX_DIMENSION * aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[NakuNode APIDescriptionGenerator] Image resized to {img.width}x{img.height} to prevent API errors.")

        # 将图片保存到内存中的缓冲区
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    def generate_zhipu_token(self, apikey: str):
        if not jwt:
            raise ImportError("pyjwt库缺失。请在您的ComfyUI环境中运行 'pip install pyjwt' 来安装。")

        try:
            id, secret = apikey.split('.')
        except Exception as e:
            raise ValueError("无效的智谱API Key，格式应为 'id.secret'", e)

        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + 60 * 60 * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }

        return jwt.encode(
            payload,
            secret,
            algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )

    def call_llm_api(self, provider, api_key, prompt, image_base64, siliconflow_model_choice="QWENVL"):
        # 新的系统提示词
        system_prompt = """你是一名图片生成专家，通过分析用户输入的图片（画风、风格、色彩搭配、氛围等等，如果有画面有文字需具体描述字体形态、字体颜色、字体大小、字体位置、字体效果等等）以及文字需求，最终以[主体描述] + [细节修饰] + [艺术风格] + [画面构图] + [光照/色彩] + [画质参数]这样的格式输出一段客观描述的自然语句，不要有废话。不要带有主观情绪的词句例如"兼具典雅传统与时尚活力""既增添神秘感与优雅气质""增添了时尚活力与异域奇幻感"等等。示例："一位身穿未来科技感银色战甲的女战士，站在火星红色荒漠上，背景是巨大的地球和星空，赛博朋克风格，电影级光影，超高清8K，细节丰富，景深强烈"。需要避免以下问题：1.模糊不清的描述（如"好看的东西"）2.自相矛盾的元素（如"白天的满天繁星"）3.过于冗长或堆砌无关词汇。"""

        if not requests:
            raise ImportError("requests库缺失。请在您的ComfyUI环境中运行 'pip install requests' 来安装。")

        headers = {"Content-Type": "application/json"}

        if not api_key or api_key == "必须填入智谱/硅基流动的API":
            raise ValueError(f"使用「{provider}」服务商时，请在API_KEY字段中填入您的API密钥。")

        if provider == "智谱AI":
            token = self.generate_zhipu_token(api_key)
            headers["Authorization"] = token
            # 构建消息，包含图片
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下文字需求和附带的图片，生成客观的图片描述：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ]
            payload = {"model": "glm-4v-plus", "messages": messages, "stream": False}
            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        elif provider == "硅基流动":
            headers["Authorization"] = f"Bearer {api_key}"
            # 构建消息，包含图片
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下文字需求和附带的图片，生成客观的图片描述：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ]
            # 根据用户选择的硅基流动模型选择对应的模型
            model = SILICONFLOW_MODELS.get(siliconflow_model_choice, "Qwen/Qwen-VL-Chat")  # 默认为QwenVL
            payload = {"messages": messages, "model": model, "stream": False}
            api_url = "https://api.siliconflow.cn/v1/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        return prompt

    def generate_description(self, 图片, 文字需求, AI服务商, API_KEY, 随机种子, 硅基流动模型选择="QWENVL"):
        # 设置随机种子
        if 随机种子 == -1:
            随机种子 = random.randint(0, 0xffffffffffffffff)
        random.seed(随机种子)

        # 将图片转换为base64
        image_base64 = self.tensor_to_base64(图片)
        if not image_base64:
            raise ValueError("无法处理输入的图片")

        # 构建请求
        full_prompt = f"文字需求：{文字需求}"

        try:
            print(f"[NakuNode APIDescriptionGenerator] Generating description with {AI服务商}...")
            # 如果是硅基流动服务商，传递模型选择
            if AI服务商 == "硅基流动":
                description_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, image_base64, 硅基流动模型选择)
            else:
                description_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, image_base64)
            print(f"[NakuNode APIDescriptionGenerator] Generated description: {description_response}")

            # 返回AI生成的描述
            return (description_response,)
        except Exception as e:
            print(f"[NakuNode APIDescriptionGenerator] Error during description generation: {e}")
            # 发生错误时返回错误信息
            return (f"生成错误: {e}. 请检查API密钥和网络连接。",)


# --- 注册节点到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "APIDescriptionGenerator": APIDescriptionGenerator
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "APIDescriptionGenerator": "NakuNode-API图片描述生成"
}