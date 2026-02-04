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


# =================================================================================
# == 专业视频提示词选项库 (Pro-V1) ==
# =================================================================================
PRO_OPTIONS = {
    "艺术风格": [
        "随机", "无", "超现实主义", "印象派", "赛博朋克", "蒸汽朋克", "日本浮世绘", "动漫风格", "黏土动画",
        "像素艺术", "卡通渲染", "图形小说风格", "水墨画", "装饰艺术", "哥特式风格", "巴洛克风格",
        "未来主义", "蒸汽波", "低多边形", "故障艺术", "概念艺术", "极简主义", "技术原理图",
        "手绘素描", "油画质感"
    ],
    "景别": [
        "随机", "无", "远景", "大远景", "全景", "中全景", "牛仔景", "中景", "中近景",
        "近景", "大特写", "特写", "插入镜头", "反应镜头", "双人镜头", "三人镜头", "群体镜头",
        "建置镜头", "细节镜头", "单人镜头", "宏观镜头", "定场镜头", "环境肖像", "全景风光",
        "航拍远景"
    ],
    "相机角度": [
        "随机", "无", "平视角度", "高角度", "低角度", "鸟瞰视角", "仰视视角", "荷兰角/斜角",
        "过肩视角", "主观视角(POV)", "侧面视角", "正面视角", "背面视角", "臀部高度视角",
        "地面高度视角", "膝盖高度视角", "上帝视角", "倾斜视角", "镜像反射视角", "锁定视角",
        "广角畸变视角", "望远镜视角", "显微镜视角", "门框窥视视角", "仪表盘视角"
    ],
    "移动与运镜": [
        "随机", "无", "平摇", "俯仰", "推轨", "拉轨", "滑动变焦", "横向滑动", "升降", "手持拍摄",
        "斯坦尼康", "无人机航拍", "第一人称穿越机(FPV)", "弧形运镜", "旋转镜头(Roll)",
        "跟拍", "变焦", "快速推近", "环绕拍摄", "探索性运镜", "固定镜头", "摇臂镜头",

        "穿梭镜头", "身体摄像头", "慢速推轨"
    ],
    "透镜与焦点": [
        "随机", "无", "浅景深", "深景深", "焦点转移", "广角镜头", "长焦镜头", "标准镜头", "鱼眼镜头",
        "变形宽银幕镜头", "微距镜头", "移轴镜头", "柔焦效果", "锐利对焦", "失焦模糊(散景)",
        "针孔效果", "分焦镜效果", "镜头呼吸效应", "红外镜头", "紫外镜头", "热成像镜头",
        "自定义散景形状", "前景模糊", "背景模糊", "全景深"
    ],
    "光线与照明": [
        "随机", "无", "三点布光", "伦勃朗光", "蝴蝶光", "环形光", "分割光", "硬光", "柔光",
        "高调布光", "低调布光", "边缘光", "剪影", "体积光", "耶稣光/曙光", "霓虹灯光",
        "自然光", "黄金时刻", "蓝色时刻", "神奇时刻", "环境光", "顶光", "底光", "烛光", "频闪光"
    ],
    "色彩与色调": [
        "随机", "无", "单色", "互补色", "类似色", "三色系", "饱和度高", "饱和度低/褪色", "暖色调",
        "冷色调", "电影感青橙色调", "漂白效果", "交叉冲洗", "复古胶片色", "LOMO风格",
        "高对比度", "低对比度", "粉彩色调", "双色调", "红外色彩", "选择性色彩", "霓虹色谱",
        "赛璐珞动画色", "暗调/黑色电影", "明亮鲜活"
    ],
    "材质与质感": [
        "随机", "无", "抛光金属", "生锈金属", "碳纤维", "粗糙木材", "光滑玻璃", "磨砂玻璃",
        "半透明水晶", "粗糙混凝土", "光滑大理石", "柔软织物", "皮革质感", "液体质感",
        "全息显示", "哑光表面", "高光泽表面", "丝绸质感", "多毛/毛茸茸", "鳞片质感",
        "生物发光", "粘液质感", "折纸质感", "陶瓷质感", "腐朽/风化"
    ],
    "视觉与后期效果": [
        "随机", "无", "镜头光晕", "动态模糊", "色差", "光线溢出/辉光", "电影颗粒", "暗角",
        "光泄露", "故障/数据损坏", "延时摄影", "慢动作", "粒子效果(火花/尘埃)", "烟雾/薄雾",
        "HUD/UI界面叠加", "全息投影", "像素化", "热浪扭曲", "水下扭曲", "定格动画",
        "光绘/光迹", "倒放效果", "万花筒效果", "鱼眼畸变", "扫描线/CRT效果"
    ]
}

# SiliconFlow 模型映射
SILICONFLOW_MODELS = {
    "QWENVL": "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "GLM": "zai-org/GLM-4.6V",
    "KIMI": "Pro/moonshotai/Kimi-K2.5"
}


class NakuNodeLTXPrompter:
    """
    LTX视频提示词生成器 - 基于图片和描述生成LTX Video专用提示词
    """

    @classmethod
    def INPUT_TYPES(s):
        # 创建AI服务商列表
        provider_list = ["智谱AI", "硅基流动"]

        inputs = {
            "required": {
                "图片": ("IMAGE", {}),
                "用户描述": ("STRING", {"multiline": True, "default": "一只可爱的小猫在阳光下玩耍"}),
                "AI服务商": (provider_list,),
                "API_KEY": ("STRING", {"multiline": False, "default": "选择内置服务商时无需填写"}),
                "随机种子": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        # 动态添加所有专业选项分类，并设默认为"无"
        for category, options_list in PRO_OPTIONS.items():
            inputs["required"][category] = (options_list, {"default": "无"})

        inputs["optional"] = {
            "硅基流动模型选择": (["QWENVL", "GLM", "KIMI"], {"default": "QWENVL"}),  # 仅在选择硅基流动时使用
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")  # AI生成提示词, 初始提示词
    RETURN_NAMES = ("AI 生成提示词", "初始提示词")
    FUNCTION = "generate_ltx_prompt"
    CATEGORY = "NakuNode/提示词生成"

    def tensor_to_base64(self, image_tensor):
        """将张量转换为base64编码的图片"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode LTXPrompter] Warning: numpy is not installed.")
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
            print(f"[NakuNode LTXPrompter] Image resized to {img.width}x{img.height} to prevent API errors.")

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
        # LTX Video 专用系统提示词
        system_prompt = """Role
你是一位专精于 LTX Video (Lightricks Video Model) 的 AI 视频导演。你深入理解 LTX Video 基于 DiT 架构的特性，知晓它是如何通过 T5 文本编码器处理自然语言的。你的任务是将用户简单的想法，转化为符合 LTX Video 最佳实践的、电影级的详细提示词（Prompt）。

Skills
分析参考图，并用自然语言编写：你摒弃传统的"标签堆砌（Tag salad）"写法，擅长将关键词扩展为流畅、描述性强的英语长句。
时空连续性构建：你特别注重描述视频中的"变化"和"动作轨迹"，确保生成的视频不是动态 PPT，而是有真实物理交互的短片。
电影镜头语言：熟练运用 Slow zoom in, Handheld camera shake, Rack focus, Drone shot 等术语来定义视觉风格。
环境氛围营造：通过描述光线（如 Volumetric lighting）、天气和材质质感来增强真实感。
Workflow
意图识别：分析用户提供的原始想法（主体是什么？动作是什么？风格是什么？）。
结构化扩充 (The LTX Formula)：
Subject (主体)：详细描述外观、纹理、颜色。
Action (动作)：使用动词描述即时发生的动作（e.g., "The girl turns her head slowly" 而不是 "A turned head"）。
Environment (环境)：描述背景、氛围、光照。
Camera (运镜)：指定观察视角和镜头运动。
负面词过滤：确保不使用 Negative Prompts（因为 LTX Video 不需要/不支持），也不堆砌 4k, best quality 等无意义词汇。
最终输出：输出一段连贯的、约 100-200 词的英文段落。
Constraints
禁止标签化：不要输出 tag1, tag2, tag3 这种格式，必须是完整的英文句子。
专注可见性：只描述视觉上能看到的东西，不要描述心理活动或抽象概念。
首句点题：提示词的第一句话必须清晰定义主体和核心动作，因为 T5 编码器对头部信息最敏感。
Output Format
请按照以下格式输出：(不要出现无关的废话)

[A detailed, descriptive paragraph in English. Starts with the main subject and action. Includes specific details about lighting, texture, and camera movement. Flowing naturally without breaking into comma-separated tags.]"""

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
                    {"type": "text", "text": f"根据以下用户描述和附带的图片，生成LTX Video专用提示词：{prompt}"},
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
                    {"type": "text", "text": f"根据以下用户描述和附带的图片，生成LTX Video专用提示词：{prompt}"},
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

    def generate_ltx_prompt(self, 图片, 用户描述, AI服务商, API_KEY, 随机种子, 硅基流动模型选择="QWENVL", **kwargs):
        # 设置随机种子
        if 随机种子 == -1:
            随机种子 = random.randint(0, 0xffffffffffffffff)
        random.seed(随机种子)

        # 将专业选项融合到用户描述后面，使用逗号分隔
        parts = [用户描述]
        for category, options_list in PRO_OPTIONS.items():
            selected = kwargs.get(category)

            if selected == "无":
                continue
            elif selected == "随机":
                # 从选项列表中排除"随机"和"无"
                valid_options = [opt for opt in options_list if opt not in ["随机", "无"]]
                if valid_options:
                    chosen = random.choice(valid_options)
                    parts.append(chosen)
            else:
                parts.append(selected)

        full_description = "，".join(filter(None, parts))

        # 将图片转换为base64
        image_base64 = self.tensor_to_base64(图片)
        if not image_base64:
            raise ValueError("无法处理输入的图片")

        # 构建请求
        full_prompt = f"用户描述：{full_description}"

        try:
            print(f"[NakuNode LTXPrompter] Generating LTX prompt with {AI服务商}...")
            # 如果是硅基流动服务商，传递模型选择
            if AI服务商 == "硅基流动":
                optimized_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, image_base64, 硅基流动模型选择)
            else:
                optimized_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, image_base64)
            print(f"[NakuNode LTXPrompter] Generated response: {optimized_response}")

            # 返回结果 (AI生成提示词, 初始提示词)
            return (optimized_response, full_description)
        except Exception as e:
            print(f"[NakuNode LTXPrompter] Error during LLM processing: {e}")
            # 发生错误时返回融合后的描述
            return (f"处理错误: {e}. 原始描述: {full_description}", f"Processing Error: {e}. Original: {full_description}")


# --- 注册节点到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "NakuNodeLTXPrompter": NakuNodeLTXPrompter
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "NakuNodeLTXPrompter": "NakuNode-LTXPrompter"
}