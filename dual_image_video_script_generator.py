# -*- coding: utf-8 -*-
import random
import json
import time
from PIL import Image
import io
import base64

# 尝試導入必要的庫，如果失敗則在調用時拋出更友好的錯誤
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
    "GLM": "zai-org/GLM-4.6V"
}


class DualImageVideoScriptGenerator:
    """
    双图视频脚本生成器 - 基于两张图片生成专业的视频分镜脚本
    """

    @classmethod
    def INPUT_TYPES(s):
        # 創建AI服務商列表
        provider_list = ["智谱AI", "硅基流动"]

        inputs = {
            "required": {
                "起始图片": ("IMAGE", {}),
                "结束图片": ("IMAGE", {}),
                "用户描述": ("STRING", {"multiline": True, "default": "根据两张图片生成一段连贯的视频分镜脚本"}),
                "AI服务商": (provider_list,),
                "API_KEY": ("STRING", {"multiline": False, "default": "选择内置服务商时无需填写"}),
                "随机种子": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

        # 动态添加所有专业选项分类，并设默认为"无"
        for category, options_list in PRO_OPTIONS.items():
            inputs["required"][category] = (options_list, {"default": "无"})

        inputs["optional"] = {
            "硅基流动模型选择": (["QWENVL", "GLM"], {"default": "QWENVL"}),  # 仅在选择硅基流动时使用
        }

        return inputs

    RETURN_TYPES = ("STRING", "STRING")  # AI改写提示词, 初始提示词
    RETURN_NAMES = ("AI 改写提示词", "初始提示词")
    FUNCTION = "generate_script"
    CATEGORY = "NakuNode/提示词生成"

    def tensor_to_base64(self, image_tensor):
        """将张量转换为base64编码的图片"""
        if image_tensor is None:
            return None

        try:
            import numpy as np
        except ImportError:
            print("[NakuNode DualImageScriptGen] Warning: numpy is not installed.")
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
            print(f"[NakuNode DualImageScriptGen] Image resized to {img.width}x{img.height} to prevent API errors.")

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
            r'<.*?>',  # 移除所有HTML/XML风格的标签
        ]

        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL)

        # 清理多余的空白字符
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # 移除多余的空行
        cleaned_text = cleaned_text.strip()

        return cleaned_text

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

    def call_llm_api(self, provider, api_key, prompt, start_image_base64, end_image_base64, siliconflow_model_choice="QWENVL"):
        # 新的系统提示词
        system_prompt = """你是一位专业视频导演，参考视频生成一段完整的，视频分镜脚本，不要废话，以自然语言呈现，不要表格形式。脚本一共5秒，完整一段输出。这段视频是通过两个图片判断其内在逻辑，联系，生成一段连贯的，有逻辑的，专业的视频分镜脚本。在创作时，需要严格按照如下需求：
1、分析两张图片，起始图和结尾图的差异，如两个图片差异较小，请专注于动态细节的表示，让动作更佳自然的变换，如两个图片差异较大，比如场景改变等，用明确的详细的运镜方式让整个画面的衔接更流畅。
2、描述时候不要废话，时长一般为 5-6秒，需要在逻辑范围内视频可以表现出该时长的镜头，避免描述过于抽象，请明确场景内主角，环境，场景，特效等变化
3、核心描述为图像间的合理变化，镜头的合理变化，环境的合理变化，特效的合理变化，场景的变化，动作的变化，服装的变化等等
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
镜头描述-镜头尺寸：标准焦距、中焦距、广角、长焦、望远、超广角-鱼眼
镜头描述-镜头角度：过肩角度、高角度、低角度、平视角度、倾斜角度、航拍、俯视角度、贴地角度
镜头描述-镜头类型：单人镜头、双人镜头、三人镜头、群像镜头、定场镜头
色调 暖色调、冷色调、高饱和度、低饱和度等。
描述情绪：
人物情绪：愤怒、恐惧、高兴、悲伤、惊讶、诧异、微笑、淡定、忧伤、痛苦。
描述运镜：
基础运镜 镜头推进、镜头拉远、镜头向右移动、镜头向左移动、 镜头上摇 高级运镜 手持镜头、复合运镜、跟随镜头、环绕运镜
风格化-视觉风格 毛毡风格、3D卡通、像素风格、木偶动画、3D游戏、黏土风格、二次元、水彩画、黑白动画、油画风格 风格化-特效镜头 移轴摄影、延时拍摄。
6、特別注意：确保镜头与镜头之间的衔接流畅，不能出现例如「手持跟拍轨道推进」这种不合理的运镜方式，因为手持跟拍是有抖动的，轨道推进是平滑的。最终输出一段中文的自然语言，不能换行，不能在段头和段尾增加意义不明的符号，提示词以：中文提示词/... 这样的格式输出。例如：中文提示词/一位身穿红色西装外套的女性..."""

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
                    {"type": "text", "text": f"根据以下用户描述和两张图片，生成视频分镜脚本：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{start_image_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{end_image_base64}"}}
                ]}
            ]
            payload = {"model": "glm-4v-plus", "messages": messages, "stream": False}
            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

        elif provider == "OpenRouter":
            headers["Authorization"] = f"Bearer {api_key}"
            headers["HTTP-Referer"] = "http://localhost"
            # 构建消息，包含图片
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"根据以下用户描述和两张图片，生成视频分镜脚本：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{start_image_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{end_image_base64}"}}
                ]}
            ]
            payload = {"messages": messages, "model": "qwen/qwen2-vl-7b-instruct:free", "stream": False}
            api_url = "https://openrouter.ai/api/v1/chat/completions"
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
                    {"type": "text", "text": f"根据以下用户描述和两张图片，生成视频分镜脚本：{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{start_image_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{end_image_base64}"}}
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

    def generate_script(self, 起始图片, 结束图片, 用户描述, AI服务商, API_KEY, 随机种子, 硅基流动模型选择="QWENVL", **kwargs):
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
        start_image_base64 = self.tensor_to_base64(起始图片)
        end_image_base64 = self.tensor_to_base64(结束图片)
        
        if not start_image_base64 or not end_image_base64:
            raise ValueError("無法處理輸入的圖片")

        # 構建請求
        full_prompt = f"用戶描述：{full_description}"

        try:
            print(f"[NakuNode DualImageScriptGen] Generating script with {AI服务商}...")
            # 如果是硅基流动服务商，传递模型选择
            if AI服务商 == "硅基流动":
                optimized_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, start_image_base64, end_image_base64, 硅基流动模型选择)
            else:
                optimized_response = self.call_llm_api(AI服务商, API_KEY, full_prompt, start_image_base64, end_image_base64)
            print(f"[NakuNode DualImageScriptGen] Generated response: {optimized_response}")

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

            # 如果解析结果太短，使用AI的完整响应
            if len(zh_part) < len(cleaned_response) / 2:
                zh_part = cleaned_response

            # 确保中文部分不是空的
            if not zh_part.strip():
                zh_part = cleaned_response

            # 返回结果 (AI改写提示词, 初始提示词)
            return (zh_part, full_description)
        except Exception as e:
            print(f"[NakuNode DualImageScriptGen] Error during LLM processing: {e}")
            # 发生错误时返回融合后的描述
            return (f"处理错误: {e}. 原始描述: {full_description}", f"Processing Error: {e}. Original: {full_description}")


# --- 註冊節點到 ComfyUI ---
NODE_CLASS_MAPPINGS = {
    "DualImageVideoScriptGenerator": DualImageVideoScriptGenerator
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "DualImageVideoScriptGenerator": "NakuNode-首尾帧视频提示词生成器"
}